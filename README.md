# Utah Court Calendar System

A complete system for searching Utah court calendar by attorney name, including a web frontend, REST API, and Python module.

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Option 1: Web Frontend (Streamlit)

The easiest way to search for cases with a visual interface:

```bash
streamlit run app.py
```

Then open your browser to **http://localhost:8501**

### Option 2: REST API (FastAPI)

For programmatic access or integration with other systems:

```bash
python api.py
```

The API will be available at **http://localhost:8000**

### Option 3: Python Module

Use directly in your Python code:

```python
from search import search_court_cases

cases = search_court_cases(
    search_type="a",
    first_name="CHRIS",
    last_name="DEXTER"
)
```

---

## 🖥️ Web Frontend Features

The Streamlit web app (`app.py`) provides:

- 🔍 **Simple Search Interface** - Enter attorney name and search
- 📊 **Summary Metrics** - Total cases, virtual hearings, court types
- 📋 **Detailed Case Cards** - All case information in organized expandable cards
- 🎥 **WebEx Links** - Direct links to join virtual hearings
- 📥 **Export to CSV** - Download all results for further analysis
- 📅 **Date Filtering** - Search all dates or specific dates
- 📍 **Location Filtering** - Filter by court location

---

## 🔌 REST API Documentation

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
