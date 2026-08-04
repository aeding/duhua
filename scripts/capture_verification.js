const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  
  console.log('Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173');
  
  console.log('Clicking Demo Mode button...');
  await page.click('button:has-text("Demo Mode")');
  
  console.log('Waiting for image and overlays to render...');
  await page.waitForTimeout(2000);
  
  console.log('Saving screenshot...');
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/ui_verification.png', fullPage: true });
  
  await browser.close();
  console.log('Screenshot saved successfully!');
})();
