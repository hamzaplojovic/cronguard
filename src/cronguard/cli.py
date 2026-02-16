"""Command-line interface for cronguard."""

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from cronguard import __version__
from cronguard.core import format_duration, run_command

app = typer.Typer(
    name="cronguard",
    help="Wrap cron jobs with timing, output capture, and exit code tracking.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"cronguard [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Wrap cron jobs with timing, output capture, and exit code tracking."""


@app.command()
def run(
    command: Annotated[
        str,
        typer.Argument(help="The command to run."),
    ],
    timeout: Annotated[
        Optional[float],
        typer.Option(
            "--timeout",
            "-t",
            help="Timeout in seconds. Exit code 124 on timeout.",
        ),
    ] = None,
    label: Annotated[
        Optional[str],
        typer.Option(
            "--label",
            "-l",
            help="Human-readable label for this job.",
        ),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output results as JSON.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Only output on failure. Silent success.",
        ),
    ] = False,
) -> None:
    """Run a command and report results."""
    result = run_command(
        command=command,
        timeout=timeout,
        label=label,
    )

    if output_json:
        console.print_json(result.to_json())
        raise typer.Exit(code=result.exit_code)

    if quiet and result.ok:
        raise typer.Exit(code=0)

    # Build the summary panel
    exit_style = "green" if result.ok else "red bold"
    exit_display = f"[{exit_style}]{result.exit_code}[/{exit_style}]"

    if result.timed_out:
        exit_display += " [red bold](timed out)[/red bold]"

    lines = []
    if result.label:
        lines.append(f"[bold]Label:[/bold]    {result.label}")
    lines.append(f"[bold]Command:[/bold]  {result.command}")
    lines.append(f"[bold]Exit Code:[/bold] {exit_display}")
    lines.append(f"[bold]Duration:[/bold]  {format_duration(result.duration_seconds)}")
    lines.append(
        f"[bold]Started:[/bold]   {result.started_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    lines.append(
        f"[bold]Finished:[/bold]  {result.finished_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

    panel_style = "green" if result.ok else "red"
    title = "cronguard"
    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title=title,
            border_style=panel_style,
        )
    )

    # On failure, show stdout and stderr
    if not result.ok:
        output_parts = []
        if result.stdout.strip():
            output_parts.append(f"[bold]stdout:[/bold]\n{result.stdout.strip()}")
        if result.stderr.strip():
            output_parts.append(f"[bold]stderr:[/bold]\n{result.stderr.strip()}")

        if output_parts:
            console.print()
            console.print(
                Panel(
                    "\n\n".join(output_parts),
                    title="Output",
                    border_style="red",
                )
            )

    raise typer.Exit(code=result.exit_code)


if __name__ == "__main__":
    app()
