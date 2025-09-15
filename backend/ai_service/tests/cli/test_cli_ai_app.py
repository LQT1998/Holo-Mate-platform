from typer.testing import CliRunner

from ai_service.src.cli.app import app


runner = CliRunner()


def test_ai_cli_companion_create_invokes_service():
    result = runner.invoke(app, ["companion", "create", "--name", "Luna"])    
    # Intentionally expect a string that would be produced by a real service
    # This should FAIL until wired to AICompanionService
    assert "Created companion id" in result.stdout


def test_ai_cli_conversation_start_invokes_service():
    result = runner.invoke(app, ["conversation", "start", "--companion-id", "123", "--title", "Hello"])    
    # Should FAIL until wired to ConversationService
    assert "Conversation started id" in result.stdout


