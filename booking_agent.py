import asyncio
from playwright.async_api import async_playwright
import datetime
import random

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch browser with a standard user agent to avoid bot detection
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Snipe Started.")

        # 1. PERSISTENT LOGIN PHASE (30 Retries)
        # This addresses the "Server unresponsive" errors seen in image_6ab461.png
        login_success = False
        for attempt in range(30):
            try:
                print(f"Login Attempt {attempt + 1} of 30...")
                # 90s timeout to account for severe site lag at 6:00 PM
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", 
                               timeout=90000, wait_until="domcontentloaded")
                
                await page.wait_for_selector("#txtUserID", timeout=60000)
                await page.fill("#txtUserID", "IO06456")
                await page.fill("#txtPassword", "240877")
                await page.click("#btnLogin")
                
                # Confirm redirection to the booking area
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=60000)
                print(f"SUCCESS: Logged in on attempt {attempt + 1}!")
                login_success = True
                break 
            except Exception:
                print(f"Attempt {attempt + 1} stalled/timed out. Resetting session...")
                await context.clear_cookies() 
                # Random delay to mimic human retry behavior and bypass rate limits
                await asyncio.sleep(random.uniform(2, 5)) 

        if not login_success:
            print("CRITICAL: All 30 login attempts failed. NSRCC server is completely down.")
            await browser.close()
            return

        # 2. DATE CALCULATION
        # Thursday -> Next Saturday = 9 days. 
        # (Change to 10 if running on Thursday for the Sunday 10 days away)
        target_dt = datetime.date.today() + datetime.timedelta(days=9)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {target_dt.strftime('%A, %d %B %Y')} ({date_str})")

        # 3. REFRESH LOOP
        found = False
        booking_url = "https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx"
        
        for i in range(1000): 
            try:
                await page.goto(booking_url, timeout=60000, wait_until="domcontentloaded")
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"DATE RELEASED: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 20 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Polling for date release...")
            
            await asyncio.sleep(random.uniform(0.4, 0.8)) 

        if not found:
            print(f"CRITICAL: {date_str} not released after 1000 pings.")
            await browser.close()
            return

        # 4. SLOT SELECTION
        try:
            await page.click("input[value='Morning']", timeout=60000)
            await asyncio.sleep(1.5) 

            # Priority 1: Your preferred 07:57 slot
            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            # Priority 2: Any 18-hole morning slot (excluding 7:01 and 7:08)
            fallback_xpath = "//tr[not(contains(., '07:01')) and not(contains(., '07:08')) and (contains(., '07:') or contains(., '08:'))]//input[@type='radio']"

            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target 07:57 AM slot selected.")
            else:
                print("07:57 AM unavailable. Grabbing fallback 18-hole slot...")
                await page.locator(fallback_xpath).first.click()

            await page.click("input[value='Book']")
            
            # 5. PARTNER ENTRY
            print("Entering partners...")
            await page.wait_for_selector("#txtPartner1", timeout=60000)
            await page.fill("#txtPartner1", "NK13990")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # 6. FINAL CONFIRMATION
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=60000)
            await page.click("#btnConfirm")
            
            print(f"BOOKING SUCCESSFUL: {date_str} has been submitted!")
            
        except Exception as e:
            print(f"Error during selection/checkout: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
