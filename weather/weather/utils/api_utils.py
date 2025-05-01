import logging
import os
import requests

from weather.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


WEATHER_ORG_KEY = os.getenv("WEATHER_ORG_KEY")


def get_weather(location: str) -> dict:
    """
    Fetches weather data from openweathermap.org for a location.
    
    Args:
        location: The location to get weather for.

    Returns:
        dict[str]: The weather from openweathermap.org.

    Raises:
        ValueError: If the response from openweathermap.org is not a valid float.
        RuntimeError: If the request to openweathermap.org fails due to a timeout or other request-related error.

    """
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_ORG_KEY}"
    try:
        logger.info(f"Fetching weather from {api_url}")

        response = requests.get(api_url, timeout=5)
        data = response.json()

        # Check if the request was successful
        response.raise_for_status()
        
        if not isinstance(data, dict):
            raise ValueError(f"Invalid response from openweathermap.org: {data}")
        
        try: 
            weather = data['weather']
            if len(weather) >= 1:
                weather_desc = weather[0].get('description')
                
            main = data['main']
            temp_k = main['temp']
            temp_f = round((9/5) * (temp_k-273.15) + 32, 2)
            temp_c = round(temp_k-273.15, 2)
            humidity = main['humidity']
            wind = data['wind']
            wind_speed = wind['speed']
            
            weather = {
                'Location': location,
                'Fahrenheit': temp_f,
                'Celsius': temp_c,
                'Humidity': humidity,
                'Wind Speed': wind_speed,
                'Weather Description': weather_desc
            }
        except KeyError:
            raise ValueError(f"Invalid response from openweathermap.org: {data}")

        logger.debug(f"Received weather for {location}: {weather}")
        logger.info(f"Successfully fetched weather from {location}")

        return weather

    except requests.exceptions.Timeout:
        logger.error("Request to openweathermap.org timed out.")
        raise RuntimeError("Request to openweathermap.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to openweathermap.org failed: {e}")
        raise RuntimeError(f"Request to openweathermap.org failed: {e}")
