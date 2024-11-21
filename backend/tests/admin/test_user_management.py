from playwright.sync_api import Page, expect
import re

def test_login_and_navigate_to_user_management(page: Page):
    # Login as admin
    page.goto("http://localhost:5000/login")
    page.fill('input[name="email"]', "admin@example.com")
    page.fill('input[name="password"]', "123456")
    page.click('button[type="submit"]')
    
    # Navigate to User Management
    page.click("text=User Management")
    expect(page).to_have_url("http://localhost:5000/admin/user_management")
    expect(page.locator("h3.nk-block-title")).to_have_text("User Management")

def test_user_list_display(page: Page):
    # Ensure users are displayed
    user_rows = page.locator(".nk-tb-item:not(.nk-tb-head)") 
    users = user_rows.count()
    assert users > 0, f"Expected room count to be greater than zero, got '{users}'"
    print(f"Number of rooms displayed: {users}")
    
    # Check if user details are displayed correctly
    first_user = user_rows.first
    expect(first_user.locator(".tb-lead")).to_be_visible()
    expect(first_user.locator(".tb-amount")).to_be_visible()
    expect(first_user.locator(".tb-status")).to_be_visible()

def test_user_role_display(page: Page):
    # Check if both admin and regular user roles are displayed
    admin_roles = page.locator(".tb-status.text-success:text('Admin')")
    user_roles = page.locator(".tb-status.text-info:text('User')")
    
    admin_count = admin_roles.count()
    user_count = user_roles.count()
    
    print(f"Number of admin roles found: {admin_count}")
    print(f"Number of user roles found: {user_count}")
    
    assert admin_count > 0, "Expected at least one admin role, but found none"
    assert user_count > 0, "Expected at least one user role, but found none"
    
    # Check if the first instance of each role is visible
    expect(admin_roles.first).to_be_visible()
    expect(user_roles.first).to_be_visible()

def test_view_bookings_button(page: Page):
    # Check if the "View Bookings" button is present for each user
    view_bookings_buttons = page.locator("button.view-bookings")
    button_count = view_bookings_buttons.count()
    print(f"Number of 'View Bookings' buttons found: {button_count}")
    assert button_count > 0, "Expected at least one 'View Bookings' button, but found none"

def test_view_user_bookings(page: Page):
    # Find the first "View Bookings" button
    first_view_bookings_button = page.locator("button.view-bookings").first
    
    # Check if the button exists
    assert first_view_bookings_button.count() > 0, "No 'View Bookings' button found"
    
    # If the button is not immediately visible, try to open the dropdown menu
    if not first_view_bookings_button.is_visible():
        # Find and click the dropdown toggle
        dropdown_toggle = page.locator(".dropdown-toggle").first
        dropdown_toggle.click()
        print("Clicked dropdown toggle")
        
        # Wait for the dropdown menu to be visible
        page.locator(".dropdown-menu", state="visible")
        print("Dropdown menu is visible")
    
    # Now try to click the "View Bookings" button
    user_name = first_view_bookings_button.get_attribute("data-user-name")
    first_view_bookings_button.click()
    print(f"Clicked 'View Bookings' button for user: {user_name}")
    
    # Check if the modal appears
    modal = page.locator("#userBookingsModal")
    expect(modal).to_be_visible(timeout=5000)  # Wait up to 5 seconds for the modal to appear
    print("User bookings modal is visible")
    
    # Check if the modal title contains the user's name
    modal_title = page.locator("#userBookingsTitle")
    expect(modal_title).to_contain_text(user_name)
    print(f"Modal title contains user name: {user_name}")
    
    # Check if bookings are displayed or a "No bookings" message is shown
    bookings_list = page.locator("#userBookingsList")
    expect(bookings_list).to_be_visible()
    
    # Wait for the content to load
    page.wait_for_load_state("networkidle")
    
    # Check if there are bookings or a "No bookings" message
    no_bookings_message = bookings_list.locator(".alert-info")
    bookings = bookings_list.locator(".nk-activity-item")
    
    if no_bookings_message.is_visible():
        print("No bookings found for this user")
        expect(no_bookings_message).to_contain_text("No bookings found for this user")
    else:
        booking_count = bookings.count()
        print(f"Found {booking_count} bookings for this user")
        assert booking_count > 0, "Expected to find bookings, but none were displayed"

def test_no_bookings_message(page: Page):
    # This test assumes there's a user with no bookings
    # You might need to create such a user or skip this test if not applicable
    page.reload()
    page.wait_for_load_state("networkidle")
    print("Page reloaded and ready")

    # Find all "View Bookings" buttons
    view_bookings_buttons = page.locator("button.view-bookings")
    button_count = view_bookings_buttons.count()
    print(f"Found {button_count} 'View Bookings' buttons")

    for i in range(button_count):
        button = view_bookings_buttons.nth(i)
        
        # If the button is not immediately visible, try to open the dropdown menu
        if not button.is_visible():
            dropdown_toggle = page.locator(".dropdown-toggle").nth(i)
            dropdown_toggle.click()
            print(f"Clicked dropdown toggle for button {i+1}")
            page.wait_for_selector(".dropdown-menu", state="visible")

        # Get the user name before clicking the button
        user_name = button.get_attribute("data-user-name")
        print(f"Checking bookings for user: {user_name}")

        # Click the "View Bookings" button
        button.click()
        print(f"Clicked 'View Bookings' button for user {i+1}")
        
        # Wait for the modal to appear
        modal = page.locator("#userBookingsModal")
        expect(modal).to_be_visible(timeout=5000)
        print("User bookings modal is visible")
        
        # Wait for content to load
        page.wait_for_load_state("networkidle")
        
        # Check if "No bookings found" message is displayed
        no_bookings_message = page.locator("#userBookingsList .alert-info")
        if no_bookings_message.is_visible():
            message_text = no_bookings_message.inner_text()
            print(f"Found no bookings message: {message_text}")
            expect(no_bookings_message).to_contain_text("No bookings found for this user")
            # Close the modal
            close_button = page.locator("button.btn-secondary:text('Close')")
            close_button.click()
            print("Closed the modal")
            expect(modal).not_to_be_visible(timeout=5000)
            print(f"Found a user ({user_name}) with no bookings. Test passed.")
            return

    print("Warning: No user without bookings was found")
    assert False, "Test failed: Could not find a user without bookings"

def run_tests():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        tests = [
            ("Login and Navigate to User Management", test_login_and_navigate_to_user_management),
            ("User List Display", test_user_list_display),
            ("User Role Display", test_user_role_display),
            ("View Bookings Button", test_view_bookings_button),
            ("View User Bookings", test_view_user_bookings),
            ("No Bookings Message", test_no_bookings_message)
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