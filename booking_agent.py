import asyncio
from playwright.async_api import async_playwright
import datetime
import random

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

        # 2. DYNAMIC DATE CALCULATION (9 Days Ahead for Saturday booking)
        target_dt = datetime.date.today() + datetime.timedelta(days=9)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {target_dt.strftime('%A, %d %B %Y')} ({date_str})")

        # 3. REFRESH LOOP (Wait for 6:00 PM Opening)
        # 720 attempts = 12 minutes. Bot starts at 5:50 PM and waits for 6:00 PM.
        found = False
        booking_url = "https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx"
        
        for i in range(720):
            await page.goto(booking_url)
            
            try:
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"Match Found and Selected: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 30 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Still waiting for {date_str}...")
            
            # Use a slightly randomized sleep to look more human
            await asyncio.sleep(random.uniform(0.8, 1.5)) 

        if not found:
            print(f"CRITICAL: Target date {date_str} not released.")
            await browser.close()
            return

        # 4. SLOT SELECTION (Avoiding 9-hole traps)
        try:
            # Click Morning filter
            await page.click("input[value='Morning']", timeout=5000)
            await asyncio.sleep(1) # Wait for UI to filter

            # Priority 1: Target the 07:57 slot specifically
            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            
            # Priority 2: Any 18-hole slot (skipping 7:01 and 7:08)
            fallback_xpath = "//tr[not(contains(., '07:01')) and not(contains(., '07:08')) and (contains(., '07:') or contains(., '08:'))]//input[@type='radio']"

            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target 07:57 AM slot secured.")
            else:
                print("07:57 AM taken. Searching for 18-hole fallback...")
                await page.locator(fallback_xpath).first.click()
                print("Fallback 18-hole slot selected.")

            # Click 'Book' button
            await page.click("input[value='Book']")
            
            # 5. PARTNER ENTRY
            print("Entering Partner Details...")
            await page.wait_for_selector("#txtPartner1", timeout=10000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # 6. FINAL CONFIRMATION
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=5000)
            await page.click("#btnConfirm")
            
            print(f"SUCCESS: Booking for {date_str} has been submitted!")
            
        except Exception as e:
            print(f"Error during booking process: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
