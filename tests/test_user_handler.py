import pytest
from unittest.mock import patch, MagicMock, ANY
from io import BytesIO
from prompt_handler.llm import UserPromptHandler
from prompt_handler.different_llms.base import LLMBase

# Простий імітований LLM для UserPromptHandler
class SimpleLLMForUserHandler(LLMBase):
    def answer(self, prompt_text):
        return f"LLM відповіло на: {prompt_text}"

@pytest.fixture
@patch('prompt_handler.llm.TTS') # Імітуємо клас TTS
@patch('prompt_handler.llm.WhisperModel') # Імітуємо клас WhisperModel
@patch('prompt_handler.llm.torch.cuda.is_available', return_value=False) # CUDA недоступна
def user_prompt_h_fixture(mock_cuda_check, MockWhisper, MockTTS):
    MockTTS.return_value.to.return_value = MockTTS.return_value # .to() повертає той самий об'єкт

    h = UserPromptHandler(
        model=SimpleLLMForUserHandler(),
        tts_model="any_tts_model_name",
        whisper_model_size="tiny"
    )
    return h, MockTTS.return_value, MockWhisper.return_value

def test_uph_generate_audio_file(user_prompt_h_fixture):
    u_handler, mock_tts, _ = user_prompt_h_fixture
    text_for_speech = "Тестова фраза для звуку"

    mock_uuid_obj = MagicMock()
    mock_uuid_obj.hex = "testaudio123"
    mock_uuid_obj.__str__ = MagicMock(return_value="testaudio123")

    with patch('prompt_handler.llm.uuid.uuid4', return_value=mock_uuid_obj):
        with patch('prompt_handler.llm.os.path.join', return_value="static/testaudio123.wav") as mock_join:
            audio_file_path = u_handler._generate_tts_audio(text_for_speech)

    assert audio_file_path == "static/testaudio123.wav"
    mock_join.assert_called_once_with("static", "testaudio123.wav") # Перевірка os.path.join
    mock_tts.tts_to_file.assert_called_once_with(text_for_speech, file_path="static/testaudio123.wav")

@patch('prompt_handler.llm.CommandsHandler.process_prompt') # Імітуємо внутрішній CommandsHandler
def test_uph_process_simple_text(mock_cmd_handler_proc, user_prompt_h_fixture):
    u_handler, _, _ = user_prompt_h_fixture
    test_uid = 1
    text_from_user = "Привіт, бот"

    mock_cmd_handler_proc.return_value = "Бот каже: Привіт!"

    with patch.object(u_handler, '_generate_tts_audio', return_value="static/generated_speech.wav") as mock_gen_audio:
        result_dict = u_handler.process_prompt(test_uid, text_from_user)

    mock_cmd_handler_proc.assert_called_once_with(test_uid, text_from_user)
    mock_gen_audio.assert_called_once_with("Бот каже: Привіт!")
    assert result_dict["response_text"] == "Бот каже: Привіт!"
    assert result_dict["audio_file_path"] == "static/generated_speech.wav"
    assert result_dict["timer_timestamp"] is None


def test_uph_process_audio_input(user_prompt_h_fixture):
    u_handler, _, mock_whisper = user_prompt_h_fixture
    test_uid = 1
    dummy_audio_stream = BytesIO(b"audio data example")

    fake_segment1 = MagicMock()
    fake_segment1.text = "Розпізнано "
    fake_segment2 = MagicMock()
    fake_segment2.text = "з аудіо"
    mock_whisper.transcribe.return_value = ([fake_segment1, fake_segment2], {"language": "en"})

    recognized_text = "Розпізнано з аудіо"
    with patch.object(u_handler, 'process_prompt', return_value={
        "response_text": f"Відповідь на: {recognized_text}",
        "audio_file_path": "static/audio_reply.wav",
        "timer_timestamp": None
    }) as mock_internal_txt_proc:
        result_dict = u_handler.process_prompt_by_audio_file(test_uid, dummy_audio_stream)

    mock_whisper.transcribe.assert_called_once_with(dummy_audio_stream, language="en", beam_size=5)
    mock_internal_txt_proc.assert_called_once_with(test_uid, recognized_text)
    assert result_dict["response_text"] == f"Відповідь на: {recognized_text}"