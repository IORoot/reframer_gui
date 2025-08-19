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
    console.log('Using Apple ID:', process.env.APPLE_ID);
    console.log('Using Team ID: 43DRWGP9KX');
    
    const notarizeCommand = [
      'xcrun', 'notarytool', 'submit',
      '--apple-id', process.env.APPLE_ID,
      '--password', process.env.APPLE_APP_SPECIFIC_PASSWORD,
      '--team-id', '43DRWGP9KX',
      tempZip
    ].join(' ');

    console.log('Running command:', notarizeCommand.replace(process.env.APPLE_APP_SPECIFIC_PASSWORD, '***'));
    
    const result = execSync(notarizeCommand, { encoding: 'utf8', stdio: 'pipe' });
    
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

      const statusResult = execSync(statusCommand, { encoding: 'utf8', stdio: 'pipe' });
      
      if (statusResult.includes('status: Accepted')) {
        console.log('Notarization completed successfully!');
        break;
      } else if (statusResult.includes('status: Invalid')) {
        console.error('Notarization failed - status: Invalid');
        console.error('Full status response:', statusResult);
        throw new Error('Notarization failed with Invalid status');
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
    console.error('Error details:', error);
    
    // If it's a subprocess error, show the command output
    if (error.stdout) {
      console.error('Command stdout:', error.stdout);
    }
    if (error.stderr) {
      console.error('Command stderr:', error.stderr);
    }
    
    // Exit with error code so the build fails and you can see the issue
    process.exit(1);
  }
}

// Run the notarization
notarize(); 