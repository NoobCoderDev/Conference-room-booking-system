from playwright.sync_api import Page, expect, sync_playwright
import re

def test_sidebar_structure(page: Page):
    page.goto("http://localhost:5000/login")

    # Check if the sidebar is present and has the correct classes
    sidebar = page.locator('.nk-sidebar')
    expect(sidebar).to_be_visible()
    expect(sidebar).to_have_class(re.compile('nk-sidebar-fixed'))
    expect(sidebar).to_have_class(re.compile('is-dark'))
    expect(sidebar).to_have_class(re.compile('sidebar-collapsed'))

    # Check for the presence of the logo
    expect(page.locator('.nk-sidebar-logo img')).to_be_visible()

    # Check for the presence of menu items when not authenticated
    expect(page.locator('.nk-menu-link.sign-in')).to_be_visible()
    expect(page.locator('.nk-menu-link.sign-up')).to_be_visible()

def test_navigation(page: Page):
    page.goto("http://localhost:5000/login")

    # Test navigation to Sign Up page
    page.click('.nk-menu-link.sign-up')
    expect(page).to_have_url("http://localhost:5000/register")

    # Test navigation back to Sign In page
    page.click('.nk-menu-link.sign-in')
    expect(page).to_have_url("http://localhost:5000/login")

def test_responsive_design(page: Page):
    page.goto("http://localhost:5000/login")

    # Test on mobile size
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator('.nk-sidebar')).to_have_class('sidebar-collapsed')
    expect(page.locator('.nk-header-brand')).to_be_visible()

    # Test on desktop size
    page.set_viewport_size({"width": 1280, "height": 720})
    expect(page.locator('.nk-sidebar')).to_be_visible()
    expect(page.locator('.nk-header-brand')).to_be_hidden()

def test_footer(page: Page):
    page.goto("http://localhost:5000/login")

    # Footer should not be visible when not authenticated
    expect(page.locator('.nk-footer')).to_be_hidden()

    # TODO: Add a test for authenticated user to check if footer is visible
    # This would require implementing a login process in the test

def test_page_title(page: Page):
    page.goto("http://localhost:5000/login")
    expect(page).to_have_title("Sign-In")

    page.goto("http://localhost:5000/register")
    expect(page).to_have_title(re.compile("Sign-Up|Register"))

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("\nTesting sidebar structure...")
            test_sidebar_structure(page)

            print("\nTesting navigation...")
            test_navigation(page)

            print("\nTesting responsive design...")
            test_responsive_design(page)

            print("\nTesting footer...")
            test_footer(page)

            print("\nTesting page titles...")
            test_page_title(page)

            print("\nAll tests passed successfully!")

        except Exception as e:
            print(f"\nAn error occurred during testing: {str(e)}")
            print(f"Current URL: {page.url}")
            print(f"Page content: {page.content()}")

        finally:
            browser.close()
            print("\nBrowser closed.")

if __name__ == "__main__":
    run_tests()