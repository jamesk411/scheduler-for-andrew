import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

url = "https://legacy.utcourts.gov/cal/search.php"
params = {
    "t": "a",         # search type: attorney
    "f": "CHRIS",     # first name
    "l": "DEXTER",    # last name
    "d": "all",       # date: all
    "loc": "all"      # location: all
}

response = requests.get(url, params=params, timeout=30)

# Print status
print(f"Status: {response.status_code}")

# Save to file
with open("court_search_results.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ Saved raw HTML to court_search_results.html")

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find all case containers
cases = []
case_containers = soup.find_all('div', class_='casehover')

print(f"\n📋 Found {len(case_containers)} cases\n")

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
            case_data['detail_url'] = "https://legacy.utcourts.gov/cal/" + str(href)
    
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

# Save parsed data to JSON
with open("court_cases_parsed.json", "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

print("✅ Saved parsed case data to court_cases_parsed.json\n")
print(json.dumps(cases, indent=2, ensure_ascii=False))