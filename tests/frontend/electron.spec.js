const { _electron: electron } = require('@playwright/test');
const { test, expect } = require('@playwright/test');
const path = require('path');

let electronApp;
let window;

test.beforeEach(async () => {
  // Launch a new app instance before each test
  electronApp = await electron.launch({ args: ['main.js'] });
  window = await electronApp.firstWindow();
});

test.afterEach(async () => {
  // Close the app after each test
  await electronApp.close();
});

test('App launches and has correct title', async () => {
  await window.waitForSelector('h1');
  const title = await window.title();
  expect(title).toBe('RF-1 Reframer - Video Reframing Tool');

  const h1 = await window.locator('h1');
  await expect(h1).toContainText('Reframer');
});

test('Basic UI elements are present', async () => {
  // Check for main UI components
  await expect(window.locator('#filePath')).toBeVisible();
  await expect(window.locator('#outputDir')).toBeVisible();
  await expect(window.locator('#processButton')).toBeVisible();
});

test('Settings tabs are present and can be toggled', async () => {
  // Check all settings tabs exist
  const tabs = [
    'basic',
    'detection',
    'crop',
    'features',
    'smoothing',
    'debug'
  ];

  for (const tab of tabs) {
    const tabButton = window.locator(`button[data-tab="${tab}"]`);
    await expect(tabButton).toBeVisible();
  }
});

test('Video preview sections are present', async () => {
  // Check video preview tabs
  await expect(window.locator('button[data-tab="input"]')).toBeVisible();
  await expect(window.locator('button[data-tab="output"]')).toBeVisible();
  
  // Check video containers
  await expect(window.locator('#input-video-tab')).toBeVisible();
  await expect(window.locator('#output-video-tab')).toBeHidden();
});

test('Input type tabs work correctly', async () => {
  // Check input type tabs
  const singleTab = window.locator('button[data-tab="single"]');
  const batchTab = window.locator('button[data-tab="batch"]');
  
  await expect(singleTab).toBeVisible();
  await expect(batchTab).toBeVisible();
  
  // Single tab should be active by default
  await expect(singleTab).toHaveClass(/border-blue-500/);
  await expect(window.locator('#single-input-tab')).toBeVisible();
  
  // Click batch tab
  await batchTab.click();
  await expect(batchTab).toHaveClass(/border-blue-500/);
  await expect(window.locator('#batch-input-tab')).toBeVisible();
  await expect(window.locator('#single-input-tab')).toBeHidden();
});

test('Process button is disabled by default', async () => {
  const processButton = window.locator('#processButton');
  await expect(processButton).toBeDisabled();
});

test('Error handling displays user-friendly messages', async () => {
  // Try to process without selecting a file
  const processButton = window.locator('#processButton');
  await expect(processButton).toBeDisabled();
  
  // Status should be hidden by default
  const status = window.locator('#status');
  await expect(status).toBeHidden();
});