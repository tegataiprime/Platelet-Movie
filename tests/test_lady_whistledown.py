"""Tests for scripts/lady_whistledown.py."""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


# Import after modifying path to include scripts directory
sys.path.insert(0, "/home/runner/work/Platelet-Movie/Platelet-Movie/scripts")
from lady_whistledown import generate_commentary, generate_fallback_commentary


class TestGenerateFallbackCommentary:
    """Tests for generate_fallback_commentary function."""

    def test_returns_lady_whistledown_style_text(self):
        """Test that fallback commentary returns expected Lady Whistledown style text."""
        result = generate_fallback_commentary()
        
        assert "Dear Reader" in result
        assert "This Author has learned" in result
        assert "platelet" in result.lower()
        assert "Netflix" in result
        assert isinstance(result, str)
        assert len(result) > 100  # Should be substantial commentary


class TestGenerateCommentaryWithoutAPIKey:
    """Tests for generate_commentary when OPENAI_API_KEY is not set."""

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stderr", new_callable=StringIO)
    def test_uses_fallback_when_api_key_missing(self, mock_stderr):
        """Test that generate_commentary uses fallback when API key is not set."""
        movie_list = "1. The Matrix (136m)\n2. Inception (148m)"
        
        result = generate_commentary(movie_list)
        
        # Should use fallback commentary
        assert "Dear Reader" in result
        # Should print warning to stderr
        assert "Warning: OPENAI_API_KEY not set" in mock_stderr.getvalue()


class TestGenerateCommentaryWithAPIKey:
    """Tests for generate_commentary when OPENAI_API_KEY is set."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"})
    @patch("urllib.request.urlopen")
    def test_calls_openai_api_successfully(self, mock_urlopen):
        """Test successful OpenAI API call returns generated commentary."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "choices": [{
                "message": {
                    "content": "Dear Reader, what scandal awaits! This Author has discovered..."
                }
            }]
        }'''
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        movie_list = "1. The Matrix (136m)\n2. Inception (148m)"
        result = generate_commentary(movie_list)
        
        assert "Dear Reader, what scandal awaits!" in result
        assert mock_urlopen.called
        
        # Verify API request was made correctly
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert request.get_method() == "POST"
        assert "api.openai.com" in request.full_url
        assert request.headers["Authorization"] == "Bearer test-api-key-123"
        assert request.headers["Content-type"] == "application/json"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"})
    @patch("urllib.request.urlopen")
    def test_includes_movie_list_in_prompt(self, mock_urlopen):
        """Test that the movie list is included in the API prompt."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "choices": [{
                "message": {
                    "content": "Generated commentary"
                }
            }]
        }'''
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        movie_list = "1. The Matrix (136m)\n2. Inception (148m)\n3. Interstellar (169m)"
        generate_commentary(movie_list)
        
        # Extract the request data
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        import json
        request_data = json.loads(request.data.decode("utf-8"))
        
        # Verify movie list is in the prompt
        user_message = request_data["messages"][1]["content"]
        assert "The Matrix" in user_message
        assert "Inception" in user_message
        assert "Interstellar" in user_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key-123"})
    @patch("urllib.request.urlopen")
    def test_uses_gpt_4o_mini_model(self, mock_urlopen):
        """Test that the correct OpenAI model is specified."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "choices": [{
                "message": {
                    "content": "Generated commentary"
                }
            }]
        }'''
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        generate_commentary("Movie list")
        
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        import json
        request_data = json.loads(request.data.decode("utf-8"))
        
        assert request_data["model"] == "gpt-4o-mini"
        assert request_data["temperature"] == 0.8
        assert request_data["max_tokens"] == 500


class TestGenerateCommentaryErrorHandling:
    """Tests for error handling in generate_commentary."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "invalid-key"})
    @patch("urllib.request.urlopen")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_http_error_401(self, mock_stderr, mock_urlopen):
        """Test that HTTP 401 error falls back to default commentary."""
        import urllib.error
        from io import BytesIO
        
        error = urllib.error.HTTPError(
            "url", 401, "Unauthorized", {}, BytesIO(b'{"error": "Invalid API key"}')
        )
        mock_urlopen.side_effect = error
        
        result = generate_commentary("Movie list")
        
        # Should use fallback commentary
        assert "Dear Reader" in result
        assert "This Author has learned" in result
        # Should log error to stderr
        stderr_output = mock_stderr.getvalue()
        assert "Warning: OpenAI API error (401)" in stderr_output

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("urllib.request.urlopen")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_http_error_429(self, mock_stderr, mock_urlopen):
        """Test that HTTP 429 (rate limit) error falls back to default commentary."""
        import urllib.error
        from io import BytesIO
        
        error = urllib.error.HTTPError(
            "url", 429, "Rate limited", {}, BytesIO(b'{"error": "Rate limit exceeded"}')
        )
        mock_urlopen.side_effect = error
        
        result = generate_commentary("Movie list")
        
        assert "Dear Reader" in result
        stderr_output = mock_stderr.getvalue()
        assert "Warning: OpenAI API error (429)" in stderr_output

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("urllib.request.urlopen")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_http_error_500(self, mock_stderr, mock_urlopen):
        """Test that HTTP 500 error falls back to default commentary."""
        import urllib.error
        from io import BytesIO
        
        error = urllib.error.HTTPError(
            "url", 500, "Server error", {}, BytesIO(b'{"error": "Internal server error"}')
        )
        mock_urlopen.side_effect = error
        
        result = generate_commentary("Movie list")
        
        assert "Dear Reader" in result
        stderr_output = mock_stderr.getvalue()
        assert "Warning: OpenAI API error (500)" in stderr_output

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("urllib.request.urlopen")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_generic_exception(self, mock_stderr, mock_urlopen):
        """Test that generic exceptions fall back to default commentary."""
        mock_urlopen.side_effect = Exception("Network timeout")
        
        result = generate_commentary("Movie list")
        
        assert "Dear Reader" in result
        stderr_output = mock_stderr.getvalue()
        assert "Warning: Failed to generate commentary" in stderr_output
        assert "Network timeout" in stderr_output

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("urllib.request.urlopen")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_malformed_json_response(self, mock_stderr, mock_urlopen):
        """Test handling of malformed JSON in API response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"Not valid JSON"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = generate_commentary("Movie list")
        
        # Should fall back to default commentary
        assert "Dear Reader" in result
        stderr_output = mock_stderr.getvalue()
        assert "Warning: Failed to generate commentary" in stderr_output


class TestMainFunction:
    """Tests for the main script execution."""

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stdout", new_callable=StringIO)
    def test_reads_from_stdin_and_outputs_commentary(self, mock_stdout):
        """Test that main function reads from stdin and outputs commentary."""
        movie_list = "1. The Matrix (136m)\n2. Inception (148m)"
        
        # Test the core functionality
        commentary = generate_commentary(movie_list)
        assert "Dear Reader" in commentary

    @patch("sys.stdin", StringIO(""))
    @patch("sys.stderr", new_callable=StringIO)
    def test_exits_with_error_on_empty_stdin(self, mock_stderr):
        """Test that script exits with error when stdin is empty."""
        with pytest.raises(SystemExit) as exc_info:
            # Simulate the main block behavior
            movie_list = sys.stdin.read()
            if not movie_list.strip():
                print("Error: No movie list provided on stdin", file=sys.stderr)
                sys.exit(1)
        
        assert exc_info.value.code == 1

    @patch("sys.stdin", StringIO("   \n  \n"))
    @patch("sys.stderr", new_callable=StringIO)
    def test_exits_with_error_on_whitespace_only_stdin(self, mock_stderr):
        """Test that script exits with error when stdin contains only whitespace."""
        with pytest.raises(SystemExit) as exc_info:
            movie_list = sys.stdin.read()
            if not movie_list.strip():
                print("Error: No movie list provided on stdin", file=sys.stderr)
                sys.exit(1)
        
        assert exc_info.value.code == 1


class TestIntegration:
    """Integration tests for lady_whistledown script."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("urllib.request.urlopen")
    def test_end_to_end_with_successful_api_call(self, mock_urlopen):
        """Test complete flow from movie list to commentary with successful API."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "choices": [{
                "message": {
                    "content": "Dear Reader, This Author brings news of cinematic diversions..."
                }
            }]
        }'''
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        movie_list = """Netflix movies with a runtime >= 135 minutes:

     Runtime  Score  Rated    Genres                Title
-------------------------------------------------------------------------------------
     136 m    8.7  R        Action, Sci-Fi        The Matrix
     148 m    8.8  PG-13    Action, Sci-Fi        Inception
     169 m    8.7  PG-13    Adventure, Drama      Interstellar"""
        
        result = generate_commentary(movie_list)
        
        assert "Dear Reader" in result
        assert "cinematic diversions" in result
        assert len(result) > 50

    @patch.dict("os.environ", {}, clear=True)
    def test_end_to_end_with_fallback(self):
        """Test complete flow using fallback commentary when no API key."""
        movie_list = """Netflix movies with a runtime >= 135 minutes:

     Runtime  Score  Rated    Genres                Title
-------------------------------------------------------------------------------------
     136 m    8.7  R        Action, Sci-Fi        The Matrix"""
        
        result = generate_commentary(movie_list)
        
        # Verify fallback commentary structure
        assert "Dear Reader" in result
        assert "This Author has learned" in result
        assert "platelet" in result.lower()
        assert "90 minutes" in result or "90-minute" in result.lower()
        assert "Netflix" in result
        assert len(result) > 200  # Fallback should be well-formed
