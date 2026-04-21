import asyncio
from playwright.async_api import async_playwright
import datetime

async def book_nsrcc():
    async with async_playwright() as p:
        # Launch browser
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
        
        # 2. CALCULATE TARGET (10 Days Ahead)
        target_dt = datetime.date.today() + datetime.timedelta(days=10)
        date_str = target_dt.strftime("%d/%m/%Y") # e.g. 01/05/2026
        print(f"Opening window for: {target_dt.strftime('%A, %d %B')} ({date_str})")
        
        # 3. REFRESH LOOP (Starts at 5:58 PM, waits for 6:00 PM)
        found = False
        for _ in range(120): # Try for 2 minutes
            await page.goto("https://myresort.nsrcc.com.sg/NsrccGolfProject/eGolf/e_Trx02Availableflight.aspx")
            
            # Look for the date string in the dropdown options
            options = await page.locator("#ddlBookingDate option").all_inner_texts()
            match = next((opt for opt in options if date_str in opt), None)
            
            if match:
                await page.select_option("#ddlBookingDate", label=match)
                print(f"Selected Date: {match}")
                found = True
                break
            else:
                await asyncio.sleep(1) # Refresh every second
        
        if not found:
            print("Target date not visible yet.")
            return

        # 4. SLOT & PARTNERS
        try:
            await page.click("input[value='Morning']", timeout=3000)
            
            # Target 07:57 or Fallback
            slot_xpath = "//tr[contains(., '07:57')]//input[@type='radio']"
            try:
                await page.wait_for_selector(slot_xpath, timeout=3000)
                await page.click(slot_xpath)
                print("Secured 07:57.")
            except:
                print("07:57 taken, grabbing first morning slot.")
                await page.click("input[type='radio']")

            await page.click("input[value='Book']")
            
            # Partners
            await page.wait_for_selector("#txtPartner1", timeout=5000)
            await page.fill("#txtPartner1", "IO06456")
            await page.fill("#txtPartner2", "SC17122")
            await page.fill("#txtPartner3", "SG17515")
            
            # Final Confirmation
            await page.click("#btnNext")
            await page.wait_for_selector("#btnConfirm", timeout=5000)
            await page.click("#btnConfirm")
            print("SUCCESS: BOOKING COMPLETE.")
            
        except Exception as e:
            print(f"Error during selection: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(book_nsrcc())
