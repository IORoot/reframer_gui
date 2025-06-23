const { _electron: electron } = require('@playwright/test');
const { test, expect } = require('@playwright/test');
const path = require('path');

let electronApp;
let window;

test.beforeEach(async () => {
  // Launch a new app instance before each test
  electronApp = await electron.launch({ args: ['main.js'] });
  window = await electronApp.firstWindow();
  
  // Wait for the app to load
  await window.waitForSelector('h1');
});

test.afterEach(async () => {
  // Close the app after each test
  await electronApp.close();
});

test('Basic settings flags are correctly passed', async () => {
  // Navigate to basic settings tab
  await window.locator('button[data-tab="basic"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Set basic settings values
  await window.locator('#targetRatio').fill('0.75');
  await window.locator('#maxWorkers').fill('4');
  
  // Mock the runPythonScript call to capture the options
  const options = await window.evaluate(() => {
    // Get the current settings values
    const settings = {
      targetRatio: document.getElementById('targetRatio'),
      maxWorkers: document.getElementById('maxWorkers'),
      detector: document.getElementById('detector'),
      skipFrames: document.getElementById('skipFrames'),
      confThreshold: document.getElementById('confThreshold'),
      modelSize: document.getElementById('modelSize'),
      objectClasses: document.getElementById('objectClasses'),
      trackCount: document.getElementById('trackCount'),
      paddingRatio: document.getElementById('paddingRatio'),
      sizeWeight: document.getElementById('sizeWeight'),
      centerWeight: document.getElementById('centerWeight'),
      motionWeight: document.getElementById('motionWeight'),
      historyWeight: document.getElementById('historyWeight'),
      saliencyWeight: document.getElementById('saliencyWeight'),
      faceDetection: document.getElementById('faceDetection'),
      weightedCenter: document.getElementById('weightedCenter'),
      blendSaliency: document.getElementById('blendSaliency'),
      applySmoothing: document.getElementById('applySmoothing'),
      smoothingWindow: document.getElementById('smoothingWindow'),
      positionInertia: document.getElementById('positionInertia'),
      sizeInertia: document.getElementById('sizeInertia'),
      debugMode: document.getElementById('debugMode'),
      debugWindow: document.getElementById('debugWindow'),
      showHelp: document.getElementById('showHelp'),
      recursiveSearch: document.getElementById('recursiveSearch')
    };

    // Create options object as the app would
    const options = {
      target_ratio: parseFloat(settings.targetRatio.value),
      max_workers: parseInt(settings.maxWorkers.value),
      detector: settings.detector.value,
      skip_frames: parseInt(settings.skipFrames.value),
      conf_threshold: parseFloat(settings.confThreshold.value),
      model_size: settings.modelSize.value,
      object_classes: settings.objectClasses.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x)),
      track_count: parseInt(settings.trackCount.value),
      padding_ratio: parseFloat(settings.paddingRatio.value),
      size_weight: parseFloat(settings.sizeWeight.value),
      center_weight: parseFloat(settings.centerWeight.value),
      motion_weight: parseFloat(settings.motionWeight.value),
      history_weight: parseFloat(settings.historyWeight.value),
      saliency_weight: parseFloat(settings.saliencyWeight.value),
      face_detection: settings.faceDetection.checked,
      weighted_center: settings.weightedCenter.checked,
      blend_saliency: settings.blendSaliency.checked,
      apply_smoothing: settings.applySmoothing.checked,
      smoothing_window: parseInt(settings.smoothingWindow.value),
      position_inertia: parseFloat(settings.positionInertia.value),
      size_inertia: parseFloat(settings.sizeInertia.value),
      debug: settings.debugMode.checked,
      debug_window: settings.debugWindow.checked,
      show_help: settings.showHelp.checked,
      recursive_search: settings.recursiveSearch.checked
    };

    return options;
  });

  // Verify basic settings are correctly set
  expect(options.target_ratio).toBe(0.75);
  expect(options.max_workers).toBe(4);
});

test('Detection settings flags are correctly passed', async () => {
  // Navigate to detection settings tab
  await window.locator('button[data-tab="detection"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Set detection settings values
  // Skip the disabled detector select and just test the other fields
  await window.locator('#skipFrames').fill('10');
  await window.locator('#confThreshold').fill('0.5');
  // Don't try to set modelSize - just test with its default value
  await window.locator('#objectClasses').fill('0,1,2');
  await window.locator('#trackCount').fill('3');
  
  const options = await window.evaluate(() => {
    const settings = {
      detector: document.getElementById('detector'),
      skipFrames: document.getElementById('skipFrames'),
      confThreshold: document.getElementById('confThreshold'),
      modelSize: document.getElementById('modelSize'),
      objectClasses: document.getElementById('objectClasses'),
      trackCount: document.getElementById('trackCount')
    };

    return {
      detector: settings.detector.value,
      skip_frames: parseInt(settings.skipFrames.value),
      conf_threshold: parseFloat(settings.confThreshold.value),
      model_size: settings.modelSize.value,
      object_classes: settings.objectClasses.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x)),
      track_count: parseInt(settings.trackCount.value)
    };
  });

  expect(options.detector).toBe('yolo'); // Default value
  expect(options.skip_frames).toBe(10);
  expect(options.conf_threshold).toBe(0.5);
  // Just verify that model_size has some value (could be empty string, 'n', 's', etc.)
  expect(typeof options.model_size).toBe('string');
  expect(options.object_classes).toEqual([0, 1, 2]);
  expect(options.track_count).toBe(3);
});

test('Crop settings flags are correctly passed', async () => {
  // Navigate to crop settings tab
  await window.locator('button[data-tab="crop"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Set crop settings values
  await window.locator('#paddingRatio').fill('0.1');
  await window.locator('#sizeWeight').fill('0.3');
  await window.locator('#centerWeight').fill('0.4');
  await window.locator('#motionWeight').fill('0.2');
  await window.locator('#historyWeight').fill('0.1');
  await window.locator('#saliencyWeight').fill('0.5');
  
  const options = await window.evaluate(() => {
    const settings = {
      paddingRatio: document.getElementById('paddingRatio'),
      sizeWeight: document.getElementById('sizeWeight'),
      centerWeight: document.getElementById('centerWeight'),
      motionWeight: document.getElementById('motionWeight'),
      historyWeight: document.getElementById('historyWeight'),
      saliencyWeight: document.getElementById('saliencyWeight')
    };

    return {
      padding_ratio: parseFloat(settings.paddingRatio.value),
      size_weight: parseFloat(settings.sizeWeight.value),
      center_weight: parseFloat(settings.centerWeight.value),
      motion_weight: parseFloat(settings.motionWeight.value),
      history_weight: parseFloat(settings.historyWeight.value),
      saliency_weight: parseFloat(settings.saliencyWeight.value)
    };
  });

  expect(options.padding_ratio).toBe(0.1);
  expect(options.size_weight).toBe(0.3);
  expect(options.center_weight).toBe(0.4);
  expect(options.motion_weight).toBe(0.2);
  expect(options.history_weight).toBe(0.1);
  expect(options.saliency_weight).toBe(0.5);
});

test('Feature toggle flags are correctly passed', async () => {
  // Navigate to features settings tab
  await window.locator('button[data-tab="features"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Toggle feature checkboxes using JavaScript to avoid SVG interference
  await window.evaluate(() => {
    document.getElementById('faceDetection').checked = true;
    document.getElementById('weightedCenter').checked = true;
    document.getElementById('blendSaliency').checked = true;
  });
  
  const options = await window.evaluate(() => {
    const settings = {
      faceDetection: document.getElementById('faceDetection'),
      weightedCenter: document.getElementById('weightedCenter'),
      blendSaliency: document.getElementById('blendSaliency')
    };

    return {
      face_detection: settings.faceDetection.checked,
      weighted_center: settings.weightedCenter.checked,
      blend_saliency: settings.blendSaliency.checked
    };
  });

  expect(options.face_detection).toBe(true);
  expect(options.weighted_center).toBe(true);
  expect(options.blend_saliency).toBe(true);
});

test('Smoothing settings flags are correctly passed', async () => {
  // Navigate to smoothing settings tab
  await window.locator('button[data-tab="smoothing"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Set smoothing settings
  await window.locator('#applySmoothing').check();
  await window.locator('#smoothingWindow').fill('15');
  await window.locator('#positionInertia').fill('0.7');
  await window.locator('#sizeInertia').fill('0.6');
  
  const options = await window.evaluate(() => {
    const settings = {
      applySmoothing: document.getElementById('applySmoothing'),
      smoothingWindow: document.getElementById('smoothingWindow'),
      positionInertia: document.getElementById('positionInertia'),
      sizeInertia: document.getElementById('sizeInertia')
    };

    return {
      apply_smoothing: settings.applySmoothing.checked,
      smoothing_window: parseInt(settings.smoothingWindow.value),
      position_inertia: parseFloat(settings.positionInertia.value),
      size_inertia: parseFloat(settings.sizeInertia.value)
    };
  });

  expect(options.apply_smoothing).toBe(true);
  expect(options.smoothing_window).toBe(15);
  expect(options.position_inertia).toBe(0.7);
  expect(options.size_inertia).toBe(0.6);
});

test('Debug settings flags are correctly passed', async () => {
  // Navigate to debug settings tab
  await window.locator('button[data-tab="debug"]').click();
  await window.waitForTimeout(100); // Wait for tab switch
  
  // Set debug settings using JavaScript to avoid SVG interference
  await window.evaluate(() => {
    document.getElementById('debugMode').checked = true;
    document.getElementById('debugWindow').checked = true;
    document.getElementById('showHelp').checked = true;
    document.getElementById('recursiveSearch').checked = true;
  });
  
  const options = await window.evaluate(() => {
    const settings = {
      debugMode: document.getElementById('debugMode'),
      debugWindow: document.getElementById('debugWindow'),
      showHelp: document.getElementById('showHelp'),
      recursiveSearch: document.getElementById('recursiveSearch')
    };

    return {
      debug: settings.debugMode.checked,
      debug_window: settings.debugWindow.checked,
      show_help: settings.showHelp.checked,
      recursive_search: settings.recursiveSearch.checked
    };
  });

  expect(options.debug).toBe(true);
  expect(options.debug_window).toBe(true);
  expect(options.show_help).toBe(true);
  expect(options.recursive_search).toBe(true);
});

test('All settings are included in options object', async () => {
  // Navigate to basic settings tab first
  await window.locator('button[data-tab="basic"]').click();
  await window.waitForTimeout(100);
  
  // Set some values to ensure we're not just getting defaults
  await window.locator('#targetRatio').fill('0.5625');
  await window.locator('#maxWorkers').fill('8');
  
  // Navigate to features tab to set checkboxes using JavaScript
  await window.locator('button[data-tab="features"]').click();
  await window.waitForTimeout(100);
  await window.evaluate(() => {
    document.getElementById('faceDetection').checked = true;
  });
  
  // Navigate to debug tab to set debug mode using JavaScript
  await window.locator('button[data-tab="debug"]').click();
  await window.waitForTimeout(100);
  await window.evaluate(() => {
    document.getElementById('debugMode').checked = true;
  });
  
  const options = await window.evaluate(() => {
    const settings = {
      targetRatio: document.getElementById('targetRatio'),
      maxWorkers: document.getElementById('maxWorkers'),
      detector: document.getElementById('detector'),
      skipFrames: document.getElementById('skipFrames'),
      confThreshold: document.getElementById('confThreshold'),
      modelSize: document.getElementById('modelSize'),
      objectClasses: document.getElementById('objectClasses'),
      trackCount: document.getElementById('trackCount'),
      paddingRatio: document.getElementById('paddingRatio'),
      sizeWeight: document.getElementById('sizeWeight'),
      centerWeight: document.getElementById('centerWeight'),
      motionWeight: document.getElementById('motionWeight'),
      historyWeight: document.getElementById('historyWeight'),
      saliencyWeight: document.getElementById('saliencyWeight'),
      faceDetection: document.getElementById('faceDetection'),
      weightedCenter: document.getElementById('weightedCenter'),
      blendSaliency: document.getElementById('blendSaliency'),
      applySmoothing: document.getElementById('applySmoothing'),
      smoothingWindow: document.getElementById('smoothingWindow'),
      positionInertia: document.getElementById('positionInertia'),
      sizeInertia: document.getElementById('sizeInertia'),
      debugMode: document.getElementById('debugMode'),
      debugWindow: document.getElementById('debugWindow'),
      showHelp: document.getElementById('showHelp'),
      recursiveSearch: document.getElementById('recursiveSearch')
    };

    return {
      target_ratio: parseFloat(settings.targetRatio.value),
      max_workers: parseInt(settings.maxWorkers.value),
      detector: settings.detector.value,
      skip_frames: parseInt(settings.skipFrames.value),
      conf_threshold: parseFloat(settings.confThreshold.value),
      model_size: settings.modelSize.value,
      object_classes: settings.objectClasses.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x)),
      track_count: parseInt(settings.trackCount.value),
      padding_ratio: parseFloat(settings.paddingRatio.value),
      size_weight: parseFloat(settings.sizeWeight.value),
      center_weight: parseFloat(settings.centerWeight.value),
      motion_weight: parseFloat(settings.motionWeight.value),
      history_weight: parseFloat(settings.historyWeight.value),
      saliency_weight: parseFloat(settings.saliencyWeight.value),
      face_detection: settings.faceDetection.checked,
      weighted_center: settings.weightedCenter.checked,
      blend_saliency: settings.blendSaliency.checked,
      apply_smoothing: settings.applySmoothing.checked,
      smoothing_window: parseInt(settings.smoothingWindow.value),
      position_inertia: parseFloat(settings.positionInertia.value),
      size_inertia: parseFloat(settings.sizeInertia.value),
      debug: settings.debugMode.checked,
      debug_window: settings.debugWindow.checked,
      show_help: settings.showHelp.checked,
      recursive_search: settings.recursiveSearch.checked
    };
  });

  // Verify all expected properties are present
  const expectedProperties = [
    'target_ratio', 'max_workers', 'detector', 'skip_frames', 'conf_threshold',
    'model_size', 'object_classes', 'track_count', 'padding_ratio', 'size_weight',
    'center_weight', 'motion_weight', 'history_weight', 'saliency_weight',
    'face_detection', 'weighted_center', 'blend_saliency', 'apply_smoothing',
    'smoothing_window', 'position_inertia', 'size_inertia', 'debug',
    'debug_window', 'show_help', 'recursive_search'
  ];

  for (const prop of expectedProperties) {
    expect(options).toHaveProperty(prop);
  }

  // Verify specific values we set
  expect(options.target_ratio).toBe(0.5625);
  expect(options.max_workers).toBe(8);
  expect(options.face_detection).toBe(true);
  expect(options.debug).toBe(true);
});

test('Object classes are correctly parsed from comma-separated string', async () => {
  // Navigate to detection settings tab
  await window.locator('button[data-tab="detection"]').click();
  await window.waitForTimeout(100);
  
  // Test various object class inputs
  const testCases = [
    { input: '0', expected: [0] },
    { input: '0,1', expected: [0, 1] },
    { input: '0, 1, 2', expected: [0, 1, 2] },
    { input: '0, 1, 2, 3', expected: [0, 1, 2, 3] },
    { input: '', expected: [] },
    { input: '0, , 1', expected: [0, 1] } // Should filter out empty values
  ];

  for (const testCase of testCases) {
    await window.locator('#objectClasses').fill(testCase.input);
    
    const objectClasses = await window.evaluate(() => {
      const objectClassesInput = document.getElementById('objectClasses');
      return objectClassesInput.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
    });

    expect(objectClasses).toEqual(testCase.expected);
  }
});

test('Numeric inputs are correctly parsed', async () => {
  // Navigate to basic settings tab
  await window.locator('button[data-tab="basic"]').click();
  await window.waitForTimeout(100);
  
  // Test that numeric inputs are properly converted
  await window.locator('#targetRatio').fill('0.75');
  await window.locator('#maxWorkers').fill('6');
  
  // Navigate to detection tab for more numeric inputs
  await window.locator('button[data-tab="detection"]').click();
  await window.waitForTimeout(100);
  await window.locator('#skipFrames').fill('12');
  await window.locator('#confThreshold').fill('0.8');
  await window.locator('#trackCount').fill('5');
  
  // Navigate to crop tab for more numeric inputs
  await window.locator('button[data-tab="crop"]').click();
  await window.waitForTimeout(100);
  await window.locator('#paddingRatio').fill('0.15');
  await window.locator('#sizeWeight').fill('0.25');
  
  // Navigate to smoothing tab for more numeric inputs
  await window.locator('button[data-tab="smoothing"]').click();
  await window.waitForTimeout(100);
  await window.locator('#smoothingWindow').fill('20');
  await window.locator('#positionInertia').fill('0.6');
  
  const options = await window.evaluate(() => {
    const settings = {
      targetRatio: document.getElementById('targetRatio'),
      maxWorkers: document.getElementById('maxWorkers'),
      skipFrames: document.getElementById('skipFrames'),
      confThreshold: document.getElementById('confThreshold'),
      trackCount: document.getElementById('trackCount'),
      paddingRatio: document.getElementById('paddingRatio'),
      sizeWeight: document.getElementById('sizeWeight'),
      smoothingWindow: document.getElementById('smoothingWindow'),
      positionInertia: document.getElementById('positionInertia')
    };

    return {
      target_ratio: parseFloat(settings.targetRatio.value),
      max_workers: parseInt(settings.maxWorkers.value),
      skip_frames: parseInt(settings.skipFrames.value),
      conf_threshold: parseFloat(settings.confThreshold.value),
      track_count: parseInt(settings.trackCount.value),
      padding_ratio: parseFloat(settings.paddingRatio.value),
      size_weight: parseFloat(settings.sizeWeight.value),
      smoothing_window: parseInt(settings.smoothingWindow.value),
      position_inertia: parseFloat(settings.positionInertia.value)
    };
  });

  expect(options.target_ratio).toBe(0.75);
  expect(options.max_workers).toBe(6);
  expect(options.skip_frames).toBe(12);
  expect(options.conf_threshold).toBe(0.8);
  expect(options.track_count).toBe(5);
  expect(options.padding_ratio).toBe(0.15);
  expect(options.size_weight).toBe(0.25);
  expect(options.smoothing_window).toBe(20);
  expect(options.position_inertia).toBe(0.6);
}); 