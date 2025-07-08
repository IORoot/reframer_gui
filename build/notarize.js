const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

async function notarize() {
  console.log('Starting notarization process...');

  // Check if environment variables are set
  if (!process.env.APPLE_ID || !process.env.APPLE_APP_SPECIFIC_PASSWORD) {
    console.log('Skipping notarization: APPLE_ID or APPLE_APP_SPECIFIC_PASSWORD not set');
    return;
  }

  // Find the built app in dist directory
  const distDir = path.join(__dirname, '..', 'dist');
  const appPath = path.join(distDir, 'mac-arm64', 'Reframe.app');

  if (!fs.existsSync(appPath)) {
    console.log('App not found at:', appPath);
    console.log('Available files in dist:', fs.readdirSync(distDir));
    return;
  }

  console.log('Found app at:', appPath);

  try {
    // Create a temporary zip file for notarization
    const tempZip = path.join(distDir, 'temp_notarize.zip');
    console.log('Creating temporary zip for notarization...');
    execSync(`ditto -c -k --keepParent "${appPath}" "${tempZip}"`);

    // Submit for notarization using notarytool
    console.log('Submitting to Apple for notarization...');
    const notarizeCommand = [
      'xcrun', 'notarytool', 'submit',
      '--apple-id', process.env.APPLE_ID,
      '--password', process.env.APPLE_APP_SPECIFIC_PASSWORD,
      '--team-id', '43DRWGP9KX',
      tempZip
    ].join(' ');

    const result = execSync(notarizeCommand, { encoding: 'utf8' });
    
    // Extract the submission ID from the result
    const idMatch = result.match(/id: ([a-f0-9-]+)/);
    if (!idMatch) {
      throw new Error('Failed to get notarization submission ID');
    }
    
    const submissionId = idMatch[1];
    console.log('Notarization submitted with ID:', submissionId);

    // Wait for notarization to complete
    console.log('Waiting for notarization to complete (this may take several minutes)...');
    
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
      
      const statusCommand = [
        'xcrun', 'notarytool', 'info',
        '--apple-id', process.env.APPLE_ID,
        '--password', process.env.APPLE_APP_SPECIFIC_PASSWORD,
        '--team-id', '43DRWGP9KX',
        submissionId
      ].join(' ');

      const statusResult = execSync(statusCommand, { encoding: 'utf8' });
      
      if (statusResult.includes('status: Accepted')) {
        console.log('Notarization completed successfully!');
        break;
      } else if (statusResult.includes('status: Invalid')) {
        throw new Error('Notarization failed');
      } else if (statusResult.includes('status: In Progress')) {
        console.log('Still in progress...');
      } else {
        console.log('Status:', statusResult);
      }
    }

    // Staple the notarization ticket
    console.log('Stapling notarization ticket...');
    execSync(`xcrun stapler staple "${appPath}"`);

    // Clean up
    execSync(`rm -f "${tempZip}"`);
    
    console.log('Notarization process completed successfully!');
    console.log('The app is now ready for distribution:');
    console.log('- Code signed with Developer ID Application certificate');
    console.log('- Notarized by Apple');
    console.log('- Users can run it without security warnings');
  } catch (error) {
    console.error('Notarization failed:', error.message);
    process.exit(1);
  }
}

// Run the notarization
notarize(); 