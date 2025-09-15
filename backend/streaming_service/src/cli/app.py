import typer

from . import device_commands as device
from . import streaming_commands as session

app = typer.Typer(help="Streaming Service CLI")
app.add_typer(device.app, name="device")
app.add_typer(session.app, name="session")


if __name__ == "__main__":
    app()


