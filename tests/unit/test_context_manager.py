import os
import pytest
from unittest.mock import patch, MagicMock
from src.core.context_manager import ContextManager

class TestContextManager:
    @pytest.fixture
    def context_manager(self, tmp_path):
        with patch('src.core.context_manager.CONTEXT_FILE', str(tmp_path / 'context.json')):
            return ContextManager()

    def test_initialization(self, context_manager, tmp_path):
        assert context_manager.context_file == str(tmp_path / 'context.json')
        assert isinstance(context_manager.context, dict)
        assert 'conversation_history' in context_manager.context
        assert 'environment' in context_manager.context
        assert 'command_history' in context_manager.context

    def test_add_to_history(self, context_manager):
        context_manager.add_to_history('user', 'Hello')
        assert len(context_manager.context['conversation_history']) == 1
        assert context_manager.context['conversation_history'][0] == {'role': 'user', 'content': 'Hello'}

    def test_update_environment(self, context_manager):
        env_update = {'cwd': '/test/path', 'user': 'testuser'}
        context_manager.update_environment(env_update)
        assert context_manager.context['environment'].items() >= env_update.items()

    def test_save_and_load_context(self, context_manager, tmp_path):
        # Add some data
        context_manager.add_to_history('user', 'Test message')
        context_manager.update_environment({'test': 'value'})
        
        # Save and create a new instance to load
        context_manager._save_context()
        new_manager = ContextManager()
        
        # Verify data was saved and loaded correctly
        assert len(new_manager.context['conversation_history']) == 1
        assert new_manager.context['environment']['test'] == 'value'
