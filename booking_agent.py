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

        # 1. LAG-PROOF LOGIN PHASE (With 5 Retries)
        login_success = False
        for attempt in range(5):
            try:
                # Increased timeout to 60s for heavy server load
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", timeout=60000)
                await page.wait_for_selector("#txtUserID", timeout=60000)
                await page.fill("#txtUserID", "YH24242")
                await page.fill("#txtPassword", "stefan12")
                await page.click("#btnLogin")
                
                # Check if we actually got past the login page
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=60000)
                print(f"Login Successful on attempt {attempt + 1}.")
                login_success = True
                break 
            except Exception as e:
                print(f"Login attempt {attempt + 1} timed out or failed. Retrying...")
                await asyncio.sleep(2) 

        if not login_success:
            print("CRITICAL: All login attempts failed due to server timeout.")
            await browser.close()
            return

        # 2. DATE CALCULATION (9 Days Ahead for Saturday booking)
        target_dt = datetime.date.today() + datetime.timedelta(days=9)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {target_dt.strftime('%A, %d %B %Y')} ({date_str})")

        # 3. REFRESH LOOP
        found = False
        booking_url = "https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx"
        
        for i in range(800): # Increased range to cover more time
            try:
                await page.goto(booking_url, timeout=60000)
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"Match Found: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 30 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Waiting for {date_str}...")
            
            await asyncio.sleep(random.uniform(0.6, 1.2)) # Slightly faster polling

        if not found:
            print(f"CRITICAL: Target date {date_str} not released.")
            await browser.close()
            return

        # 4. SLOT SELECTION (Avoiding 9-hole traps)
        try:
            await page.click("input[value='Morning']", timeout=60000)
            await asyncio.sleep(1.5) 

            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            fallback_xpath = "//tr[not(contains(., '07:01')) and not(contains(., '07:08')) and (contains(., '07:') or contains(., '08:'))]//input[@type='radio']"

            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target 07:57 AM slot secured.")
            else:
                print("07:57 AM taken. Sniping first available 18-hole morning slot...")
                await page.locator(fallback_xpath).first.click()

            await page.click("input[value='Book']")
            
            # 5. PARTNER ENTRY
            print("Entering Partner Details...")
            await page.wait_for_selector("#txtPartner1", timeout=60000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # 6. FINAL CONFIRMATION
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=60000)
            await page.click("#btnConfirm")
            
            print(f"SUCCESS: Booking for {date_str} submitted!")
            
        except Exception as e:
            print(f"Error during selection/confirmation: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
