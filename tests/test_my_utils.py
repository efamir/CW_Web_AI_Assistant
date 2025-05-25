import pytest
from unittest.mock import patch, Mock
from prompt_handler import utils

def test_format_seconds():
    assert utils.format_seconds_to_human_readable(65) == "1 minute and 5 seconds"
    assert utils.format_seconds_to_human_readable(3600) == "1 hour"
    assert utils.format_seconds_to_human_readable(0) == "0 seconds"

@patch('prompt_handler.utils.requests.get') # Імітуємо requests.get
def test_get_weather_ok(mock_requests_get):
    fake_api_reply = Mock()
    fake_api_reply.status_code = 200
    fake_api_reply.json.return_value = {
        "name": "Kyiv",
        "weather": [{"description": "clear"}],
        "main": {"temp": 293.15, "feels_like": 292.15, "humidity": 60}, # 20°C
        "wind": {"speed": 3.0}
    }
    mock_requests_get.return_value = fake_api_reply

    with patch('prompt_handler.api_keys.key', "VALID_WEATHER_KEY"):
        report = utils.get_weather_info_response("Kyiv")

    assert ("Currently, it's clear in the Kyiv. The temperature is 20.0 degrees Celsius, feeling like 19.0 degrees Celsius."
            " The wind is coming at approximately 3.0 meters per second. Humidity is at 60 percent.") in report

@patch('prompt_handler.utils.requests.get')
def test_get_weather_city_not_found(mock_requests_get):
    fake_api_reply = Mock()
    fake_api_reply.status_code = 404
    fake_api_reply.raise_for_status.side_effect = utils.requests.exceptions.HTTPError(response=fake_api_reply)
    mock_requests_get.return_value = fake_api_reply

    with patch('prompt_handler.api_keys.key', "VALID_WEATHER_KEY"):
        report = utils.get_weather_info_response("МістоЯкогоНемає")
    assert "City МістоЯкогоНемає not found" in report
