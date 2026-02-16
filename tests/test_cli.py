"""Tests for cronguard.cli."""

import json
import re

from typer.testing import CliRunner

from cronguard import __version__
from cronguard.cli import app

runner = CliRunner()

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in _strip_ansi(result.output)


def test_version_short_flag() -> None:
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert __version__ in _strip_ansi(result.output)


# ---------------------------------------------------------------------------
# Successful command
# ---------------------------------------------------------------------------


def test_run_successful_command() -> None:
    result = runner.invoke(app, ["run", "echo hello"])
    clean = _strip_ansi(result.output)
    assert result.exit_code == 0
    assert "echo hello" in clean
    assert "Exit Code:" in clean
    assert "Duration:" in clean


# ---------------------------------------------------------------------------
# Failing command
# ---------------------------------------------------------------------------


def test_run_failing_command() -> None:
    result = runner.invoke(app, ["run", "bash -c 'echo fail >&2; exit 1'"])
    clean = _strip_ansi(result.output)
    assert result.exit_code == 1
    assert "Exit Code:" in clean
    assert "Output" in clean


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def test_run_json_output() -> None:
    result = runner.invoke(app, ["run", "echo json-test", "--json"])
    parsed = json.loads(_strip_ansi(result.output))
    assert parsed["command"] == "echo json-test"
    assert parsed["ok"] is True
    assert parsed["exit_code"] == 0


def test_run_json_failing() -> None:
    result = runner.invoke(app, ["run", "bash -c 'exit 2'", "--json"])
    parsed = json.loads(_strip_ansi(result.output))
    assert parsed["ok"] is False
    assert parsed["exit_code"] == 2


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------


def test_run_timeout() -> None:
    result = runner.invoke(app, ["run", "sleep 10", "--timeout", "1"])
    clean = _strip_ansi(result.output)
    assert result.exit_code == 124
    assert "timed out" in clean


# ---------------------------------------------------------------------------
# Quiet mode
# ---------------------------------------------------------------------------


def test_run_quiet_success() -> None:
    result = runner.invoke(app, ["run", "echo quiet-test", "--quiet"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_run_quiet_failure() -> None:
    result = runner.invoke(app, ["run", "bash -c 'exit 1'", "--quiet"])
    assert result.exit_code == 1
    # Failure should still produce output
    clean = _strip_ansi(result.output)
    assert "Exit Code:" in clean


# ---------------------------------------------------------------------------
# Label
# ---------------------------------------------------------------------------


def test_run_with_label() -> None:
    result = runner.invoke(app, ["run", "echo hi", "--label", "nightly-backup"])
    clean = _strip_ansi(result.output)
    assert result.exit_code == 0
    assert "nightly-backup" in clean


def test_run_label_in_json() -> None:
    result = runner.invoke(app, ["run", "echo hi", "--label", "my-job", "--json"])
    parsed = json.loads(_strip_ansi(result.output))
    assert parsed["label"] == "my-job"


# ---------------------------------------------------------------------------
# No args shows help
# ---------------------------------------------------------------------------


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "Usage" in result.output
