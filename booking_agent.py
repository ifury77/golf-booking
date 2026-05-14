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
            browser = await p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ])
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

            # LOAD COOKIES
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
                print("❌ SESSION EXPIRED!")
                sys.exit(1)

            # TARGET DATE - Change this for your next target!
            target_date = "24/05/2026" 
            print(f"🎯 Target Date: {target_date}")

            # POLLING LOOP (High Speed)
            found = False
            for i in range(1, 1500): # Increased attempts for early start
                await page.reload(wait_until="domcontentloaded")
                
                # Fast check for date
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if target_date in opt), None)
                
                if match:
                    print(f"🟢 FOUND AT {datetime.datetime.now().strftime('%H:%M:%S')}!")
                    await page.select_option("#ddlBookingDate", label=match)
                    found = True
                    break
                
                # Rapid-fire polling: Only 0.2 to 0.5 second delay
                await asyncio.sleep(random.uniform(0.2, 0.5))

            if found:
                # SELECT MORNING & SLOT
                await page.click("input[value='Morning']", timeout=5000)
                # Wait for any radio button to appear (the actual slot)
                await page.wait_for_selector("input[type='radio']", timeout=5000)
                
                slots = page.locator("input[type='radio']")
                if await slots.count() > 0:
                    await slots.first.click()
                    await page.click("input[value='Book']")
                    
                    # FILL PARTNERS
                    await page.wait_for_selector("#txtPartner1", timeout=5000)
                    await page.fill("#txtPartner1", "IO06456")
                    await page.fill("#txtPartner2", "SC17122")
                    await page.fill("#txtPartner3", "SG17515")
                    
                    # FINAL CONFIRM
                    await page.click("#btnNext")
                    await page.wait_for_selector("#btnConfirm", timeout=5000)
                    await page.click("#btnConfirm")
                    print("🏆 BOOKING COMPLETE!")
            
            await browser.close()

        except Exception as e:
            print(f"❌ ERROR: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
