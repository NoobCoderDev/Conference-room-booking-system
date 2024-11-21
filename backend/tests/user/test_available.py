from playwright.sync_api import Page, expect
import datetime

def test_login_and_navigate_to_available_rooms(page: Page):
    # Login
    page.goto("http://localhost:5000/login")
    page.fill('input[name="email"]', "test@example.com")
    page.fill('input[name="password"]', "123456")
    page.click('button[type="submit"]')
    
    # Check if redirected to dashboard
    expect(page).to_have_url("http://localhost:5000/user/dashboard")
    print("Logged in successfully")

    # Wait for the sidebar to be visible
    page.wait_for_selector(".nk-sidebar", state="visible")

    # Click on the "Available Rooms" link in the sidebar
    available_rooms_link = page.locator("text=Available Rooms").first
    available_rooms_link.click()

    # Check if redirected to available rooms page
    expect(page).to_have_url("http://localhost:5000/user/available_rooms")
    print("Navigated to user available room page")

    # Verify that we're on the correct page
    expect(page.locator("h3.nk-block-title")).to_have_text("Available Rooms")
    print("Confirmed arrival on Available Rooms page")

def test_available_rooms_page(page: Page):
    # Navigate to the available rooms page
    page.goto("http://localhost:5000/user/available_rooms")

    # Check if the page title is correct
    expect(page).to_have_title("Available Rooms")

    # Check if the main heading is present
    expect(page.locator("h3.nk-block-title")).to_have_text("Available Rooms")

    # Check if the search form is present
    expect(page.locator(".form-class")).to_be_visible()

def test_search_functionality(page: Page):
    page.goto("http://localhost:5000/user/available_rooms")

    # Fill in the search form
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    page.fill("#date", tomorrow)
    page.fill("#start_time", "09:00")
    page.fill("#end_time", "10:00")

    # Submit the form
    page.click("button[type='submit']")

    # Check if the page reloads with the search parameters
    expect(page).to_have_url(f"http://localhost:5000/user/available_rooms?date={tomorrow}&start_time=09%3A00&end_time=10%3A00")

def test_room_display(page: Page):
    page.goto("http://localhost:5000/user/available_rooms")

    # Check if rooms are displayed
    room_cards = page.locator(".card.card-bordered.h-100")
    expect(room_cards).to_have_count(5)  # Assuming there are 4 rooms available

    # Check if room information is displayed correctly
    first_room = room_cards.first
    expect(first_room.locator(".project-title .title")).to_be_visible()
    expect(first_room.locator(".project-progress-task")).to_be_visible()
    expect(first_room.locator(".project-details")).to_contain_text("Facilities :")

def test_booking_modal(page: Page):
    page.goto("http://localhost:5000/user/available_rooms")

    # Click on the "Book Room" button for the first room
    page.click(".book-room:first-child")

    # Check if the booking modal appears
    modal = page.locator("#bookingModal")
    expect(modal).to_be_visible()

    # Check if the room name is displayed in the modal
    room_name = page.locator(".project-title .title").first.inner_text()
    expect(modal.locator("#roomName")).to_have_text(room_name)

def test_booking_confirmation(page: Page):
    page.goto("http://localhost:5000/user/available_rooms")

    # Click on the "Book Room" button for the first room
    page.click(".book-room:first-child")

    # Wait for the modal to appear
    page.wait_for_selector("#bookingModal")

    # Click on the "Confirm Booking" button
    page.click("#confirmBooking")

    # Wait for the SweetAlert to appear
    page.wait_for_selector(".swal2-popup")

    # Confirm the booking
    page.click(".swal2-confirm")

    # Wait for the success message
    page.wait_for_selector(".swal2-success")

    # Check if the success message is displayed
    expect(page.locator(".swal2-title")).to_have_text("Success!")

def run_tests():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        tests = [
            ("Login and navigating available rooms", test_login_and_navigate_to_available_rooms),
            ("Available Rooms Page Structure", test_available_rooms_page),
            ("Search Functionality", test_search_functionality),
            ("Room Display", test_room_display),
            ("Booking Modal", test_booking_modal),
            ("Booking Confirmation", test_booking_confirmation),
        ]

        for test_name, test_function in tests:
            try:
                print(f"\nRunning test: {test_name}")
                test_function(page)
                print(f"{test_name} test passed")
            except Exception as e:
                print(f"Error in {test_name} test: {str(e)}")
                print(f"Current URL: {page.url}")
                page.screenshot(path=f"error_{test_name.lower().replace(' ', '_')}.png")

        print("\n--- Cleaning up after tests ---")
        page.evaluate("window.localStorage.clear()")
        page.evaluate("window.sessionStorage.clear()")
        page.context.clear_cookies()
        print("Cleared local storage, session storage, and cookies")
        browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    run_tests()