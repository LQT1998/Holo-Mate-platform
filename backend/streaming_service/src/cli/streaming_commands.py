import typer

app = typer.Typer(help="Streaming Service - Session commands")


@app.command("start")
def start_session(user_id: str):
    # TODO: Wire to StreamingService once implemented
    typer.echo(f"[dry-run] Started session for user: {user_id}")


@app.command("status")
def session_status(session_id: str):
    # TODO: Wire to StreamingService once implemented
    typer.echo(f"[dry-run] Status for session: {session_id}")


