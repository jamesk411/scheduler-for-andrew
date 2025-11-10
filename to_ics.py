"""
Convert court case JSON data to ICS calendar files.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re


def parse_date_time(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Parse date and time strings into a datetime object.
    
    Args:
        date_str: Date in format MM/DD/YYYY (e.g., "11/12/2025")
        time_str: Time in format HH:MM AM/PM (e.g., "2:00 PM")
    
    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Combine date and time
        datetime_str = f"{date_str} {time_str}"
        # Parse the combined string
        dt = datetime.strptime(datetime_str, "%m/%d/%Y %I:%M %p")
        return dt
    except Exception as e:
        print(f"Error parsing date/time: {date_str} {time_str} - {e}")
        return None


def format_ics_datetime(dt: datetime) -> str:
    """Format datetime for ICS file (YYYYMMDDTHHMMSS)"""
    return dt.strftime("%Y%m%dT%H%M%S")


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filename"""
    # Remove or replace invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Limit length
    return text[:100]


def escape_ics_text(text: str) -> str:
    """Escape special characters for ICS format"""
    if not text:
        return ""
    # Replace newlines with \n
    text = text.replace('\n', '\\n')
    # Escape commas, semicolons, and backslashes
    text = text.replace('\\', '\\\\')
    text = text.replace(',', '\\,')
    text = text.replace(';', '\\;')
    return text


def create_ics_event(case: Dict[str, Any]) -> str:
    """
    Create an ICS VEVENT from a court case dictionary.
    
    Args:
        case: Dictionary containing case information
    
    Returns:
        ICS VEVENT string
    """
    # Parse date and time
    date_str = case.get('date', '')
    time_str = case.get('time', '')
    
    start_dt = parse_date_time(date_str, time_str)
    if not start_dt:
        return ""
    
    # Assume 1 hour duration
    end_dt = start_dt + timedelta(hours=1)
    
    # Create UID
    case_number = case.get('case_number', 'unknown')
    uid = f"{case_number}-{int(start_dt.timestamp() * 1000)}@court-scheduling"
    
    # Create timestamp
    dtstamp = format_ics_datetime(datetime.now())
    
    # Format start and end times
    dtstart = format_ics_datetime(start_dt)
    dtend = format_ics_datetime(end_dt)
    
    # Create summary
    defendant = case.get('defendant', 'N/A').split()[0] if case.get('defendant') else 'N/A'
    hearing_type = case.get('hearing_type', 'HEARING').upper()
    hearing_purpose = case.get('hearing_purpose', 'HEARING')
    court = case.get('court', 'Court').split('-')[0].strip() if case.get('court') else 'Court'
    judge = case.get('judge', 'Judge')
    attorney = case.get('attorney', 'CD')
    
    # Determine if virtual or in person
    webex_url = case.get('webex_url', '')
    hearing_mode = "VIRTUAL" if webex_url else "IN PERSON"
    
    # Build summary like the examples
    summary = f"{defendant} – {hearing_mode} – {hearing_purpose} – {court} – J.{judge.split()[-1] if judge != 'N/A' else 'N/A'} – {case_number} – {attorney.split()[0] if attorney else 'CD'}"
    summary = escape_ics_text(summary)
    
    # Create description
    description_parts = [
        "RESTRICTED LINK FOR DEXTER LAW INTERNAL USE ONLY",
        "N/A",
        "",
        "---",
        "",
        "Hello,",
        "",
        "This is a reminder of your upcoming Court appearance. Please confirm your attendance.",
        "",
        "For questions, concerns, and technical difficulties you can call or text the number 801-225-9900 or email your primary attorney at attorney@dexterlaw.com and cc assistant Andrew@DexterLaw.com",
        "",
        "If you have a conflict that may prevent your appearance, please reach out.",
        "Please note that a continuance/virtual appearance cannot be guaranteed and it's ultimately up to the Judge's discretion.",
        "",
        "Best Wishes!",
        "DEXTER & DEXTER LAW",
        "",
        "---",
        "",
        "COURT NOTICE",
        "",
        "UCJA Rule 4-401.02: court proceedings, including electronic proceedings, may NOT be recorded, photographed, or transmitted. Failure to comply with this prohibition may be treated as contempt of court, punishable by fine and time in jail.",
        "",
        "Individuals needing special accommodation (including auxiliary communicative aids and services) should call three days prior to their hearing.",
        "For TTY service call Utah Relay at 800-346-4128.",
        "The general information phone number is 801-724-3900"
    ]
    description = escape_ics_text('\n'.join(description_parts))
    
    # Location is WebEx URL if virtual, otherwise court name
    if webex_url:
        location = escape_ics_text(webex_url)
    else:
        location = escape_ics_text(case.get('court', 'Court'))
    
    # Build the VEVENT
    vevent = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:Hearing reminder - 24 hours before
END:VALARM
END:VEVENT"""
    
    return vevent


def cases_to_ics(cases: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
    """
    Convert a list of court cases to an ICS calendar file.
    
    Args:
        cases: List of case dictionaries
        output_path: Optional path to save the ICS file
    
    Returns:
        ICS calendar string
    """
    # Create ICS header
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Court Scheduling//Court Hearing//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
    
    # Add each case as an event
    for case in cases:
        event = create_ics_event(case)
        if event:
            ics_content += event + "\n"
    
    # Close calendar
    ics_content += "END:VCALENDAR\n"
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        print(f"✅ Saved calendar to {output_path}")
    
    return ics_content


def case_to_ics_file(case: Dict[str, Any], output_dir: str = ".") -> str:
    """
    Create an individual ICS file for a single case.
    
    Args:
        case: Case dictionary
        output_dir: Directory to save the file
    
    Returns:
        Path to the created file
    """
    # Create filename
    case_number = case.get('case_number', 'unknown')
    defendant = case.get('defendant', 'defendant').split()[0] if case.get('defendant') else 'defendant'
    defendant = sanitize_filename(defendant.upper())
    
    filename = f"{case_number}_{defendant}.ics"
    output_path = f"{output_dir}/{filename}"
    
    # Create ICS content for single case
    cases_to_ics([case], output_path)
    
    return output_path


# Example usage
if __name__ == "__main__":
    import json
    from search import search_court_cases
    
    print("🔍 Searching for court cases...")
    
    # Search for cases
    cases = search_court_cases(
        search_type="a",
        first_name="CHRIS",
        last_name="DEXTER",
        date="all",
        location="all"
    )
    
    print(f"✅ Found {len(cases)} cases")
    
    if cases:
        # Option 1: Create one calendar file with all cases
        print("\n📅 Creating combined calendar file...")
        cases_to_ics(cases, "all_court_cases.ics")
        
        # Option 2: Create individual files for each case
        print("\n📅 Creating individual calendar files...")
        for case in cases:
            file_path = case_to_ics_file(case, ".")
            print(f"   Created: {file_path}")
        
        print(f"\n✅ Created {len(cases) + 1} calendar file(s)")
    else:
        print("❌ No cases found")
