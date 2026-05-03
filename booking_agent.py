import asyncio
from playwright.async_api import async_playwright
import datetime
import random
import json
import os

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch with stealth settings to bypass detection on the booking page
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # 1. LOAD PERSISTENT COOKIES
        # This allows the bot to inherit your manual login session
        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)
            print("Successfully loaded session cookies. Skipping login page...")
        else:
            print("CRITICAL: cookies.json not found! Ensure you have uploaded the file.")
            await browser.close()
            return

        page = await context.new_page()
        
        # 2. DIRECT ACCESS TO BOOKING PAGE
        # By bypassing the login URL, we avoid the most aggressive bot filters
        try:
            print(f"[{datetime.datetime.now()}] Snipe Started (Direct Access).")
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                           timeout=60000, wait_until="domcontentloaded")
            
            # Check if session is actually valid
            if "Trx01Login" in page.url:
                print("SESSION EXPIRED: The cookies in cookies.json are no longer valid. Re-export them!")
                await browser.close()
                return
            else:
                print("Session validated. Proceeding to date selection.")
        except Exception as e:
            print(f"Error accessing booking page: {e}")
            await browser.close()
            return

        # 3. DATE CALCULATION
        # Logic: Current Date + 6 days targets next Saturday (May 9th) from today (May 3rd).
        target_dt = datetime.date.today() + datetime.timedelta(days=6)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {date_str}")

        # 4. REFRESH LOOP
        found = False
        for i in range(1000): 
            try:
                # Reload specifically the booking table page
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                               timeout=60000, wait_until="domcontentloaded")
                
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"DATE RELEASED: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 25 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Polling for {date_str}...")
            
            # Small random wait to avoid being flagged for rhythmic refreshing
            await asyncio.sleep(random.uniform(1.0, 2.0)) 

        if not found:
            print(f"Finished polling. Date {date_str} was not detected.")
            await browser.close()
            return

        # 5. SLOT SELECTION AND PARTNER ENTRY
        try:
            # Refresh slots for the selected date
            await page.click("input[value='Morning']", timeout=60000)
            await asyncio.sleep(1.5)

            # Preference: 07:57 AM, fallback to first available 18-hole slot
            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target 07:57 AM slot selected.")
            else:
                print("07:57 AM unavailable. Grabbing fallback morning slot...")
                await page.locator("//tr[not(contains(., '07:01')) and not(contains(., '07:08'))]//input[@type='radio']").first.click()

            await page.click("input[value='Book']")
            
            # Fill partners
            await page.wait_for_selector("#txtPartner1", timeout=60000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # Confirm booking
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=60000)
            await page.click("#btnConfirm")
            
            print(f"BOOKING SUCCESSFUL for {date_str}!")
            
        except Exception as e:
            print(f"Error during slot selection: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
