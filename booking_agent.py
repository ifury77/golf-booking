import asyncio
from playwright.async_api import async_playwright
import datetime
import random
import json
import os
import sys

async def book_nsrcc():
    async with async_playwright() as p:
        print("🚀 Launching AGGRESSIVE NSRCC Sniper...")
        
        try:
            # 1. BROWSER SETUP
            browser = await p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ])
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

            # 2. LOAD COOKIES
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r') as f:
                    raw_cookies = json.load(f)
                formatted_cookies = []
                for cookie in raw_cookies:
                    clean_cookie = {'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain'], 'path': cookie['path']}
                    if 'secure' in cookie: clean_cookie['secure'] = bool(cookie['secure'])
                    if 'httpOnly' in cookie: clean_cookie['httpOnly'] = bool(cookie['httpOnly'])
                    if 'sameSite' in cookie and cookie['sameSite']:
                        ss_value = str(cookie['sameSite']).capitalize()
                        if ss_value in ['Strict', 'Lax', 'None']: clean_cookie['sameSite'] = ss_value
                    formatted_cookies.append(clean_cookie)
                await context.add_cookies(formatted_cookies)
                print("✅ Cookies loaded.")
            else:
                print("❌ ERROR: cookies.json missing!")
                sys.exit(1)

            page = await context.new_page()
            
            print("Navigating to booking page...")
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", timeout=60000)
            
            if "Trx01Login" in page.url:
                print("❌ SESSION EXPIRED! Refresh cookies.json now.")
                sys.exit(1)
            else:
                print("✅ Login Bypassed Successfully.")

            # 3. TARGET DATE FOR MAY 30th
            target_date = "30/05/2026" 
            print(f"🎯 Target Date: {target_date}")

            # 4. AGGRESSIVE POLLING LOOP
            found = False
            # 2000 attempts at ~0.5s each covers about 15-20 minutes
            for i in range(1, 2000): 
                await page.reload(wait_until="domcontentloaded")
                
                # Fast check for date in dropdown
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if target_date in opt), None)
                
                if match:
                    print(f"🟢 DATE RELEASED: {match} (Found at Attempt {i})")
                    await page.select_option("#ddlBookingDate", label=match)
                    found = True
                    break
                
                if i % 50 == 0:
                    print(f"Still polling... (Attempt {i})")
                
                # Rapid polling delay (0.3s to 0.6s)
                await asyncio.sleep(random.uniform(0.3, 0.6))

            if found:
                # 5. SELECT MORNING
                print("Checking for Morning slots...")
                await page.click("input[value='Morning']", timeout=10000)
                
                # Wait for any slot (radio button) to appear
                try:
                    await page.wait_for_selector("input[type='radio']", timeout=8000)
                    slots = page.locator("input[type='radio']")
                    
                    if await slots.count() > 0:
                        await slots.first.click()
                        print("✅ Slot selected.")
                        await page.click("input[value='Book']")
                        
                        # 6. FILL PARTNERS
                        print("Filling partner details...")
                        await page.wait_for_selector("#txtPartner1", timeout=10000)
                        await page.fill("#txtPartner1", "IO06456")
                        await page.fill("#txtPartner2", "SC17122")
                        await page.fill("#txtPartner3", "SG17515")
                        
                        # 7. FINAL CONFIRMATION
                        print("🚀 Submitting final booking...")
                        await page.click("#btnNext")
                        await page.wait_for_selector("#btnConfirm", timeout=10000)
                        await page.click("#btnConfirm")
                        print("🏆 SUCCESS: Booking confirmed for May 30th!")
                    else:
                        print("⚠️ Date found, but no morning slots available.")
                except:
                    print("⚠️ Timeout waiting for slot table. Server might be lagging.")
            
            await browser.close()

        except Exception as e:
            print(f"❌ CRASHED: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
