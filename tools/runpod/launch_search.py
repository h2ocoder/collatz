"""Run one tree search split across several RunPod CPU pods, fetch the results, tear everything down.

    python tools/runpod/launch_search.py --bits 64 --pods 10 --max-minutes 90 --max-usd 20            (dry run)
    python tools/runpod/launch_search.py --bits 64 --pods 10 --max-minutes 90 --max-usd 20 --launch   (spends money)

How it works, with no SSH and no custom image:
  * The Rust crate (scripts/double_halving_rs) is packed into a base64 tarball and handed to
    each pod in an environment variable.
  * Each pod (image rust:1-bookworm) builds it, runs shard k/K under `timeout`, writes
    result.json and a DONE marker into /work/out, and serves that folder on port 8000,
    which RunPod exposes at https://<pod-id>-8000.proxy.runpod.net/.
  * This script polls for DONE, downloads the result, and terminates the pod straight away.

Three independent layers make sure nothing is left running:
  1. try/finally here terminates every pod this run created, including on Ctrl-C or a crash.
  2. Each pod tries to terminate itself when it finishes or hits its time limit.
  3. Every pod name carries its expiry time; tools/runpod/watchdog.py (hourly) terminates
     any of our pods that is past it.

Money guards: a dry run is the default; --max-usd is checked against the ACTUAL hourly price
returned by the first pod, and the run aborts (terminating that pod) if the worst case exceeds it.
"""

import argparse
import base64
import io
import json
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))
from runpod_api import Client, RunPodError, pod_name  # noqa: E402

CRATE = ROOT / "scripts" / "double_halving_rs"
IMAGE = "rust:1-bookworm"
GRACE_MINUTES = 20            # build time + fetch time on top of the compute limit

POD_SCRIPT = r"""
set -u
mkdir -p /work/out && cd /work
say() { echo "$(date -u +%H:%M:%S) $*" | tee -a /work/out/status.txt; }
command -v python3 >/dev/null || (apt-get update -qq && apt-get install -y -qq python3 >/dev/null)
(cd /work/out && python3 -m http.server 8000 >/dev/null 2>&1 &)
say "unpacking"
echo "$SRC_B64" | base64 -d | tar xz
say "building"
cargo build --release >/work/out/build.log 2>&1 || { say "BUILD FAILED"; echo 101 > /work/out/exit_code; touch /work/out/DONE; }
if [ ! -f /work/out/DONE ]; then
  say "running $PROGRAM $ARGS on $(nproc) threads, limit ${MAX_MINUTES}m"
  FAMILY_SHARD="$SHARD" timeout "${MAX_MINUTES}m" ./target/release/$PROGRAM $ARGS >/work/out/result.json 2>/work/out/err.log
  echo $? > /work/out/exit_code
  say "finished with exit code $(cat /work/out/exit_code)"
  touch /work/out/DONE
fi
sleep "${LINGER_SECONDS}"
say "self-terminating"
curl -s -X DELETE -H "Authorization: Bearer ${RUNPOD_API_KEY:-}" "https://rest.runpod.io/v1/pods/${RUNPOD_POD_ID:-none}" || true
sleep 3600
"""


def pack_crate() -> str:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for path in sorted(CRATE.rglob("*")):
            relative = path.relative_to(CRATE)
            if path.is_file() and relative.parts[0] != "target":
                tar.add(path, arcname=str(relative).replace("\\", "/"))
    return base64.b64encode(buffer.getvalue()).decode()


def program_args(program: str, bits: int, vcpus: int, shard: str, extra: list[str]) -> str:
    if program == "double_halving":
        return f"{bits} {vcpus} {shard}"
    if program == "family":
        return f"{bits} {vcpus} " + " ".join(extra)          # shard passed via FAMILY_SHARD
    raise SystemExit(f"unknown program {program}")


def fetch(pod_id: str, name: str, timeout=30):
    url = f"https://{pod_id}-8000.proxy.runpod.net/{name}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode(errors="replace")
    except (urllib.error.URLError, OSError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--program", default="double_halving", choices=["double_halving", "family"])
    parser.add_argument("--bits", type=int, required=True)
    parser.add_argument("--pods", type=int, default=4)
    parser.add_argument("--vcpus", type=int, default=32, help="vCPUs per pod (RunPod CPU pods top out at 32)")
    parser.add_argument("--max-minutes", type=int, required=True, help="hard compute limit per pod")
    parser.add_argument("--max-usd", type=float, required=True, help="abort if the worst case costs more")
    parser.add_argument("--assumed-usd-per-vcpu-hour", type=float, default=0.06)
    parser.add_argument("--cloud", default="SECURE", choices=["SECURE", "COMMUNITY"])
    parser.add_argument("--job", default=None)
    parser.add_argument("--launch", action="store_true", help="actually create pods; without it, dry run")
    parser.add_argument("extra", nargs="*", help="forbidden factors for --program family")
    args = parser.parse_args()

    job = args.job or f"{'dh' if args.program == 'double_halving' else 'fam'}{args.bits}"
    hours = (args.max_minutes + GRACE_MINUTES) / 60
    estimate = args.pods * args.vcpus * args.assumed_usd_per_vcpu_hour * hours
    print(f"job {job}: {args.pods} pods x {args.vcpus} vCPU, limit {args.max_minutes} min (+{GRACE_MINUTES} grace)")
    print(f"worst-case cost at the ASSUMED ${args.assumed_usd_per_vcpu_hour}/vCPU-h: ${estimate:.2f}   budget ${args.max_usd:.2f}")
    if estimate > args.max_usd:
        sys.exit("refusing: the estimate already exceeds --max-usd")
    source = pack_crate()
    print(f"crate packed: {len(source):,} base64 characters")
    if not args.launch:
        print("DRY RUN - nothing created. Add --launch to spend money.")
        return

    client = Client()
    expiry = int(time.time() + (args.max_minutes + GRACE_MINUTES) * 60)
    out_dir = ROOT / "research" / "investigate-pinball-analogy" / "results" / "runpod" / f"{job}-{expiry}"
    out_dir.mkdir(parents=True, exist_ok=True)
    created, pending, results = [], {}, []
    try:
        for k in range(args.pods):
            shard = f"{k}/{args.pods}"
            env = {"SRC_B64": source, "PROGRAM": args.program, "SHARD": shard,
                   "ARGS": program_args(args.program, args.bits, args.vcpus, shard, args.extra),
                   "MAX_MINUTES": str(args.max_minutes), "LINGER_SECONDS": "900"}
            pod = client.create_cpu_pod(pod_name(f"{job}-s{k}", expiry), args.vcpus, IMAGE,
                                        ["bash", "-c", POD_SCRIPT], env, cloud_type=args.cloud)
            created.append(pod["id"])
            pending[pod["id"]] = k
            price = pod.get("adjustedCostPerHr") or pod.get("costPerHr") or 0
            print(f"  created shard {shard}: pod {pod['id']} at ${price:.3f}/h")
            if k == 0 and price * hours * args.pods > args.max_usd:
                raise SystemExit(f"aborting: real price ${price:.3f}/h per pod makes the worst case "
                                 f"${price * hours * args.pods:.2f} > budget ${args.max_usd:.2f}")

        while pending and time.time() < expiry:
            time.sleep(30)
            for pod_id, k in list(pending.items()):
                if fetch(pod_id, "DONE") is None:
                    continue
                code = (fetch(pod_id, "exit_code") or "?").strip()
                for name in ("result.json", "err.log", "build.log", "status.txt"):
                    text = fetch(pod_id, name)
                    if text is not None:
                        (out_dir / f"shard{k}_{name}").write_text(text, encoding="utf-8")
                client.delete_pod(pod_id)
                created.remove(pod_id)
                del pending[pod_id]
                print(f"  shard {k} done (exit {code}); pod {pod_id} terminated; {len(pending)} still running")
                if code == "0":
                    results.append(out_dir / f"shard{k}_result.json")
        if pending:
            print(f"TIME LIMIT: shards {sorted(pending.values())} did not finish")
    finally:
        for pod_id in list(created):
            try:
                client.delete_pod(pod_id)
                print(f"  cleanup: terminated {pod_id}")
            except RunPodError as err:
                print(f"  CLEANUP FAILED for {pod_id}: {err}  <-- terminate it by hand: "
                      f"python tools/runpod/runpod_api.py kill-ours")

    if args.program == "double_halving" and len(results) == args.pods:
        import contextlib
        from merge_search_shards import main as merge
        with open(out_dir / "merged.json", "w") as handle, contextlib.redirect_stdout(handle):
            merge([str(p) for p in results])
        merged = json.loads((out_dir / "merged.json").read_text())
        print(f"merged: {merged['leaves']:,} leaves, record {merged['best'][0]}, results in {out_dir}")
    else:
        print(f"{len(results)}/{args.pods} shards succeeded; results in {out_dir}")


if __name__ == "__main__":
    main()
