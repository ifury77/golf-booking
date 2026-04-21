import asyncio
from playwright.async_api import async_playwright
import datetime

async def book_nsrcc_holiday():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # 1. LOGIN
        await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx01Login.aspx")
        await page.fill("#txtUserID", "YH24242")
        await page.fill("#txtPassword", "stefan12")
        await page.click("#btnLogin")
        await page.wait_for_load_state("networkidle")
        
        # 2. WAIT FOR 6:00 PM OPENING ON APRIL 29
        target_date = "01/05/2026 Friday" 
        print(f"Targeting Public Holiday: {target_date}...")
        
        found = False
        for _ in range(60): # Retry for 1 minute
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")
            try:
                await page.select_option("#ddlBookingDate", label=target_date, timeout=1000)
                found = True
                break
            except:
                await asyncio.sleep(1)
        
        if not found:
            print("Holiday date not yet available.")
            return

        # 3. SELECTION
        try:
            await page.click("input[value='Morning']")
            # Select first available morning slot
            await page.click("input[type='radio']")
            await page.click("input[value='Book']")
            
            # Partner Input
            await page.wait_for_selector("#txtPartner1", timeout=5000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # Final Confirmation
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=5000)
            await page.click("#btnConfirm")
            print(f"SUCCESS: Public Holiday booking submitted for {target_date}!")
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc_holiday())
