import time

import pytest

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


# --- Create Location ---

def test_create_existing_location(app):
    with app.app_context():
        Locations.create_location(name="Miami", fahrenheit=82.4, celsius=28.0, humidity=63, wind_speed=6.17, weather_description='few clouds')
        
        with pytest.raises(ValueError, match="UNIQUE constraint failed"):
            Locations.create_location(name="Miami", fahrenheit=82.4, celsius=28.0, humidity=63, wind_speed=6.17, weather_description='few clouds')

def test_create_location_invalid_data(cls, name, fahrenheit, celsius, humidity, wind_speed, weather_description):
    """Test validation errors when creating a location."""
    with pytest.raises(ValueError, match=err_msg):
        Locations.create_location(cls, name, fahrenheit, celsius, humidity, wind_speed, weather_description)

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
    sample_location1.update_weather("win")
    assert sample_location1.fights == 1
    assert sample_location1.wins == 1

    assert sample_location1.fahrenheit == weather_data.get('Fahrenheit', self.fahrenheit)
    assert sample_location1.celsius == weather_data.get('Celsius', self.celsius)
    assert sample_location1.humidity == weather_data.get('Humidity', self.humidity)
    assert sample_location1.wind_speed == weather_data.get('Wind Speed', self.wind_speed)
    assert sample_location1.weather_description == weather_data.get('Weather Description', self.weather_description)
    assert sample_location1.last_updated == datetime.now()
  
#Needs to be fixed
def test_get_all_locations(sample_locations):
    """Test retrieving all locations from the database."""
    retrieved_locations = Locations.get_all_locations()
    sample_locations.extend([location.id for location in sample_locations])

    locations = sample_locations.get_all_locations()
    assert locations == sample_locations, "Expected get_boxers to return the correct boxers list."



def test_get_all_locations_empty(session):
    """Test retrieving locations when the database is empty."""
    retrieved_locations = Locations.get_all_locations()

    assert retrieved_locations == []