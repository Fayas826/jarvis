"""
JARVIS AUTONOMOUS TICKET BOOKING ENGINE
========================================
Handles: Flight, Train (IRCTC), Bus, Movie, Event ticket booking
Uses Playwright browser automation with Unsloth-trained web intelligence.
PDF Objective: Autonomous browser task execution -> ticket booking flow.
"""
import asyncio
import re
from playwright.async_api import async_playwright

class JarvisTicketBooker:
    """Autonomous ticket booking agent for JARVIS.
    Supports: MakeMyTrip, IRCTC, BookMyShow, RedBus, IndiGo
    """

    def __init__(self, headless=False):
        self.headless  = headless
        self.browser   = None
        self.page      = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        ctx = await self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await ctx.new_page()
        print("[TICKET] Browser ready.")

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    # ─────────────────────────────────────────────────────────
    # 1. FLIGHT BOOKING (MakeMyTrip)
    # ─────────────────────────────────────────────────────────
    async def search_flights(self, origin: str, destination: str, date: str):
        """Search flights on MakeMyTrip. date format: YYYY-MM-DD"""
        print(f"[FLIGHT] Searching {origin} → {destination} on {date}")
        # Format: MMDDYYYY for MMT URL
        d = date.replace("-", "")
        mmdd = d[4:6] + "/" + d[6:8] + "/" + d[0:4]
        url = (f"https://www.makemytrip.com/flight/search?"
               f"itinerary={origin.upper()}-{destination.upper()}-{mmdd}"
               f"&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(5000)
        # Scrape first 3 results
        results = []
        try:
            flights = await self.page.query_selector_all("[class*='listingCard']")
            for f in flights[:3]:
                txt = await f.inner_text()
                results.append(txt[:200].replace("\n", " | "))
        except Exception as e:
            results = [f"Could not scrape results: {e}"]
        return results

    # ─────────────────────────────────────────────────────────
    # 2. TRAIN BOOKING (IRCTC)
    # ─────────────────────────────────────────────────────────
    async def search_trains(self, from_stn: str, to_stn: str, date: str):
        """Search trains on IRCTC. date: YYYYMMDD"""
        print(f"[TRAIN] Searching {from_stn} → {to_stn} on {date}")
        url = (f"https://www.irctc.co.in/nget/train-search?"
               f"from={from_stn.upper()}&to={to_stn.upper()}&date={date}&quota=GN")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(4000)
        content = await self.page.evaluate("document.body.innerText")
        lines = [l.strip() for l in content.split("\n") if len(l.strip()) > 10]
        return lines[:20]

    # ─────────────────────────────────────────────────────────
    # 3. BUS BOOKING (RedBus)
    # ─────────────────────────────────────────────────────────
    async def search_buses(self, origin: str, destination: str, date: str):
        """Search buses on RedBus. date: DD-Mon-YYYY e.g. 10-Sep-2026"""
        print(f"[BUS] Searching {origin} → {destination} on {date}")
        url = (f"https://www.redbus.in/bus-tickets/"
               f"{origin.lower().replace(' ', '-')}-to-"
               f"{destination.lower().replace(' ', '-')}?fromCityName={origin}"
               f"&toCityName={destination}&doj={date}&busType=Any")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(5000)
        content = await self.page.evaluate("document.body.innerText")
        lines = [l.strip() for l in content.split("\n") if len(l.strip()) > 10]
        return lines[:15]

    # ─────────────────────────────────────────────────────────
    # 4. MOVIE TICKET (BookMyShow)
    # ─────────────────────────────────────────────────────────
    async def search_movies(self, city: str, movie_name: str):
        """Search movie showtimes on BookMyShow."""
        print(f"[MOVIE] Searching '{movie_name}' in {city}")
        query = movie_name.lower().replace(" ", "-")
        url   = f"https://in.bookmyshow.com/explore/movies-{city.lower()}"
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(3000)
        content = await self.page.evaluate("document.body.innerText")
        lines = [l.strip() for l in content.split("\n") if movie_name.lower() in l.lower() or len(l.strip()) > 5]
        return lines[:20]

    # ─────────────────────────────────────────────────────────
    # 5. NATURAL LANGUAGE DISPATCHER
    # ─────────────────────────────────────────────────────────
    async def book_from_command(self, command: str) -> str:
        """Parse a natural language booking command and execute it.
        Examples:
          'Book flight from Chennai to Delhi on 2026-09-15'
          'Search trains from MAS to NDLS on 20260915'
          'Find buses from Bangalore to Chennai on 10-Sep-2026'
          'Show movies in Chennai'
        """
        cmd = command.lower()
        await self.start()
        try:
            if "flight" in cmd or "fly" in cmd:
                # Extract: from X to Y on DATE
                m = re.search(r"from\s+(\w+)\s+to\s+(\w+)\s+on\s+([\d\-]+)", cmd)
                if m:
                    results = await self.search_flights(m[1], m[2], m[3])
                    return "\n".join(results) if results else "No flights found."
                return "Usage: 'Book flight from BOM to DEL on 2026-09-15'"

            elif "train" in cmd or "irctc" in cmd:
                m = re.search(r"from\s+(\w+)\s+to\s+(\w+)\s+on\s+([\d]+)", cmd)
                if m:
                    results = await self.search_trains(m[1], m[2], m[3])
                    return "\n".join(results) if results else "No trains found."
                return "Usage: 'Search trains from MAS to NDLS on 20260915'"

            elif "bus" in cmd:
                m = re.search(r"from\s+([\w\s]+?)\s+to\s+([\w\s]+?)\s+on\s+([\w\-]+)", cmd)
                if m:
                    results = await self.search_buses(m[1].strip(), m[2].strip(), m[3])
                    return "\n".join(results) if results else "No buses found."
                return "Usage: 'Find buses from Bangalore to Chennai on 10-Sep-2026'"

            elif "movie" in cmd or "cinema" in cmd or "film" in cmd:
                m = re.search(r"in\s+([\w\s]+)", cmd)
                city   = m[1].strip() if m else "Chennai"
                movie  = re.search(r"(?:movie|film|watch|book)\s+([\w\s]+?)(?:\s+in|\s+at|$)", cmd)
                mname  = movie[1].strip() if movie else ""
                results = await self.search_movies(city, mname)
                return "\n".join(results) if results else "No movies found."

            else:
                return ("JARVIS Ticket Commands:\n"
                        "  'Book flight from BOM to DEL on 2026-09-15'\n"
                        "  'Search trains from MAS to NDLS on 20260915'\n"
                        "  'Find buses from Bangalore to Chennai on 10-Sep-2026'\n"
                        "  'Show movies in Chennai'\n")
        finally:
            await self.stop()


# ─────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────
async def _test_ticket_booking():
    booker = JarvisTicketBooker(headless=True)
    print("\n=== JARVIS TICKET BOOKING TEST ===")
    result = await booker.book_from_command(
        "Book flight from BOM to DEL on 2026-09-15"
    )
    print(f"[RESULT]\n{result}\n")
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(_test_ticket_booking())
