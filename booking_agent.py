import asyncio
from playwright.async_api import async_playwright
import datetime
import random
import json
import os
import sys

async def book_nsrcc():
    async with async_playwright() as p:
        print("🚀 Launching NSRCC Sniper for Wednesday Drop...")
        
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

            # 1. LOAD & CLEAN COOKIES
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r') as f:
                    raw_cookies = json.load(f)
                
                formatted_cookies = []
                for cookie in raw_cookies:
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie['path']
                    }
                    if 'secure' in cookie: clean_cookie['secure'] = bool(cookie['secure'])
                    if 'httpOnly' in cookie: clean_cookie['httpOnly'] = bool(cookie['httpOnly'])
                    if 'sameSite' in cookie and cookie['sameSite']:
                        ss_value = str(cookie['sameSite']).capitalize()
                        if ss_value in ['Strict', 'Lax', 'None']:
                            clean_cookie['sameSite'] = ss_value
                    formatted_cookies.append(clean_cookie)
                
                await context.add_cookies(formatted_cookies)
                print("✅ Cookies loaded.")
            else:
                print("❌ ERROR: cookies.json missing!")
                sys.exit(1)

            page = await context.new_page()
            
            # 2. NAVIGATION
            print("Navigating to NSRCC Available Flights...")
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                           timeout=60000, wait_until="domcontentloaded")
            
            if "Trx01Login" in page.url:
                print("❌ SESSION EXPIRED: You MUST update cookies.json on Wednesday morning!")
                sys.exit(1)
            
            # 3. SET TARGET DATE TO 23/05/2026
            # If today is Wednesday (13th), days=10 targets the 23rd.
            target_date = "23/05/2026"
            print(f"🎯 Target Date set to: {target_date}")

            # 4. POLLING LOOP (Wait for 6:00 PM Release)
            found = False
            for i in range(1, 500): # Polls for ~15 minutes
                await page.reload(wait_until="domcontentloaded")
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                
                if any(target_date in opt for opt in options):
                    print(f"🟢 DATE FOUND at attempt {i}!")
                    await page.select_option("#ddlBookingDate", label=[opt for opt in options if target_date in opt][0])
                    found = True
                    break
                
                if i % 10 == 0: print(f"Still polling... (Attempt {i})")
                await asyncio.sleep(random.uniform(0.5, 1.2))

            if found:
                # 5. SELECT SLOT & FILL DETAILS
                await page.click("input[value='Morning']")
                await asyncio.sleep(1)
                
                # Clicks the first available morning radio button
                slots = page.locator("input[type='radio']")
                if await slots.count() > 0:
                    await slots.first.click()
                    await page.click("input[value='Book']")
                    
                    # Fill Partners
                    await page.wait_for_selector("#txtPartner1", timeout=5000)
                    await page.fill("#txtPartner1", "IO06456")
                    await page.fill("#txtPartner2", "SC17122")
                    await page.fill("#txtPartner3", "SG17515")
                    
                    # 6. FINAL CONFIRMATION
                    await page.click("#btnNext")
                    await page.wait_for_selector("#btnConfirm")
                    await page.click("#btnConfirm")
                    print("🏆 BOOKING COMPLETE!")
            
            await browser.close()

        except Exception as e:
            print(f"❌ CRASHED: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
