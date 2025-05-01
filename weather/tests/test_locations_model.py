import time

import pytest

from sqlalchemy.exc import IntegrityError


from datetime import datetime, timedelta
from app import db, Locations
from weather.models.favorites_model import FavoritesModel
from weather.models.locations_model import Locations


@pytest.fixture
def sample_location1(session):
    location = Locations(
        name="Miami",
        fahrenheit=82.4,
        celsius=28.0,
        humidity=63,
        wind_speed=6.17,
        weather_description='few clouds'
    )
    # now we need to not only create the location but also add it to the database
    # and commit the session to persist the changes
    session.add(location)
    session.commit()
    return location

@pytest.fixture
def sample_location2(session):
    location = Locations(
        name="Brussels",
        fahrenheit=56.52,
        celsius=13.62,
        humidity=66,
        wind_speed=2.06,
        weather_description='clear sky'
    )
    session.add(location)
    session.commit()
    return location

@pytest.fixture
def sample_locations(sample_location1, sample_location2):
    return [sample_location1, sample_location2]

# --- Create Location ---
def test_create_location(session, app):
    name="Boston"
    fahrenheit=82.4
    celsius=28.0
    humidity=63
    wind_speed=6.17
    weather_description='few clouds'
    with app.app_context(): 
        location = Locations.create_location(
            name=name,
            fahrenheit=fahrenheit,
            celsius=celsius,
            humidity=humidity,
            wind_speed=wind_speed,
            weather_description= weather_description
        )

    location = Locations.query.filter_by(name=name).first()

    assert location is not None
    assert location.fahrenheit == fahrenheit
    assert location.celsius == celsius
    assert location.humidity == humidity
    assert location.wind_speed == wind_speed
    assert location.weather_description == weather_description


def test_create_existing_location(app, sample_location1):
    with app.app_context():
        
        with pytest.raises(IntegrityError):
            Locations.create_location(name="Miami", fahrenheit=82.4, celsius=28.0, humidity=63, wind_speed=6.17, weather_description='few clouds')

# --- Get Location ---

def test_get_location_by_id(sample_location1):
    """Test fetching a location by ID."""
    fetched = Locations.get_location_by_id(sample_location1.id)
    assert fetched.name == "Miami"

def test_get_location_by_id_not_found(app):
    """Test error when fetching nonexistent location by ID."""
    with pytest.raises(ValueError, match="not found"):
        Locations.get_location_by_id(999)

def test_get_location_by_name(sample_location1):
    """Test fetching a location by name."""
    fetched = Locations.get_location_by_name("Miami")
    assert fetched.id == sample_location1.id

def test_get_location_by_name_not_found(app):
    """Test error when fetching nonexistent location by name."""
    with pytest.raises(ValueError, match="not found"):
        Locations.get_location_by_name("Ghost Town")

# --- Delete Location ---

def test_delete_location_by_id(session, sample_location1):
    """Test deleting a location by ID."""
    Locations.delete_location(sample_location1.id)
    assert session.query(Locations).get(sample_location1.id) is None

def test_delete_location_not_found(app):
    """Test deleting a non-existent location by ID."""
    with pytest.raises(ValueError, match="not found"):
        Locations.delete_location(999)

# --- Weather Update ---

#Needs to be fixed
def test_update_weather(session, sample_location1):
    """Test weather updating for all attributes."""
    weather_data = {
        'Fahrenheit': 90.0,
        'Celsius': 32.22,
        'Humidity': 70,
        'Wind Speed': 8.0,
        'Weather Description': 'clear sky'
    }

    sample_location1.update_weather(weather_data)
    db.session.refresh(sample_location1)

        # Assertions to ensure that the location's weather info was updated
    assert sample_location1.fahrenheit == 90.0
    assert sample_location1.celsius == 32.22
    assert sample_location1.humidity == 70
    assert sample_location1.wind_speed == 8.0
    assert sample_location1.weather_description == 'clear sky'
    assert isinstance(sample_location1.last_updated, datetime)  # Ensure last_updated is a datetime object
    assert sample_location1.last_updated > datetime.now() - timedelta(seconds=1)  # Ensure the update was recent

        # Ensure the update was committed to the database
    assert sample_location1.fahrenheit == 90.0
  

def test_get_all_locations(sample_locations, app):
    """Test retrieving all locations from the database."""
    with app.app_context():
        # Fetch all locations from the database
        retrieved_locations = Locations.get_all_locations()

        # Assert the number of retrieved locations matches the sample data
        assert len(retrieved_locations) == len(sample_locations), (
            "The number of retrieved locations should match the number of sample locations."
        )

        # Assert all attributes match for each location
        for i, location in enumerate(sample_locations):
            assert retrieved_locations[i].name == location.name, "Location names should match."
            assert retrieved_locations[i].fahrenheit == location.fahrenheit, "Temperatures (F) should match."
            assert retrieved_locations[i].celsius == location.celsius, "Temperatures (C) should match."
            assert retrieved_locations[i].humidity == location.humidity, "Humidity levels should match."
            assert retrieved_locations[i].wind_speed == location.wind_speed, "Wind speeds should match."
            assert retrieved_locations[i].weather_description == location.weather_description, (
                "Weather descriptions should match."
            )


def test_get_all_locations_empty(session, app, sample_locations):
    """Test retrieving locations when the database is empty."""
    with app.app_context():
        # Fetch all locations from the database
        retrieved_locations = Locations.get_all_locations()

        # Assert the number of retrieved locations matches the sample data
        assert len(retrieved_locations) == len(sample_locations), (
            "The number of retrieved locations should match the number of sample locations."
        )

        # Assert all attributes match for each location
        for i, location in enumerate(sample_locations):
            assert retrieved_locations[i].name == location.name, "Location names should match."
            assert retrieved_locations[i].fahrenheit == location.fahrenheit, "Temperatures (F) should match."
            assert retrieved_locations[i].celsius == location.celsius, "Temperatures (C) should match."
            assert retrieved_locations[i].humidity == location.humidity, "Humidity levels should match."
            assert retrieved_locations[i].wind_speed == location.wind_speed, "Wind speeds should match."
            assert retrieved_locations[i].weather_description == location.weather_description, (
                "Weather descriptions should match."
            )