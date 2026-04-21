import asyncio
from playwright.async_api import async_playwright
import datetime

async def book_nsrcc():
    async with async_playwright() as p:
        # We run 'headless' in the cloud
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Navigating to Login...")
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx")

        # Handle potential session expiry screen
        if await page.query_selector("text='Session has expired'"):
            print("Refreshing expired session...")
            await page.reload()

        # Login
        await page.fill("#txtUserID", "YH24242")
        await page.fill("#txtPassword", "stefan12")
        await page.click("#btnLogin")
        await page.wait_for_load_state("networkidle")

        # Navigate to Booking Page
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")

        # 1. Select the date (Logic for 10 days out)
        # 2. Select 'Changi'
        # 3. Look for '07:57'
        try:
            # Click the 07:57 radio button specifically for 1st Tee Changi
            # This uses a specific selector for the time slot in your screenshot
            await page.click("//tr[contains(., '07:57')]//input[@type='radio']")
            await page.click("#btnNext")
            
            # Fill Partners
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # Final Confirm (Uncomment the line below when you are ready for real booking)
            # await page.click("#btnConfirm")
            print("Booking form filled successfully!")
        except Exception as e:
            print(f"Target slot 07:57 not found or already taken: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
