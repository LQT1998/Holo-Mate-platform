import typer

app = typer.Typer(help="Streaming Service - Device commands")


@app.command("register")
def register_device(serial: str):
    # TODO: Wire to DeviceService once implemented
    typer.echo(f"[dry-run] Registered device: {serial}")


@app.command("list")
def list_devices(limit: int = 50):
    # TODO: Wire to DeviceService once implemented
    typer.echo(f"[dry-run] Listing first {limit} devices")


