import asyncio
from playwright.async_api import async_playwright
import datetime

# --- CONFIGURATION ---
# The Saturday we are targeting is 10 days from the Wednesday booking day.
# ---------------------

async def book_nsrcc():
    async with async_playwright() as p:
        # Launching with a specific viewport to ensure buttons are visible
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Snipe Initialized. Navigating to Login...")
        
        # 1. LOGIN
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx")
        await page.fill("#txtUserID", "YH24242")
        await page.fill("#txtPassword", "stefan12")
        await page.click("#btnLogin")
        await page.wait_for_load_state("networkidle")
        print("Login Successful.")

        # 2. DATE & COURSE SELECTION
        # Direct navigation to the selection page to save time
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")
        
        # Select 'Morning' filter
        try:
            await page.click("input[value='Morning']", timeout=3000)
        except:
            print("Morning filter not found, proceeding with default...")

        # 3. SELECT TARGET SLOT (07:57 at Changi)
        try:
            # This selector finds the row with 07:57 and clicks its radio button
            slot_xpath = "//tr[contains(., '07:57')]//input[@type='radio']"
            await page.wait_for_selector(slot_xpath, timeout=10000)
            await page.click(slot_xpath)
            print("Target slot 07:57 selected.")
            
            # Click 'Next' to move to Partner page
            # Note: The button is often named 'btnNext' or 'Book' depending on the step
            await page.click("#btnNext") 
            
        except Exception as e:
            print(f"CRITICAL: Could not find 07:57. Attempting first available morning slot...")
            try:
                await page.click("input[type='radio']")
                await page.click("#btnNext")
            except:
                print("No slots available at all.")
                return

        # 4. PARTNER INPUT
        print("Filling Partners...")
        await page.wait_for_selector("#txtPartner1", timeout=5000)
        await page.fill("#txtPartner1", "IO06456")
        await page.fill("#txtPartner2", "SC17122")
        await page.fill("#txtPartner3", "SG17515")

        # 5. FINAL AUTOMATIC CONFIRMATION
        # This is the 'Point of No Return'
        print("Finalizing Booking...")
        
        # Click the Book/Confirm button
        # Based on NSRCC portal, the final button is usually 'btnBook' or 'btnConfirm'
        try:
            await page.click("#btnBook") # This clicks the confirmation
            print("BOOKING SUBMITTED SUCCESSFULLY.")
        except:
            await page.click("#btnConfirm")
            print("BOOKING CONFIRMED VIA ALTERNATE BUTTON.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
