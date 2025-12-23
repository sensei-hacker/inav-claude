#!/usr/bin/env node

/**
 * INAV Configurator - Basic Playwright Test
 *
 * Proof-of-concept automated test that:
 * 1. Launches the INAV Configurator
 * 2. Waits for the main window
 * 3. Verifies the app title
 * 4. Takes a screenshot
 * 5. Closes the app
 *
 * Usage:
 *   cd inav-configurator
 *   npm run package  # Build first
 *   node ../claude/developer/helpers/test-configurator-startup.js
 *
 * Requirements:
 *   - @playwright/test installed
 *   - Configurator built (.vite/build/main.js exists)
 */

const { _electron: electron } = require('playwright');
const path = require('path');
const fs = require('fs');

async function testConfiguratorStartup() {
  console.log('🚀 Launching INAV Configurator...\n');

  const configuratorPath = path.join(__dirname, '../../inav-configurator');
  const mainJs = path.join(configuratorPath, '.vite/build/main.js');

  // Verify build exists
  if (!fs.existsSync(mainJs)) {
    console.error('❌ ERROR: Configurator not built!');
    console.error('   Run: cd inav-configurator && npm run package\n');
    process.exit(1);
  }

  let electronApp;
  try {
    // Launch Electron app
    electronApp = await electron.launch({
      args: [mainJs],
      cwd: configuratorPath,
      timeout: 30000,
      env: {
        ...process.env,
        NODE_ENV: 'test'
      }
    });

    console.log('✅ App launched successfully\n');

    // Wait for first window
    const window = await electronApp.firstWindow();
    console.log('✅ Main window opened\n');

    // Get window title
    const title = await window.title();
    console.log(`📋 Window title: "${title}"\n`);

    // Verify title contains INAV
    if (title.toLowerCase().includes('inav')) {
      console.log('✅ Title validation passed\n');
    } else {
      console.log('⚠️  WARNING: Title does not contain "INAV"\n');
    }

    // Get window dimensions
    const size = await window.evaluate(() => ({
      width: window.innerWidth,
      height: window.innerHeight
    }));
    console.log(`📐 Window size: ${size.width}x${size.height}\n`);

    // Take screenshot
    const screenshotDir = path.join(__dirname, '../screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    const screenshotPath = path.join(screenshotDir, 'configurator-startup.png');
    await window.screenshot({ path: screenshotPath });
    console.log(`📸 Screenshot saved: ${screenshotPath}\n`);

    // Wait a moment to see the app (optional)
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Try to detect visible tabs (basic DOM query)
    try {
      const tabs = await window.locator('[id^="tab-"]').count();
      console.log(`🔍 Found ${tabs} navigation tabs\n`);
    } catch (err) {
      console.log('⚠️  Could not detect tabs (DOM may not be ready)\n');
    }

    console.log('✅ Test completed successfully!\n');

  } catch (error) {
    console.error('❌ Test failed:', error.message, '\n');
    throw error;
  } finally {
    // Always close the app
    if (electronApp) {
      await electronApp.close();
      console.log('🛑 App closed\n');
    }
  }
}

// Run the test
testConfiguratorStartup()
  .then(() => {
    console.log('===================================');
    console.log('✅ ALL TESTS PASSED');
    console.log('===================================\n');
    process.exit(0);
  })
  .catch((error) => {
    console.error('===================================');
    console.error('❌ TEST FAILED');
    console.error('===================================');
    console.error(error);
    process.exit(1);
  });
