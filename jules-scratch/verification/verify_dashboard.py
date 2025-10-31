from playwright.sync_api import sync_playwright, expect

def verify_full_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Increase navigation timeout and wait for network to be idle
            page.goto("http://localhost:3000", timeout=60000, wait_until='networkidle')

            page.set_viewport_size({"width": 1600, "height": 900})

            # Increase individual locator timeouts
            timeout = 15000
            expect(page.get_by_role("heading", name="Crypto Trading Bot Dashboard")).to_be_visible(timeout=timeout)
            expect(page.get_by_role("heading", name__regex=r"BTCUSDT Chart.*")).to_be_visible(timeout=timeout)
            expect(page.get_by_role("heading", name="Launch a New Bot")).to_be_visible(timeout=timeout)
            expect(page.get_by_role("heading", name="Active Bots")).to_be_visible(timeout=timeout)
            expect(page.get_by_role("heading", name="Trade History")).to_be_visible(timeout=timeout)

            # Give chart a bit more time to render
            page.wait_for_timeout(3000)

            screenshot_path = "jules-scratch/verification/full_dashboard.png"
            page.screenshot(path=screenshot_path)

            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_full_dashboard()
