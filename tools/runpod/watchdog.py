"""Hourly safety net: make sure no RunPod pod is quietly draining the account.

Rules
  1. A pod of ours (name 'collatz-<job>-x<expiry>') that is past its expiry is
     TERMINATED. No questions: the launcher set that deadline itself.
  2. Any other running pod is REPORTED, never touched, because it may be work that
     has nothing to do with this project. Use --kill-foreign to terminate those too.
  3. Everything is appended to ~/.runpod/watchdog.log, and a Windows pop-up is shown
     whenever something was running or was terminated.

Exit code: 0 nothing running, 1 something running or terminated, 2 could not check
(network error, rejected key). That also raises a pop-up, because a watchdog that
fails silently is worse than none. The one quiet case is "no key configured yet".

Designed to be run from Task Scheduler by install_watchdog.ps1, from a copy in
~/.runpod/ so it keeps working if the git worktree is deleted.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runpod_api import Client, NoKeyError, RunPodError, summarize  # noqa: E402

LOG = Path.home() / ".runpod" / "watchdog.log"


def decide(rows: list[dict], kill_foreign: bool = False):
    """Pure decision function: returns (to_terminate, to_report)."""
    terminate, report = [], []
    for row in rows:
        if not row["running"]:
            continue
        if row["ours"] and row["overdue"]:
            terminate.append(row)
        elif not row["ours"] and kill_foreign:
            terminate.append(row)
        else:
            report.append(row)
    return terminate, report


def log(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(time.strftime("%Y-%m-%d %H:%M:%S ") + line + "\n")
    print(line)


def popup(text: str) -> None:
    """Best-effort Windows notification; never raises."""
    try:
        subprocess.run(["msg", "*", "/TIME:3600", text[:250]], timeout=20, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def main(argv) -> int:
    kill_foreign = "--kill-foreign" in argv
    quiet = "--no-popup" in argv
    try:
        client = Client()
        rows = summarize(client.list_pods())
    except NoKeyError as err:
        # not configured yet: nothing can be running under a key we do not have. Log, no pop-up.
        log(f"not configured: {err}")
        return 2
    except (RunPodError, OSError) as err:
        log(f"CHECK FAILED: {err}")
        if not quiet:
            popup(f"RunPod watchdog could not check your pods: {err}")
        return 2

    terminate, report = decide(rows, kill_foreign)
    for row in terminate:
        try:
            client.delete_pod(row["id"])
            log(f"TERMINATED {row['name']} ({row['id']}) at ${row['cost_per_hr']:.3f}/h "
                f"- {'overdue' if row['ours'] else 'foreign pod, --kill-foreign'}")
        except RunPodError as err:
            log(f"FAILED TO TERMINATE {row['name']} ({row['id']}): {err}")
    for row in report:
        left = f", {row['minutes_left']} min left" if row["ours"] else ", NOT created by this project"
        log(f"RUNNING {row['name']} ({row['id']}) at ${row['cost_per_hr']:.3f}/h{left}")
    if not terminate and not report:
        log("ok: nothing running")
        return 0

    burn = sum(r["cost_per_hr"] for r in report)
    message = (f"RunPod: {len(report)} pod(s) running (${burn:.2f}/hour), "
               f"{len(terminate)} overdue pod(s) terminated. See {LOG}")
    if not quiet:
        popup(message)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
