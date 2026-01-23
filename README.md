# ReservationAPI

A meeting room reservation API built with FastAPI, SQLAlchemy, and SQLite. This API provides endpoints for managing meeting rooms and reservations with comprehensive business rule validation.

## Features

- **Room Management**: Create and list meeting rooms
- **Reservation Management**: Create, list, and cancel reservations
- **Business Rules Validation**:
  - No duplicate/overlapping reservations
  - Reservation time cannot be in the past
  - Reservation start time must be before end time
  - Minimum reservation duration: 1 hour
  - Reservations must start on the hour (e.g., 10:00, 14:00)
- **Finnish Timezone**: All time operations use Europe/Helsinki timezone
- **Comprehensive Testing**: Full test coverage with pytest
- **SQLite Database**: Lightweight database with SQLAlchemy ORM

## Requirements

- Python 3.14
- uv (Python package manager)

## Project Structure

```
ReservationAPI/
├── api/
│   ├── __init__.py          # API router aggregation
│   └── routes/
│       ├── reservations.py  # Reservation endpoints
│       └── rooms.py         # Room endpoints
├── tests/
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_main.py         # Main app tests
│   ├── test_reservations.py # Reservation endpoint tests
│   └── test_rooms.py        # Room endpoint tests
├── database.py              # SQLAlchemy models and DB config
├── main.py                  # FastAPI application entry point
├── models.py                # Pydantic models for validation
├── schema.sql               # Database schema and initial data
├── pyproject.toml           # Project dependencies and config
└── README.md                # This file
```

## Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd ReservationAPI
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies from pyproject.toml
   - Install development dependencies (pytest, pytest-cov, httpx)

## Running the Application

### Start the Development Server

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Root & Health

- `GET /` - API information
- `GET /health` - Health check

### Rooms

- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create a new room
- `GET /api/rooms/{room_id}` - Get room details

### Reservations

- `GET /api/reservations/` - List all reservations
- `POST /api/reservations/` - Create a new reservation
- `GET /api/reservations/room/{room_id}` - List reservations for a specific room
- `DELETE /api/reservations/{reservation_id}` - Cancel a reservation

## Usage Examples

### Create a Room

```bash
curl -X POST "http://localhost:8000/api/rooms/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conference Room D",
    "capacity": 15,
    "location": "Floor 4"
  }'
```

### List All Rooms

```bash
curl "http://localhost:8000/api/rooms/"
```

### Create a Reservation

```bash
curl -X POST "http://localhost:8000/api/reservations/" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "start_time": "2026-01-23T10:00:00+02:00",
    "end_time": "2026-01-23T11:00:00+02:00",
    "created_by": "John Doe"
  }'
```

### List Reservations for a Room

```bash
curl "http://localhost:8000/api/reservations/room/1"
```

### Cancel a Reservation

```bash
curl -X DELETE "http://localhost:8000/api/reservations/1"
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Tests with Coverage

```bash
uv run pytest --cov=. --cov-report=html --cov-report=term-missing
```

This will:
- Run all tests in the `tests/` directory
- Generate a coverage report in HTML format (in `htmlcov/`)
- Display coverage summary in the terminal

### Run Specific Test Files

```bash
uv run pytest tests/test_reservations.py
uv run pytest tests/test_rooms.py
```

### View Coverage Report

After running tests with coverage, open the HTML report:

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## Database

The application uses SQLite with the following tables:

### Rooms Table

| Column     | Type      | Description                    |
|------------|-----------|--------------------------------|
| id         | INTEGER   | Primary key                    |
| name       | TEXT      | Unique room name               |
| capacity   | INTEGER   | Maximum occupancy              |
| location   | TEXT      | Room location (optional)       |
| created_at | TIMESTAMP | Creation timestamp             |

### Reservations Table

| Column      | Type      | Description                    |
|-------------|-----------|--------------------------------|
| id          | INTEGER   | Primary key                    |
| room_id     | INTEGER   | Foreign key to rooms           |
| title       | TEXT      | Reservation title              |
| description | TEXT      | Optional description           |
| start_time  | TIMESTAMP | Start time (on the hour)       |
| end_time    | TIMESTAMP | End time (on the hour)         |
| created_by  | TEXT      | Creator name                   |
| created_at  | TIMESTAMP | Creation timestamp             |

### Initial Data

The `schema.sql` file automatically populates the database with 3 sample rooms:

1. Conference Room A (10 people, Floor 1, Wing A)
2. Meeting Room B (6 people, Floor 2, Wing B)
3. Board Room (20 people, Floor 3, Executive Suite)

## Business Rules

### 1. No Duplicate Reservations
- The system prevents overlapping reservations for the same room
- Returns 409 Conflict if a time slot is already reserved

### 2. Reservation Time Cannot Be in the Past
- Start time must be in the future
- Returns 400 Bad Request for past times

### 3. Start Time Must Be Before End Time
- Validates that the reservation makes logical sense
- Returns 400 Bad Request if violated

### Additional Rules

- **Minimum Duration**: Reservations must be at least 1 hour long
- **On the Hour**: Start and end times must be on the hour (minute=0, second=0)
- **Room Existence**: Room must exist before creating a reservation

## Development

### Project Dependencies

Main dependencies:
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation
- **pytz**: Timezone support

Development dependencies:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for testing

### Code Structure

- **models.py**: Pydantic models for request/response validation
- **database.py**: SQLAlchemy models and database configuration
- **api/routes/**: Route handlers for different resource types
- **main.py**: Application initialization and lifecycle management

### Documentation

All code includes comprehensive docstrings:
- Module-level documentation at the top of each file
- Class documentation for each model and database table
- Function documentation for all endpoints and utilities

## License

This project is created as a demonstration API for meeting room reservations.

## Contributing

1. Ensure all tests pass before submitting changes
2. Maintain test coverage above 90%
3. Follow existing code style and documentation patterns
4. Add tests for new features

## Support

For issues or questions, please refer to the API documentation at `/docs` when the server is running.
