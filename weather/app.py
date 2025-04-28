from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from flask_cors import CORS

from config import ProductionConfig

from weather.db import db
from weather.models.favorites_model import FavoritesModel
from weather.models.locations_model import Locations
from weather.utils.logger import configure_logger


load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)


    favorites_model = FavoritesModel()


    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)


    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    ##########################################################
    #
    # Locations
    #
    ##########################################################

    @app.route('/api/reset-locations', methods=['DELETE'])
    def reset_locations() -> Response:
        """Recreate the locations table to delete locations.

        Returns:
            JSON response indicating the success of recreating the Locations table.

        Raises:
            500 error if there is an issue recreating the Locations table.
        """
        try:
            app.logger.info("Received request to recreate Locations table")
            with app.app_context():
                Locations.__table__.drop(db.engine)
                Locations.__table__.create(db.engine)
            app.logger.info("Locations table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Locations table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Locations table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)


    @app.route('/api/add-location', methods=['POST'])
    @login_required
    def add_location() -> Response:
        """Route to add a new favorite.

        Expected JSON Input:
            - name (str): The locations's name.
            - fahrenheit (float): The location's temperature in fahrenheit.
            - celsius (float): The location's temperature in celsius.
            - humidity (int): The location's humidity.
            - wind_speed (float): The location's wind_speed.
            - weather_description (str): A description of the location's weather.

        Returns:
            JSON response indicating the success of the location addition.

        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the location to the database.

        """
        app.logger.info("Received request to create new location")

        try:
            data = request.get_json()

            required_fields = ["name", "fahrenheit", "celsius", "humidity", "wind_speed", "weather_description"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            name = data["name"]
            fahrenheit = data["fahrenheit"]
            celsius = data["celsius"]
            humidity = data["humidity"]
            wind_speed = data["wind_speed"]
            weather_description = data["weather_description"]

            if (
                not isinstance(name, str)
                or not isinstance(fahrenheit, (int, float))
                or not isinstance(celsius, (int, float))
                or not isinstance(humidity, (int, float))
                or not isinstance(wind_speed, int, float)
                or not isinstance(weather_description, str)
            ):
                app.logger.warning("Invalid input data types")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: name/weather_description should be a string, fahrenheit/celsius/humidity/wind_speed should be numbers"
                }), 400)

            app.logger.info(f"Adding location: {name}, {fahrenheit}F, {celsius}C, {humidity}, {wind_speed}, {weather_description}.")
            Locations.create_boxer(name, fahrenheit, celsius, humidity, wind_speed, weather_description)

            app.logger.info(f"Location added successfully: {name}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Location '{name}' added successfully"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add location: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the location",
                "details": str(e)
            }), 500)


    @app.route('/api/delete-location/<int:location_id>', methods=['DELETE'])
    @login_required
    def delete_location(location_id: int) -> Response:
        """Route to delete a location by ID.

        Path Parameter:
            - location_id (int): The ID of the location to delete.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            400 error if the location does not exist.
            500 error if there is an issue removing the location from the database.

        """
        try:
            app.logger.info(f"Received request to delete location with ID {location_id}")

            # Check if the boxer exists before attempting to delete
            location = Locations.get_location_by_id(location_id)
            if not location:
                app.logger.warning(f"Location with ID {location_id} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location with ID {location_id} not found"
                }), 400)

            Locations.delete_location(location_id)
            app.logger.info(f"Successfully deleted location with ID {location_id}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Location with ID {location_id} deleted successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to add location: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting the location",
                "details": str(e)
            }), 500)


    @app.route('/api/get-location-by-id/<int:location_id>', methods=['GET'])
    @login_required
    def get_location_by_id(location_id: int) -> Response:
        """Route to get a location by its ID.

        Path Parameter:
            - location_id (int): The ID of the location.

        Returns:
            JSON response containing the location details if found.

        Raises:
            400 error if the location is not found.
            500 error if there is an issue retrieving the location from the database.

        """
        try:
            app.logger.info(f"Received request to retrieve location with ID {location_id}")

            location = Locations.get_location_by_id(location_id)

            if not location:
                app.logger.warning(f"Location with ID {location_id} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location with ID {location_id} not found"
                }), 400)

            app.logger.info(f"Successfully retrieved location: {location}")
            return make_response(jsonify({
                "status": "success",
                "location": location
            }), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving location with ID {location_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the location",
                "details": str(e)
            }), 500)


    @app.route('/api/get-location-by-name/<string:location_name>', methods=['GET'])
    @login_required
    def get_location_by_name(location_name: str) -> Response:
        """Route to get a location by its name.

        Path Parameter:
            - location_name (str): The name of the location.

        Returns:
            JSON response containing the location details if found.

        Raises:
            400 error if the location name is missing or not found.
            500 error if there is an issue retrieving the location from the database.

        """
        try:
            app.logger.info(f"Received request to retrieve location with name '{location_name}'")

            location = Locations.get_location_by_name(location_name)

            if not location:
                app.logger.warning(f"Location '{location_name}' not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location '{location_name}' not found"
                }), 400)

            app.logger.info(f"Successfully retrieved location: {location}")
            return make_response(jsonify({
                "status": "success",
                "location": location
            }), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving location with name '{location_name}': {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the location",
                "details": str(e)
            }), 500)


    ############################################################
    #
    # Ring
    #
    ############################################################


    @app.route('/api/fight', methods=['GET'])
    @login_required
    def bout() -> Response:
        """Route that triggers the fight between the two current boxers.

        Returns:
            JSON response indicating the winner of the fight.

        Raises:
            400 error if the fight cannot be triggered due to insufficient combatants.
            500 error if there is an issue during the fight.

        """
        try:
            app.logger.info("Initiating fight...")

            winner = ring_model.fight()

            app.logger.info(f"Fight complete. Winner: {winner}")
            return make_response(jsonify({
                "status": "success",
                "message": "Fight complete",
                "winner": winner
            }), 200)

        except ValueError as e:
            app.logger.warning(f"Fight cannot be triggered: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)

        except Exception as e:
            app.logger.error(f"Error while triggering fight: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while triggering the fight",
                "details": str(e)
            }), 500)


    @app.route('/api/clear-favorites', methods=['POST'])
    @login_required
    def clear_favorites() -> Response:
        """Route to clear the list of locations from the favorites.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            500 error if there is an issue clearing locations.

        """
        try:
            app.logger.info("Clearing all locations...")

            favorite_model.clear_favorites()

            app.logger.info("Locations cleared from favorites successfully.")
            return make_response(jsonify({
                "status": "success",
                "message": "Locations have been cleared from favorites."
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to clear favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while clearing favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/add-favorite', methods=['POST'])
    @login_required
    def add_favorite() -> Response:
        """Route to add a favorite location to the app.

        Expected JSON Input:
            - name (str): The location's name.

        Returns:
            JSON response indicating the success of adding the favorite.

        Raises:
            400 error if the request is invalid (e.g., favorite name missing).
            500 error if there is an issue with adding the favorite.

        """
        try:
            data = request.get_json()
            location_name = data.get("name")

            if not location_name:
                app.logger.warning("Attempted to add favorite without specifying a location.")
                return make_response(jsonify({
                    "status": "error",
                    "message": "You must name a location"
                }), 400)

            app.logger.info(f"Attempting to add {location_name} to favorites.")

            location = Locations.get_location_by_name(location_name)

            if not location:
                app.logger.warning(f"Location '{location_name}' not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Location '{location_name}' not found"
                }), 400)

            try:
                favorite_model.add_favorite(location)
            except ValueError as e:
                app.logger.warning(f"Cannot enter {location_name}: {e}")
                return make_response(jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400)

            favorites = favorite_model.get_favorites()

            app.logger.info(f"Location '{location_name}' added to favorites. Current favorites: {favorites}")

            return make_response(jsonify({
                "status": "success",
                "message": f"Location '{location_name}' is now in favorites.",
                "favorites": favorites
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to add location to favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding location to favorites",
                "details": str(e)
            }), 500)


    @app.route('/api/get-favorites', methods=['GET'])
    @login_required
    def get_favorites() -> Response:
        """Route to get the list of locations in favorites.

        Returns:
            JSON response with the list of favorites.

        Raises:
            500 error if there is an issue getting the favorites.

        """
        try:
            app.logger.info("Retrieving list of favorites...")

            favorites = favorite_model.get_favorites()

            app.logger.info(f"Retrieved {len(favorites)} favorite(s).")
            return make_response(jsonify({
                "status": "success",
                "favorites": favorites
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve favorites: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving favorites",
                "details": str(e)
            }), 500)
            
    return app


if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
