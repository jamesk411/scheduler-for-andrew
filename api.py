from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict, Any
import uvicorn

from search import search_court_cases

app = FastAPI(
    title="Utah Court Calendar API",
    description="API for searching Utah court calendar by attorney name",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Utah Court Calendar API",
        "endpoints": {
            "/search/attorney": "Search court cases by attorney name"
        },
        "docs": "/docs"
    }


@app.get("/search/attorney", response_model=List[Dict[str, Any]])
async def search_by_attorney(
    first_name: str = Query(..., description="Attorney's first name", min_length=2),
    last_name: str = Query(..., description="Attorney's last name", min_length=2),
    date: str = Query("all", description="Date filter (all or YYYY-MM-DD)"),
    location: str = Query("all", description="Court location (all or specific court code)")
) -> List[Dict[str, Any]]:
    """
    Search for court cases by attorney name.
    
    **Parameters:**
    - **first_name**: Attorney's first name (required, minimum 2 characters)
    - **last_name**: Attorney's last name (required, minimum 2 characters)
    - **date**: Date filter - "all" or specific date in YYYY-MM-DD format (optional, default: "all")
    - **location**: Location filter - "all" or specific court code (optional, default: "all")
    
    **Returns:**
    - List of court case objects with details including:
        - time, date, case_number, case_type
        - court, court_type, hearing_type, hearing_purpose
        - judge, room, attorney, plaintiff, defendant
        - webex_url (if available), detail_url
    
    **Example:**
    ```
    GET /search/attorney?first_name=CHRIS&last_name=DEXTER
    ```
    """
    try:
        cases = search_court_cases(
            search_type="a",
            first_name=first_name.upper(),
            last_name=last_name.upper(),
            date=date,
            location=location
        )
        
        return cases
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching court cases: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Utah Court Calendar API"}


if __name__ == "__main__":
    # Run the API server
    print("🚀 Starting Utah Court Calendar API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Example: http://localhost:8000/search/attorney?first_name=CHRIS&last_name=DEXTER")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
