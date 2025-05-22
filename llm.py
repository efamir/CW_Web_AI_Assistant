import json

import ollama
from ollama import GenerateResponse
from faster_whisper import WhisperModel
import enum
import facts_and_jokes
import random
from TTS.api import TTS
import torch
from utils import *
import db

import prompts
from abc import ABC, abstractmethod
import re


class CommandTypes(enum.Enum):
    conversation = 1
    weather = 2
    timer = 3
    create_note = 4
    tell_joke = 5
    tell_fact = 6


class CommandExtractor(ABC):
    @abstractmethod
    def __call__(self, prompt: str) -> str:
        pass


class DeepSeekCommandExtractor(CommandExtractor):
    def __call__(self, prompt: str) -> str:
        return prompt.split("</think>")[1].strip()


class DefaultCommandExtractor(CommandExtractor):
    def __call__(self, prompt: str) -> str:
        result = re.search(r"\*\*\*\*(\d)\*\*\*\*", prompt)
        return result.groups()[0] if result else 1


class DeepSeekConversationExtractor(CommandExtractor):
    def __call__(self, prompt: str) -> str:
        return prompt.split("</think>")[-1].replace('```', '').replace('json', '')


class CommandsHandler:
    def __init__(
            self,
            model: str,
            command_extractor: CommandExtractor = DefaultCommandExtractor(),
            conversation_extractor: CommandExtractor | None = None
    ):
        self.__model = model
        self.__command_extractor = command_extractor
        self.__conversation_extractor = conversation_extractor

    def process_prompt(self, user_id: int, prompt: str) -> str | dict:
        command: CommandTypes = self.determine_command(prompt)
        if command == command.conversation:
            response = ollama.generate(model=self.__model, prompt=prompt).response
            if self.__conversation_extractor:
                response = self.__conversation_extractor(response)
            return response
        if command == command.weather:
            response = ollama.generate(model=self.__model,
                                       prompt=prompts.extract_weather_details_short.format(prompt)).response
            if self.__conversation_extractor:
                response = self.__conversation_extractor(response)

            error_response = "Sorry, I didn't hear quite well. Could you repeat?"
            try:
                response_dict = json.loads(response)
                city_name = response_dict.get("city")
                if not city_name:
                    print(response)
                    return error_response
                if city_name.lower() == "error":
                    return "Please, tell me the city name, so i could give you the current weather there."
            except json.decoder.JSONDecodeError:
                print(response)
                return error_response

            return get_weather_info_response(city_name)
        if command == command.timer:
            response = ollama.generate(model=self.__model,
                                       prompt=prompts.extract_timer_details_short.format(prompt)).response
            if self.__conversation_extractor:
                response = self.__conversation_extractor(response)

            error_response = "Sorry, I didn't hear quite well. Could you repeat?"
            try:
                response_dict = json.loads(response)
                seconds = response_dict.get("seconds")
                seconds = int(seconds)
                if not seconds:
                    print(response)
                    return error_response
                if isinstance(seconds, str):
                    return "Please, tell me for how long would you like to set the timer."
            except json.decoder.JSONDecodeError:
                print(response)
                return error_response
            except ValueError:
                print(response)
                return error_response

            if seconds <= 0:
                return "I can't set a timer that has negative or 0 seconds in it."

            response = f"I set the timer for {format_seconds_to_human_readable(seconds)}"

            return {"response": response, "timestamp": get_future_time_as_unix_milliseconds(seconds)}
        if command == command.create_note:
            response = ollama.generate(model=self.__model,
                                       prompt=prompts.extract_note_content_short.format(prompt)).response
            if self.__conversation_extractor:
                response = self.__conversation_extractor(response)

            note = db.Note(text=response, user_id=user_id)
            db.session.add(note)
            db.session.commit()

            return f"I written {response} down into the notes. You can check them later in the separate menu."
        if command == command.tell_joke:
            return random.choice(facts_and_jokes.jokes)
        if command == command.tell_fact:
            return random.choice(facts_and_jokes.fun_facts)
        return ""

    def determine_command(self, prompt) -> CommandTypes:
        response: GenerateResponse = ollama.generate(model=self.__model,
                                                     prompt=prompts.determine_command.format(prompt))
        command = CommandTypes.conversation
        response_text = self.__command_extractor(response.response) if self.__command_extractor else response.response
        try:
            command = CommandTypes(int(response_text))
        except ValueError:
            print(f"Value error. Response: ", response.response)
            pass

        print(command)
        return command


class UserPromptHandler:
    def __init__(self, model: str, tts_model: str,
                 command_extractor: CommandExtractor = DefaultCommandExtractor(),
                 conversation_extractor: CommandExtractor | None = None,
                 whisper_model_size: str = "small"):
        self.__command_handler = CommandsHandler(model, command_extractor, conversation_extractor)
        self.__model = model
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        self.__tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch").to(self.__device)
        self.__whisper = WhisperModel(whisper_model_size, device=self.__device, compute_type="float16")

    def process_prompt(self, user_id: int, prompt: str):
        response = self.__command_handler.process_prompt(user_id, prompt)
        if isinstance(response, str):
            self.tts(response)
            return response

        response_text = response.get("response", "Sorry, something went wrong. Could you repeat?")
        self.tts(response_text)
        return response_text

    def tts(self, text):
        self.__tts.tts_to_file(text, file_path="tts-test.wav")

    def process_prompt_by_audio_file(self, user_id: int, filepath: str):
        segments, info = self.__whisper.transcribe(filepath, beam_size=5)
        input_text = ""
        for segment in segments:
            input_text += segment.text
        print("Transcribed audio:", input_text)
        return self.process_prompt(user_id, input_text)


if __name__ == '__main__':
    # a = CommandsHandler("deepseek-r1:8b")  # llama2-uncensored:7b deepseek-r1:8b mistral
    # while True:
    #     user_inp = input(">>> ")
    #     if user_inp == "q":
    #         break
    #     print(a.determine_command(user_inp))

    a = UserPromptHandler("deepseek-r1:8b", "tts_models/en/ljspeech/fast_pitch",
                          conversation_extractor=DeepSeekConversationExtractor())
    # answer = a.process_prompt(1, input(">>>"))
    # print(answer)
    # answer = a.process_prompt(1, input(">>>"))
    # print(answer)

    print("Answer:", a.process_prompt_by_audio_file(1, "audio_tests\\gigle.mp3"))
    print("Answer:", a.process_prompt_by_audio_file(1, "audio_tests\\lost.mp3"))
    print("Answer:", a.process_prompt_by_audio_file(1, "audio_tests\\timer.mp3"))
