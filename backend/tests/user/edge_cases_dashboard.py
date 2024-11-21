import re
from playwright.sync_api import Playwright, sync_playwright, expect
import datetime

def test_invalid_login(page):
    page.goto("http://localhost:5000/login")
    page.get_by_placeholder("Enter your email address").fill("invalid@example.com")
    page.get_by_placeholder("Enter your passcode").fill("wrongpassword")
    page.get_by_role("button", name="Sign in").click()
    error_message = page.locator(".alert")
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Invalid email or password")

def test_access_protected_page_without_login(page):
    page.goto("http://localhost:5000/login")
    page.goto("http://localhost:5000/user/dashboard")
    expect(page).to_have_url("http://localhost:5000/login?next=%2Fuser%2Fdashboard")
    
    error_message = page.locator(".alert")
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Please log in to access this page.")

def test_book_room_end_before_start(page):
    page.goto("http://localhost:5000/user/dashboard")
    current_time = datetime.datetime.now()
    future_time = (current_time + datetime.timedelta(hours=1)).strftime("%H:%M")
    
    page.evaluate(f"""
        () => {{
                    
            allEvents = []
            
            const selectInfo = {{
                startStr: '{current_time.strftime("%Y-%m-%d")}T{future_time}:00',
                endStr: '{current_time.strftime("%Y-%m-%d")}T{current_time.strftime("%H:%M")}:00',
                allDay: false
            }};
            if (typeof openBookingModal === 'function') {{
                openBookingModal(selectInfo);
            }}
        
        function updateAvailableRooms(date, startTime, endTime) {{
            const roomSelect = document.getElementById('roomSelect');
            const selectedStart = new Date(date + 'T' + startTime);
            const selectedEnd = new Date(date + 'T' + endTime);

            // Clear existing options
            roomSelect.innerHTML = '';

            // Get all rooms
            const allRooms = Array.from(document.querySelectorAll('.room-toggle')).map(checkbox => ({{
                id: checkbox.value,
                name: checkbox.nextSibling.textContent.trim()
            }}));

            // Filter available rooms
            const availableRooms = allRooms.filter(room => {{
                return !allEvents.some(event => 
                    event.extendedProps.room_id == room.id &&
                    new Date(event.start) < selectedEnd &&
                    new Date(event.end) > selectedStart
                );
            }});

            // Add available rooms to select
            availableRooms.forEach(room => {{
                const option = document.createElement('option');
                option.value = room.id;
                option.textContent = room.name;
                roomSelect.appendChild(option);
            }});

            if (availableRooms.length === 0) {{
                const option = document.createElement('option');
                option.textContent = 'No rooms available';
                roomSelect.appendChild(option);
                document.getElementById('confirmBooking').disabled = true;
            }} else {{
                document.getElementById('confirmBooking').disabled = false;
            }}
        }}
        
        function openBookingModal(info) {{
            const date = info.startStr.split('T')[0];
            const startTime = info.startStr.split('T')[1].substr(0, 5);
            const endTime = info.endStr.split('T')[1].substr(0, 5);

            document.getElementById('bookingDate').value = date;
            document.getElementById('startTime').value = startTime;
            document.getElementById('endTime').value = endTime;

            document.getElementById('dateDisplay').textContent = date;
            document.getElementById('startTimeDisplay').textContent = startTime;
            document.getElementById('endTimeDisplay').textContent = endTime;

            // Update available rooms
            updateAvailableRooms(date, startTime, endTime);

            new bootstrap.Modal(document.getElementById('bookingModal')).show();
        }}
        
        // Manually call the openBookingModal function
        if (typeof openBookingModal === 'function') {{
            openBookingModal(selectInfo);
        }} else {{
            throw new Error('openBookingModal function not found');
        }}
    }}
    """)
    page.wait_for_selector("#bookingModal", state="visible")
    
    page.get_by_role("button", name="Book Room").click()
    
    print("Book room is successfully clicked...")
    page.wait_for_selector(".swal2-popup", state="visible")
    
    error_title = page.locator(".swal2-title")
    expect(error_title).to_be_visible()
    expect(error_title).to_have_text("Confirm Booking")
    page.get_by_role("button", name="Yes, book it!").click()
    
    error_title = page.locator(".swal2-title")
    expect(error_title).to_be_visible()
    expect(error_title).to_have_text("Error!")
    
    error_message = page.locator(".swal2-html-container")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("End time must be after start time")
    
    page.click(".swal2-confirm")
    
def test_error_in_calendar_api(page):
    page.route("**/fullcalendar@5.10.2/main.min.js", lambda route: route.abort())
    
    page.goto("http://localhost:5000/user/dashboard");

    # Check if error message is displayed when FullCalendar is undefined
    errorMessage = page.locator('.alert-danger');
    expect(errorMessage).to_be_visible();
    expect(errorMessage).to_have_text("Calendar component failed to load. Please refresh the page or contact support.");

def login(page, email, password):
    page.goto("http://localhost:5000/login")
    page.get_by_placeholder("Enter your email address").fill(email)
    page.get_by_placeholder("Enter your passcode").fill(password)
    page.get_by_role("button", name="Sign in").click()

def logout(page):
    page.get_by_role("link", name="Logout").click()

def run_edge_tests(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    page = context.new_page()

    test_functions = [
        ("Invalid Login Test", test_invalid_login),
        ("Access Protected Page Without Login Test", test_access_protected_page_without_login),
        ("Book Room End Before Start Test", test_book_room_end_before_start),
        ("Error-handling in calendar api Test", test_error_in_calendar_api)
    ]

    for test_name, test_function in test_functions:
        print(f"\n--- Starting {test_name} ---")
        try:
            if test_name != "Invalid Login Test" and test_name != "Access Protected Page Without Login Test":
                login(page, "devanshu.sonbhurra@softude.com", "123456")
            
            test_function(page)
            
            if test_name != "Invalid Login Test" and test_name != "Access Protected Page Without Login Test":
                logout(page)
            
            print(f"--- {test_name} Passed ---")
        except Exception as e:
            print(f"--- {test_name} Failed ---")
            print(f"Error: {str(e)}")
        
    # Close the browser
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_edge_tests(playwright)