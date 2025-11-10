# Utah Court Calendar API

A simple API for searching Utah court calendar by attorney name.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Start the API server:

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Search by Attorney Name

**GET** `/search/attorney`

Search for court cases by attorney name.

**Query Parameters:**

- `first_name` (required) - Attorney's first name (min 2 characters)
- `last_name` (required) - Attorney's last name (min 2 characters)
- `date` (optional) - Date filter: "all" or "YYYY-MM-DD" (default: "all")
- `location` (optional) - Court location: "all" or court code (default: "all")

**Example Request:**

```bash
curl "http://localhost:8000/search/attorney?first_name=CHRIS&last_name=DEXTER"
```

**Example Response:**

```json
{
	"success": true,
	"count": 6,
	"results": [
		{
			"time": "2:00 PM",
			"date": "11/12/2025",
			"case_number": "220907725",
			"case_type": "Contract: Fraud",
			"court": "THIRD JUDICIAL DISTRICT - SALT LAKE COUNTY DI",
			"hearing_type": "Hybrid Virtual/In Person Hearing",
			"judge": "RICHARD PEHRSON",
			"room": "WEST JORDAN ROOM 24",
			"attorney": "CHRIS DEXTER",
			"plaintiff": "JASON WOODS et al.",
			"defendant": "SHANE FOREST DAVIS et al.",
			"webex_url": "https://utcourts.webex.com/...",
			"detail_url": "https://legacy.utcourts.gov/cal/details.php?..."
		}
	]
}
```

### Health Check

**GET** `/health`

Check if the API is running.

**Example:**

```bash
curl http://localhost:8000/health
```

## Interactive Documentation

Once the API is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Using as a Module

You can also import and use the search functions directly in Python:

```python
from search import search_court_cases

# Search by attorney
cases = search_court_cases(
    search_type="a",
    first_name="CHRIS",
    last_name="DEXTER",
    date="all",
    location="all"
)

print(f"Found {len(cases)} cases")
```
