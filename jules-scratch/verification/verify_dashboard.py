from playwright.sync_api import sync_playwright, expect

def verify_full_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:3000", timeout=60000, wait_until='networkidle')
            page.set_viewport_size({"width": 1600, "height": 900})

            timeout = 15000
            expect(page.locator("text=CryptoTrader")).to_be_visible(timeout=timeout)
            expect(page.locator("text=Dashboard")).to_be_visible(timeout=timeout)
            expect(page.locator("text=Bot Management")).to_be_visible(timeout=timeout)
            expect(page.locator("text=Trade History")).to_be_visible(timeout=timeout)

            # Verify Dashboard Page
            expect(page.get_by_role("heading", name__regex=r"BTCUSDT Chart.*")).to_be_visible(timeout=timeout)
            page.screenshot(path="jules-scratch/verification/01_dashboard_page.png")

            # Navigate to Bot Management and verify
            page.locator("text=Bot Management").click()
            expect(page.get_by_role("heading", name="Launch a New Bot")).to_be_visible(timeout=timeout)
            expect(page.get_by_role("heading", name="Active Bots")).to_be_visible(timeout=timeout)
            page.screenshot(path="jules-scratch/verification/02_bots_page.png")

            # Navigate to Trade History and verify
            page.locator("text=Trade History").click()
            expect(page.get_by_role("heading", name="Trade History")).to_be_visible(timeout=timeout)
            page.screenshot(path="jules-scratch/verification/03_history_page.png")

            print(f"Screenshots saved successfully.")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_full_dashboard()
