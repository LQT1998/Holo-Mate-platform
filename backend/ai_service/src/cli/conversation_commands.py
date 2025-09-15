import typer

app = typer.Typer(help="AI Service - Conversation commands")


@app.command("start")
def start_conversation(companion_id: str, title: str = "New Conversation"):
    # TODO: Wire to ConversationService once implemented
    typer.echo(f"[dry-run] Started conversation with {companion_id}: {title}")


@app.command("history")
def history(conversation_id: str, limit: int = 50):
    # TODO: Wire to ConversationService once implemented
    typer.echo(f"[dry-run] Show last {limit} messages of {conversation_id}")


