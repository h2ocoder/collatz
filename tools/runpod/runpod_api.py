"""Minimal RunPod REST client (standard library only).

API reference: https://docs.runpod.io/api-reference  (base URL https://rest.runpod.io/v1)

The API key is read from the environment variable RUNPOD_API_KEY, or from the file
~/.runpod/api_key (one line). It is never written to disk by this code and never
printed.

Every pod this project creates is named

    collatz-<job>-x<expiry>

where <expiry> is a Unix timestamp. The name is the single source of truth for
"this pod is ours" and "this pod should be gone by now", so the watchdog needs no
local state and works from any machine.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://rest.runpod.io/v1"
PREFIX = "collatz-"
KEY_FILE = Path.home() / ".runpod" / "api_key"
_NAME = re.compile(r"^collatz-(?P<job>[a-z0-9-]+)-x(?P<expiry>\d{9,11})$")


class RunPodError(RuntimeError):
    pass


class NoKeyError(RunPodError):
    """No API key configured yet (as opposed to a key that fails)."""


def api_key() -> str:
    key = os.environ.get("RUNPOD_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise NoKeyError(f"no API key: set RUNPOD_API_KEY or write it to {KEY_FILE}")
    return key


def pod_name(job: str, expiry: int) -> str:
    """Example: pod_name('dh64-s3', 1790000000) = 'collatz-dh64-s3-x1790000000'"""
    job = re.sub(r"[^a-z0-9-]", "-", job.lower()).strip("-")
    return f"{PREFIX}{job}-x{int(expiry)}"


def parse_name(name: str):
    """Return (job, expiry) for one of our pods, or None for anything else."""
    m = _NAME.match(name or "")
    return (m.group("job"), int(m.group("expiry"))) if m else None


def is_running(pod: dict) -> bool:
    return pod.get("desiredStatus") == "RUNNING"


class Client:
    """Thin wrapper; `transport` can be replaced in tests."""

    def __init__(self, key: str | None = None, transport=None):
        self._key = key
        self._transport = transport or self._http

    def _http(self, method: str, path: str, body=None):
        request = urllib.request.Request(
            BASE_URL + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": f"Bearer {self._key or api_key()}",
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                text = response.read().decode()
                return json.loads(text) if text.strip() else None
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")[:400]
            raise RunPodError(f"{method} {path} -> HTTP {err.code}: {detail}") from None

    def list_pods(self) -> list[dict]:
        return self._transport("GET", "/pods") or []

    def get_pod(self, pod_id: str) -> dict:
        return self._transport("GET", f"/pods/{pod_id}")

    def delete_pod(self, pod_id: str) -> None:
        """Terminate the pod. This is what stops billing."""
        self._transport("DELETE", f"/pods/{pod_id}")

    def create_cpu_pod(self, name: str, vcpus: int, image: str, start_cmd: list[str], env: dict,
                       flavors=("cpu5c", "cpu3c"), cloud_type="SECURE", disk_gb=10) -> dict:
        body = {
            "name": name, "computeType": "CPU", "cpuFlavorIds": list(flavors), "vcpuCount": vcpus,
            "imageName": image, "dockerStartCmd": start_cmd, "env": env,
            "containerDiskInGb": disk_gb, "volumeInGb": 0, "ports": ["8000/http"],
            "cloudType": cloud_type, "interruptible": False,
        }
        return self._transport("POST", "/pods", body)


def summarize(pods: list[dict], now: float | None = None) -> list[dict]:
    """One row per pod: ours or not, running or not, overdue or not, hourly cost."""
    now = time.time() if now is None else now
    rows = []
    for pod in pods:
        parsed = parse_name(pod.get("name", ""))
        rows.append({
            "id": pod.get("id"), "name": pod.get("name"), "running": is_running(pod),
            "ours": parsed is not None,
            "overdue": bool(parsed and now > parsed[1]),
            "minutes_left": round((parsed[1] - now) / 60) if parsed else None,
            "cost_per_hr": pod.get("adjustedCostPerHr") or pod.get("costPerHr") or 0,
        })
    return rows


if __name__ == "__main__":
    import sys
    client = Client()
    command = sys.argv[1] if len(sys.argv) > 1 else "list"
    if command == "list":
        rows = summarize(client.list_pods())
        running = [r for r in rows if r["running"]]
        print(f"{len(rows)} pods, {len(running)} running, "
              f"burning ${sum(r['cost_per_hr'] for r in running):.2f}/hour")
        for r in rows:
            print(f"  {r['id']}  {r['name']:<40} running={r['running']} ours={r['ours']} "
                  f"overdue={r['overdue']} ${r['cost_per_hr']:.3f}/h")
    elif command == "kill-ours":
        for r in summarize(client.list_pods()):
            if r["ours"]:
                client.delete_pod(r["id"])
                print("terminated", r["name"])
    elif command == "kill-all":
        if "--yes" not in sys.argv:
            sys.exit("kill-all terminates EVERY pod in the account, not only this project's. Add --yes.")
        for r in summarize(client.list_pods()):
            client.delete_pod(r["id"])
            print("terminated", r["name"])
    else:
        sys.exit("usage: runpod_api.py [list | kill-ours | kill-all --yes]")
