"""Tests for tools/runpod: naming, watchdog decisions, client plumbing. No network, no API key."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "runpod"))

import runpod_api  # noqa: E402
import watchdog  # noqa: E402


# ---- pod names carry the expiry ----

def test_pod_name_round_trip():
    """The name encodes job and expiry and parses back."""
    name = runpod_api.pod_name("dh64-s3", 1790000000)
    assert name == "collatz-dh64-s3-x1790000000"
    assert runpod_api.parse_name(name) == ("dh64-s3", 1790000000)


def test_pod_name_is_sanitised():
    assert runpod_api.pod_name("My Job_1", 1790000000) == "collatz-my-job-1-x1790000000"


def test_foreign_names_do_not_parse():
    """Anything not created by this project must never be mistaken for ours."""
    for name in ("my pod", "collatz", "collatz-x1", "stable-diffusion-x1790000000", "", None):
        assert runpod_api.parse_name(name) is None


# ---- summarize ----

def _pods(now):
    return [
        {"id": "a", "name": runpod_api.pod_name("dh64-s0", now - 60), "desiredStatus": "RUNNING", "costPerHr": 1.5},
        {"id": "b", "name": runpod_api.pod_name("dh64-s1", now + 3600), "desiredStatus": "RUNNING", "costPerHr": 1.5},
        {"id": "c", "name": "someone elses pod", "desiredStatus": "RUNNING", "costPerHr": 0.4},
        {"id": "d", "name": runpod_api.pod_name("old", now - 9999), "desiredStatus": "EXITED", "costPerHr": 1.5},
    ]


def test_summarize_flags_overdue_and_foreign():
    now = 1_790_000_000
    rows = {r["id"]: r for r in runpod_api.summarize(_pods(now), now)}
    assert rows["a"]["ours"] and rows["a"]["overdue"]
    assert rows["b"]["ours"] and not rows["b"]["overdue"] and rows["b"]["minutes_left"] == 60
    assert not rows["c"]["ours"] and not rows["c"]["overdue"]
    assert not rows["d"]["running"]


# ---- watchdog decisions ----

def test_watchdog_terminates_only_our_overdue_pods():
    """Overdue + ours -> terminate. In-time or foreign -> report only. Stopped -> ignore."""
    now = 1_790_000_000
    terminate, report = watchdog.decide(runpod_api.summarize(_pods(now), now))
    assert [r["id"] for r in terminate] == ["a"]
    assert sorted(r["id"] for r in report) == ["b", "c"]


def test_watchdog_kill_foreign_is_opt_in():
    now = 1_790_000_000
    terminate, report = watchdog.decide(runpod_api.summarize(_pods(now), now), kill_foreign=True)
    assert sorted(r["id"] for r in terminate) == ["a", "c"]
    assert [r["id"] for r in report] == ["b"]


def test_watchdog_nothing_running():
    assert watchdog.decide([]) == ([], [])


# ---- client plumbing with a fake transport ----

def test_client_calls():
    calls = []

    def transport(method, path, body=None):
        calls.append((method, path, body))
        return [{"id": "p1"}] if (method, path) == ("GET", "/pods") else {"id": "new"}

    client = runpod_api.Client(key="unused", transport=transport)
    assert client.list_pods() == [{"id": "p1"}]
    client.delete_pod("p1")
    pod = client.create_cpu_pod("collatz-t-x1790000000", 32, "rust:1-bookworm", ["bash"], {"A": "1"})
    assert pod == {"id": "new"}
    assert calls[1] == ("DELETE", "/pods/p1", None)
    body = calls[2][2]
    assert body["computeType"] == "CPU" and body["vcpuCount"] == 32 and body["interruptible"] is False
    assert body["volumeInGb"] == 0 and body["ports"] == ["8000/http"]


def test_missing_key_is_a_clear_error(monkeypatch, tmp_path):
    monkeypatch.delenv("RUNPOD_API_KEY", raising=False)
    monkeypatch.setattr(runpod_api, "KEY_FILE", tmp_path / "nope")
    try:
        runpod_api.api_key()
    except runpod_api.RunPodError as err:
        assert "RUNPOD_API_KEY" in str(err)
    else:
        raise AssertionError("expected RunPodError")
