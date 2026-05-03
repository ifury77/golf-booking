import asyncio
from playwright.async_api import async_playwright
import datetime
import random

async def book_nsrcc():
    async with async_playwright() as p:
        # 1. DISABLE AUTOMATION FLAGS
        # We add arguments to prevent the browser from announcing it is a 'headless' bot
        browser = await p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-infobars',
            '--window-position=0,0',
            '--ignore-certifcate-errors',
            '--ignore-certifcate-errors-spki-list',
        ])
        
        # 2. CREATE A 'HUMAN' CONTEXT
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            locale="en-SG",
            timezone_id="Asia/Singapore"
        )

        # 3. STEALTH SCRIPT INJECTION
        # This script deletes the 'webdriver' property and mimics real browser plugins
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-SG', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)
        
        page = await context.new_page()
        print(f"[{datetime.datetime.now()}] Advanced Stealth Snipe Started.")

        # 4. PERSISTENT LOGIN PHASE (15 Retries)
        login_success = False
        for attempt in range(15):
            try:
                print(f"Login Attempt {attempt + 1}...")
                # Increase timeout to 90s for heavy congestion
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx", 
                               timeout=90000, wait_until="domcontentloaded")
                
                await page.wait_for_selector("#txtUserID", timeout=45000)
                
                # Mimic human typing speeds
                await page.type("#txtUserID", "YH24242", delay=random.randint(120, 250))
                await page.type("#txtPassword", "stefan12", delay=random.randint(120, 250))
                
                # Small pause to look like a human thinking
                await asyncio.sleep(random.uniform(1.5, 3.0))
                await page.click("#btnLogin")
                
                # Confirm redirection
                await page.wait_for_url("**/e_Trx02Availableflight.aspx", timeout=60000)
                print(f"SUCCESS: Logged in on attempt {attempt + 1}!")
                login_success = True
                break 
            except Exception:
                print(f"Attempt {attempt + 1} blocked/stalled. Clearing context and retrying...")
                await context.clear_cookies()
                # Wait longer between retries to avoid IP banning
                await asyncio.sleep(random.uniform(5, 10)) 

        if not login_success:
            print("CRITICAL: Failed to bypass server firewall.")
            await browser.close()
            return

        # 5. DATE CALCULATION
        # Thursday -> Next Saturday = 9 days.
        target_dt = datetime.date.today() + datetime.timedelta(days=9)
        date_str = target_dt.strftime("%d/%m/%Y") 
        print(f"Targeting Play Date: {date_str}")

        # 6. REFRESH LOOP
        found = False
        for i in range(800): 
            try:
                await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx", 
                               timeout=60000, wait_until="domcontentloaded")
                options = await page.locator("#ddlBookingDate option").all_inner_texts()
                match = next((opt for opt in options if date_str in opt), None)
                
                if match:
                    await page.select_option("#ddlBookingDate", label=match)
                    print(f"MATCH FOUND: {match}")
                    found = True
                    break
            except Exception:
                pass
            
            if i % 25 == 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Polling...")
            
            await asyncio.sleep(random.uniform(0.6, 1.2)) 

        if found:
            # Slot Selection Logic
            await page.click("input[value='Morning']", timeout=60000)
            await asyncio.sleep(2)
            
            target_slot = "//tr[contains(., '07:57')]//input[@type='radio']"
            if await page.locator(target_slot).count() > 0:
                await page.click(target_slot)
                print("Target slot selected.")
            else:
                print("Grabbing first available 18-hole morning slot...")
                await page.locator("//tr[not(contains(., '07:01')) and not(contains(., '07:08'))]//input[@type='radio']").first.click()

            await page.click("input[value='Book']")
            # Partners
            await page.wait_for_selector("#txtPartner1", timeout=60000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=60000)
            await page.click("#btnConfirm")
            print("BOOKING SUBMITTED.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
