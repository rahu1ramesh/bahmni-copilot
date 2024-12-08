import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.utils.openai import OpenAIUtils


class TestOpenAIUtils(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key"})
    @patch("os.path.exists", return_value=False)
    def test_transcribe_audio_file_not_exist(self, mock_exists):
        with self.assertRaises(HTTPException) as context:
            OpenAIUtils.transcribe_audio("non_existent_file.mp3")
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("File 'non_existent_file.mp3' does not exist.", context.exception.detail)

    @patch.object(OpenAIUtils, "_client", create=True)
    def test_prepare_context_success(self, mock_client):
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="{'name': 'John Doe', 'email': 'john.doe@example.com'}"))]
        )
        transcription_text = "My name is John Doe and my email is john.doe@example.com."
        form_structure = {"name": "Full Name", "email": "Email Address"}
        result = OpenAIUtils.prepare_context(transcription_text, form_structure)
        expected_result = {"name": "John Doe", "email": "john.doe@example.com"}
        self.assertEqual(result, expected_result)
        mock_client.chat.completions.create.assert_called_once()

    @patch.object(OpenAIUtils, "_client", create=True)
    def test_prepare_context_exception(self, mock_client):
        mock_client.chat.completions.create.side_effect = Exception("API error")
        transcription_text = "My name is John Doe and my email is john.doe@example.com."
        form_structure = {"name": "Full Name", "email": "Email Address"}
        with self.assertRaises(HTTPException) as context:
            OpenAIUtils.prepare_context(transcription_text, form_structure)
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("Failed to parse the AI's response: API error", context.exception.detail)

    @patch.object(OpenAIUtils, "_client", create=True)
    def test_prepare_context_invalid_response(self, mock_client):
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="'Not a dictionary'"))]
        )
        transcription_text = "My name is John Doe and my email is john.doe@example.com."
        form_structure = {"name": "Full Name", "email": "Email Address"}
        with self.assertRaises(HTTPException) as context:
            OpenAIUtils.prepare_context(transcription_text, form_structure)
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn(
            "Failed to parse the AI's response: The AI response is not a valid dictionary.", context.exception.detail
        )

    class TestOpenAIUtils(unittest.TestCase):
        @patch.object(OpenAIUtils, "_client", create=True)
        @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="audio data")
        def test_transcribe_audio_exception(self, mock_open, mock_client):
            mock_client.audio.transcriptions.create.side_effect = Exception("Transcription error")
            with self.assertRaises(HTTPException) as context:
                OpenAIUtils.transcribe_audio("test_audio.mp3")
            self.assertEqual(context.exception.status_code, 424)
            self.assertIn(
                "Failed to transcribe audio from the file: test_audio.mp3. Error: Transcription error",
                context.exception.detail,
            )
