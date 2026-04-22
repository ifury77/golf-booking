import asyncio
from playwright.async_api import async_playwright
import datetime

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch browser - headless=True is required for GitHub Actions
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Snipe Started.")

        # 1. LOGIN PHASE
        try:
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx")
            await page.fill("#txtUserID", "YH24242")
            await page.fill("#txtPassword", "stefan12")
            await page.click("#btnLogin")
            await page.wait_for_load_state("networkidle")
            print("Login Successful.")
        except Exception as e:
            print(f"Login Failed: {e}")
            await browser.close()
            return

        # 2. DYNAMIC DATE CALCULATION (10 Days Ahead)
        target_dt = datetime.date.today() + datetime.timedelta(days=10)
        date_str = target_dt.strftime("%d/%m/%Y") # Formats as 02/05/2026
        print(f"Targeting Play Date: {target_dt.strftime('%A, %d %B %Y')} ({date_str})")

        # 3. REFRESH LOOP (Wait for 6:00 PM Opening)
        # 720 attempts at 1-second intervals = 12 minutes of patience.
        # This allows the bot to start at 5:50 PM and wait for the 6:00 PM drop.
        found = False
        booking_url = "https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx"
        
        for i in range(720):
            await page.goto(booking_url)
            
            # Get all options in the date dropdown
            try:
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                # Find the option that contains our date string (e.g., "02/05/2026")
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"Match Found and Selected: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 30 == 0: # Print status every 30 seconds
                print(f"Still waiting for {date_str} to be released...")
            
            await asyncio.sleep(1) 

        if not found:
            print(f"CRITICAL: Target date {date_str} was not released within the 12-minute window.")
            await browser.close()
            return

        # 4. SLOT SELECTION
        try:
            # Click Morning filter
            await page.click("input[value='Morning']", timeout=5000)
            
            # Priority 1: Target the 07:57 slot specifically
            slot_xpath = "//tr[contains(., '07:57')]//input[@type='radio']"
            try:
                await page.wait_for_selector(slot_xpath, timeout=3000)
                await page.click(slot_xpath)
                print("Target 07:57 AM slot secured.")
            except:
                # Priority 2: Fallback to the first available morning radio button
                print("07:57 AM taken. Sniping first available morning slot...")
                await page.click("input[type='radio']")

            # Click 'Book' button to move to partner entry
            await page.click("input[value='Book']")
            
            # 5. PARTNER ENTRY
            print("Entering Partner Details...")
            await page.wait_for_selector("#txtPartner1", timeout=10000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # 6. FINAL CONFIRMATION
            # First confirmation step
            await page.click("#btnNext")
            
            # Final "Confirm" button
            await page.wait_for_selector("#btnConfirm", timeout=5000)
            await page.click("#btnConfirm")
            
            print(f"SUCCESS: Booking for {date_str} has been submitted!")
            
        except Exception as e:
            print(f"Error during booking process: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
