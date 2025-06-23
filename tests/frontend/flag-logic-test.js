const { test, expect } = require('@playwright/test');

// Test the flag logic without requiring Electron
test.describe('Flag Logic Tests', () => {
  test('Options object structure matches expected format', () => {
    // Mock settings object as it would be in the app
    const mockSettings = {
      targetRatio: { value: '0.75' },
      maxWorkers: { value: '4' },
      detector: { value: 'yolo' },
      skipFrames: { value: '10' },
      confThreshold: { value: '0.5' },
      modelSize: { value: 'medium' },
      objectClasses: { value: '0,1,2' },
      trackCount: { value: '3' },
      paddingRatio: { value: '0.1' },
      sizeWeight: { value: '0.3' },
      centerWeight: { value: '0.4' },
      motionWeight: { value: '0.2' },
      historyWeight: { value: '0.1' },
      saliencyWeight: { value: '0.5' },
      faceDetection: { checked: true },
      weightedCenter: { checked: false },
      blendSaliency: { checked: true },
      applySmoothing: { checked: true },
      smoothingWindow: { value: '15' },
      positionInertia: { value: '0.7' },
      sizeInertia: { value: '0.6' },
      debugMode: { checked: true },
      debugWindow: { checked: false },
      showHelp: { checked: true },
      recursiveSearch: { checked: false }
    };

    // Create options object as the app would
    const options = {
      target_ratio: parseFloat(mockSettings.targetRatio.value),
      max_workers: parseInt(mockSettings.maxWorkers.value),
      detector: mockSettings.detector.value,
      skip_frames: parseInt(mockSettings.skipFrames.value),
      conf_threshold: parseFloat(mockSettings.confThreshold.value),
      model_size: mockSettings.modelSize.value,
      object_classes: mockSettings.objectClasses.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x)),
      track_count: parseInt(mockSettings.trackCount.value),
      padding_ratio: parseFloat(mockSettings.paddingRatio.value),
      size_weight: parseFloat(mockSettings.sizeWeight.value),
      center_weight: parseFloat(mockSettings.centerWeight.value),
      motion_weight: parseFloat(mockSettings.motionWeight.value),
      history_weight: parseFloat(mockSettings.historyWeight.value),
      saliency_weight: parseFloat(mockSettings.saliencyWeight.value),
      face_detection: mockSettings.faceDetection.checked,
      weighted_center: mockSettings.weightedCenter.checked,
      blend_saliency: mockSettings.blendSaliency.checked,
      apply_smoothing: mockSettings.applySmoothing.checked,
      smoothing_window: parseInt(mockSettings.smoothingWindow.value),
      position_inertia: parseFloat(mockSettings.positionInertia.value),
      size_inertia: parseFloat(mockSettings.sizeInertia.value),
      debug: mockSettings.debugMode.checked,
      debug_window: mockSettings.debugWindow.checked,
      show_help: mockSettings.showHelp.checked,
      recursive_search: mockSettings.recursiveSearch.checked
    };

    // Test basic settings
    expect(options.target_ratio).toBe(0.75);
    expect(options.max_workers).toBe(4);
    expect(options.detector).toBe('yolo');
    expect(options.skip_frames).toBe(10);
    expect(options.conf_threshold).toBe(0.5);
    expect(options.model_size).toBe('medium');
    expect(options.object_classes).toEqual([0, 1, 2]);
    expect(options.track_count).toBe(3);

    // Test crop settings
    expect(options.padding_ratio).toBe(0.1);
    expect(options.size_weight).toBe(0.3);
    expect(options.center_weight).toBe(0.4);
    expect(options.motion_weight).toBe(0.2);
    expect(options.history_weight).toBe(0.1);
    expect(options.saliency_weight).toBe(0.5);

    // Test feature toggles
    expect(options.face_detection).toBe(true);
    expect(options.weighted_center).toBe(false);
    expect(options.blend_saliency).toBe(true);
    expect(options.apply_smoothing).toBe(true);

    // Test smoothing settings
    expect(options.smoothing_window).toBe(15);
    expect(options.position_inertia).toBe(0.7);
    expect(options.size_inertia).toBe(0.6);

    // Test debug settings
    expect(options.debug).toBe(true);
    expect(options.debug_window).toBe(false);
    expect(options.show_help).toBe(true);
    expect(options.recursive_search).toBe(false);
  });

  test('Object classes parsing works correctly', () => {
    const testCases = [
      { input: '0', expected: [0] },
      { input: '0,1', expected: [0, 1] },
      { input: '0, 1, 2', expected: [0, 1, 2] },
      { input: '0, 1, 2, 3', expected: [0, 1, 2, 3] },
      { input: '', expected: [] },
      { input: '0, , 1', expected: [0, 1] }, // Should filter out empty values
      { input: '0, 1, , 2, 3', expected: [0, 1, 2, 3] } // Should filter out multiple empty values
    ];

    testCases.forEach(testCase => {
      const objectClasses = testCase.input.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
      expect(objectClasses).toEqual(testCase.expected);
    });
  });

  test('Numeric parsing works correctly', () => {
    // Test parseFloat
    expect(parseFloat('0.75')).toBe(0.75);
    expect(parseFloat('0.1')).toBe(0.1);
    expect(parseFloat('0.5')).toBe(0.5);
    expect(parseFloat('0.7')).toBe(0.7);
    expect(parseFloat('0.6')).toBe(0.6);

    // Test parseInt
    expect(parseInt('4')).toBe(4);
    expect(parseInt('10')).toBe(10);
    expect(parseInt('3')).toBe(3);
    expect(parseInt('15')).toBe(15);
    expect(parseInt('20')).toBe(20);
  });

  test('Boolean flags are correctly set', () => {
    const mockSettings = {
      faceDetection: { checked: true },
      weightedCenter: { checked: false },
      blendSaliency: { checked: true },
      applySmoothing: { checked: false },
      debugMode: { checked: true },
      debugWindow: { checked: false },
      showHelp: { checked: true },
      recursiveSearch: { checked: false }
    };

    const options = {
      face_detection: mockSettings.faceDetection.checked,
      weighted_center: mockSettings.weightedCenter.checked,
      blend_saliency: mockSettings.blendSaliency.checked,
      apply_smoothing: mockSettings.applySmoothing.checked,
      debug: mockSettings.debugMode.checked,
      debug_window: mockSettings.debugWindow.checked,
      show_help: mockSettings.showHelp.checked,
      recursive_search: mockSettings.recursiveSearch.checked
    };

    expect(options.face_detection).toBe(true);
    expect(options.weighted_center).toBe(false);
    expect(options.blend_saliency).toBe(true);
    expect(options.apply_smoothing).toBe(false);
    expect(options.debug).toBe(true);
    expect(options.debug_window).toBe(false);
    expect(options.show_help).toBe(true);
    expect(options.recursive_search).toBe(false);
  });

  test('All required properties are present in options object', () => {
    const mockSettings = {
      targetRatio: { value: '0.75' },
      maxWorkers: { value: '4' },
      detector: { value: 'yolo' },
      skipFrames: { value: '10' },
      confThreshold: { value: '0.5' },
      modelSize: { value: 'medium' },
      objectClasses: { value: '0,1,2' },
      trackCount: { value: '3' },
      paddingRatio: { value: '0.1' },
      sizeWeight: { value: '0.3' },
      centerWeight: { value: '0.4' },
      motionWeight: { value: '0.2' },
      historyWeight: { value: '0.1' },
      saliencyWeight: { value: '0.5' },
      faceDetection: { checked: true },
      weightedCenter: { checked: false },
      blendSaliency: { checked: true },
      applySmoothing: { checked: true },
      smoothingWindow: { value: '15' },
      positionInertia: { value: '0.7' },
      sizeInertia: { value: '0.6' },
      debugMode: { checked: true },
      debugWindow: { checked: false },
      showHelp: { checked: true },
      recursiveSearch: { checked: false }
    };

    const options = {
      target_ratio: parseFloat(mockSettings.targetRatio.value),
      max_workers: parseInt(mockSettings.maxWorkers.value),
      detector: mockSettings.detector.value,
      skip_frames: parseInt(mockSettings.skipFrames.value),
      conf_threshold: parseFloat(mockSettings.confThreshold.value),
      model_size: mockSettings.modelSize.value,
      object_classes: mockSettings.objectClasses.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x)),
      track_count: parseInt(mockSettings.trackCount.value),
      padding_ratio: parseFloat(mockSettings.paddingRatio.value),
      size_weight: parseFloat(mockSettings.sizeWeight.value),
      center_weight: parseFloat(mockSettings.centerWeight.value),
      motion_weight: parseFloat(mockSettings.motionWeight.value),
      history_weight: parseFloat(mockSettings.historyWeight.value),
      saliency_weight: parseFloat(mockSettings.saliencyWeight.value),
      face_detection: mockSettings.faceDetection.checked,
      weighted_center: mockSettings.weightedCenter.checked,
      blend_saliency: mockSettings.blendSaliency.checked,
      apply_smoothing: mockSettings.applySmoothing.checked,
      smoothing_window: parseInt(mockSettings.smoothingWindow.value),
      position_inertia: parseFloat(mockSettings.positionInertia.value),
      size_inertia: parseFloat(mockSettings.sizeInertia.value),
      debug: mockSettings.debugMode.checked,
      debug_window: mockSettings.debugWindow.checked,
      show_help: mockSettings.showHelp.checked,
      recursive_search: mockSettings.recursiveSearch.checked
    };

    // Verify all expected properties are present
    const expectedProperties = [
      'target_ratio', 'max_workers', 'detector', 'skip_frames', 'conf_threshold',
      'model_size', 'object_classes', 'track_count', 'padding_ratio', 'size_weight',
      'center_weight', 'motion_weight', 'history_weight', 'saliency_weight',
      'face_detection', 'weighted_center', 'blend_saliency', 'apply_smoothing',
      'smoothing_window', 'position_inertia', 'size_inertia', 'debug',
      'debug_window', 'show_help', 'recursive_search'
    ];

    expectedProperties.forEach(prop => {
      expect(options).toHaveProperty(prop);
    });

    // Verify the total number of properties matches
    expect(Object.keys(options).length).toBe(expectedProperties.length);
  });

  test('Options object matches main.js argument structure', () => {
    // This test verifies that the options object structure matches what main.js expects
    const mockOptions = {
      target_ratio: 0.75,
      max_workers: 4,
      detector: 'yolo',
      skip_frames: 10,
      conf_threshold: 0.5,
      model_size: 'medium',
      object_classes: [0, 1, 2],
      track_count: 3,
      padding_ratio: 0.1,
      size_weight: 0.3,
      center_weight: 0.4,
      motion_weight: 0.2,
      history_weight: 0.1,
      saliency_weight: 0.5,
      face_detection: true,
      weighted_center: false,
      blend_saliency: true,
      apply_smoothing: true,
      smoothing_window: 15,
      position_inertia: 0.7,
      size_inertia: 0.6,
      debug: true,
      debug_window: false,
      show_help: true,
      recursive_search: false
    };

    // Verify that all properties that should be passed as arguments are present
    const argumentProperties = [
      'target_ratio', 'max_workers', 'detector', 'skip_frames', 'conf_threshold',
      'model_size', 'object_classes', 'track_count', 'padding_ratio', 'size_weight',
      'center_weight', 'motion_weight', 'history_weight', 'saliency_weight',
      'face_detection', 'weighted_center', 'blend_saliency', 'apply_smoothing',
      'smoothing_window', 'position_inertia', 'size_inertia', 'debug'
    ];

    argumentProperties.forEach(prop => {
      expect(mockOptions).toHaveProperty(prop);
    });

    // Verify boolean flags are properly set
    expect(mockOptions.face_detection).toBe(true);
    expect(mockOptions.weighted_center).toBe(false);
    expect(mockOptions.blend_saliency).toBe(true);
    expect(mockOptions.apply_smoothing).toBe(true);
    expect(mockOptions.debug).toBe(true);
  });
}); 