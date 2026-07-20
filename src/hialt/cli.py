from uuid import uuid4

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from hialt.agents.graph import build_graph
from hialt.state import AgentState, CriticIssue, ExecutionPlan

app = typer.Typer(help="hialt: Plan-Execute-Verify agent CLI", no_args_is_help=True)
console = Console()


@app.callback()
def main() -> None:
    """hialt CLI entry point."""


def _format_value(key: str, value: object) -> str:
    if key == "plan" and isinstance(value, ExecutionPlan):
        return value.objective
    if key == "critic_feedback" and isinstance(value, list):
        if not value:
            return "[]"
        parts = []
        for issue in value:
            if isinstance(issue, CriticIssue):
                parts.append(f"{issue.severity}: {issue.description}")
            else:
                parts.append(str(issue))
        return "; ".join(parts)
    return str(value)


@app.command()
def run(
    task: str = typer.Option(..., "--task", help="Task for the agent to execute"),
) -> None:
    """Run the Plan-Execute-Verify graph for a task."""
    thread_id = str(uuid4())
    initial_state: AgentState = {
        "task": task,
        "plan": None,
        "current_code": "",
        "critic_feedback": [],
        "iteration": 0,
        "status": "planning",
    }
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    console.print(
        Panel(f"[bold]task[/bold] {escape(task)}\n[bold]thread[/bold] {thread_id}")
    )

    for update in graph.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, payload in update.items():
            console.print(f"[cyan]{escape(node_name)}[/cyan]")
            for key, value in payload.items():
                rendered = _format_value(key, value)
                console.print(f"  [dim]{escape(str(key))}[/dim]: {escape(rendered)}")

    console.print("[green]done[/green]")


if __name__ == "__main__":
    app()
