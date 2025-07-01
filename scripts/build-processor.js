#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load build configuration
const buildConfig = require('../build-config.js');

console.log('🔧 Processing build configuration...');
console.log(`BETA watermark enabled: ${buildConfig.beta.enabled}`);
console.log(`BETA text: "${buildConfig.beta.text}"`);
console.log(`BETA position: ${buildConfig.beta.position}`);
console.log(`BETA opacity: ${buildConfig.beta.opacity}`);

// Paths to Python files that need to be processed
const pythonFiles = [
  'python/main.py',
  'python/video_processor.py'
];

// Process each Python file
pythonFiles.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    console.log(`Processing ${filePath}...`);
    
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace the generate_output_video call to include BETA watermark
    if (filePath === 'python/main.py') {
      // Find the generate_output_video call and add the BETA watermark parameter
      const generateOutputVideoRegex = /video_processor\.generate_output_video\(\s*output_path=args\.output,\s*crop_windows=smoothed_windows,\s*fps=fps\s*\)/;
      
      if (generateOutputVideoRegex.test(content)) {
        if (buildConfig.beta.enabled) {
          // Add BETA watermark parameter
          content = content.replace(
            generateOutputVideoRegex,
            `video_processor.generate_output_video(
                output_path=args.output,
                crop_windows=smoothed_windows,
                fps=fps,
                add_beta_watermark=True,
                beta_text="${buildConfig.beta.text}",
                beta_position="${buildConfig.beta.position}",
                beta_opacity=${buildConfig.beta.opacity}
            )`
          );
          
          // Add the print statement for BETA watermark
          const printStatement = '        if args.beta_watermark:\n            print("BETA watermark will be added to output video")';
          const replacement = `        print("${buildConfig.beta.text} watermark will be added to output video")\n        ${printStatement}`;
          
          content = content.replace(printStatement, replacement);
        } else {
          // Disable BETA watermark
          content = content.replace(
            generateOutputVideoRegex,
            `video_processor.generate_output_video(
                output_path=args.output,
                crop_windows=smoothed_windows,
                fps=fps,
                add_beta_watermark=False
            )`
          );
          
          // Remove the BETA watermark print statement
          content = content.replace(/        print\(".*watermark will be added to output video"\)\s*\n/, '');
        }
      }
    }
    
    // Update video_processor.py to handle the new parameters
    if (filePath === 'python/video_processor.py') {
      // Update the generate_output_video method signature
      const methodSignatureRegex = /def generate_output_video\(self, output_path, crop_windows, fps=None, add_beta_watermark=False\):/;
      
      if (methodSignatureRegex.test(content)) {
        content = content.replace(
          methodSignatureRegex,
          `def generate_output_video(self, output_path, crop_windows, fps=None, add_beta_watermark=False, beta_text="BETA", beta_position="bottom-right", beta_opacity=0.7):`
        );
      }
      
      // Update the watermark call
      const watermarkCallRegex = /cropped_frame = self\.add_watermark\(cropped_frame, "BETA", "bottom-right", 0\.8\)/;
      
      if (watermarkCallRegex.test(content)) {
        content = content.replace(
          watermarkCallRegex,
          `cropped_frame = self.add_watermark(cropped_frame, beta_text, beta_position, beta_opacity)`
        );
      }
    }
    
    // Write the processed content back to the file
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ Processed ${filePath}`);
  } else {
    console.log(`⚠️  File not found: ${filePath}`);
  }
});

console.log('🎉 Build configuration processing complete!'); 