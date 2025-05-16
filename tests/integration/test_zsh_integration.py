import os
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

class TestZshIntegration:
    @pytest.fixture
    def mock_home(self, tmp_path, monkeypatch):
        """Mock the home directory for testing."""
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        return home

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_zsh_integration_install(self, mock_run, mock_which, mock_home):
        # Mock which to return a path to zsh
        mock_which.return_value = "/bin/zsh"
        
        # Mock subprocess.run to succeed
        mock_run.return_value.returncode = 0
        
        # Mock the zshrc file
        zshrc = mock_home / ".zshrc"
        zshrc.touch()
        
        # Import here to apply the monkeypatch first
        from src.zsh_integration.install import install_zsh_integration
        
        # Call the installation function
        install_zsh_integration()
        
        # Verify the zshrc was modified
        with open(zshrc, 'r') as f:
            content = f.read()
            assert "# AI Terminal Integration" in content
        
        # Verify the completion script was created
        completion_dir = mock_home / ".zsh" / "completion"
        completion_file = completion_dir / "_ai_terminal"
        assert completion_file.exists()
    
    @patch('shutil.which')
    def test_zsh_integration_uninstall(self, mock_which, mock_home):
        # Mock which to return a path to zsh
        mock_which.return_value = "/bin/zsh"
        
        # Create a zshrc with our integration
        zshrc = mock_home / ".zshrc"
        with open(zshrc, 'w') as f:
            f.write("# AI Terminal Integration\n")
            f.write("source ~/.zsh/completion/_ai_terminal\n")
        
        # Import here to apply the monkeypatch first
        from src.zsh_integration.install import uninstall_zsh_integration
        
        # Call the uninstallation function
        uninstall_zsh_integration()
        
        # Verify the zshrc was cleaned up
        with open(zshrc, 'r') as f:
            content = f.read()
            assert "# AI Terminal Integration" not in content
            assert "source ~/.zsh/completion/_ai_terminal" not in content
