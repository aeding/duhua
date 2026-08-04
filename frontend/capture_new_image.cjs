const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  
  console.log('Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173');
  
  console.log('Selecting Instant Demo 2...');
  await page.selectOption('select', 'demo2');
  
  console.log('Waiting for image render (2s)...');
  await page.waitForTimeout(2000);
  
  console.log('Saving screenshot...');
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/new_image_verification.png', fullPage: true });
  
  await browser.close();
  console.log('Screenshot saved successfully!');
})();
