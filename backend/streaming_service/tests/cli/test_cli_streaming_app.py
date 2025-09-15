from typer.testing import CliRunner

from streaming_service.src.cli.app import app


runner = CliRunner()


def test_stream_cli_device_register_invokes_service():
    result = runner.invoke(app, ["device", "register", "--serial", "DEV-001"])    
    # Should FAIL until wired to DeviceService
    assert "Device registered id" in result.stdout


def test_stream_cli_session_start_invokes_service():
    result = runner.invoke(app, ["session", "start", "--user-id", "U1"])    
    # Should FAIL until wired to StreamingService
    assert "Session started id" in result.stdout


