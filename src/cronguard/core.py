"""Core execution logic. No CLI dependencies."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string.

    Examples: "45s", "2m 31s", "1h 5m"
    """
    if seconds < 0:
        seconds = 0.0

    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60

    if h > 0:
        return f"{h}h {m}m" if m > 0 else f"{h}h"
    if m > 0:
        return f"{m}m {s}s" if s > 0 else f"{m}m"
    return f"{s}s"


@dataclass
class JobResult:
    """Result of a command execution."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    started_at: datetime
    finished_at: datetime
    timed_out: bool = False
    label: str | None = None

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "label": self.label,
            "exit_code": self.exit_code,
            "ok": self.ok,
            "timed_out": self.timed_out,
            "duration_seconds": round(self.duration_seconds, 3),
            "duration_human": format_duration(self.duration_seconds),
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "stdout": self.stdout,
            "stderr": self.stderr,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def run_command(
    command: str,
    timeout: float | None = None,
    shell: bool = True,
    label: str | None = None,
) -> JobResult:
    """Run a command and capture everything.

    Always returns a JobResult, never raises.
    """
    started_at = datetime.now(UTC)
    start_time = time.monotonic()

    try:
        proc = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start_time
        finished_at = datetime.now(UTC)

        return JobResult(
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_seconds=elapsed,
            started_at=started_at,
            finished_at=finished_at,
            timed_out=False,
            label=label,
        )

    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start_time
        finished_at = datetime.now(UTC)

        return JobResult(
            command=command,
            exit_code=124,
            stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
            stderr=exc.stderr or "" if isinstance(exc.stderr, str) else "",
            duration_seconds=elapsed,
            started_at=started_at,
            finished_at=finished_at,
            timed_out=True,
            label=label,
        )

    except FileNotFoundError:
        elapsed = time.monotonic() - start_time
        finished_at = datetime.now(UTC)

        return JobResult(
            command=command,
            exit_code=127,
            stdout="",
            stderr=f"Command not found: {command}",
            duration_seconds=elapsed,
            started_at=started_at,
            finished_at=finished_at,
            timed_out=False,
            label=label,
        )

    except PermissionError:
        elapsed = time.monotonic() - start_time
        finished_at = datetime.now(UTC)

        return JobResult(
            command=command,
            exit_code=126,
            stdout="",
            stderr=f"Permission denied: {command}",
            duration_seconds=elapsed,
            started_at=started_at,
            finished_at=finished_at,
            timed_out=False,
            label=label,
        )
