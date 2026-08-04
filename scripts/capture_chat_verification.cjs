const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('Capturing UI Chat Verification Screenshots...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1400, height: 950 } });
  const page = await context.newPage();

  try {
    console.log('Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

    // 1. Select Demo 1
    const select = page.locator('select');
    await select.selectOption('demo1');
    await page.waitForTimeout(1000);

    // Click "✨ Translate this page" quick prompt
    const translateBtn = page.locator('button', { hasText: 'Translate this page' });
    if (await translateBtn.isVisible()) {
      console.log('Clicking Translate this page quick prompt...');
      await translateBtn.click();
      // Wait for agent response
      await page.waitForTimeout(14000);
    }

    const screenshot1 = path.join(__dirname, '..', 'screenshots', 'agent_chat_demo1_verification.png');
    await page.screenshot({ path: screenshot1, fullPage: true });
    console.log(`Saved ${screenshot1}`);

  } catch (err) {
    console.error('Error during chat verification:', err);
  } finally {
    await browser.close();
  }
})();
