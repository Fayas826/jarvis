const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    page.on('requestfailed', request =>
      console.log('REQUEST FAILED:', request.url(), request.failure().errorText)
    );

    console.log("Navigating to localhost:5173...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // Check if the RED SCREEN is there
    const bodyHtml = await page.evaluate(() => document.body.innerHTML);
    if (bodyHtml.includes("REACT CRITICAL ERROR")) {
       console.log("FOUND REACT ERROR ON PAGE!");
       const errorText = await page.evaluate(() => document.body.innerText);
       console.log(errorText);
    } else {
       console.log("NO REACT ERROR FOUND. Body HTML snippet:");
       console.log(bodyHtml.substring(0, 500));
    }
    
    await browser.close();
  } catch (err) {
    console.error("PUPPETEER SCRIPT ERROR:", err);
  }
})();
