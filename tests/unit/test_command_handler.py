import pytest
from unittest.mock import MagicMock, patch
from src.handlers.command_handler import CommandHandler

class TestCommandHandler:
    @pytest.fixture
    def handler(self):
        mock_llm = MagicMock()
        mock_context = MagicMock()
        return CommandHandler(mock_llm, mock_context)

    def test_handle_command_generation(self, handler):
        # Test command generation
        handler.llm_client.generate_response.return_value = "ls -la"
        result = handler.handle("list files in current directory")
        assert "ls -la" in result
        handler.llm_client.generate_response.assert_called_once()

    def test_handle_command_explanation(self, handler):
        # Test command explanation
        handler.llm_client.generate_response.return_value = "This command lists all files..."
        result = handler.handle("what does 'ls -la' do?")
        assert "lists all files" in result.lower()

    @patch('subprocess.run')
    def test_execute_command(self, mock_run, handler):
        # Mock subprocess.run for command execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"file1.txt\nfile2.txt"
        mock_run.return_value = mock_result

        output = handler._execute_command("ls")
        assert "file1.txt" in output
        assert "file2.txt" in output
        mock_run.assert_called_once_with(
            ["ls"], capture_output=True, text=True, shell=False, check=False
        )
