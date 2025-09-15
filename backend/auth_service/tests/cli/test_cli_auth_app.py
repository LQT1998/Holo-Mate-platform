from typer.testing import CliRunner

from auth_service.src.cli.user_commands import app


runner = CliRunner()


def test_auth_cli_create_user_invokes_service():
    result = runner.invoke(app, ["create-user", "--email", "a@b.com", "--password", "secret123"])    
    # Should FAIL until wired to UserService with DB
    assert "Created user id" in result.stdout


