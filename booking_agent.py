import asyncio
from playwright.async_api import async_playwright
import datetime
import random

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch with automation bypass
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        # Hide the 'webdriver' property
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        print(f"[{datetime.datetime.now()}] Stealth Snipe Started.")

        # 1. LOGIN PHASE (15 Retries)
        login_success = False
        for attempt in range(15):
            try:
                print(f"Login Attempt {attempt + 1}...")
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", 
                               timeout=60000, wait_until="networkidle")
                
                await page.wait_for_selector("#txtUserID", timeout=30000)
                await page.type("#txtUserID", "YH24242", delay=random.randint(100, 200))
                await page.type("#txtPassword", "stefan12", delay=random.randint(100, 200))
                
                await asyncio.sleep(random.uniform(1, 2))
                await page.click("#btnLogin")
                
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=45000)
                print("SUCCESS: Logged in.")
                login_success = True
                break 
            except Exception:
                print(f"Attempt {attempt + 1} failed. Retrying...")
                await context.clear_cookies()
                await asyncio.sleep(random.uniform(2, 4))

        if not login_success:
            print("CRITICAL: Failed to bypass login filter.")
            await browser.close()
            return

        # 2. DATE CALCULATION (Targeting Sat, May 9th)
        # Since today is May 3rd, +6 days = May 9th. 
        # For a standard Thursday run for the following Sat, use 9.
        target_dt = datetime.date.today() + datetime.timedelta(days=6)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {date_str}")

        # 3. REFRESH LOOP
        found = False
        for i in range(500): 
            try:
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                               timeout=45000, wait_until="domcontentloaded")
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"MATCH FOUND: {match}")
                    found = True
                    break
            except Exception:
                pass
            await asyncio.sleep(random.uniform(0.8, 1.5)) 

        if not found:
            print(f"Finished polling. Date {date_str} not available.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
