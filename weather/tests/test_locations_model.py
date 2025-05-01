import pytest

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

def test_create_location(session):
    name="Boston"
    fahrenheit=82.4
    celsius=28.0
    humidity=63
    wind_speed=6.17
    weather_description='few clouds'
    Locations.create_location(
        name=name,
        fahrenheit=fahrenheit,
        celsius=celsius,
        humidity=humidity,
        wind_speed=wind_speed,
        weather_description= weather_description
    )

    location = session.query(Locations).filter_by(name=name).first()

    assert location is not None
    assert location.fahrenheit == fahrenheit
    assert location.celsius == celsius
    assert location.humidity == humidity
    assert location.wind_speed == wind_speed
    assert location.weather_description == weather_description


def test_create_location_duplicate(session, sample_location1):
    """Test creating a location with a duplicate name"""
    with pytest.raises(ValueError, match="Location with name 'Miami' already exists."):
        Locations.create_location("Miami", 86.4, 28.5, 65, 4.17, 'a lot of clouds')
        
@pytest.mark.parametrize("name, fahrenheit, celsius, humidity, wind_speed, weather_description", [
    ("", 50, 20, 60, 2.5, "cloudy"),
    ("Valid Name", "", 20, 60, 2.5, "cloudy"),
    ("Valid Name", 50, "", 60, 2.5, "cloudy"),
    ("Valid Name", 50, 20, "", 2.5, "cloudy"),
    ("Valid Name", 50, 20, 60, "", "cloudy"),
    ("Valid Name", 50, 20, 60, 2.5, 100),
])
def test_create_location_invalid_data(name, fahrenheit, celsius, humidity, wind_speed, weather_description):
    """Test validation errors when creating a location."""
    with pytest.raises(ValueError):
        Locations.create_location(name, fahrenheit, celsius, humidity, wind_speed, weather_description)

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

def test_update_weather(session, sample_location1):
    """Test weather updating for all attributes."""
    weather_data = {
        'Fahrenheit': 20,
        'Celsius': 40,
        'Humidity': 60,
        'Wind Speed': 2.5,
        'Weather Description': 'very cloudy' 
    }
    sample_location1.update_weather(weather_data)

    assert sample_location1.fahrenheit == weather_data.get('Fahrenheit')
    assert sample_location1.celsius == weather_data.get('Celsius')
    assert sample_location1.humidity == weather_data.get('Humidity')
    assert sample_location1.wind_speed == weather_data.get('Wind Speed')
    assert sample_location1.weather_description == weather_data.get('Weather Description')
  

def test_get_all_locations(sample_locations):
    """Test retrieving all locations from the database."""
    retrieved_locations = Locations.get_all_locations()

    assert retrieved_locations == sample_locations, "Expected get_boxers to return the correct boxers list."



def test_get_all_locations_empty(session):
    """Test retrieving locations when the database is empty."""
    retrieved_locations = Locations.get_all_locations()

    assert retrieved_locations == []
