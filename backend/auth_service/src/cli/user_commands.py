import typer

app = typer.Typer(help="Auth Service CLI")


@app.command("create-user")
def create_user(email: str, password: str):
    # TODO: Wire to UserService with DB session
    typer.echo(f"[dry-run] Created: {email}")


if __name__ == "__main__":
    app()


