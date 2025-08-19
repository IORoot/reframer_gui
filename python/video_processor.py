import cv2
import numpy as np
import os
import sys
import platform
from pathlib import Path

# Use absolute imports that work in both development and bundled environments
try:
    # Try direct import first (when in same directory)
    from watermark import watermark_renderer
except ImportError:
    # Fallback to python directory import (when bundled)
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from python.watermark import watermark_renderer

def get_app_path():
    """Get the path to the application's resources directory."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        if platform.system() == 'Darwin':  # macOS
            # Get the path to the Resources directory
            # sys.executable is in Contents/MacOS, so we need to go up two levels
            bundle_path = Path(os.path.dirname(sys.executable)).parent.parent
            resources_path = bundle_path / 'Resources'
            print(f"Running in bundle, bundle path: {bundle_path}")
            print(f"Running in bundle, resources path: {resources_path}")
            print(f"sys.executable: {sys.executable}")
            return resources_path
        elif platform.system() == 'Windows':
            path = Path(os.path.dirname(sys.executable))
            print(f"Running in bundle, app path: {path}")
            return path
        else:  # Linux
            path = Path(os.path.dirname(sys.executable))
            print(f"Running in bundle, app path: {path}")
            return path
    else:
        # Running in normal Python environment
        # When not frozen, we need to look in the app bundle's Resources directory
        # This is a bit of a hack, but it works for development
        current_path = Path(__file__).parent
        while current_path.name != 'Resources' and current_path.parent != current_path:
            current_path = current_path.parent
        if current_path.name == 'Resources':
            print(f"Running in normal Python environment, found Resources at: {current_path}")
            return current_path
        print(f"Running in normal Python environment, using current directory: {current_path}")
        return current_path

class VideoProcessor:
    def __init__(self):
        self.cap = None
        self.writer = None
        self.frames = None
        self.current_frame_idx = 0
        self.video_info = {}
        print("VideoProcessor initialized with OpenCV for detection and MoviePy for video processing")
    
    def load_video(self, video_path):
        """Load video file and extract basic information."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(video_path)
        # self.cap = cv2.VideoCapture(video_path, cv2.CAP_DSHOW)
        self.video_info = {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'total_frames': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'path': video_path
        }
        
        self.current_frame_idx = 0
        return self.video_info
    
    def frame_generator(self):
        """Generator that yields frames from the video."""
        if self.cap is None:
            raise ValueError("No video loaded. Call load_video() first.")
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame_idx = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            yield frame
            self.current_frame_idx += 1
    
    def apply_crop(self, frame, crop_window):
        """Apply crop window to a frame."""
        x, y, w, h = crop_window
        
        # Ensure crop window is within frame boundaries
        x = max(0, min(x, frame.shape[1] - 1))
        y = max(0, min(y, frame.shape[0] - 1))
        w = max(1, min(w, frame.shape[1] - x))
        h = max(1, min(h, frame.shape[0] - y))
        
        # Apply crop
        return frame[y:y+h, x:x+w]
    
    def convert_to_h264(self, input_path):
        """Convert the given video to H.264 format using MoviePy (preserves audio)."""
        temp_output = "temp_h264_output.mp4"
        
        try:
            print(f"Converting video to H.264 with MoviePy: {temp_output}")
            
            # Import MoviePy here to ensure it's available
            try:
                from moviepy import VideoFileClip
            except ImportError:
                # Fallback to editor import
                from moviepy.editor import VideoFileClip
            
            # Load the video (this preserves audio)
            video = VideoFileClip(input_path)
            
            # Write with H.264 codec (preserves audio)
            print("Writing H.264 video with audio...")
            video.write_videofile(
                temp_output,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Clean up
            video.close()
            
            # Overwrite original video with the new one
            os.replace(temp_output, input_path)
            print(f"H.264 conversion completed with audio preserved")
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_output):
                os.remove(temp_output)
            raise RuntimeError(f"H.264 conversion failed: {e}")


    # merge_audio method removed - no longer needed with MoviePy approach

    
    
    def generate_output_video(self, output_path, crop_windows, fps=None):
        """Generate output video with the specified crop windows using MoviePy."""
        if self.cap is None:
            raise ValueError("No video loaded. Call load_video() first.")
        
        if fps is None:
            fps = self.video_info['fps']
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            # Import MoviePy
            from moviepy import VideoFileClip
            print("Using MoviePy for video processing...")
            
            # Load original video with MoviePy (preserves audio)
            original_video = VideoFileClip(self.video_info['path'])
            print(f"Loaded original video: {original_video.duration:.2f}s, {original_video.fps} fps")
            
            # Get first crop window to determine output dimensions
            first_crop = crop_windows[0]
            crop_width, crop_height = first_crop[2], first_crop[3]
            print(f"Output dimensions: {crop_width}x{crop_height}")
            
            # Process frames one by one and create a new video clip
            print("Processing video frames with MoviePy...")
            
            # Create a list to store processed frames
            processed_frames = []
            
            # Process each frame using OpenCV for cropping, then convert to MoviePy
            for i in range(len(crop_windows)):
                # Get frame from OpenCV (we already have this capability)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Apply crop window
                crop_window = crop_windows[i]
                x, y, w, h = crop_window
                
                # Ensure crop coordinates are within bounds
                x = max(0, min(x, frame.shape[1] - w))
                y = max(0, min(y, frame.shape[0] - h))
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)
                
                # Crop the frame
                cropped_frame = frame[y:y+h, x:x+w]
                
                # Resize if needed
                if cropped_frame.shape[1] != crop_width or cropped_frame.shape[0] != crop_height:
                    cropped_frame = cv2.resize(cropped_frame, (crop_width, crop_height))
                
                # Apply watermark
                watermarked_frame = watermark_renderer.apply_watermark(cropped_frame)
                
                # Convert BGR to RGB for MoviePy
                rgb_frame = cv2.cvtColor(watermarked_frame, cv2.COLOR_BGR2RGB)
                processed_frames.append(rgb_frame)
                
                if i % 100 == 0:
                    print(f"\r🎥 Processed {i}/{len(crop_windows)} frames", end='', flush=True)
            
            print(f"\n✅ Successfully processed {len(processed_frames)} frames")
            
            # Extract and save audio separately for debugging
            print("Extracting audio for debugging...")
            if original_video.audio is not None:
                audio_path = output_path.replace('.mp4', '_audio.wav')
                original_video.audio.write_audiofile(audio_path)
                print(f"✅ Audio extracted to: {audio_path}")
                print(f"Audio info: {original_video.audio.duration:.2f}s, {original_video.audio.fps} Hz")
            else:
                print("❌ No audio found in original video")
            
            # Create MoviePy clip from processed frames
            from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
            processed_video = ImageSequenceClip(processed_frames, fps=fps)
            
            # Add audio from original video
            print("Adding audio to processed video...")
            if original_video.audio is not None:
                print(f"Audio found: {original_video.audio.duration:.2f}s")
                # Create final video with audio by setting the audio attribute
                final_video = processed_video
                final_video.audio = original_video.audio
                print(f"Audio added: {original_video.audio.duration:.2f}s")
            else:
                print("No audio found in original video")
                final_video = processed_video
            
            # Write the final video with H.264 video and AAC audio
            print("Writing final video with MoviePy...")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=fps
            )
            
            # Clean up
            original_video.close()
            processed_video.close()
            
            # Verify output file exists and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 0:
                    print(f"✅ Video processing completed successfully! Output: {output_path} ({file_size} bytes)")
                else:
                    raise RuntimeError("Output file is empty")
            else:
                raise RuntimeError("Output file was not created")
                
        except Exception as e:
            print(f"❌ Error in MoviePy video processing: {e}")
            # Clean up output file if it exists
            if os.path.exists(output_path):
                os.remove(output_path)
            raise

    
    def __del__(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release() 