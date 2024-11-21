from playwright.sync_api import Page, expect, sync_playwright
import time

def test_login_page(page: Page):
    # Navigate to the login page
    page.goto("http://localhost:5000/login")

    # Check if the page title is correct
    expect(page).to_have_title("Sign-In")

    # Check if the login form elements are present
    expect(page.locator('input[name="email"]')).to_be_visible()
    expect(page.locator('input[name="password"]')).to_be_visible()
    expect(page.locator('button[type="submit"]')).to_be_visible()

def test_successful_login(page: Page):
    # Navigate to the login page
    page.goto("http://localhost:5000/login")

    # Fill in the login form
    page.fill('input[name="email"]', "test@example.com")
    page.fill('input[name="password"]', "123456")

    # Click the login button
    page.click('button[type="submit"]')

    # Check if redirected to the dashboard
    expect(page).to_have_url("http://localhost:5000/user/dashboard")
    time.sleep(3)

def test_failed_login(page: Page):
    # Navigate to the login page
    page.goto("http://localhost:5000/login")

    # Fill in the login form with incorrect credentials
    page.fill('input[name="email"]', "wrong@example.com")
    page.fill('input[name="password"]', "wrongpassword")

    # Click the login button
    page.click('button[type="submit"]')

    # Check if the error message is displayed
    expect(page.locator('.alert-danger')).to_be_visible()
    expect(page.locator('.alert-danger')).to_contain_text("Invalid email or password")
    
def test_empty_form_submission(page: Page):
    # Navigate to the login page
    page.goto("http://localhost:5000/login")

    # Click the login button without filling any fields
    page.click('button[type="submit"]')

    # Check if the form validation prevents submission
    # This could be checking for browser's default validation messages or custom validation
    expect(page).to_have_url("http://localhost:5000/login")  # URL should not change
    
    # Check for validation messages 
    expect(page.locator('input[name="email"]:invalid')).to_be_visible()
    expect(page.locator('input[name="password"]:invalid')).to_be_visible()
    
def test_password_visibility_toggle(page: Page):
    page.goto("http://localhost:5000/login")
    
    page.fill('input[name="password"]', "123456")
    
    password_input = page.locator('input[name="password"]')
    visibility_toggle = page.locator('.passcode-switch')

    expect(password_input).to_have_attribute("type", "password")
    visibility_toggle.click()
    expect(password_input).to_have_attribute("type", "text")
    visibility_toggle.click()
    expect(password_input).to_have_attribute("type", "password")
    
def test_navigation_to_register_page(page: Page):
    page.goto("http://localhost:5000/login")
    
    # Click the create account link
    page.locator('text="Create an account"').first.click()
    
    expect(page).to_have_url("http://localhost:5000/register")
    
def test_navigation_to_register_page_sidebar(page: Page):
    page.goto("http://localhost:5000/login")
    
    # Click the create account link
    page.locator('sign-up').click()
    
    expect(page).to_have_url("http://localhost:5000/register")

def run_tests():
    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=False, slow_mo=300)
            page = browser.new_page()
            
            print("\n Test 1. Check login page elements...")
            test_login_page(page)
            
            print("\n Test 2. successful login...")
            test_successful_login(page)
            
            print("\n Test 3. failed login...")
            test_failed_login(page)
            
            print("\n Test 4. empty form submission...")
            test_empty_form_submission(page)
            
            print("\n Test 5. password visibility toggle...")
            test_password_visibility_toggle(page)
            
            print("\n Test 6. Navigated to register page...")
            test_navigation_to_register_page(page)
            
            print("\n All tests passed successfully...")
        
        except Exception as e:
            print(f"\n An error occurred during testing: {str(e)}")
        
        finally:
            if browser:
                browser.close()
                print("\n Browser closed.")

if __name__ == "__main__":
    run_tests()