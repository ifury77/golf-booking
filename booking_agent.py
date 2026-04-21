import asyncio
from playwright.async_api import async_playwright
import datetime

async def book_nsrcc():
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
        
        # 2. WAIT FOR 6:00 PM OPENING
        # We will loop and refresh the booking page until the Saturday option appears
        target_date = "02/05/2026 Saturday" 
        print(f"Waiting for 6:00 PM opening to book {target_date}...")
        
        found = False
        for _ in range(120): # Try for 2 minutes
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")
            try:
                # Check if the Saturday date is now in the dropdown
                await page.select_option("#ddlBookingDate", label=target_date, timeout=1000)
                found = True
                break
            except:
                await asyncio.sleep(1) # Wait 1 second before refreshing
        
        if not found:
            print("Target date not found after 2 minutes. Ending script.")
            return

        # 3. SELECT SLOT & PARTNERS
        try:
            await page.click("input[value='Morning']", timeout=2000)
            # Find 07:57 radio button
            slot_xpath = "//tr[contains(., '07:57')]//input[@type='radio']"
            await page.wait_for_selector(slot_xpath, timeout=5000)
            await page.click(slot_xpath)
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
            print("SUCCESS: Booking confirmed for 07:57!")
        except Exception as e:
            print(f"Error during selection: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
