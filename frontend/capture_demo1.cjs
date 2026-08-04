const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  
  console.log('Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173');
  
  console.log('Selecting Instant Demo 1...');
  await page.selectOption('select', 'demo1');
  
  console.log('Waiting for image render (2s)...');
  await page.waitForTimeout(2000);
  
  console.log('Saving screenshot...');
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/demo1_verification.png', fullPage: true });
  
  await browser.close();
  console.log('Screenshot saved successfully!');
})();
