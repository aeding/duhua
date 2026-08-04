const { chromium } = require('playwright');
const assert = require('assert');

(async () => {
  console.log('Starting Playwright OCR Alignment Regression Test...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  try {
    console.log('Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

    // 1. Test Demo 1 Selection
    const select = await page.locator('select');
    await select.selectOption('demo1');
    await page.waitForTimeout(1000);

    // Verify image element
    const img = page.locator('img[alt="Manhua"]');
    await img.waitFor({ state: 'visible' });

    // Verify bounding box overlays are rendered
    const boxes = page.locator('div[style*="position: absolute"][style*="border: 1.5px solid"]');
    const boxCount = await boxes.count();
    console.log(`Demo 1 rendered ${boxCount} bounding box overlays.`);
    assert(boxCount > 0, 'Demo 1 should render at least 1 bounding box');

    // Check style percentage attributes on bounding boxes
    for (let i = 0; i < Math.min(boxCount, 10); i++) {
      const style = await boxes.nth(i).getAttribute('style');
      assert(style.includes('%'), `Box ${i} style should use percentage positioning: ${style}`);
      
      // Parse left, top, width, height percentages
      const leftMatch = style.match(/left:\s*([\d.]+)%/);
      const topMatch = style.match(/top:\s*([\d.]+)%/);
      const widthMatch = style.match(/width:\s*([\d.]+)%/);
      const heightMatch = style.match(/height:\s*([\d.]+)%/);

      assert(leftMatch, `Box ${i} missing left percentage`);
      assert(topMatch, `Box ${i} missing top percentage`);
      assert(widthMatch, `Box ${i} missing width percentage`);
      assert(heightMatch, `Box ${i} missing height percentage`);

      const left = parseFloat(leftMatch[1]);
      const top = parseFloat(topMatch[1]);
      const width = parseFloat(widthMatch[1]);
      const height = parseFloat(heightMatch[1]);

      assert(left >= 0 && left <= 100, `Box ${i} left % out of bounds: ${left}`);
      assert(top >= 0 && top <= 100, `Box ${i} top % out of bounds: ${top}`);
      assert(width > 0 && width <= 100, `Box ${i} width % invalid: ${width}`);
      assert(height > 0 && height <= 100, `Box ${i} height % invalid: ${height}`);
      assert(left + width <= 100.1, `Box ${i} overflows right boundary: ${left + width}%`);
      assert(top + height <= 100.1, `Box ${i} overflows bottom boundary: ${top + height}%`);
    }

    // 2. Test Demo 2 Selection
    await select.selectOption('demo2');
    await page.waitForTimeout(1000);

    const demo2BoxCount = await boxes.count();
    console.log(`Demo 2 rendered ${demo2BoxCount} bounding box overlays.`);
    assert(demo2BoxCount > 0, 'Demo 2 should render at least 1 bounding box');

    console.log('✅ OCR Alignment Regression Test Passed Successfully!');
  } catch (err) {
    console.error('❌ Test Failed:', err);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
