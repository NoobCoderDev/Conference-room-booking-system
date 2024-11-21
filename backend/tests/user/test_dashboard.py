import re
from playwright.sync_api import Playwright, sync_playwright, expect
import datetime


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:5000/login")
    page.locator(".d-flex").first.click()
    page.get_by_role("link", name=" Sign In").click()
    page.locator(".brand-logo").click()
    page.get_by_text("Sign-In Access the dashboard").click()
    page.locator("form div").filter(has_text="Email").nth(1).click()
    page.get_by_placeholder("Enter your email address").click()
    page.get_by_placeholder("Enter your email address").fill("devanshu.sonbhurra@softude.com")
    page.locator("form div").filter(has_text="Passcode").first.click()
    page.get_by_placeholder("Enter your passcode").click()
    page.get_by_placeholder("Enter your passcode").fill("123456")
    page.get_by_role("button", name="Sign in").click()
    page.locator(".d-flex").click()
    page.get_by_role("link", name=" User Dashboard").click()
    page.get_by_role("heading", name="Welcome, Devanshu Sonbhurra").click()
    page.get_by_role("heading", name="Your Bookings").click()
    page.get_by_role("link", name="Active").click()
    page.get_by_text("No active bookings").click()
    page.get_by_role("link", name="Past").click()
    page.get_by_text("Unknown Room Date: 2024-11-16").click()
    page.get_by_role("link", name="Upcoming").click()
    page.get_by_role("heading", name="Room Calendar").click()
    page.locator("label").filter(has_text="test1").click()
    page.locator("label").filter(has_text="Room A").click()
    page.get_by_label("Room A").click()
    page.get_by_label("Room A").click()
    page.locator("label").filter(has_text="test1").click()
    page.get_by_label("Room A").check()
    page.get_by_role("button", name="").click()
    page.get_by_role("button", name="").click()
    page.get_by_role("button", name="").click()
    page.get_by_role("button", name="today").click()
    page.get_by_role("button", name="month").click()
    page.get_by_role("button", name="week").click()
    page.get_by_role("button", name="day", exact=True).click()
    page.get_by_role("button", name="week").click()
    page.wait_for_selector("#calendar")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    page.evaluate(f"""
        () => {{
            const calendarEl = document.getElementById('calendar');
            if (!calendarEl) {{
                throw new Error('Calendar element not found');
            }}
            
            // Select tomorrow from 3 PM to 4 PM
            const start = new Date('{tomorrow}T15:00:00');
            const end = new Date('{tomorrow}T16:00:00');
            
            // Simulate a selection event
            const selectInfo = {{
                startStr: start.toISOString(),
                endStr: end.toISOString(),
                allDay: false
            }};
            
            allEvents = []
            
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

    page.get_by_role("textbox", name="test1").click()
    page.get_by_role("option", name="Room C").click()
    page.get_by_role("button", name="Book Room").click()
    page.get_by_role("button", name="Yes, book it!").click()
    # Find and click the "OK" button
    ok_button = page.locator("button.swal2-confirm")
    expect(ok_button).to_be_visible()
    expect(ok_button).to_have_text("OK")
    ok_button.click()
    
    page.locator("#bookingModal").click()
    page.get_by_role("link", name=" Available Rooms").click()
    page.get_by_role("heading", name="Available Rooms").click()
    page.get_by_text("Find and book the perfect").click()
    page.locator("#start_time").click()
    page.locator("#end_time").click()
    page.get_by_role("button", name=" Search").click()
    page.locator(".col-sm-6 > .card > .card-inner").first.click()
    page.locator("div:nth-child(3) > .card > .card-inner").click()
    page.get_by_role("link", name=" Logout").click()
    page.get_by_role("link", name=" Sign In").click()
    page.get_by_role("heading", name="Sign-In").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
