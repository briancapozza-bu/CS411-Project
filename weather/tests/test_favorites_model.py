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

def test_clear_cache(favorite_model, sample_location1):
    favorite_model._location_cache[sample_location1.id] = sample_location1
    favorite_model._ttl[sample_location1.id] = time.time() + 100

    favorite_model.clear_cache()

    assert favorite_model._location_cache == {}
    assert favorite_model._ttl == {}

