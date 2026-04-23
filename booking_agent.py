import asyncio
from playwright.async_api import async_playwright
import datetime
import random

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[{datetime.datetime.now()}] Snipe Started.")

        # 1. ULTRA-AGGRESSIVE LOGIN PHASE (10 Retries)
        login_success = False
        for attempt in range(10):
            try:
                print(f"Login Attempt {attempt + 1}...")
                # wait_until="domcontentloaded" allows us to interact before the whole page is 'pretty'
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", 
                               timeout=60000, wait_until="domcontentloaded")
                
                await page.wait_for_selector("#txtUserID", timeout=45000)
                await page.fill("#txtUserID", "YH24242")
                await page.fill("#txtPassword", "stefan12")
                await page.click("#btnLogin")
                
                # Check for successful redirection to the booking page
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=60000)
                print(f"Login Successful on attempt {attempt + 1}!")
                login_success = True
                break 
            except Exception as e:
                print(f"Attempt {attempt + 1} stalled/timed out. Clearing cookies and retrying...")
                await context.clear_cookies() # Clear session to try fresh
                await asyncio.sleep(2) 

        if not login_success:
            print("CRITICAL: All login attempts failed. Server is likely unresponsive.")
            await browser.close()
            return

        # 2. DATE CALCULATION (9 Days Ahead for Saturday booking)
        target_dt = datetime.date.today() + datetime.timedelta(days=9)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {target_dt.strftime('%A, %d %B %Y')} ({date_str})")

        # 3. REFRESH LOOP (Wait for release)
        found = False
        booking_url = "https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx"
        
        for i in range(800): 
            try:
                # Use a fast goto to check the dropdown
                await page.goto(booking_url, timeout=45000, wait_until="domcontentloaded")
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"MATCH FOUND: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 20 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pinging server for {date_str}...")
            
            await asyncio.sleep(random.uniform(0.5, 1.0)) 

        if not found:
            print(f"CRITICAL: Target date {date_str} was never released in time.")
            await browser.close()
            return

        # 4. SLOT SELECTION (Excluding 9-hole times 7:01/7:08)
        try:
            # Filter for Morning
            await page.click("input[value='Morning']", timeout=45000)
            await asyncio.sleep(1.5) 

            # Priority 1: Specific 07:57 target
            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            # Priority 2: Any 07xx or 08xx 18-hole slot (skips 7:01 and 7:08)
            fallback_xpath = "//tr[not(contains(., '07:01')) and not(contains(., '07:08')) and (contains(., '07:') or contains(., '08:'))]//input[@type='radio']"

            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target 07:57 AM slot secured.")
            else:
                print("07:57 AM taken. Sniping fallback 18-hole morning slot...")
                await page.locator(fallback_xpath).first.click()

            await page.click("input[value='Book']")
            
            # 5. PARTNER ENTRY
            print("Entering Partner Details...")
            await page.wait_for_selector("#txtPartner1", timeout=45000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # 6. FINAL CONFIRMATION
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=45000)
            await page.click("#btnConfirm")
            
            print(f"SUCCESS: Booking for {date_str} submitted!")
            
        except Exception as e:
            print(f"Error during final stages: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
