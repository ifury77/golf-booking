import asyncio
from playwright.async_api import async_playwright
import datetime
import random

async def book_nsrcc():
    async with async_playwright() as p:
        # 1. ADD STEALTH ARGUMENTS
        browser = await p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
        ])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        # Bypasses common bot detection scripts
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        print(f"[{datetime.datetime.now()}] Stealth Snipe Started.")

        login_success = False
        for attempt in range(15):
            try:
                print(f"Login Attempt {attempt + 1}...")
                # Go to page and wait for a natural amount of time
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", 
                               timeout=60000, wait_until="networkidle")
                
                await page.wait_for_selector("#txtUserID", timeout=30000)
                
                # 2. MIMIC HUMAN TYPING (delay between keystrokes)
                await page.type("#txtUserID", "YH24242", delay=random.randint(100, 200))
                await page.type("#txtPassword", "stefan12", delay=random.randint(100, 200))
                
                # 3. RANDOM DELAY BEFORE CLICKING
                await asyncio.sleep(random.uniform(1, 3))
                await page.click("#btnLogin")
                
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=45000)
                print("SUCCESS: Logged in.")
                login_success = True
                break 
            except Exception:
                print(f"Attempt {attempt + 1} failed. Moving mouse and retrying...")
                # Random mouse movement to "wake up" the session
                await page.mouse.move(random.randint(0, 500), random.randint(0, 500))
                await context.clear_cookies()
                await asyncio.sleep(random.uniform(3, 6))

        if not login_success:
            print("CRITICAL: Bot is likely being blocked by the club's firewall.")
            await browser.close()
            return

        # Rest of the script (Date calculation and booking) remains the same...
        # ... [Insert the Date Calculation and Slot Selection from the previous script here] ...
