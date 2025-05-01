
# Weather API Documentation

  

## Overview

This application allows users to get weather data for any location by its name (e.g., Miami, Brussels). It also enables users to store favorite locations for easier weather retrieval later on.

  

## Authentication

Many routes in this API require authentication. After creating an account and logging in, subsequent requests will maintain your session.

  

## API Endpoints

  

### Health Check

  

#### Route: `/api/health`

-  **Request Type**: GET

-  **Purpose**: Check if the service is running properly.

-  **Authentication**: None

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Service is running" }`

  

---

  

### User Management

  

#### Route: `/api/create-user`

-  **Request Type**: PUT

-  **Purpose**: Creates a new user account.

-  **Authentication**: None

-  **Request Body**:

-  `username` (String): User's chosen username.

-  `password` (String): User's chosen password.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `201`

- Content: `{ "status": "success", "message": "User '{username}' created successfully" }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "Username and password are required" }`

  

**Example Request:**

```json

{

"username": "weatheruser",

"password": "securepassword123"

}

```

  

#### Route: `/api/login`

-  **Request Type**: POST

-  **Purpose**: Authenticates a user and creates a session.

-  **Authentication**: None

-  **Request Body**:

-  `username` (String): User's username.

-  `password` (String): User's password.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "User '{username}' logged in successfully" }`

-  **Error Response**:

- Code: `401`

- Content: `{ "status": "error", "message": "Invalid username or password" }`

  

**Example Request:**

```json

{

"username": "weatheruser",

"password": "securepassword123"

}

```

  

#### Route: `/api/logout`

-  **Request Type**: POST

-  **Purpose**: Logs out the current user and ends their session.

-  **Authentication**: Required

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "User logged out successfully" }`

  

#### Route: `/api/change-password`

-  **Request Type**: POST

-  **Purpose**: Changes the password for the current authenticated user.

-  **Authentication**: Required

-  **Request Body**:

-  `new_password` (String): User's new password.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Password changed successfully" }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "New password is required" }`

  

**Example Request:**

```json

{

"new_password": "newSecurePassword456"

}

```

  

#### Route: `/api/reset-users`

-  **Request Type**: DELETE

-  **Purpose**: Resets the users table (administrative function).

-  **Authentication**: None (but should be restricted in production)

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Users table recreated successfully" }`

  

---

  

### Locations Management

  

#### Route: `/api/reset-locations`

-  **Request Type**: DELETE

-  **Purpose**: Resets the locations table (administrative function).

-  **Authentication**: None (but should be restricted in production)

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Locations table recreated successfully" }`

  

#### Route: `/api/add-location`

-  **Request Type**: POST

-  **Purpose**: Adds a new location with weather data to the database.

-  **Authentication**: Required

-  **Request Body**:

-  `name` (String): The location's name.

-  `fahrenheit` (Number): The temperature in Fahrenheit.

-  `celsius` (Number): The temperature in Celsius.

-  `humidity` (Number): The humidity percentage.

-  `wind_speed` (Number): The wind speed.

-  `weather_description` (String): Description of the weather.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `201`

- Content: `{ "status": "success", "message": "Location '{name}' added successfully" }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "Missing required fields: {fields}" }`

  

**Example Request:**

```json

{

"name": "Miami",

"fahrenheit": 82.4,

"celsius": 28.0,

"humidity": 65,

"wind_speed": 8.5,

"weather_description": "Partly cloudy"

}

```

  

#### Route: `/api/delete-location/<int:location_id>`

-  **Request Type**: DELETE

-  **Purpose**: Deletes a location by its ID.

-  **Authentication**: Required

-  **URL Parameter**:

-  `location_id` (Integer): The ID of the location to delete.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Location with ID {location_id} deleted successfully" }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "Location with ID {location_id} not found" }`

  

#### Route: `/api/get-location-by-id/<int:location_id>`

-  **Request Type**: GET

-  **Purpose**: Retrieves a location's details by its ID.

-  **Authentication**: Required

-  **URL Parameter**:

-  `location_id` (Integer): The ID of the location to retrieve.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "location": {...} }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "Location with ID {location_id} not found" }`

  

#### Route: `/api/get-location-by-name/<string:location_name>`

-  **Request Type**: GET

-  **Purpose**: Retrieves a location's details by its name.

-  **Authentication**: Required

-  **URL Parameter**:

-  `location_name` (String): The name of the location to retrieve.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "location": {...} }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "Location '{location_name}' not found" }`

  

---

  

### Favorites Management

  

#### Route: `/api/clear-favorites`

-  **Request Type**: POST

-  **Purpose**: Clears all locations from the user's favorites list.

-  **Authentication**: Required

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Locations have been cleared from favorites." }`

  

#### Route: `/api/add-favorite`

-  **Request Type**: POST

-  **Purpose**: Adds a location to the user's favorites list.

-  **Authentication**: Required

-  **Request Body**:

-  `name` (String): The name of the location to add to favorites.

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "message": "Location '{location_name}' is now in favorites.", "favorites": [...] }`

-  **Error Response**:

- Code: `400`

- Content: `{ "status": "error", "message": "You must name a location" }`

  

**Example Request:**

```json

{

"name": "Miami"

}

```

  

#### Route: `/api/get-favorites`

-  **Request Type**: GET

-  **Purpose**: Retrieves the list of the user's favorite locations.

-  **Authentication**: Required

-  **Response Format**: JSON

-  **Success Response**:

- Code: `200`

- Content: `{ "status": "success", "favorites": [...] }`

  

## Error Handling

  

All API endpoints return appropriate HTTP status codes:

  

-  `200`: Success

-  `201`: Resource created successfully

-  `400`: Bad request (client error)

-  `401`: Unauthorized (authentication required)

-  `500`: Internal server error

  

Error responses include a descriptive message to help troubleshoot the issue.
