import pytest
from unittest.mock import patch, MagicMock
from src.main import main

class TestMainFlow:
    @patch('src.main.argparse.ArgumentParser')
    @patch('src.main.ContextManager')
    @patch('src.main.MistralClient')
    @patch('src.main.ModeDetector')
    def test_main_flow_command_mode(self, mock_detector, mock_llm, mock_context, mock_parser):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.query = ["list files"]
        mock_args.mode = None
        mock_parser.return_value.parse_args.return_value = mock_args
        
        # Mock mode detector to return command mode
        mock_detector.return_value.detect_mode.return_value = "command"
        
        # Mock command handler response
        mock_handler = MagicMock()
        mock_handler.handle.return_value = "ls -la"
        
        with patch.dict('sys.modules', {
            'src.handlers.command_handler': MagicMock(return_value=mock_handler),
            'src.handlers.conversation_handler': MagicMock(),
            'src.handlers.document_handler': MagicMock()
        }):
            # Call main function
            main()
            
            # Verify command handler was called
            mock_handler.handle.assert_called_once_with("list files")
    
    @patch('src.main.argparse.ArgumentParser')
    @patch('src.main.ContextManager')
    @patch('src.main.MistralClient')
    @patch('builtins.input', return_value="exit")
    def test_main_flow_interactive_mode(self, mock_input, mock_llm, mock_context, mock_parser):
        # Setup mocks for interactive mode
        mock_args = MagicMock()
        mock_args.query = None
        mock_args.mode = None
        mock_parser.return_value.parse_args.return_value = mock_args
        
        # Mock mode detector to return conversation mode
        mock_detector = MagicMock()
        mock_detector.detect_mode.return_value = "conversation"
        
        # Mock conversation handler
        mock_handler = MagicMock()
        mock_handler.handle.return_value = "Hello! How can I help you?"
        
        with patch('src.main.ModeDetector', return_value=mock_detector), \
             patch.dict('sys.modules', {
                'src.handlers.command_handler': MagicMock(),
                'src.handlers.conversation_handler': MagicMock(return_value=mock_handler),
                'src.handlers.document_handler': MagicMock()
             }):
            # Call main function
            main()
            
            # Verify conversation handler was called with exit command
            mock_handler.handle.assert_called_once_with("exit")
