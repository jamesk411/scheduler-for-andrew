from to_ics import create_ics_event

case = {
    'date': '11/12/2025',
    'time': '2:00 PM',
    'case_number': '12345',
    'defendant': 'TEST',
    'hearing_type': 'H',
    'hearing_purpose': 'T',
    'court': 'TC',
    'judge': 'S',
    'attorney': 'J'
}

print("=" * 50)
print("Test 1: Empty string (should use default)")
print("=" * 50)
event1 = create_ics_event(case, filevine_link='', attorney_email='')
if 'attorney@dexterlaw.com' in event1:
    print("✅ Default email used")
else:
    print("❌ Default email NOT found")

print("\n" + "=" * 50)
print("Test 2: chris@dexterlaw.com (should use custom)")
print("=" * 50)
event2 = create_ics_event(case, filevine_link='', attorney_email='chris@dexterlaw.com')
if 'chris@dexterlaw.com' in event2:
    print("✅ Custom email found")
else:
    print("❌ Custom email NOT found")
    print("\nSearching for 'attorney@dexterlaw.com'...")
    if 'attorney@dexterlaw.com' in event2:
        print("❌ ERROR: Still using default email!")

print("\n" + "=" * 50)
print("Extracting description from event2:")
print("=" * 50)
for line in event2.split('\n'):
    if 'DESCRIPTION:' in line:
        desc = line.replace('DESCRIPTION:', '')
        # Find the email part
        parts = desc.split('\\n')
        for part in parts:
            if 'email your primary attorney at' in part:
                print(part)
