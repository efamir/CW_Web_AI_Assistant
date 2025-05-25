import pytest
from unittest.mock import patch, MagicMock
from prompt_handler.different_llms.gemini import GeminiFlash2

@patch('prompt_handler.different_llms.gemini.genai.Client') # Імітуємо клієнт Gemini
def test_gemini_answer(mock_genai_constructor):
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.text = "Gemini каже привіт!"
    fake_client.models.generate_content.return_value = fake_response
    mock_genai_constructor.return_value = fake_client

    with patch('prompt_handler.different_llms.gemini.gemini_key', "TEST_GEMINI_KEY"):
        gemini_model = GeminiFlash2()
        my_prompt = "Як справи, Gemini?"
        api_response = gemini_model.answer(my_prompt)

    assert api_response == "Gemini каже привіт!"
    fake_client.models.generate_content.assert_called_once_with(
        model="gemini-2.0-flash",
        contents=my_prompt
    )
