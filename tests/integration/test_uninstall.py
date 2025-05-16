import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestUninstallScript:
    @pytest.fixture
    def mock_dirs(self, tmp_path, monkeypatch):
        """Set up mock directories and environment variables."""
        # Create fake home directory
        home = tmp_path / "home"
        home.mkdir()
        
        # Create fake config directory and files
        config_dir = home / ".ai_terminal"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("test config")
        (config_dir / "context.json").write_text("{}")
        
        # Create fake cache directory
        cache_dir = home / ".cache" / "ai_terminal"
        cache_dir.mkdir(parents=True)
        (cache_dir / "cache.db").write_text("test cache")
        
        # Create fake log directory
        log_dir = home / ".local" / "share" / "ai_terminal" / "logs"
        log_dir.mkdir(parents=True)
        (log_dir / "app.log").write_text("test log")
        
        # Create fake zsh integration
        zsh_completion = home / ".zsh" / "completion"
        zsh_completion.mkdir(parents=True)
        (zsh_completion / "_ai_terminal").write_text("# completion script")
        
        # Create .zshrc with our integration
        zshrc = home / ".zshrc"
        zshrc.write_text("# AI Terminal Integration\nsource ~/.zsh/completion/_ai_terminal\n")
        
        # Set environment variables
        monkeypatch.setenv("HOME", str(home))
        
        return {
            'home': home,
            'config_dir': config_dir,
            'cache_dir': cache_dir,
            'log_dir': log_dir,
            'zsh_completion': zsh_completion,
            'zshrc': zshrc
        }

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('builtins.input', return_value='y')
    def test_uninstall_script(self, mock_input, mock_run, mock_which, mock_dirs):
        # Mock which to return a path to zsh
        mock_which.return_value = "/bin/zsh"
        
        # Mock subprocess.run to succeed
        mock_run.return_value.returncode = 0
        
        # Import here to apply the monkeypatch first
        import uninstall
        
        # Verify files exist before uninstall
        assert mock_dirs['config_dir'].exists()
        assert mock_dirs['cache_dir'].exists()
        assert mock_dirs['log_dir'].exists()
        assert mock_dirs['zsh_completion'].exists()
        
        # Run the uninstall script
        uninstall.main()
        
        # Verify files were removed
        assert not mock_dirs['config_dir'].exists()
        assert not mock_dirs['cache_dir'].exists()
        assert not mock_dirs['log_dir'].exists()
        assert not mock_dirs['zsh_completion'].exists()
        
        # Verify zshrc was cleaned up
        with open(mock_dirs['zshrc'], 'r') as f:
            content = f.read()
            assert "# AI Terminal Integration" not in content
            assert "source ~/.zsh/completion/_ai_terminal" not in content
    
    @patch('shutil.which')
    @patch('builtins.input', return_value='n')
    def test_uninstall_cancellation(self, mock_input, mock_which, mock_dirs):
        # Mock which to return a path to zsh
        mock_which.return_value = "/bin/zsh"
        
        # Import here to apply the monkeypatch first
        import uninstall
        
        # Run the uninstall script but cancel
        uninstall.main()
        
        # Verify files were not removed
        assert mock_dirs['config_dir'].exists()
        assert mock_dirs['cache_dir'].exists()
        assert mock_dirs['log_dir'].exists()
        assert mock_dirs['zsh_completion'].exists()
