import pytest
from unittest.mock import patch, MagicMock
from src.core.llm_client import MistralClient

class TestMistralClient:
    @pytest.fixture
    def mock_client(self):
        with patch('src.core.llm_client.Mistral') as mock_mistral:
            client = MistralClient(api_key="test_key")
            client.client = mock_mistral.return_value
            yield client

    def test_initialization(self, mock_client):
        assert mock_client.api_key == "test_key"
        assert mock_client.client is not None

    def test_generate_response(self, mock_client):
        # Mock the chat completion response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.client.chat.completions.create.return_value = mock_response

        response = mock_client.generate_response("Test input")
        assert response == "Test response"
        mock_client.client.chat.completions.create.assert_called_once()

    def test_generate_streaming_response(self, mock_client):
        # Mock streaming response
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = "Streaming"
        mock_response = [mock_chunk, mock_chunk]
        mock_client.client.chat.completions.create.return_value = mock_response

        responses = list(mock_client.generate_streaming_response("Test input"))
        assert len(responses) == 2
        assert all(r == "Streaming" for r in responses)
