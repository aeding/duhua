const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  
  console.log('Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173');
  
  console.log('Clicking Instant Demo Mode button...');
  await page.click('button:has-text("Instant Demo Mode")');
  await page.waitForTimeout(2000);
  
  console.log('Hovering over text box to trigger dictionary tooltip...');
  const spans = await page.$$('span[style*="cursor: pointer"]');
  if (spans.length > 5) {
    await spans[5].hover();
    await page.waitForTimeout(1000);
  }
  
  console.log('Saving screenshot...');
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/ui_verification.png', fullPage: true });
  
  await browser.close();
  console.log('Tooltip screenshot saved successfully!');
})();
