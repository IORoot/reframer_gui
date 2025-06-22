# Frontend Testing Framework

This directory contains end-to-end tests for the Electron frontend of Reframer GUI using Playwright Test.

## Setup

The testing framework is already configured in the project's `package.json`. All necessary dependencies are included.

## Running Tests

To run the frontend tests:

```bash
npm run test:frontend
```

This will execute all tests in the `tests/frontend` directory.

## Test Structure

The tests are organized as follows:

- `electron.spec.js` - Main test suite for the Electron application
  - Basic application launch and title verification
  - UI element presence and interaction
  - Settings panel functionality
  - Form persistence
  - Debug output verification
  - Progress tracking
  - Error handling

## Writing New Tests

When adding new tests:

1. Add test cases to `electron.spec.js` or create new spec files for specific features
2. Use the existing `beforeEach` and `afterEach` hooks for proper app lifecycle management
3. Follow the existing patterns for element selection and assertions
4. Use meaningful test descriptions that clearly indicate what is being tested

## Best Practices

- Keep tests focused and atomic
- Use meaningful selectors (preferably IDs) for elements
- Add appropriate wait times for async operations
- Clean up resources after tests
- Document any special setup requirements
- Use the provided hooks for setup and teardown

## Debugging Tests

To debug tests:

1. Use the `--debug` flag when running tests:
   ```bash
   npm run test:frontend -- --debug
   ```
2. Use the Playwright Inspector to step through tests
3. Check the test report in the `playwright-report` directory

## CI Integration

The tests are configured to run in CI environments with appropriate retry logic and parallel execution settings. The configuration can be found in `playwright.config.js`.

## Common Issues

- If tests fail to launch the app, ensure the main process file path is correct
- For timing issues, adjust the timeout settings in the config file
- For element not found errors, check if selectors match the current UI

## Maintenance

- Keep test selectors up to date with UI changes
- Update test cases when new features are added
- Remove or update tests when features are deprecated
- Regularly review and update test coverage 