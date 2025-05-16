import pytest
from unittest.mock import MagicMock, mock_open, patch
from pathlib import Path
from src.handlers.document_handler import DocumentHandler

class TestDocumentHandler:
    @pytest.fixture
    def handler(self):
        mock_llm = MagicMock()
        mock_context = MagicMock()
        return DocumentHandler(mock_llm, mock_context)

    def test_handle_summarize(self, handler):
        # Test document summarization
        test_content = "This is a test document. It contains multiple sentences."
        expected_summary = "Test summary of the document."
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            handler.llm_client.generate_response.return_value = expected_summary
            result = handler.handle("summarize test.txt")
            
            assert expected_summary in result
            handler.llm_client.generate_response.assert_called_once()

    def test_handle_analyze(self, handler):
        # Test document analysis
        test_content = "This is a test document with some data."
        expected_analysis = "Analysis: The document contains test data."
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            handler.llm_client.generate_response.return_value = expected_analysis
            result = handler.handle("analyze test.txt")
            
            assert "Analysis:" in result

    @patch('pathlib.Path.exists')
    def test_handle_nonexistent_file(self, mock_exists, handler):
        # Test handling of non-existent file
        mock_exists.return_value = False
        result = handler.handle("summarize missing.txt")
        assert "Error: File not found" in result

    def test_extract_text_from_pdf(self, handler):
        # Test PDF text extraction (mocked)
        with patch('PyPDF2.PdfReader') as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content"
            mock_pdf.return_value.pages = [mock_page]
            
            result = handler._extract_text_from_pdf("test.pdf")
            assert result == "PDF content"
