import typer

app = typer.Typer(help="AI Service - Companion commands")


@app.command("create")
def create_companion(name: str):
    # TODO: Wire to AICompanionService once implemented
    typer.echo(f"[dry-run] Created companion: {name}")


@app.command("list")
def list_companions(limit: int = 20):
    # TODO: Wire to AICompanionService once implemented
    typer.echo(f"[dry-run] Listing first {limit} companions")


