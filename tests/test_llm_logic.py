import pytest
from unittest.mock import MagicMock, patch
from prompt_handler.llm import (
    CommandTypes, DefaultCommandExtractor, CommandsHandler
)
from prompt_handler.different_llms.base import LLMBase
from prompt_handler import facts_and_jokes, prompts

class MyMockLLM(LLMBase):
    def __init__(self, replies):
        self.replies = replies
        self.reply_idx = 0
        self.last_prompt = ""

    def answer(self, prompt_text) -> str:
        self.last_prompt = prompt_text
        reply = self.replies[self.reply_idx]
        self.reply_idx = (self.reply_idx + 1) % len(self.replies)
        return reply

def test_default_cmd_extractor():
    extractor = DefaultCommandExtractor()
    assert extractor("Текст ****1**** текст") == "1"
    assert extractor("Інший текст без зірочок") == 1

def test_cmd_handler_determine_convo():
    llm = MyMockLLM(replies=["****1****"])
    handler = CommandsHandler(model=llm)

    user_q = "Привіт, як справи?"
    cmd_type = handler.determine_command(user_q)

    assert cmd_type == CommandTypes.conversation
    expected_cmd_prompt = prompts.determine_command.format(user_q)
    assert llm.last_prompt == expected_cmd_prompt

def test_cmd_handler_process_joke():
    llm = MyMockLLM(replies=["****5****"])
    handler = CommandsHandler(model=llm)

    test_user_id = 100
    user_q = "Розкажи анекдот"
    reply = handler.process_prompt(test_user_id, user_q)

    assert reply in facts_and_jokes.jokes

@patch('prompt_handler.llm.get_weather_info_response') # Імітуємо функцію погоди
def test_cmd_handler_process_weather_req(mock_get_weather):
    llm = MyMockLLM(replies=[
        "****2****",
        "{\"city\": \"Lviv\"}"
    ])
    handler = CommandsHandler(model=llm)

    mock_get_weather.return_value = "У Львові сьогодні хмарно."

    test_user_id = 1
    user_q = "Погода у Львові яка?"
    reply = handler.process_prompt(test_user_id, user_q)

    assert reply == "У Львові сьогодні хмарно."
    mock_get_weather.assert_called_once_with("Lviv")