import logging
import os
import requests

from weather.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


WEATHER_ORG_KEY = os.getenv("WEATHER_ORG_KEY")


def get_weather(location: str) -> float:
    """
    Fetches weather data from openweathermap.org for a location.
    
    Args:
        location: The location to get weather for.

    Returns:
        dict[str]: The weather from random.org.

    Raises:
        ValueError: If the response from openweathermap.org is not a valid float.
        RuntimeError: If the request to openweathermap.org fails due to a timeout or other request-related error.

    """
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_ORG_KEY}"
    try:
        logger.info(f"Fetching weather from {api_url}")

        response = requests.get(api_url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()
        
        try: 
            weather = response['weather']
            if len(weather) >= 1:
                weather_desc = weather[0].get('description')
                
            main = response['main']
            temp_k = main['temp']
            temp_f = (9/5) * (temp_k-273.15) + 32
            temp_c = temp_k-273.15
            humidity = main['humidity']
            wind = response['wind']
            wind_speed = wind['speed']
            
            weather = {
                'Location': location,
                'Fahrenheit': temp_f,
                'Celsius': temp_c,
                'Humidity': humidity,
                'Wind Speed': wind_speed
            }
        except KeyError:
            raise ValueError(f"Invalid response from openweathermap.org: {response}")

        logger.debug(f"Received weather for {location}: {weather:.3f}")
        logger.info(f"Successfully fetched weather from {location}")

        return weather

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")

