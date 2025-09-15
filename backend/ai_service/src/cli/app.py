import typer

from . import companion_commands as companion
from . import conversation_commands as conversation

app = typer.Typer(help="AI Service CLI")
app.add_typer(companion.app, name="companion")
app.add_typer(conversation.app, name="conversation")


if __name__ == "__main__":
    app()


