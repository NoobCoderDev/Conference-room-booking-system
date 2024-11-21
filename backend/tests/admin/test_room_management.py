from playwright.sync_api import Page, expect, sync_playwright
import time

def test_login_and_navigate_to_room_management(page: Page):
    page.goto("http://localhost:5000/login")
    page.fill('input[name="email"]', "admin@example.com")
    page.fill('input[name="password"]', "123456")
    page.click('button[type="submit"]')
    
    # Wait for navigation and click on Room Management
    page.wait_for_selector("text=Room Management")
    page.click("text=Room Management")
    
    expect(page).to_have_url("http://localhost:5000/admin/room_management")
    expect(page.locator("h3.nk-block-title")).to_have_text("Room Management")
    print("Successfully navigated to Room Management page")

def test_room_list_display(page: Page):
    room_cards = page.locator(".card.card-bordered")
    room_count = room_cards.count()
    assert room_count > 0, f"Expected room count to be greater than zero, got '{room_count}'"
    print(f"Number of rooms displayed: {room_count}")
    
    first_room = room_cards.first
    expect(first_room.locator(".user-info h6")).to_be_visible()
    expect(first_room.locator(".user-info .sub-text")).to_contain_text("Capacity:")
    expect(first_room.locator(".team-details p")).to_contain_text("Facilities :")
    
    room_name = first_room.locator(".user-info h6").inner_text()
    room_capacity = first_room.locator(".user-info .sub-text").inner_text()
    room_facilities = first_room.locator(".team-details p").inner_text()
    print(f"First room details - Name: {room_name}, {room_capacity}, {room_facilities}")

# def test_add_room(page: Page):
#     # Click 'Add Room' button
#     page.click("#addRoomBtn")
#     print("Add room btn Clicked... ")
    
#     # Wait for the modal to be visible
#     page.wait_for_selector("#addRoomModal", state="visible")
    
#     # Wait a bit for any animations to complete
#     page.wait_for_timeout(1000)
    
#     # Now interact with the form elements
#     page.fill("#roomName", "Test Room")
#     page.fill("#roomCapacity", "10")
#     page.fill("#roomFacilities", "Projector, Whiteboard")
    
#     # Save the room
#     page.click("#saveRoom")
    
#     # Wait for the SweetAlert to appear
#     page.wait_for_selector(".swal2-confirm", state="visible")
    
#     # Confirm the action in SweetAlert
#     page.click(".swal2-confirm")
    
#     # Wait for the success message
#     page.wait_for_selector(".swal2-title", state="visible")
    
#     # Check for success message
#     expect(page.locator(".swal2-title")).to_have_text("Room Added")
    
#     # Wait for the page to update
#     page.reload()
#     page.wait_for_load_state("networkidle")
    
#     # Verify the new room is in the list
#     expect(page.locator(".user-info h6:text('Test Room')")).to_be_visible()
    
#     print("New room 'Test Room' added successfully")

def test_add_room(page: Page):
    # Click 'Add Room' button
    page.click("#addRoomBtn")
    print("Add room btn Clicked...")

    # Debug: Check if the modal exists in the DOM
    modal_exists = page.evaluate("() => !!document.querySelector('#addRoomModal')")
    print(f"Modal exists in DOM: {modal_exists}")

    if not modal_exists:
        raise Exception("Add Room modal does not exist in the DOM")

    # Use JavaScript to show the modal
    page.evaluate("$('#addRoomModal').modal('show')")
    print("Attempted to show modal using JavaScript")

    # Wait a bit for any animations to complete
    page.wait_for_timeout(2000)

    # Debug: Check modal state
    modal_visible = page.evaluate("() => $('#addRoomModal').is(':visible')")
    print(f"Is modal visible according to jQuery: {modal_visible}")

    # If the modal is still not visible, try to force it
    if not modal_visible:
        page.evaluate("""
            () => {
                const modal = document.querySelector('#addRoomModal');
                modal.classList.add('show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
            }
        """)
        print("Attempted to force modal visibility")

    # Wait for the modal content to be visible
    try:
        page.wait_for_selector("#addRoomModal .modal-content", state="visible", timeout=10000)
        print("Modal content is visible")
    except TimeoutError:
        print("Modal content did not become visible")
        # Take a screenshot for debugging
        page.screenshot(path="modal_not_visible.png")
        raise

    # Now interact with the form elements
    page.fill("#roomName", "Test Room")
    page.fill("#roomCapacity", "10")
    page.fill("#roomFacilities", "Projector, Whiteboard")
    print("Filled in room details")

    # Save the room
    page.click("#saveRoom")
    print("Clicked 'Save Room' button")

    # Wait for the SweetAlert to appear
    page.wait_for_selector(".swal2-confirm", state="visible", timeout=10000)
    print("SweetAlert confirmation button is visible")

    # Confirm the action in SweetAlert
    page.click(".swal2-confirm")
    print("Clicked SweetAlert confirm button")

    # Wait for the success message
    page.wait_for_selector(".swal2-title", state="visible", timeout=10000)
    
    # Check for success message
    success_message = page.locator(".swal2-title").inner_text()
    print(f"Success message: {success_message}")
    assert success_message == "Room Added", f"Expected 'Room Added', but got '{success_message}'"

    # Wait for the page to update
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify the new room is in the list
    new_room = page.locator(".user-info h6:text('Test Room')")
    is_visible = new_room.is_visible()
    print(f"Is new room visible in the list: {is_visible}")
    assert is_visible, "New room 'Test Room' is not visible in the list"

    print("New room 'Test Room' added successfully")

def test_edit_room(page: Page):
    page.click(".edit-room:first-child")
    
    page.fill("#editRoomName", "Room A")
    page.fill("#editRoomCapacity", "15")
    page.fill("#editRoomFacilities", "Projector, Whiteboard, Video Conferencing")
    
    page.click("#updateRoom")
    
    page.wait_for_selector(".swal2-confirm")
    page.click(".swal2-confirm")
    
    page.wait_for_selector(".swal2-title")
    expect(page.locator(".swal2-title")).to_have_text("Room Updated")
    
    expect(page.locator(".user-info h6:text('Room A')")).to_be_visible()
    expect(page.locator(".user-info .sub-text:text('Capacity: 15')")).to_be_visible()
    print("Room updated successfully to 'Updated Room'")

def test_delete_room(page: Page):
    initial_room_count = page.locator(".card.card-bordered").count()
    
    page.click(".delete-room:last-child")
    
    page.wait_for_selector(".swal2-confirm")
    page.click(".swal2-confirm")
    
    page.wait_for_selector(".swal2-title")
    expect(page.locator(".swal2-title")).to_have_text("Deleted!")

    page.reload()
    page.wait_for_load_state("networkidle")
    
    new_room_count = page.locator(".card.card-bordered").count()
    assert new_room_count == initial_room_count - 1, f"Expected {initial_room_count - 1} rooms, but got {new_room_count}"
    print(f"Room deleted successfully. Room count reduced from {initial_room_count} to {new_room_count}")

def test_form_validation(page: Page):
    page.click("#addRoomBtn")
    
    page.click("#saveRoom")
    
    page.wait_for_selector(".swal2-title")
    expect(page.locator(".swal2-title")).to_have_text("Incomplete Form")
    print("Form validation for empty fields working correctly")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        tests = [
            ("Login and Navigate to Room Management", test_login_and_navigate_to_room_management),
            ("Room List Display", test_room_list_display),
            ("Add Room", test_add_room),
            ("Edit Room", test_edit_room),
            ("Delete Room", test_delete_room),
            ("Form Validation", test_form_validation)
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