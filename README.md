# SWIFT Codes API

This is a RESTful API for managing SWIFT/BIC codes. It allows for retrieving, adding, and deleting SWIFT codes, with special handling for bank headquarters and branches.

## Project Structure

```
remitly-swift-api/
├── main.py                # FastAPI application entry point
├── db.py                  # Database connection setup
├── models/                # SQLAlchemy ORM models
│   └── swift_code.py      # SWIFT code data model
├── schemas/               # Pydantic schemas for validation
│   └── swift_code.py      # SWIFT code schemas
├── load_excel.py          # Script to import Excel data
├── routers/               # API route handlers
│   └── swift_codes.py     # SWIFT code endpoints
├── tests/                 # Unit and integration tests
    └── conftest.py        # Modifies import search path.
│   └── test_endpoints.py  # API endpoint tests
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Docker Compose configuration
```

## Features

- Parse SWIFT codes from Excel file, identifying headquarters vs. branches
- Store data in SQLite database (can be replaced with any SQL database)
- RESTful API with endpoints for:
  - Retrieving single SWIFT code details
  - Retrieving all SWIFT codes for a country
  - Adding new SWIFT codes
  - Deleting SWIFT codes
- Automatic association of branches with headquarters
- Containerized application with Docker

## Prerequisites

- Docker and Docker Compose
- Python 3.9+

## Setup and Running

### Using Docker (Recommended)

1. Clone the repository
   ```bash
   git clone https://github.com/SHIMHOUND/remitly-swift-api.git
   cd remitly-swift-api
   ```

2. Place your SWIFT codes Excel file in the project root directory and name it `Interns_2025_SWIFT_CODES.xlsx`

3. Build and start the containers
   ```bash
   docker-compose up --build
   ```

4. The API will be available at http://localhost:8080
   - API documentation: http://localhost:8080/docs

### Manual Setup

1. Clone the repository
   ```bash
   git clone https://github.com/SHIMHOUND/remitly-swift-api.git
   cd remitly-swift-api
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Place your SWIFT codes Excel file in the project root directory and name it `Interns_2025_SWIFT_CODES.xlsx`

5. Load data from Excel to the database
   ```bash
   python load_excel.py
   ```

6. Start the API server
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

7. The API will be available at http://localhost:8080
   - API documentation: http://localhost:8080/docs

## API Endpoints

### Get SWIFT Code Details

```
GET /v1/swift-codes/{swift-code}
```

```
curl http://localhost:8080/v1/swift-codes/{swift-code} | jq 

```


Returns details of a specific SWIFT code. If the code is for a headquarters, it includes a list of all branches.

### Get Country SWIFT Codes(Win, (macOS/Linux/Git Bash/WSL))

```
GET /v1/swift-codes/country/{countryISO2code}
```

```
curl http://localhost:8080/v1/swift-codes/country/{countryISO2code} | jq
```

Returns all SWIFT codes for a specific country (using ISO-2 country code).

### Add New SWIFT Code

```
POST /v1/swift-codes
```

```
curl -X POST http://localhost:8080/v1/swift-codes \
-H "Content-Type: application/json" \
-d '{"swift_code": "NEWCODE", "bank_name": "New Bank", "country": "US", "headquarters": true}'

```

Adds a new SWIFT code to the database. Automatically associates branches with headquarters.

### Delete SWIFT Code

```
DELETE /v1/swift-codes/{swift-code}
```

```
curl -X DELETE http://localhost:8080/v1/swift-codes/{swift-code}
```



Deletes a SWIFT code from the database.

## Testing

Run the tests with pytest or docker:

```bash
pytest
```

or

```bash
docker compose run test
```


## Design Decisions

1. **SQLite Database**: For simplicity, this project uses SQLite. In a production environment, you might want to switch to PostgreSQL or another RDBMS.

2. **Data Model**: SWIFT codes are modeled with a self-referential relationship to represent headquarters-branch relationships.

3. **Containerization**: Docker and Docker Compose are used for easy setup and deployment.

4. **Code Organization**: Following best practices, the project is organized into separate modules for models, schemas, and routers.

5. **Error Handling**: Comprehensive error handling is implemented for all API endpoints.

©️ The project was made by Daler Khisamutdinov on macOS Sequoia 15.1.1

Contact me by email: khisamutdinovdaler@gmail.com