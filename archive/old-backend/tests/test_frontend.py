#!/usr/bin/env python3
"""
Test the actual frontend rendering with Playwright and capture console logs
"""
import asyncio
from playwright.async_api import async_playwright

async def test_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Capture console logs
        page.on("console", lambda msg: print(f"🖥️  CONSOLE: {msg.text}"))
        page.on("pageerror", lambda error: print(f"❌ PAGE ERROR: {error}"))
        
        print("🔍 Testing frontend at http://localhost:3000...")
        
        try:
            await page.goto("http://localhost:3000", wait_until="networkidle")
            await page.screenshot(path="/mnt/c/kiro/frontend_test.png", full_page=True)
            print("📸 Screenshot saved")
            
            # Wait to see console logs
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_frontend())
