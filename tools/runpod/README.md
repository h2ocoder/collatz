# RunPod tools

Rent CPU pods for the tree searches, and make sure none is ever left running.

| File | What it does |
|---|---|
| `runpod_api.py` | Minimal REST client. `python tools/runpod/runpod_api.py list` shows every pod and the hourly burn; `kill-ours` terminates this project's pods; `kill-all --yes` terminates everything in the account. |
| `launch_search.py` | Splits one search across K pods, fetches the results, terminates the pods. **Dry run unless `--launch`.** |
| `watchdog.py` | Hourly check. Terminates our overdue pods, reports anything else that is running, pops up a Windows message. |
| `install_watchdog.ps1` | Registers the hourly scheduled task `CollatzRunPodWatchdog` (copies the scripts to `~/.runpod/`). `-Remove` uninstalls. |

## One-time setup

1. In the RunPod console: add a **fixed amount of prepaid credit** (for example $25) and turn **auto-reload off**. The balance is then the most that can ever be lost.
2. Create an API key. Give it to the tools in one of two ways — never paste it into a chat or commit it:
   - `setx RUNPOD_API_KEY "<key>"` (then open a new terminal), or
   - put it on one line in `%USERPROFILE%\.runpod\api_key`.
3. `pwsh tools/runpod/install_watchdog.ps1` (already done on this machine on 2026-09-19).
4. Check: `python tools/runpod/runpod_api.py list`.

## Running a search

    python tools/runpod/launch_search.py --bits 64 --pods 10 --max-minutes 60 --max-usd 30            # dry run
    python tools/runpod/launch_search.py --bits 64 --pods 10 --max-minutes 60 --max-usd 30 --launch   # spends money
    python tools/runpod/launch_search.py --program family --bits 44 --pods 4 --max-minutes 30 --max-usd 10 --launch 000

Results land in `research/investigate-pinball-analogy/results/runpod/<job>-<expiry>/`; for `double_halving` the shards are merged and the leaf count is checked against the Fibonacci number.

## Why a pod cannot be left running

1. `launch_search.py` terminates every pod it created in a `finally` block — normal exit, error, or Ctrl-C.
2. Each pod runs under `timeout`, then tries to terminate itself.
3. Every pod is named `collatz-<job>-x<expiry>`. The hourly watchdog terminates any such pod past its expiry, from any machine, with no local state.
4. Pods are created with no persistent volume, so a terminated pod leaves no storage charge behind.
5. Anything running that is *not* ours is reported, with a pop-up, but never touched unless you pass `--kill-foreign`.

Log: `%USERPROFILE%\.runpod\watchdog.log`.

## Not yet verified against the live API

Written from the public API reference without a key, so the first real run should be a tiny one (`--bits 40 --pods 1 --vcpus 4 --max-minutes 5 --max-usd 1`):

- that `rust:1-bookworm` starts as a CPU pod and the proxy URL `https://<pod-id>-8000.proxy.runpod.net/` serves the results;
- that a ~7 KB environment variable (the packed crate) is accepted;
- whether the pod-scoped `RUNPOD_API_KEY` is allowed to terminate its own pod (layer 2). Layers 1 and 3 do not depend on it;
- the real price per vCPU-hour (the launcher re-checks the budget against the price the API returns for the first pod).
