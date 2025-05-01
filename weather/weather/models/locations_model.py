from typing import List
from datetime import datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from weather.db import db
from weather.utils.logger import configure_logger

import logging

logger = logging.getLogger(__name__)
configure_logger(logger)


class Locations(db.Model):
    """Represents a weather location in the system.

    This model maps to the 'locations' table in the database and stores location
    information and current weather data such as temperature, humidity, and wind speed.
    """
    
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    fahrenheit = db.Column(db.Float)
    celsius = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    weather_description = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime)

    def __init__(self, name: str, fahrenheit=None, celsius=None, humidity=None, wind_speed=None, weather_description=None):
        """Initialize a new Location instance with basic attributes.

        Args:
            name (str): The location name. Must be unique.
            fahrenheit (float, optional): Temperature in Fahrenheit.
            celsius (float, optional): Temperature in Celsius.
            humidity (float, optional): Humidity percentage.
            wind_speed (float, optional): Wind speed.
            weather_description (str, optional): Description of the weather.
        """
        self.name = name
        self.fahrenheit = fahrenheit
        self.celsius = celsius
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_description = weather_description
        self.last_updated = datetime.now()

    @classmethod
    def create_location(cls, name: str, fahrenheit=None, celsius=None, humidity=None, wind_speed=None, weather_description=None) -> None:
        """Creates a new location and saves it to the database.

        Args:
            name (str): The location name.
            fahrenheit (float, optional): Temperature in Fahrenheit.
            celsius (float, optional): Temperature in Celsius.
            humidity (float, optional): Humidity percentage.
            wind_speed (float, optional): Wind speed.
            weather_description (str, optional): Description of the weather.

        Returns:
            None

        Raises:
            IntegrityError: If a location with the same name already exists.
        """
        logger.info(f"Received request to create location: {name}")
        
        location = cls(
            name=name,
            fahrenheit=fahrenheit,
            celsius=celsius,
            humidity=humidity,
            wind_speed=wind_speed,
            weather_description=weather_description
        )
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not fahrenheit or (not isinstance(fahrenheit, int) and not isinstance(fahrenheit, float)):
            raise ValueError("Fahrenheit must be an int or float.")
        if not celsius or (not isinstance(celsius, int) and not isinstance(celsius, float)):
            raise ValueError("Celsius must be an int or float.")
        if not humidity or (not isinstance(humidity, int) and not isinstance(humidity, float)):
            raise ValueError("Humidity must be an int or float.")
        if not wind_speed or (not isinstance(wind_speed, int) and not isinstance(wind_speed, float)):
            raise ValueError("Wind Speed must be an int or float.")
        if not weather_description or not isinstance(weather_description, str):
            raise ValueError("Weather Description must be a non-empty string.")
        
        try:
            # Check for existing location with key name
            existing = Locations.query.filter_by(name=name.strip()).first()
            if existing:
                logger.error(f"Location already exists: {name}")
                raise ValueError(f"Location with name '{name}' already exists.")

            db.session.add(location)
            db.session.commit()
            logger.info(f"Location successfully added: {name}")

        except IntegrityError:
            logger.error(f"Location already exists: {name}")
            db.session.rollback()
            raise ValueError(f"Location with name '{name}' already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating location: {e}")
            db.session.rollback()
            raise

    @classmethod
    def get_location_by_id(cls, location_id: int) -> "Locations":
        """Get a location by its ID.

        Args:
            location_id (int): The ID of the location to retrieve.

        Returns:
            Locations: The location object with the given ID.

        Raises:
            ValueError: If no location with the given ID exists.
        """
        logger.info(f"Attempting to retrieve location with ID {location_id}")

        try:
            location = cls.query.get(location_id)

            if not location:
                logger.info(f"Location with ID {location_id} not found")
                raise ValueError(f"Location with ID {location_id} not found")

            logger.info(f"Successfully retrieved location: {location.name}")
            return location

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by ID {location_id}: {e}")
            raise

    @classmethod
    def get_location_by_name(cls, name: str) -> "Locations":
        """Get a location by its name.

        Args:
            name (str): The name of the location to retrieve.

        Returns:
            Locations: The location object with the given name.

        Raises:
            ValueError: If no location with the given name exists.
        """
        logger.info(f"Attempting to retrieve location with name '{name}'")

        try:
            location = cls.query.filter_by(name=name.strip()).first()

            if not location:
                logger.info(f"Location with name '{name}' not found")
                raise ValueError(f"Location with name '{name}' not found")

            logger.info(f"Successfully retrieved location: {location.name}")
            return location

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by name '{name}'")
            raise

    @classmethod
    def delete_location(cls, location_id: int) -> None:
        """Delete a location by its ID.

        Args:
            location_id (int): The ID of the location to delete.

        Returns:
            None

        Raises:
            ValueError: If no location with the given ID exists.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete location with ID {location_id}")

        try:
            location = cls.query.get(location_id)
            if not location:
                logger.warning(f"Attempted to delete non-existent location with ID {location_id}")
                raise ValueError(f"Location with ID {location_id} not found")

            db.session.delete(location)
            db.session.commit()
            logger.info(f"Successfully deleted location with ID {location_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting location with ID {location_id}: {e}")
            db.session.rollback()
            raise

    def update_weather(self, weather_data: dict) -> None:
        """Update weather information for this location.

        Args:
            weather_data (dict): Dictionary containing updated weather data.
                Expected keys: 'Fahrenheit', 'Celsius', 'Humidity', 'Wind Speed', 'Weather Description'

        Returns:
            None
        """
        self.fahrenheit = weather_data.get('Fahrenheit', self.fahrenheit)
        self.celsius = weather_data.get('Celsius', self.celsius)
        self.humidity = weather_data.get('Humidity', self.humidity)
        self.wind_speed = weather_data.get('Wind Speed', self.wind_speed)
        self.weather_description = weather_data.get('Weather Description', self.weather_description)
        self.last_updated = datetime.now()
        
        db.session.commit()
        logger.info(f"Updated weather for location {self.name}")

    @staticmethod
    def get_all_locations() -> List["Locations"]:
        """Get all locations from the database.

        Returns:
            List[Locations]: A list of all location objects.
        """
        locations = Locations.query.all()
        logger.info(f"Retrieved all {len(locations)} locations")
        return locations
