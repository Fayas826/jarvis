import asyncio
from playwright.async_api import async_playwright

class JarvisWebAgent:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    async def initialize(self, headless=False):
        """Starts the Chrome browser. Headless=False means you can see it working."""
        print("[JARVIS WEB AGENT] Initializing browser core...")
        self.playwright = await async_playwright().start()
        # Launch Chromium (Google Chrome engine)
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        print("[JARVIS WEB AGENT] Browser online and ready for commands.")

    async def navigate(self, url):
        """Commands JARVIS to open a specific website."""
        print(f"[JARVIS WEB AGENT] Navigating to: {url}")
        if not url.startswith("http"):
            url = "https://" + url
        await self.page.goto(url)

    async def extract_text(self):
        """Scrapes the visible text of the page to feed back into JARVIS's brain."""
        print("[JARVIS WEB AGENT] Scanning page contents...")
        return await self.page.evaluate("document.body.innerText")

    async def type_text(self, selector, text):
        """Types text into a search box or input field."""
        print(f"[JARVIS WEB AGENT] Typing '{text}' into {selector}...")
        await self.page.fill(selector, text)

    async def click_element(self, selector):
        """Clicks a button or link on the page."""
        print(f"[JARVIS WEB AGENT] Clicking element: {selector}...")
        await self.page.click(selector)

    async def close(self):
        """Shuts down the browser."""
        print("[JARVIS WEB AGENT] Shutting down browser core.")
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# --- Example Usage (How JARVIS will use this internally) ---
async def _test_agent():
    agent = JarvisWebAgent()
    await agent.initialize(headless=False)
    await agent.navigate("wikipedia.org")
    
    # We will search for Artificial Intelligence instead of printing raw text to avoid Windows Unicode errors
    print("[JARVIS WEB AGENT] Test: Searching Wikipedia for 'Artificial Intelligence'...")
    await agent.type_text("input[name='search']", "Artificial Intelligence")
    await agent.click_element("button[type='submit']")
    
    # Let the user see the result before closing
    await asyncio.sleep(5) 
    await agent.close()
    print("[JARVIS WEB AGENT] Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(_test_agent())
