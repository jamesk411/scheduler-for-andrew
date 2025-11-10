import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import quote


def search_court_cases(
    search_type: str = "a",
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    case_number: Optional[str] = None,
    party_name: Optional[str] = None,
    judge_name: Optional[str] = None,
    bar_number: Optional[str] = None,
    date: str = "all",
    location: str = "all",
    timeout: int = 30
) -> List[Dict[str, Any]]:
    """
    Search Utah court cases and return parsed results.
    
    Args:
        search_type: Type of search - "a" (attorney), "c" (case), "p" (party), "j" (judge)
        first_name: Attorney first name (for attorney search)
        last_name: Attorney/party/judge last name
        case_number: Case number (for case search)
        party_name: Party name (for party search)
        judge_name: Judge name (for judge search)
        bar_number: Bar number (for attorney search)
        date: Date filter - "all" or specific date in YYYY-MM-DD format
        location: Location filter - "all" or specific court code
        timeout: Request timeout in seconds
    
    Returns:
        List of dictionaries containing parsed case information
    """
    url = "https://legacy.utcourts.gov/cal/search.php"
    
    # Build params based on search type
    params = {
        "t": search_type,
        "d": date,
        "loc": location
    }
    
    # Add type-specific parameters
    if search_type == "a":  # Attorney search
        if first_name:
            params["f"] = first_name
        if last_name:
            params["l"] = last_name
        if bar_number:
            params["b"] = bar_number
    elif search_type == "c":  # Case number search
        if case_number:
            params["c"] = case_number
    elif search_type == "p":  # Party name search
        if party_name:
            params["p"] = party_name
    elif search_type == "j":  # Judge name search
        if judge_name:
            params["j"] = judge_name
    
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    
    return parse_court_cases(response.text)


def parse_court_cases(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse HTML content from Utah court calendar search results.
    
    Args:
        html_content: Raw HTML string from the court search page
    
    Returns:
        List of dictionaries containing parsed case information
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    cases = []
    case_containers = soup.find_all('div', class_='casehover')

    
    for container in case_containers:
        case_data = {}
        
        # Find the wrapper div that contains both time and date divs
        # We need to go back to find the parent structure
        time_date_wrapper = None
        prev = container.find_previous('div')
        
        # Look for the wrapper that contains col-xs-8 and col-xs-4
        for _ in range(5):  # Check up to 5 previous divs
            if prev and prev.find('div', class_='col-xs-8'):
                time_date_wrapper = prev
                break
            if prev:
                prev = prev.find_previous('div')
        
        if time_date_wrapper:
            # Extract time from col-xs-8 div
            time_div = time_date_wrapper.find('div', class_='col-xs-8')
            if time_div:
                time_elem = time_div.find('strong')
                if time_elem:
                    case_data['time'] = time_elem.get_text(strip=True)
                
                # Extract hearing type
                hearing_type = time_div.find('em', class_='little')
                if hearing_type:
                    hearing_type_strong = hearing_type.find('strong')
                    if hearing_type_strong:
                        case_data['hearing_type'] = hearing_type_strong.get_text(strip=True)
            
            # Extract date from col-xs-4 div
            date_div = time_date_wrapper.find('div', class_='col-xs-4')
            if date_div:
                date_elem = date_div.find('strong')
                if date_elem:
                    case_data['date'] = date_elem.get_text(strip=True)
        
        # Extract court/district information
        court_link = container.find('a', class_='caselink')
        if court_link:
            case_data['court'] = court_link.get_text(strip=True)
            
            # Extract case detail URL
            href = court_link.get('href', '')
            if href:
                # Replace spaces with %20 for proper URL encoding
                href_clean = str(href).replace(' ', '%20')
                case_data['detail_url'] = "https://legacy.utcourts.gov/cal/" + href_clean
        
        # Extract court type (District/Justice)
        court_type_em = container.find('em')
        if court_type_em:
            court_type_text = court_type_em.get_text(strip=True)
            if 'District Court' in court_type_text or 'Justice Court' in court_type_text:
                case_data['court_type'] = court_type_text
        
        # Extract attorney name
        attorney_divs = container.find_all('div', class_='bottomline')
        for div in attorney_divs:
            div_text = div.get_text(strip=True)
            if 'Attorney:' in div_text:
                # Extract the highlighted name parts
                attorney_parts = []
                for span in div.find_all('span', class_='HILI'):
                    attorney_parts.append(span.get_text(strip=True))
                if attorney_parts:
                    case_data['attorney'] = ' '.join(attorney_parts)
                break
        
        # Extract parties
        parties_div = container.find_all('div', class_='col-xs-12 col-sm-4')
        if parties_div:
            party_text = parties_div[0].get_text(separator='|', strip=True)
            parts = party_text.split('|')
            if len(parts) >= 3:
                case_data['plaintiff'] = parts[0].replace('vs.', '').strip()
                case_data['defendant'] = parts[2].strip() if len(parts) > 2 else ''
        
        # Extract judge, room, and hearing purpose
        info_divs = container.find_all('div', class_='col-xs-12 col-sm-6')
        for div in info_divs:
            text = div.get_text(separator='|', strip=True)
            if '|' in text:
                parts = text.split('|')
                if len(parts) >= 1:
                    case_data['judge'] = parts[0].strip()
                if len(parts) >= 2:
                    case_data['room'] = parts[1].strip()
                if len(parts) >= 3:
                    case_data['hearing_purpose'] = parts[2].strip()
        
        # Extract WebEx link if available
        all_links = container.find_all('a')
        for link in all_links:
            href = link.get('href', '')
            href_str = str(href).lower()
            # Check for webex.com or webex in the URL path
            if 'webex.com' in href_str or 'webex' in href_str:
                case_data['webex_url'] = href
                break
        
        # Extract case number and type
        case_div = container.find('div', class_='case')
        if case_div:
            case_text = case_div.get_text(separator='|', strip=True)
            parts = case_text.split('|')
            if len(parts) >= 1:
                case_data['case_number'] = parts[0].replace('Case #', '').strip()
            if len(parts) >= 2:
                case_data['case_type'] = parts[1].strip()
        
        cases.append(case_data)
    
    return cases


def save_cases_to_file(
    cases: List[Dict[str, Any]], 
    json_path: str = "court_cases_parsed.json",
    html_path: Optional[str] = None,
    html_content: Optional[str] = None
) -> None:
    """
    Save parsed cases to JSON file and optionally save HTML.
    
    Args:
        cases: List of parsed case dictionaries
        json_path: Path to save JSON file
        html_path: Optional path to save HTML file
        html_content: Optional HTML content to save
    """
    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    
    # Save HTML if provided
    if html_path and html_content:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)


# Main execution block - only runs when script is executed directly
if __name__ == "__main__":
    # Example usage
    print("🔍 Searching for court cases...")
    
    cases = search_court_cases(
        search_type="a",
        first_name="CHRIS",
        last_name="DEXTER",
        date="all",
        location="all"
    )
    
    print(f"✅ Found {len(cases)} cases\n")
    
    # Save to files
    save_cases_to_file(
        cases, 
        json_path="court_cases_parsed.json"
    )
    
    print("✅ Saved parsed case data to court_cases_parsed.json\n")
    print(json.dumps(cases, indent=2, ensure_ascii=False))