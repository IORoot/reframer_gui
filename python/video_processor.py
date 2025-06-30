import cv2
import numpy as np
import os
import subprocess
import sys
import platform
import gc
import traceback
from pathlib import Path

# Use absolute imports that work in both development and bundled environments
try:
    # Try direct import first (when in same directory)
    from ffmpeg_manager import get_ffmpeg_path
except ImportError:
    # Fallback to python directory import (when bundled)
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from python.ffmpeg_manager import get_ffmpeg_path

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
        self.ffmpeg_path = get_ffmpeg_path()
        print(f"VideoProcessor initialized with ffmpeg path: {self.ffmpeg_path}")
    
    def load_video(self, video_path):
        """Load video file and extract basic information."""
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.cap = cv2.VideoCapture(video_path)
            # self.cap = cv2.VideoCapture(video_path, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            self.video_info = {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'path': video_path
            }
            
            self.current_frame_idx = 0
            return self.video_info
        except Exception as e:
            print(f"Error loading video: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def frame_generator(self):
        """Generator that yields frames from the video."""
        try:
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
        except Exception as e:
            print(f"Error in frame generator: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def apply_crop(self, frame, crop_window):
        """Apply crop window to a frame."""
        try:
            # Validate input frame
            if frame is None:
                print("Warning: None frame provided to apply_crop")
                return None
            
            if not hasattr(frame, 'shape') or len(frame.shape) < 2:
                print(f"Warning: Invalid frame shape: {frame}")
                return None
            
            x, y, w, h = crop_window
            
            # Validate crop window values
            if any(not isinstance(val, (int, float)) for val in [x, y, w, h]):
                print(f"Warning: Invalid crop window values: {crop_window}")
                return None
            
            # Ensure crop window is within frame boundaries
            x = max(0, min(int(x), frame.shape[1] - 1))
            y = max(0, min(int(y), frame.shape[0] - 1))
            w = max(1, min(int(w), frame.shape[1] - x))
            h = max(1, min(int(h), frame.shape[0] - y))
            
            # Apply crop
            cropped = frame[y:y+h, x:x+w]
            
            # Validate cropped result
            if cropped is None or cropped.size == 0:
                print(f"Warning: Crop resulted in empty frame: {crop_window}")
                return None
            
            return cropped
        except Exception as e:
            print(f"Error applying crop: {e}")
            print(f"Frame shape: {frame.shape if frame is not None else 'None'}, crop_window: {crop_window}")
            # Return None instead of original frame to indicate failure
            return None

    def validate_frame(self, frame, expected_width=None, expected_height=None):
        """Validate frame before writing to video."""
        try:
            if frame is None:
                return False, "Frame is None"
            
            if not hasattr(frame, 'shape'):
                return False, "Frame has no shape attribute"
            
            if len(frame.shape) < 2:
                return False, f"Frame has invalid shape: {frame.shape}"
            
            height, width = frame.shape[:2]
            
            if width <= 0 or height <= 0:
                return False, f"Frame has invalid dimensions: {width}x{height}"
            
            if expected_width and width != expected_width:
                return False, f"Frame width mismatch: expected {expected_width}, got {width}"
            
            if expected_height and height != expected_height:
                return False, f"Frame height mismatch: expected {expected_height}, got {height}"
            
            # Check if frame data is valid
            if not frame.flags['C_CONTIGUOUS']:
                frame = np.ascontiguousarray(frame)
            
            return True, "Frame is valid"
            
        except Exception as e:
            return False, f"Frame validation error: {e}"

    def convert_to_h264(self, input_path):
        """Convert the given video to H.264 format using FFmpeg."""
        try:
            temp_h264_output = "temp_h264_output.mp4"

            ffmpeg_command = [
                self.ffmpeg_path, "-y", "-i", input_path,
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                "-c:a", "aac", "-b:a", "128k",
                temp_h264_output
            ]
            
            print(f"Encoding video to H.264: {temp_h264_output}")
            subprocess.run(ffmpeg_command, check=True)

            # Overwrite original video with the new one
            os.replace(temp_h264_output, input_path)
        except Exception as e:
            print(f"Error converting to H.264: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Don't fail the entire process if H.264 conversion fails
            pass

    def merge_audio(self, video_path, original_video):
        """Merge original audio into the processed video using FFmpeg."""
        try:
            audio_path = "temp_audio.mp3"
            temp_output = "temp_output.mp4"  # Temporary output file

            # Extract audio from the original video
            extract_cmd = [
                self.ffmpeg_path, "-i", original_video, "-q:a", "0", "-map", "0:a?", audio_path, "-y"
            ]
            result = subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if not os.path.exists(audio_path):
                print("Error extracting audio:", result.stderr.decode())
                return  # Exit if audio extraction fails

            # Merge extracted audio into a temporary file
            merge_cmd = [
                self.ffmpeg_path, "-i", video_path, "-i", audio_path, 
                "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", temp_output, "-y"
            ]
            result = subprocess.run(merge_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                print("Error merging audio:", result.stderr.decode())
                return  # Exit if merging fails

            # Overwrite original video with the new one
            os.replace(temp_output, video_path)

            # Cleanup
            os.remove(audio_path)
        except Exception as e:
            print(f"Error merging audio: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Don't fail the entire process if audio merging fails
            pass
    
    def generate_output_video(self, output_path, crop_windows, fps=None):
        """Generate output video with the specified crop windows."""
        try:
            if self.cap is None:
                raise ValueError("No video loaded. Call load_video() first.")
            
            if fps is None:
                fps = self.video_info['fps']
            
            # Validate crop_windows
            if not crop_windows or len(crop_windows) == 0:
                raise ValueError("No crop windows provided")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Reset video to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Get first valid crop window to determine output dimensions
            first_crop = None
            for crop in crop_windows:
                if crop is not None and len(crop) == 4:
                    first_crop = crop
                    break
            
            if first_crop is None:
                raise ValueError("No valid crop windows found")
            
            crop_width, crop_height = first_crop[2], first_crop[3]
            
            # Validate dimensions
            if crop_width <= 0 or crop_height <= 0:
                raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")
            
            print(f"Creating video writer: {crop_width}x{crop_height} @ {fps}fps")
            
            # Create video writer with mp4v codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(
                output_path, 
                fourcc, 
                fps, 
                (crop_width, crop_height)
            )
            
            # Check if writer was successfully created
            if not self.writer.isOpened():
                print(f"Error: Could not create video writer for {output_path}")
                print(f"Trying alternative codec...")
                # Try with a different codec
                self.writer = cv2.VideoWriter(
                    output_path, 
                    cv2.VideoWriter_fourcc(*'XVID'), 
                    fps, 
                    (crop_width, crop_height)
                )
                if not self.writer.isOpened():
                    raise ValueError(f"Failed to create video writer with multiple codecs")
            
            # Process each frame
            frames_written = 0
            frames_skipped = 0
            
            for i, frame in enumerate(self.frame_generator()):
                if i >= len(crop_windows):
                    break
                
                # Apply crop with boundary checking
                crop_window = crop_windows[i]
                if crop_window is None:
                    print(f"Warning: No crop window for frame {i}, skipping")
                    frames_skipped += 1
                    continue
                
                try:
                    # Validate input frame
                    is_valid, error_msg = self.validate_frame(frame)
                    if not is_valid:
                        print(f"Warning: Invalid frame {i}: {error_msg}, skipping")
                        frames_skipped += 1
                        continue
                    
                    # Apply crop
                    cropped_frame = self.apply_crop(frame, crop_window)
                    if cropped_frame is None:
                        print(f"Warning: Failed to crop frame {i}, skipping")
                        frames_skipped += 1
                        continue
                    
                    # Validate cropped frame
                    is_valid, error_msg = self.validate_frame(cropped_frame, crop_width, crop_height)
                    if not is_valid:
                        print(f"Warning: Invalid cropped frame {i}: {error_msg}")
                        # Try to resize the frame to match expected dimensions
                        try:
                            cropped_frame = cv2.resize(cropped_frame, (crop_width, crop_height))
                            is_valid, error_msg = self.validate_frame(cropped_frame, crop_width, crop_height)
                            if not is_valid:
                                print(f"Warning: Failed to resize frame {i}: {error_msg}, skipping")
                                frames_skipped += 1
                                continue
                        except Exception as resize_error:
                            print(f"Warning: Failed to resize frame {i}: {resize_error}, skipping")
                            frames_skipped += 1
                            continue
                    
                    # Ensure frame is contiguous in memory
                    if not cropped_frame.flags['C_CONTIGUOUS']:
                        cropped_frame = np.ascontiguousarray(cropped_frame)
                    
                    # Write to output video with error handling
                    try:
                        self.writer.write(cropped_frame)
                        frames_written += 1
                    except Exception as write_error:
                        print(f"Error writing frame {i}: {write_error}")
                        frames_skipped += 1
                        continue
                        
                except Exception as e:
                    print(f"Error processing frame {i}: {e}")
                    frames_skipped += 1
                    continue
                
                if i % 100 == 0:
                    print(f"\r🎥 Processed {i}/{len(crop_windows)} frames (written: {frames_written}, skipped: {frames_skipped})", end='', flush=True)
                    # Force garbage collection periodically for large videos
                    if i % 1000 == 0:
                        gc.collect()
            
            print(f"\nVideo generation complete: {frames_written} frames written, {frames_skipped} frames skipped")
            
            # Release resources
            if self.writer:
                self.writer.release()
                self.writer = None

            # Only proceed with audio operations if we wrote some frames
            if frames_written > 0:
                # Merge audio
                self.merge_audio(output_path, self.video_info['path'])
                self.convert_to_h264(output_path)
            else:
                print("Warning: No frames were written, skipping audio operations")
            
        except Exception as e:
            print(f"Error generating output video: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Clean up writer if it exists
            if self.writer:
                try:
                    self.writer.release()
                    self.writer = None
                except:
                    pass
            raise
    
    def __del__(self):
        """Clean up resources."""
        try:
            if self.cap:
                self.cap.release()
            if self.writer:
                self.writer.release()
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {e}") 