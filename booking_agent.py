import asyncio
from playwright.async_api import async_playwright
import datetime
import random
import json
import os
import sys

async def book_nsrcc():
    async with async_playwright() as p:
        print("🚀 Launching NSRCC Sniper...")
        
        try:
            # Launch Chromium with stealth settings
            browser = await p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ])
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

            # 1. LOAD & CLEAN COOKIES
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r') as f:
                    raw_cookies = json.load(f)
                
                # Filter cookies for Playwright compatibility
                formatted_cookies = []
                for cookie in raw_cookies:
                    # Only keep fields Playwright understands
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie['path']
                    }
                    if 'secure' in cookie: clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie: clean_cookie['httpOnly'] = cookie['httpOnly']
                    if 'sameSite' in cookie: clean_cookie['sameSite'] = cookie['sameSite']
                    formatted_cookies.append(clean_cookie)
                
                await context.add_cookies(formatted_cookies)
                print("✅ Cookies cleaned and loaded.")
            else:
                print("❌ ERROR: cookies.json not found!")
                sys.exit(1)

            page = await context.new_page()
            
            # 2. NAVIGATION
            print("Navigating to NSRCC...")
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                           timeout=60000, wait_until="domcontentloaded")
            
            if "Trx01Login" in page.url:
                print("❌ SESSION EXPIRED: Update your cookies.json!")
                sys.exit(1)
            else:
                print("✅ Login Bypassed Successfully.")

            # 3. DATE TARGETING (Testing for tomorrow)
            target_dt = datetime.date.today() + datetime.timedelta(days=1)
            date_str = target_dt.strftime("%d/%m/%Y") 
            print(f"🎯 Target Date: {date_str}")

            # 4. REFRESH LOOP
            for i in range(1, 4):
                print(f"Attempt {i}: Checking availability...")
                await page.reload(wait_until="domcontentloaded")
                await asyncio.sleep(2)

            print("🏁 Test run finished.")
            await browser.close()

        except Exception as e:
            print(f"❌ CRASHED: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
