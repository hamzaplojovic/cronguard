"""Tests for cronguard.core."""

import json
from datetime import datetime

import pytest

from cronguard.core import format_duration, run_command

# ---------------------------------------------------------------------------
# format_duration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "0s"),
        (5, "5s"),
        (45, "45s"),
        (60, "1m"),
        (61, "1m 1s"),
        (151, "2m 31s"),
        (3600, "1h"),
        (3900, "1h 5m"),
        (7200, "2h"),
    ],
)
def test_format_duration(seconds: float, expected: str) -> None:
    assert format_duration(seconds) == expected


def test_format_duration_negative() -> None:
    assert format_duration(-5) == "0s"


# ---------------------------------------------------------------------------
# run_command - success
# ---------------------------------------------------------------------------


def test_run_command_echo() -> None:
    result = run_command("echo hello")
    assert result.ok is True
    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"
    assert result.timed_out is False
    assert isinstance(result.started_at, datetime)
    assert isinstance(result.finished_at, datetime)
    assert result.duration_seconds >= 0


# ---------------------------------------------------------------------------
# run_command - failure
# ---------------------------------------------------------------------------


def test_run_command_failing() -> None:
    result = run_command("bash -c 'exit 1'")
    assert result.ok is False
    assert result.exit_code == 1
    assert result.timed_out is False


def test_run_command_nonzero_exit() -> None:
    result = run_command("bash -c 'echo oops >&2; exit 42'")
    assert result.ok is False
    assert result.exit_code == 42
    assert "oops" in result.stderr


# ---------------------------------------------------------------------------
# run_command - timeout
# ---------------------------------------------------------------------------


def test_run_command_timeout() -> None:
    result = run_command("sleep 10", timeout=1)
    assert result.timed_out is True
    assert result.exit_code == 124
    assert result.ok is False
    assert result.duration_seconds >= 1.0


# ---------------------------------------------------------------------------
# run_command - label
# ---------------------------------------------------------------------------


def test_run_command_label() -> None:
    result = run_command("echo hi", label="my-job")
    assert result.label == "my-job"
    assert result.ok is True


# ---------------------------------------------------------------------------
# JobResult.to_dict / to_json
# ---------------------------------------------------------------------------


def test_to_dict() -> None:
    result = run_command("echo test-dict")
    d = result.to_dict()

    assert d["command"] == "echo test-dict"
    assert d["ok"] is True
    assert d["exit_code"] == 0
    assert d["timed_out"] is False
    assert isinstance(d["duration_seconds"], float)
    assert isinstance(d["started_at"], str)
    assert isinstance(d["finished_at"], str)
    assert "test-dict" in d["stdout"]


def test_to_json() -> None:
    result = run_command("echo test-json")
    raw = result.to_json()
    parsed = json.loads(raw)

    assert parsed["command"] == "echo test-json"
    assert parsed["ok"] is True
    assert isinstance(parsed["duration_seconds"], float)


def test_to_dict_with_label() -> None:
    result = run_command("echo labeled", label="nightly")
    d = result.to_dict()
    assert d["label"] == "nightly"


def test_to_dict_without_label() -> None:
    result = run_command("echo no-label")
    d = result.to_dict()
    assert d["label"] is None
