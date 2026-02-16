# cronguard

Wrap cron jobs with execution tracking, timing, output capture, and exit code reporting.

[![PyPI version](https://img.shields.io/pypi/v/cronguard.svg)](https://pypi.org/project/cronguard/)
[![Downloads](https://img.shields.io/pypi/dm/cronguard.svg)](https://pypi.org/project/cronguard/)
[![Python](https://img.shields.io/pypi/pyversions/cronguard.svg)](https://pypi.org/project/cronguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
pip install cronguard
```

```bash
uv add cronguard
```

```bash
brew install cronguard
```

## Usage

### Basic run

```bash
cronguard run "echo hello"
```

### With a timeout (seconds)

```bash
cronguard run "backup.sh" --timeout 300
```

### With a human label

```bash
cronguard run "deploy.sh" --label "nightly-deploy"
```

### JSON output (good for piping to monitoring)

```bash
cronguard run "test.sh" --json
```

### Quiet mode (only output on failure)

```bash
cronguard run "cleanup.sh" --quiet
```

## Drop it in your crontab

```crontab
# Run backup every night at 2am, timeout after 1 hour
0 2 * * * cronguard run "/home/me/backup.sh" --label "nightly-backup" --timeout 3600 --quiet 2>&1 | logger -t cronguard
```

The `--quiet` flag keeps things silent when everything works. If the job fails, cronguard prints the full report so `logger` (or your monitoring) picks it up.

## All options

```
cronguard run COMMAND [OPTIONS]

Arguments:
  COMMAND              The command to run

Options:
  --timeout, -t FLOAT  Timeout in seconds. Exit code 124 on timeout.
  --label, -l TEXT     Human-readable label for this job.
  --json, -j           Output results as JSON.
  --quiet, -q          Only output on failure. Silent success.

Global:
  --version, -V        Show version and exit.
  --help               Show this message and exit.
```

## Why I built this

Cron jobs fail silently. You set up a backup script, forget about it, and three months later you find out it has been broken the whole time. I wanted something dead simple that wraps any command and gives you timing, exit codes, and captured output so you can pipe it into whatever alerting you already use. No daemons, no config files, just prefix your cron command with `cronguard run` and you get visibility.

## License

MIT
