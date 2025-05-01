import requests


def run_smoketest():
    base_url = "http://localhost:5000/api"
    username = "test"
    password = "test"

    new_york = {
        "name": "New York",
        "fahrenheit": 72.5,
        "celsius": 22.5,
        "humidity": 65.0,
        "wind_speed": 5.2,
        "weather_description": "Partly Cloudy"
    }

    los_angeles = {
        "name": "Los Angeles",
        "fahrenheit": 85.0,
        "celsius": 29.4,
        "humidity": 45.0,
        "wind_speed": 3.5,
        "weather_description": "Sunny"
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"
    print("Health check successful")

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    delete_locations_response = requests.delete(f"{base_url}/reset-locations")
    assert delete_locations_response.status_code == 200
    assert delete_locations_response.json()["status"] == "success"
    print("Reset locations successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")

    # Add first location
    create_location_resp = session.post(f"{base_url}/add-location", json=new_york)
    assert create_location_resp.status_code == 201
    assert create_location_resp.json()["status"] == "success"
    print("Location creation successful for New York")

    # Get location by ID
    get_location_resp = session.get(f"{base_url}/get-location-by-id/1")
    assert get_location_resp.status_code == 200
    assert get_location_resp.json()["status"] == "success"
    assert get_location_resp.json()["location"] == "New York"
    print("Get location by ID successful")

    # Get location by name
    get_location_by_name_resp = session.get(f"{base_url}/get-location-by-name/New York")
    assert get_location_by_name_resp.status_code == 200
    assert get_location_by_name_resp.json()["status"] == "success"
    assert get_location_by_name_resp.json()["location"] == "New York"
    print("Get location by name successful")

    # Add location to favorites
    add_favorite_resp = session.post(f"{base_url}/add-favorite", json={
        "name": 'New York'
    })
    assert add_favorite_resp.status_code == 200
    assert add_favorite_resp.json()["status"] == "success"
    print("Add favorite successful")

    # Get favorites
    get_favorites_resp = session.get(f"{base_url}/get-favorites")
    assert get_favorites_resp.status_code == 200
    assert get_favorites_resp.json()["status"] == "success"
    assert get_favorites_resp.json()["favorites"] == 1
    print("Get favorites successful")

    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Login with new password
    session = requests.Session()  # Create a new session
    login_with_new_pwd_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_with_new_pwd_resp.status_code == 200
    assert login_with_new_pwd_resp.json()["status"] == "success"
    print("Login with new password successful")

    # Add second location
    create_second_location_resp = session.post(f"{base_url}/add-location", json=los_angeles)
    assert create_second_location_resp.status_code == 201
    assert create_second_location_resp.json()["status"] == "success"
    print("Location creation successful for Los Angeles")

    # Add second location to favorites
    add_second_favorite_resp = session.post(f"{base_url}/add-favorite", json={
        "name": "Los Angeles"
    })
    assert add_second_favorite_resp.status_code == 200
    assert add_second_favorite_resp.json()["status"] == "success"
    print("Add second favorite successful")

    # Get favorites again to verify both locations are there
    get_favorites_again_resp = session.get(f"{base_url}/get-favorites")
    assert get_favorites_again_resp.status_code == 200
    assert get_favorites_again_resp.json()["status"] == "success"
    assert get_favorites_again_resp.json()["favorites"] == 2
    print("Get updated favorites successful")

    # Clear favorites
    clear_favorites_resp = session.post(f"{base_url}/clear-favorites")
    assert clear_favorites_resp.status_code == 200
    assert clear_favorites_resp.json()["status"] == "success"
    print("Clear favorites successful")

    # Verify favorites are cleared
    get_empty_favorites_resp = session.get(f"{base_url}/get-favorites")
    assert get_empty_favorites_resp.status_code == 200
    assert get_empty_favorites_resp.json()["status"] == "success"
    assert get_empty_favorites_resp.json()["favorites"] == 0
    print("Verified favorites were cleared")

    # Delete location
    delete_location_resp = session.delete(f"{base_url}/delete-location/1")
    assert delete_location_resp.status_code == 200
    assert delete_location_resp.json()["status"] == "success"
    print("Delete location successful")

    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    # Try to add location while logged out (should fail)
    create_location_logged_out_resp = session.post(f"{base_url}/add-location", json=new_york)
    assert create_location_logged_out_resp.status_code == 401
    assert create_location_logged_out_resp.json()["status"] == "error"
    print("Location creation failed as expected when logged out")


if __name__ == "__main__":
    run_smoketest()
