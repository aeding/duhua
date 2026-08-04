const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  
  console.log('Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173');
  
  // Test Demo 1
  console.log('Selecting Demo 1...');
  await page.selectOption('select', 'demo1');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/demo1_verification.png', fullPage: true });
  console.log('Saved demo1_verification.png');

  // Test Demo 2
  console.log('Selecting Demo 2...');
  await page.selectOption('select', 'demo2');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/home/admin_/duhua/screenshots/demo2_verification.png', fullPage: true });
  console.log('Saved demo2_verification.png');

  await browser.close();
})();
