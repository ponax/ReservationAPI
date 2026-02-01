# ReservationAPI

A meeting room reservation API built with FastAPI, SQLModel, and SQLite. This API provides endpoints for managing meeting rooms and reservations with comprehensive business rule validation.

## Features

- **Room Management**: Create, read, update and delete meeting rooms
- **Reservation Management**: Create, read, update and delete reservations
- **Overlap Detection**: Prevents conflicting reservations for the same room
- **Business Rules Validation**:
  - No duplicate/overlapping reservations (same room, same time)
  - Reservation time cannot be in the past
  - End time must be after start time
  - Minimum reservation duration: 1 hour
  - Reservations must start on the hour (e.g., 10:00, 14:00)
  - Reservations must end on the hour
- **Comprehensive Testing**: Full test coverage with pytest
- **SQLite Database**: Lightweight database with SQLModel ORM

## Requirements

- Python 3.14
- uv (Python package manager)

## Project Structure

```
ReservationAPI/
├── api/
│   ├── __init__.py          # API package initialization
│   ├── main.py              # API router aggregation
│   ├── deps.py              # Dependency injection (SessionDep)
│   └── routes/
│       ├── __init__.py
│       ├── reservations.py  # Reservation endpoints
│       ├── rooms.py         # Room endpoints
│       └── utils.py         # Utility endpoints (health check)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_main.py         # Main app tests
│   ├── test_reservations.py # Reservation endpoint tests (includes overlap tests)
│   ├── test_rooms.py        # Room endpoint tests
│   └── test_utils.py        # Utility endpoint tests
├── crud.py                  # CRUD operations for Room and Reservation
├── database.py              # Database configuration and initialization
├── main.py                  # FastAPI application entry point
├── models.py                # SQLModel table and schema models
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
uv run fastapi dev
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Root & Health

- `GET /` - API information
- `GET /api/utils/health` - Health check

### Rooms

- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Create a new room
- `GET /api/rooms/{room_id}` - Get room details
- `PUT /api/rooms/{room_id}` - Update room details (partial update)
- `DELETE /api/rooms/{room_id}` - Delete a room (fails if it has reservations)
- `GET /api/reservations/room/{room_id}` - List all reservations for a specific room

### Reservations

- `GET /api/reservations` - List all reservations
- `POST /api/reservations` - Create a new reservation (checks for overlaps)
- `GET /api/reservations/{reservation_id}` - Get reservation details
- `PUT /api/reservations/{reservation_id}` - Update reservation details (partial update)
- `DELETE /api/reservations/{reservation_id}` - Delete a reservation

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
curl -X POST "http://localhost:8000/api/reservations" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "start_time": "2026-02-03T10:00:00",
    "end_time": "2026-02-03T11:00:00",
    "created_by": "John Doe"
  }'
```

### Update a Reservation (Partial Update)

```bash
curl -X PATCH "http://localhost:8000/api/reservations/{reservation_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Meeting Title",
    "description": "Updated description"
  }'
```

### List Reservations for a Room

```bash
curl "http://localhost:8000/api/reservations/room/{room_id}"
```

### Delete a Reservation

```bash
curl -X DELETE "http://localhost:8000/api/reservations/{reservation_id}"
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

The application uses **SQLite** with **SQLModel** (a combination of SQLAlchemy and Pydantic) for ORM and data validation.

### Rooms Table

| Column     | Type      | Description                    |
|------------|-----------|--------------------------------|
| id         | INTEGER   | Primary key (auto-increment)   |
| name       | TEXT      | Unique room name               |
| capacity   | INTEGER   | Maximum occupancy (must be > 0)|
| location   | TEXT      | Room location (optional)       |
| created_at | DATETIME  | Creation timestamp (UTC)       |

### Reservations Table

| Column      | Type      | Description                    |
|-------------|-----------|--------------------------------|
| id          | INTEGER   | Primary key (auto-increment)   |
| room_id     | INTEGER   | Foreign key to rooms (CASCADE) |
| title       | TEXT      | Reservation title              |
| description | TEXT      | Optional description           |
| start_time  | DATETIME  | Start time (must be on hour)   |
| end_time    | DATETIME  | End time (must be on hour)     |
| created_by  | TEXT      | Creator name/identifier        |
| created_at  | DATETIME  | Creation timestamp (UTC)       |

### Database Initialization

The database is automatically initialized on first run by `database.py`:
- Creates all tables using SQLModel metadata
- Populates 3 sample rooms if the database is empty

**Initial Sample Rooms:**
1. Conference Room A (10 people, Floor 1, Wing A)
2. Meeting Room B (6 people, Floor 2, Wing B)
3. Board Room (20 people, Floor 3, Executive Suite)

## Business Rules

### 1. No Overlapping Reservations
- The system prevents overlapping reservations for the same room
- Uses time range comparison: checks if `start_time < existing_end_time AND end_time > existing_start_time`
- Returns **400 Bad Request** with a descriptive error if a conflict is found
- Different rooms can have reservations at the same time

### 2. Reservation Time Validation
- **Cannot Be in the Past**: Start time must be in the future (UTC comparison)
- **End After Start**: End time must be after start time
- **On the Hour**: Both start and end times must have minute=0, second=0, microsecond=0
- **Minimum Duration**: Reservations must be at least 1 hour long
- Returns **422 Unprocessable Entity** for validation errors

### 3. Room Validation
- Room must exist before creating a reservation (returns **404 Not Found**)
- Room capacity must be greater than 0
- Room names must be unique
- Rooms with active reservations cannot be deleted (returns **400 Bad Request**)

### 4. Data Integrity
- Foreign key relationships enforced with CASCADE delete on Room → Reservations
- Timezone-naive datetimes stored in UTC for SQLite compatibility
- All datetime fields accept both timezone-aware and naive datetimes (converted to naive UTC)

## Development

### Project Dependencies

Main dependencies:
- **FastAPI**: Modern web framework for building APIs
- **SQLModel**: SQL database ORM combining SQLAlchemy and Pydantic
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and settings management

Development dependencies:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **httpx**: Async HTTP client for testing FastAPI

### Code Structure

- **models.py**: SQLModel table models (Room, Reservation) and Pydantic schemas (Create, Update, Response)
- **crud.py**: CRUD operations (Create, Read, Update, Delete) for database entities
- **database.py**: Database engine configuration, session management, and initialization
- **api/deps.py**: FastAPI dependency injection (SessionDep for database sessions)
- **api/routes/**: Route handlers organized by resource type (rooms, reservations, utils)
- **api/main.py**: API router aggregation
- **main.py**: Application initialization, lifecycle management, and router inclusion

### Key Design Patterns

- **Dependency Injection**: Database sessions injected via `SessionDep` type alias
- **Repository Pattern**: CRUD operations separated from route handlers
- **Schema Separation**: Separate models for database tables, create requests, update requests, and responses
- **Validation at Model Level**: Pydantic validators ensure data integrity before database operations

### Documentation

All code includes comprehensive docstrings following Google style:
- Module-level documentation at the top of each file
- Class documentation for each model and database table  
- Function documentation with Args, Returns, and Raises sections for all endpoints and utilities
- Type hints throughout the codebase for better IDE support

### Testing Strategy

- **Fixtures**: Reusable test fixtures in `conftest.py` for database, client, rooms, and reservations
- **Isolation**: Each test uses a fresh in-memory SQLite database
- **Comprehensive Coverage**: Tests for success cases, error cases, edge cases, and business rule validation
- **Overlap Testing**: Dedicated tests for all overlap scenarios (exact, partial start, partial end, encompassing, different rooms)

## Error Handling

The API uses standard HTTP status codes:

- **200 OK**: Successful GET, PUT, DELETE operations
- **201 Created**: Successful POST operations
- **400 Bad Request**: Business rule violations (overlaps, invalid state)
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors (invalid data format or constraints)

## License

This project is created as a demonstration API for meeting room reservations.


## Troubleshooting

### Database Issues
- Delete `reservations.db` to start fresh
- The database is automatically recreated on next run with sample data

### Test Failures
- Tests use in-memory SQLite databases (isolated per test)
- Check that datetime values are timezone-naive or properly converted
- Ensure fixtures are properly set up in `conftest.py`

## Support

For issues or questions, please refer to the API documentation at `/docs` when the server is running.
