from typing import List, Dict, Any
import time
import os
import logging

from weather.models.locations_model import Locations
from weather.utils.logger import configure_logger
from weather.utils.api_utils import get_weather

logger = logging.getLogger(__name__)
configure_logger(logger)


class FavoritesModel:
    """A class to manage favorite weather locations.

    Provides functionality to add, retrieve, and manage favorite locations
    with their weather data.
    """

    def __init__(self):
        """Initializes the FavoritesModel with an empty list of favorite locations.

        The favorites list is initially empty, and the location cache and 
        time-to-live (TTL) caches are also initialized.
        The TTL is set to 60 seconds by default, but this can be overridden 
        by setting the TTL_SECONDS environment variable.

        Attributes:
            favorites (List[int]): The list of ids of favorite locations.
            _location_cache (dict[int, Locations]): Cache to store location objects for quick access.
            _ttl (dict[int, float]): Cache to store the time-to-live for each location.
            ttl_seconds (int): The time-to-live in seconds for cached location objects.
        """
        self.favorites: List[int] = []
        self._location_cache: dict[int, Locations] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))  # Default TTL is 60 seconds

    def add_favorite(self, location_id: int) -> None:
        """Add a location to favorites list.

        Args:
            location_id (int): The ID of the location to add to favorites.

        Returns:
            None

        Raises:
            ValueError: If the location does not exist or is already in favorites.
        """
        # Check if location exists
        try:
            location = Locations.get_location_by_id(location_id)
        except ValueError:
            logger.error(f"Cannot add to favorites: Location with id {location_id} not found.")
            raise ValueError(f"Location with id {location_id} not found.")
        
        # Check if location is already in favorites
        if location_id in self.favorites:
            logger.warning(f"Location {location.name} is already in favorites.")
            return
        
        self.favorites.append(location_id)
        self._location_cache[location_id] = location
        self._ttl[location_id] = time.time() + self.ttl_seconds
        
        logger.info(f"Added location {location.name} to favorites.")

    def remove_favorite(self, location_id: int) -> None:
        """Remove a location from favorites list.

        Args:
            location_id (int): The ID of the location to remove from favorites.

        Returns:
            None

        Raises:
            ValueError: If the location is not in favorites.
        """
        if location_id not in self.favorites:
            logger.error(f"Cannot remove from favorites: Location with id {location_id} is not in favorites.")
            raise ValueError(f"Location with id {location_id} is not in favorites.")
        
        self.favorites.remove(location_id)
        
        if location_id in self._location_cache:
            del self._location_cache[location_id]
        
        if location_id in self._ttl:
            del self._ttl[location_id]
        
        logger.info(f"Removed location with id {location_id} from favorites.")

    def clear_favorites(self) -> None:
        """Clear all favorites.

        Returns:
            None
        """
        self.favorites.clear()
        self._location_cache.clear()
        self._ttl.clear()
        logger.info("Cleared all favorites.")

    def get_favorites(self) -> List[Locations]:
        """Get all favorite locations.

        Returns:
            List[Locations]: A list of all favorite location objects.
        """
        result = []
        
        for location_id in self.favorites:
            # Check if location is in cache and not expired
            if location_id in self._location_cache and time.time() < self._ttl.get(location_id, 0):
                result.append(self._location_cache[location_id])
            else:
                try:
                    # Get location from database
                    location = Locations.get_location_by_id(location_id)
                    # Update cache
                    self._location_cache[location_id] = location
                    self._ttl[location_id] = time.time() + self.ttl_seconds
                    result.append(location)
                except ValueError:
                    logger.warning(f"Location with id {location_id} not found, removing from favorites.")
                    self.favorites.remove(location_id)
        
        logger.info(f"Retrieved {len(result)} favorite locations.")
        return result

    def get_weather_for_location(self, location_name: str) -> Dict[str, Any]:
        """Get current weather for a specific location.

        Args:
            location_name (str): The name of the location to get weather for.

        Returns:
            Dict[str, Any]: Weather data for the location.
        """
        try:
            # Try to get location from database first
            try:
                location = Locations.get_location_by_name(location_name)
                
                # If we have recent data, use it
                if location.last_updated and (datetime.now() - location.last_updated).total_seconds() < self.ttl_seconds:
                    logger.info(f"Using cached weather data for {location_name}")
                    return {
                        'Location': location.name,
                        'Fahrenheit': location.fahrenheit,
                        'Celsius': location.celsius,
                        'Humidity': location.humidity,
                        'Wind Speed': location.wind_speed
                    }
            except ValueError:
                # Location doesn't exist in database, we'll create it after getting weather data
                pass
            
            # Get weather data from API
            weather_data = get_weather(location_name)
            
            # Update existing location or create new one
            try:
                location = Locations.get_location_by_name(location_name)
                location.update_weather(weather_data)
            except ValueError:
                # Create new location
                Locations.create_location(
                    name=location_name,
                    fahrenheit=weather_data.get('Fahrenheit'),
                    celsius=weather_data.get('Celsius'),
                    humidity=weather_data.get('Humidity'),
                    wind_speed=weather_data.get('Wind Speed'),
                    weather_description=weather_data.get('Weather Description')
                )
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather for {location_name}: {str(e)}")
            raise RuntimeError(f"Error getting weather for {location_name}: {str(e)}")

    def get_all_favorites_with_weather(self) -> List[Dict[str, Any]]:
        """Get all favorites with their current weather data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing weather data for each favorite location.
        """
        result = []
        for location in self.get_favorites():
            try:
                weather_data = self.get_weather_for_location(location.name)
                result.append(weather_data)
            except Exception as e:
                logger.error(f"Error getting weather for {location.name}: {str(e)}")
                # Include the location with error message
                result.append({
                    'Location': location.name,
                    'Error': str(e)
                })
        
        return result

    def get_historical_weather_for_location(self, location_id: int) -> Dict[str, Any]:
        """Placeholder for historical weather feature.
        
        This would require additional API functionality to implement fully.

        Args:
            location_id (int): The ID of the location to get historical weather for.

        Returns:
            Dict[str, Any]: A placeholder response.
        """
        try:
            location = Locations.get_location_by_id(location_id)
            logger.info(f"Historical weather requested for {location.name} (not implemented)")
            return {
                'Location': location.name,
                'Message': 'Historical weather data not implemented yet'
            }
        except ValueError as e:
            logger.error(str(e))
            raise

    def get_forecast_for_location(self, location_id: int) -> Dict[str, Any]:
        """Placeholder for forecast feature.
        
        This would require additional API functionality to implement fully.

        Args:
            location_id (int): The ID of the location to get forecast for.

        Returns:
            Dict[str, Any]: A placeholder response.
        """
        try:
            location = Locations.get_location_by_id(location_id)
            logger.info(f"Forecast requested for {location.name} (not implemented)")
            return {
                'Location': location.name,
                'Message': 'Forecast data not implemented yet'
            }
        except ValueError as e:
            logger.error(str(e))
            raise

    def clear_cache(self) -> None:
        """Clear the location cache.

        Returns:
            None
        """
        self._location_cache.clear()
        self._ttl.clear()
        logger.info("Cleared location cache.")