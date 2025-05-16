import pytest
from unittest.mock import MagicMock, patch
from src.handlers.conversation_handler import ConversationHandler

class TestConversationHandler:
    @pytest.fixture
    def handler(self):
        mock_llm = MagicMock()
        mock_context = MagicMock()
        return ConversationHandler(mock_llm, mock_context)

    def test_handle_general_conversation(self, handler):
        # Test general conversation handling
        test_response = "Hello! How can I help you today?"
        handler.llm_client.generate_response.return_value = test_response
        
        result = handler.handle("Hello!")
        assert test_response in result
        handler.llm_client.generate_response.assert_called_once()

    def test_handle_with_context(self, handler):
        # Test conversation with context
        handler.context_manager.get_context.return_value = {
            'conversation_history': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }
        
        test_response = "Continuing our conversation..."
        handler.llm_client.generate_response.return_value = test_response
        
        result = handler.handle("What was I just asking?")
        assert test_response in result
        
        # Verify context was included in the LLM call
        call_args = handler.llm_client.generate_response.call_args[1]
        assert 'context' in call_args
        assert 'conversation_history' in call_args['context']

    def test_handle_empty_input(self, handler):
        # Test handling of empty input
        result = handler.handle("")
        assert "Please provide some input" in result
        handler.llm_client.generate_response.assert_not_called()
