import requests
import datetime
from prompt_handler.api_keys import key


def get_weather_info_response(city_name_query: str) -> str:
    api_key = key
    if api_key == "YOUR_ACTUAL_API_TOKEN" or api_key == "TOKEN":
        return "Error: Please set your OpenWeatherMap API key in the code."

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name_query.strip()}&appid={api_key}&lang=en"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        weather_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return "Error: Invalid API key. Please check your token."
        elif response.status_code == 404:
            return f"City {city_name_query} not found. Please check the name."
        else:
            return f"An HTTP error occurred. Sorry"
    except requests.exceptions.RequestException as req_err:
        return f"A request error occurred. Sorry"
    except ValueError:  # Includes JSONDecodeError
        return "Error: Could not parse the weather data from the server."

    city_name_api = weather_data.get('name', 'the specified location')
    weather_conditions_list = weather_data.get('weather', [])
    if not weather_conditions_list:
        description = "not available"
    else:
        description = weather_conditions_list[0].get('description', "not available")

    main_data = weather_data.get('main', {})
    temp_kelvin = main_data.get('temp')
    feels_like_kelvin = main_data.get('feels_like')
    humidity = main_data.get('humidity')

    wind_data = weather_data.get('wind', {})
    wind_speed_mps = wind_data.get('speed')  # meters per second

    # Check if essential data is missing
    if any(v is None for v in [temp_kelvin, feels_like_kelvin, humidity, wind_speed_mps]):
        return f"Sorry, some weather data for {city_name_api} is currently unavailable to give a full report."

    temp_celsius = temp_kelvin - 273.15
    feels_like_celsius = feels_like_kelvin - 273.15

    # --- Create the Formatted String ---
    weather_report_tts = (
        f"Currently, it's {description} in the {city_name_api}. "
        f"The temperature is {temp_celsius:.1f} degrees Celsius, feeling like {feels_like_celsius:.1f} degrees Celsius. "
        f"The wind is coming at approximately {wind_speed_mps:.1f} meters per second. "
        f"Humidity is at {humidity} percent. "
    )

    return weather_report_tts


def format_seconds_to_human_readable(total_seconds: int) -> str:
    if total_seconds < 0:
        raise ValueError("Total seconds cannot be negative.")

    if total_seconds == 0:
        return "0 seconds"

    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    time_parts = []

    def append_unit(value, unit_name):
        if value > 0:
            time_parts.append(f"{value} {unit_name}{'s' if value != 1 else ''}")

    append_unit(hours, "hour")
    append_unit(minutes, "minute")
    append_unit(seconds, "second")

    if not time_parts:
        return ""
    elif len(time_parts) == 1:
        return time_parts[0]
    elif len(time_parts) == 2:
        return f"{time_parts[0]} and {time_parts[1]}"
    else:
        return ", ".join(time_parts[:-1]) + f", and {time_parts[-1]}"


def get_future_time_as_unix_milliseconds(seconds_to_add: int) -> int:
    current_datetime = datetime.datetime.now()
    time_difference = datetime.timedelta(seconds=seconds_to_add)
    future_datetime = current_datetime + time_difference
    future_timestamp_seconds = future_datetime.timestamp()
    future_timestamp_milliseconds = int(future_timestamp_seconds * 1000)

    return future_timestamp_milliseconds
