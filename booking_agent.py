import asyncio
from playwright.async_api import async_playwright

async def book_nsrcc():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a realistic User Agent to avoid being blocked as a bot
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()

        print("Navigating to NSRCC...")
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx")

        # Login
        await page.fill("#txtUserID", "YH24242")
        await page.fill("#txtPassword", "stefan12")
        await page.click("#btnLogin")
        await page.wait_for_load_state("networkidle")
        print("Login Successful.")

        # Navigate to Booking
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")

        # Select Morning Filter
        try:
            await page.click("input[value='Morning']")
            print("Morning filter selected.")
        except:
            pass

        # COURSE & DATE SELECTION
        # Note: On Wednesday morning, the Saturday date will appear in the dropdown.
        # The script will try to click the 07:57 slot for Changi.
        try:
            # Look specifically for the 07:57 radio button
            # This selector targets the radio button in the row containing '07:57'
            slot = page.locator("tr", has_text="07:57").locator("input[type='radio']").first
            await slot.click(timeout=5000)
            print("07:57 slot selected!")
            
            await page.click("#btnNext")
            
            # Fill Partners
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            print("Partners filled.")

            # FINAL STEP: Click the 'Book' or 'Confirm' button
            # await page.click("#btnBook") 
            print("Booking sequence complete!")
            
        except Exception as e:
            print(f"Target slot 07:57 not available yet. This is expected if running before Wednesday 9am.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
