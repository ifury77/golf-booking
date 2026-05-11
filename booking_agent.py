import asyncio
from playwright.async_api import async_playwright
import datetime
import random
import json
import os
import sys

async def book_nsrcc():
    async with async_playwright() as p:
        print("Launching browser...")
        try:
            # Added 'chromium' specifically for GitHub Actions environment
            browser = await p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ])
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

            # 1. LOAD COOKIES
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)
                print("✅ Successfully loaded session cookies.")
            else:
                print("❌ CRITICAL ERROR: cookies.json not found in root directory!")
                sys.exit(1)

            page = await context.new_page()
            
            # 2. DIRECT ACCESS
            print(f"[{datetime.datetime.now()}] Navigating to booking page...")
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                           timeout=60000, wait_until="domcontentloaded")
            
            # Check if session is actually valid
            if "Trx01Login" in page.url:
                print("❌ SESSION EXPIRED: The cookies in cookies.json are no longer valid. Refresh them!")
                sys.exit(1)
            else:
                print("✅ Session validated. Proceeding.")

            # 3. DATE SETTINGS (Testing for tomorrow)
            target_dt = datetime.date.today() + datetime.timedelta(days=1)
            date_str = target_dt.strftime("%d/%m/%Y") 
            print(f"Targeting Play Date: {date_str}")

            # 4. REFRESH & POLL
            # Shortened loop for testing purposes
            for i in range(5): 
                print(f"Polling attempt {i+1}...")
                await page.reload(wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(1, 2))

            print("Test run completed. Check screenshot in artifacts if needed.")
            await browser.close()

        except Exception as e:
            print(f"❌ AN ERROR OCCURRED: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
