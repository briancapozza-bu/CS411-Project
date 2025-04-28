import pytest
import requests

from weather.utils.api_utils import get_weather

MOCK_WEATHER_RESPONSE = {
  "coord": {
    "lon": -80.1937,
    "lat": 25.7743
  },
  "weather": [
    {
      "id": 801,
      "main": "Clouds",
      "description": "few clouds",
      "icon": "02d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 301.15,
    "feels_like": 302.94,
    "temp_min": 300.37,
    "temp_max": 302.16,
    "pressure": 1020,
    "humidity": 63,
    "sea_level": 1020,
    "grnd_level": 1019
  },
  "visibility": 10000,
  "wind": {
    "speed": 6.17,
    "deg": 90,
    "gust": 10.29
  },
  "clouds": {
    "all": 20
  },
  "dt": 1745873935,
  "sys": {
    "type": 2,
    "id": 2009435,
    "country": "US",
    "sunrise": 1745837161,
    "sunset": 1745884210
  },
  "timezone": -14400,
  "id": 4164138,
  "name": "Miami",
  "cod": 200
}

MOCK_WEATHER = {
    'Location': 'Miami',
    'Fahrenheit': 82.4,
    'Celsius': 28.0,
    'Humidity': 63,
    'Wind Speed': 6.17
}   
                   
                 

@pytest.fixture
def mock_weather(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a json attribute
    mock_response.json.return_value = MOCK_WEATHER_RESPONSE
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

# ================================================================================
#
# WEATHER
#
# ================================================================================

def test_get_weather(mock_weather):
    """Test retrieving weather from openweathermap.org.

    """
    result = get_weather('Miami')

    # Assert that the result is the mocked weather
    assert result == MOCK_WEATHER, f"Expected weather {MOCK_WEATHER}, but got {result}"

def test_get_weather_request_failure(mocker):
    """Test handling of a request failure when calling openweathermap.org.

    """
    # Simulate a request failure
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to openweathermap.org failed: Connection error"):
        get_weather('Miami')

def test_get_weather_timeout(mocker):
    """Test handling of a timeout when calling openweathermap.org.

    """
    # Simulate a timeout
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to openweathermap.org timed out."):
        get_weather('Miami')

def test_get_weather_invalid_response(mock_weather):
    """Test handling of an invalid response from openweathermap.org.

    """
    # Simulate an invalid response (non-dict)
    mock_weather.json.return_value = "invalid_response"

    with pytest.raises(ValueError, match="Invalid response from openweathermap.org: invalid_response"):
        get_weather('Miami')
