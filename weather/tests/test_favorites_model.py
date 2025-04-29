import time

import pytest

from weather.models.favorites_model import FavoritesModel
from weather.models.locations_model import Locations


@pytest.fixture
def favorite_model():
    """Fixture to provide a new instance of FavoritesModel for each test.

    """
    return FavoritesModel()

# Fixtures providing sample boxers
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


##########################################################
# Favorites Prep
##########################################################


def test_clear_favorites(favorite_model):
    """Test that clear_favorites empties the favorites.

    """
    favorite_model.favorites = [1, 2]  # Assuming boxer IDs 1 and 2 are in the ring)

    favorite_model.clear_favorites()

    assert len(favorite_model.favorites) == 0, "Favorites should be empty after calling clear_favorites."

def test_clear_favorites_empty(favorite_model, caplog):
    """Test that calling clear_favorites on an empty favorites logs a warning and keeps the favorites empty.

    """
    with caplog.at_level("WARNING"):
        favorite_model.clear_favorites()

    assert len(favorite_model.favorites) == 0, "Favorites should remain empty if it was already empty."

    assert "Attempted to clear an empty favorites." in caplog.text, "Expected a warning when clearing an empty favorites."

def test_get_favorites_empty(favorite_model, caplog):
    """Test that get_favorites returns an empty list when there are no favorites and logs a warning.

    """
    with caplog.at_level("WARNING"):
        favorites = favorite_model.get_favorites()

    assert favorites == [], "Expected get_favorites to return an empty list when there are no favorites."

    assert "Retrieved 0 favorite locations." in caplog.text, "Expected a warning when getting favorites from an empty favorites."

def test_get_favorites_with_data(app, favorite_model, sample_locations):
    """Test that get_favorites returns the correct list when there are favorites.

    # Note that app is a fixture defined in the conftest.py file

    """
    favorite_model.favorites.extend([favorite.id for favorite in sample_locations])

    favorites = favorite_model.get_favorites()
    assert favorites == sample_locations, "Expected get_favorites to return the correct favorites list."

def test_get_favorites_uses_cache(favorite_model, sample_location1, mocker):
    favorite_model.favorites.append(sample_location1.id)

    favorite_model._location_cache[sample_location1.id] = sample_location1
    favorite_model._ttl[sample_location1.id] = time.time() + 100  # still valid

    mock_get_by_id = mocker.patch("weather.models.favorites_model.Locations.get_location_by_id")

    favorites = favorite_model.get_favorites()

    assert favorites[0] == sample_location1
    mock_get_by_id.assert_not_called()

def test_get_favorites_refreshes_on_expired_ttl(favorite_model, sample_location1, mocker):
    favorite_model.favorites.append(sample_location1.id)

    stale_favorite = mocker.Mock()
    favorite_model._location_cache[sample_location1.id] = stale_favorite
    favorite_model._ttl[sample_location1.id] = time.time() - 1  # TTL expired

    mock_get_by_id = mocker.patch("weather.models.favorites_model.Locations.get_location_by_id", return_value=sample_location1)

    favorites = favorite_model.get_favorites()

    assert favorites[0] == sample_location1
    mock_get_by_id.assert_called_once_with(sample_location1.id)
    assert favorite_model._location_cache[sample_location1.id] == sample_location1

def test_cache_populated_on_get_locations(favorite_model, sample_location1, mocker):
    mock_get_by_id = mocker.patch("weather.models.favorites_model.Locations.get_location_by_id", return_value=sample_location1)

    favorite_model.favorites.append(sample_location1.id)

    favorites = favorite_model.get_favorites()

    assert sample_location1.id in favorite_model._location_cache
    assert sample_location1.id in favorite_model._ttl
    assert favorites[0] == sample_location1
    mock_get_by_id.assert_called_once_with(sample_location1.id)

def test_add_favorite(favorite_model, sample_locations, app):
    """Test that a location is correctly added to the favorites.

    """
    favorite_model.add_favorite(sample_locations[0].id)

    assert len(favorite_model.favorites) == 1, "Favorites should contain one location after calling add_location."
    assert favorite_model.favorites[0] == 1, "Expected 'Miami' (id 1) in the favorites."

    favorite_model.add_favorite(sample_locations[1].id)

    assert len(favorite_model.favorites) == 2, "Favorites should contain two locations after calling add_location."
    assert favorite_model.favorites[1] == 2, "Expected 'Brussels' (id 2) in the favorites."

def test_remove_favorite(favorite_model, sample_location1):
    """Test that a location is successfully removed from favorites list.
    """
    favorite_model.favorites.append(sample_location1.id)
    
    favorite_model.remove_favorite(sample_location1.id)
    
    assert sample_location1.id not in favorite_model.favorites, "Location should be removed from favorites."

def test_remove_favorite_cleans_cache(favorite_model, sample_location1):
    """Test that removing a favorite location also removes it from cache.
    """
    favorite_model.favorites.append(sample_location1.id)
    favorite_model._location_cache[sample_location1.id] = sample_location1
    favorite_model._ttl[sample_location1.id] = time.time() + 100  # Add to TTL cache
    
    favorite_model.remove_favorite(sample_location1.id)
    
    assert sample_location1.id not in favorite_model.favorites, "Location should be removed from favorites."
    assert sample_location1.id not in favorite_model._location_cache, "Location should be removed from cache."
    assert sample_location1.id not in favorite_model._ttl, "Location should be removed from TTL cache."

def test_remove_favorite_nonexistent(favorite_model, caplog):
    """Test that trying to remove a non-existent location from favorites raises ValueError.
    """
    non_existent_id = 9999  # ID that doesn't exist in favorites
    
    with pytest.raises(ValueError, match=f"Location with id {non_existent_id} is not in favorites"):
        favorite_model.remove_favorite(non_existent_id)

def test_get_weather_recent_cache(favorite_model, sample_location1, mocker):
    """Test retrieving weather data from cache for location with recent timestamp.
    """
    location_name = sample_location1.name
    sample_weather_data = {"temp": 25, "humidity": 80}
    sample_location1.weather_data = sample_weather_data
    sample_location1.last_updated = time.time() - 10  # Recent update (10 seconds ago)
    
    mock_get_location = mocker.patch("weather.models.favorites_model.Locations.get_location_by_name", 
                                     return_value=sample_location1)
    
    mock_get_weather = mocker.patch("weather.models.favorites_model.get_weather")
    
    result = favorite_model.get_weather_for_location(location_name)
    
    assert result == sample_weather_data
    mock_get_location.assert_called_once_with(location_name)
    mock_get_weather.assert_not_called()

def test_get_weather_api_call_update(favorite_model, sample_location1, mocker):
    """Test retrieving weather via API call when cache is stale.
    """
    location_name = sample_location1.name
    old_weather = {"temp": 20, "humidity": 70}
    new_weather = {"temp": 25, "humidity": 80}
    
    sample_location1.weather_data = old_weather
    sample_location1.last_updated = time.time() - 3700  # Old update (over 1 hour ago)
    
    mock_get_location = mocker.patch("weather.models.favorites_model.Locations.get_location_by_name", 
                                     return_value=sample_location1)
    mock_get_weather = mocker.patch("weather.models.favorites_model.get_weather", 
                                    return_value=new_weather)
    mock_update = mocker.patch.object(sample_location1, "update_from_api_response")
    
    result = favorite_model.get_weather_for_location(location_name)
    
    assert result == new_weather
    mock_get_location.assert_called_once_with(location_name)
    mock_get_weather.assert_called_once_with(location_name)
    mock_update.assert_called_once_with(new_weather)

def test_get_weather_api_call_create(favorite_model, mocker):
    """Test retrieving weather via API call when location doesn't exist.
    """
    location_name = "New City"
    weather_data = {"temp": 25, "humidity": 80}
    new_location = mocker.Mock()
    
    mock_get_location = mocker.patch("weather.models.favorites_model.Locations.get_location_by_name", 
                                     side_effect=ValueError("Location not found"))
    mock_get_weather = mocker.patch("weather.models.favorites_model.get_weather", 
                                    return_value=weather_data)
    mock_create = mocker.patch("weather.models.favorites_model.Locations.create_from_api_response", 
                              return_value=new_location)
    
    result = favorite_model.get_weather_for_location(location_name)
    
    assert result == weather_data
    mock_get_location.assert_called_once_with(location_name)
    mock_get_weather.assert_called_once_with(location_name)
    mock_create.assert_called_once_with(location_name, weather_data)

def test_get_weather_api_error(favorite_model, mocker):
    """Test error handling when API call fails.
    """
    location_name = "Problem City"
    error_message = "API connection failed"
    
    mock_get_location = mocker.patch("weather.models.favorites_model.Locations.get_location_by_name", 
                                     side_effect=ValueError("Location not found"))
    mock_get_weather = mocker.patch("weather.models.favorites_model.get_weather", 
                                    side_effect=Exception(error_message))
    
    with pytest.raises(RuntimeError, match=f"Failed to get weather for {location_name}: {error_message}"):
        favorite_model.get_weather_for_location(location_name)

def test_get_all_favorites_with_weather(favorite_model, sample_locations, mocker):
    """Test retrieving weather data for all favorite locations.
    """
    favorite_model.favorites = [location.id for location in sample_locations]
    
    weather_data = [
        {"name": sample_locations[0].name, "temp": 25},
        {"name": sample_locations[1].name, "temp": 20}
    ]
    
    mock_get_weather = mocker.patch.object(favorite_model, "get_weather_for_location")
    mock_get_weather.side_effect = weather_data
    mock_get_favorites = mocker.patch.object(favorite_model, "get_favorites", return_value=sample_locations)
    
    result = favorite_model.get_all_favorites_with_weather()
    
    assert result == weather_data
    assert mock_get_favorites.call_count == 1
    assert mock_get_weather.call_count == 2
    mock_get_weather.assert_any_call(sample_locations[0].name)
    mock_get_weather.assert_any_call(sample_locations[1].name)

def test_get_all_favorites_with_weather_partial_errors(favorite_model, sample_locations, mocker, caplog):
    """Test that function continues despite weather retrieval errors for some locations.
    """
    favorite_model.favorites = [location.id for location in sample_locations]
    
    # First call succeeds, second call fails
    weather_data = {"name": sample_locations[0].name, "temp": 25}
    
    def mock_get_weather(location_name):
        if location_name == sample_locations[0].name:
            return weather_data
        else:
            raise RuntimeError(f"Failed to get weather for {location_name}")
    
    mock_get_weather_for_location = mocker.patch.object(
        favorite_model, "get_weather_for_location", side_effect=mock_get_weather
    )
    mock_get_favorites = mocker.patch.object(favorite_model, "get_favorites", return_value=sample_locations)
    
    with caplog.at_level("ERROR"):
        result = favorite_model.get_all_favorites_with_weather()
    
    assert len(result) == 1
    assert result[0] == weather_data
    assert f"Failed to get weather for {sample_locations[1].name}" in caplog.text
    assert mock_get_favorites.call_count == 1
    assert mock_get_weather_for_location.call_count == 2

def test_get_all_favorites_with_weather_empty(favorite_model, mocker):
    """Test handling of empty favorites list when getting weather for all favorites.
    """
    mock_get_favorites = mocker.patch.object(favorite_model, "get_favorites", return_value=[])
    mock_get_weather = mocker.patch.object(favorite_model, "get_weather_for_location")
    
    result = favorite_model.get_all_favorites_with_weather()
    
    assert result == []
    mock_get_favorites.assert_called_once()
    mock_get_weather.assert_not_called()

def test_clear_cache(favorite_model, sample_location1):
    favorite_model._location_cache[sample_location1.id] = sample_location1
    favorite_model._ttl[sample_location1.id] = time.time() + 100

    favorite_model.clear_cache()

    assert favorite_model._location_cache == {}
    assert favorite_model._ttl == {}

