from typing import List
from datetime import datetime

from sqlalchemy.exc import IntegrityError

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
        try:
            location = cls(
                name=name,
                fahrenheit=fahrenheit,
                celsius=celsius,
                humidity=humidity,
                wind_speed=wind_speed,
                weather_description=weather_description
            )
            db.session.add(location)
            db.session.commit()
            logger.info(f"Created location: {name}")
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Location {name} already exists.")
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
        location = cls.query.get(location_id)
        if location is None:
            logger.error(f"Location with id {location_id} not found.")
            raise ValueError(f"Location with id {location_id} not found.")
        return location

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
        location = cls.query.filter_by(name=name).first()
        if location is None:
            logger.error(f"Location with name {name} not found.")
            raise ValueError(f"Location with name {name} not found.")
        return location

    @classmethod
    def delete(cls, location_id: int) -> None:
        """Delete a location by its ID.

        Args:
            location_id (int): The ID of the location to delete.

        Returns:
            None

        Raises:
            ValueError: If no location with the given ID exists.
        """
        location = cls.query.get(location_id)
        if location is None:
            logger.error(f"Cannot delete: location with id {location_id} not found.")
            raise ValueError(f"Location with id {location_id} not found.")
        
        db.session.delete(location)
        db.session.commit()
        logger.info(f"Deleted location {location.name} (ID: {location_id})")

    def update_weather(self, weather_data: dict) -> None:
        """Update weather information for this location.

        Args:
            weather_data (dict): Dictionary containing updated weather data.
                Expected keys: 'Fahrenheit', 'Celsius', 'Humidity', 'Wind Speed'

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