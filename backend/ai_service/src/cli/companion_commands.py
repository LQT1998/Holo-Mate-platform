import typer

app = typer.Typer(help="AI Service - Companion commands")


@app.command("create")
def create_companion(
    name: str = typer.Argument(None, help="Companion name"),
    name_opt: str = typer.Option(None, "--name", help="Companion name (option)")
):
    """Create a new AI companion (DEV mock). Accepts positional NAME or --name option."""
    resolved_name = name_opt or name
    if not resolved_name:
        raise typer.BadParameter("Name is required. Provide NAME or --name.")
    # TODO: Wire to AICompanionService once implemented
    typer.echo(f"Created companion id: dev-{resolved_name}")


@app.command("list")
def list_companions(limit: int = 20):
    # TODO: Wire to AICompanionService once implemented
    typer.echo(f"[dry-run] Listing first {limit} companions")


