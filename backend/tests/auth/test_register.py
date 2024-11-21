from playwright.sync_api import Page, expect, sync_playwright
import re
import time

def test_register_page_structure(page: Page):
    page.goto("http://localhost:5000/register")

    # Check page title
    expect(page).to_have_title("Sign-Up")

    # Check for main elements
    expect(page.locator('h5:text("Register")')).to_be_visible()
    expect(page.locator('p:text("Create New Account")')).to_be_visible()

    # Check form fields
    expect(page.locator('#name')).to_be_visible()
    expect(page.locator('#email')).to_be_visible()
    expect(page.locator('#password')).to_be_visible()
    expect(page.locator('#checkbox')).to_be_visible()
    expect(page.locator('button:text("Register")')).to_be_visible()

    # Check for "Sign in instead" link
    expect(page.locator('strong:text("Sign in instead")')).to_be_visible()

    # Check for social login options
    expect(page.locator('a:text("Facebook")')).to_be_visible()
    expect(page.locator('a:text("Google")')).to_be_visible()

def test_successful_signup(page: Page):
    page.goto("http://localhost:5000/register")

    # Fill in the registration form
    page.fill('#name', "Test User")
    page.fill('#email', "testuser@example.com")
    page.fill('#password', "password123")
    page.check('#checkbox')

    # Submit the form
    page.click('button:text("Register")')

    # Wait for the SweetAlert to appear
    page.wait_for_selector('.swal2-popup')
    
    # Check the content of the SweetAlert
    expect(page.locator('.swal2-title')).to_have_text("Success!")
    expect(page.locator('.swal2-html-container')).to_have_text("Registration successful!.")
    
    # Click the "Go to dashboard" button
    page.click('button.swal2-confirm')

    # Check if redirected to the dashboard
    expect(page).to_have_url("http://localhost:5000/user/dashboard")

def test_failed_signup_invalid_email(page: Page):
    page.goto("http://localhost:5000/register")

    # Fill in the form with invalid email
    page.fill('#name', "Test User")
    page.fill('#email', "invalidemail")
    page.fill('#password', "password123")
    page.check('#checkbox')

    # Submit the form
    page.click('button:text("Register")')

    # Check for client-side validation
    expect(page.locator('#email:invalid')).to_be_visible()

def test_failed_signup_duplicate_email(page: Page):
    page.goto("http://localhost:5000/register")

    # Fill in the form with a duplicate email
    page.fill('#name', "Another User1")
    page.fill('#email', "existing@example.com")  # Assume this email already exists
    page.fill('#password', "password123")
    page.check('#checkbox')

    # Submit the form
    page.click('button:text("Register")')

    # Wait for the SweetAlert to appear
    page.wait_for_selector('.swal2-popup')
    
    # Check the content of the SweetAlert
    expect(page.locator('.swal2-title')).to_have_text("Registration Failed")
    expect(page.locator('.swal2-html-container')).to_have_text(re.compile("Email already registered|already exists"))
    
def test_failed_signup_duplicate_name(page: Page):
    page.goto("http://localhost:5000/register")

    # Fill in the form with a duplicate email
    page.fill('#name', "Another User")
    page.fill('#email', "existing1@example.com")  # Assume this email already exists
    page.fill('#password', "password123")
    page.check('#checkbox')

    # Submit the form
    page.click('button:text("Register")')

    # Wait for the SweetAlert to appear
    page.wait_for_selector('.swal2-popup')
    
    # Check the content of the SweetAlert
    expect(page.locator('.swal2-title')).to_have_text("Registration Failed")
    expect(page.locator('.swal2-html-container')).to_have_text(re.compile("Username already exists|already exists"))

def test_checkbox_validation(page: Page):
    page.goto("http://localhost:5000/register")

    # Fill in the form without checking the checkbox
    page.fill('#name', "Test User")
    page.fill('#email', "testuser@example.com")
    page.fill('#password', "password123")

    # Submit the form
    page.click('button:text("Register")')

    # Wait for the SweetAlert to appear
    page.wait_for_selector('.swal2-popup')
    
    # Check the content of the SweetAlert
    expect(page.locator('.swal2-title')).to_have_text("Oops...")
    expect(page.locator('.swal2-html-container')).to_have_text("Please agree to the Privacy Policy and Terms.")

def test_password_visibility_toggle(page: Page):
    page.goto("http://localhost:5000/register")

    # Check if password is initially hidden
    expect(page.locator('#password')).to_have_attribute("type", "password")

    # Click the visibility toggle
    page.click('.passcode-switch')

    # Check if password is now visible
    expect(page.locator('#password')).to_have_attribute("type", "text")

    # Click the visibility toggle again
    page.click('.passcode-switch')

    # Check if password is hidden again
    expect(page.locator('#password')).to_have_attribute("type", "password")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()

        tests = [
            ("Register page structure", test_register_page_structure),
            ("Successful signup", test_successful_signup),
            ("Failed signup - Invalid email", test_failed_signup_invalid_email),
            ("Failed signup - Duplicate email", test_failed_signup_duplicate_email),
            ("Checkbox validation", test_checkbox_validation),
            ("Password visibility toggle", test_password_visibility_toggle)
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

        print("\nAll tests completed.")
        browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    run_tests()