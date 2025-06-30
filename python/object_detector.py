from ultralytics import YOLO
import cv2
import numpy as np
import os
import urllib.request
from PIL import Image
import time
import gc
import traceback

class ObjectDetector:
    """Class for detecting objects in video frames using YOLOv8."""
    
    def __init__(self, confidence_threshold=0.5, model_size='n', classes=[0], debug=False, input_video_path=None):
        """
        Initialize YOLOv8 detector.
        
        Args:
            confidence_threshold: Minimum confidence score for detections
            model_size: YOLOv8 model size ('n', 's', 'm', 'l', 'x')
            classes: List of class IDs to detect (default: [0] for person)
            debug: Enable debug mode to create video with detection boxes
            input_video_path: Path to input video (used to determine debug log location)
        """
        self.confidence_threshold = confidence_threshold
        self.model_size = model_size
        self.classes = classes
        self.debug = debug
        self.input_video_path = input_video_path
        self.model = None
        self.debug_video_writer = None
        self.debug_video_path = None
        self.frame_count = 0
        
        # Initialize debug video if debug mode is enabled
        if self.debug:
            self._initialize_debug_video()
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_debug_video(self):
        """Initialize debug video writer."""
        try:
            # Determine debug folder location
            if self.input_video_path:
                # Use the directory of the input video
                input_dir = os.path.dirname(os.path.abspath(self.input_video_path))
                debug_folder = os.path.join(input_dir, "debug_logs")
            else:
                # Fallback to current directory
                debug_folder = "debug_logs"
            
            os.makedirs(debug_folder, exist_ok=True)
            
            timestamp = int(time.time())
            self.debug_video_path = os.path.join(debug_folder, f"detection_debug_{timestamp}.mp4")
            
            # We'll initialize the video writer when we get the first frame
            print(f"Debug video will be saved to: {self.debug_video_path}")
        except Exception as e:
            print(f"Error initializing debug video: {e}")
            self.debug = False  # Disable debug mode if initialization fails
    
    def _initialize_video_writer(self, frame):
        """Initialize video writer with frame dimensions."""
        try:
            if self.debug_video_writer is None and self.debug:
                height, width = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.debug_video_writer = cv2.VideoWriter(
                    self.debug_video_path, 
                    fourcc, 
                    30.0,  # FPS
                    (width, height)
                )
                print(f"Debug video writer initialized: {width}x{height} @ 30fps")
        except Exception as e:
            print(f"Error initializing video writer: {e}")
            self.debug = False  # Disable debug mode if video writer fails
    
    def _draw_detection_boxes(self, frame, detections):
        """Draw detection boxes on the frame."""
        try:
            frame_with_boxes = frame.copy()
            
            for detection in detections:
                x, y, w, h = detection['box']
                confidence = detection['confidence']
                class_name = detection['class_name']
                
                # Draw bounding box
                cv2.rectangle(frame_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw label background
                label = f"{class_name}: {confidence:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame_with_boxes, (x, y - label_height - 10), (x + label_width, y), (0, 255, 0), -1)
                
                # Draw label text
                cv2.putText(frame_with_boxes, label, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            return frame_with_boxes
        except Exception as e:
            print(f"Error drawing detection boxes: {e}")
            return frame  # Return original frame if drawing fails
    
    def finalize_debug_video(self):
        """Finalize and close the debug video writer."""
        try:
            if self.debug_video_writer is not None:
                self.debug_video_writer.release()
                self.debug_video_writer = None
                print(f"Debug video saved: {self.debug_video_path}")
                print(f"Total frames processed: {self.frame_count}")
        except Exception as e:
            print(f"Error finalizing debug video: {e}")
    
    def _initialize_model(self):
        """Initialize the YOLOv8 model."""
        try:
            model_filename = f'yolo11{self.model_size}.pt'
            local_model_path = os.path.join('models', model_filename)

            if not os.path.exists(local_model_path):
                os.makedirs('models', exist_ok=True)
                download_url = f'https://github.com/ultralytics/assets/releases/download/v8.3.0/{model_filename}'
                print(f"Downloading YOLOv11 model from {download_url}...")
                try:
                    urllib.request.urlretrieve(download_url, local_model_path)
                    print(f"Model downloaded to {local_model_path}")
                except Exception as download_error:
                    print(f"Failed to download model: {download_error}")
                    print("Trying alternative download method...")
                    try:
                        # Try alternative download method
                        import requests
                        response = requests.get(download_url, stream=True)
                        response.raise_for_status()
                        with open(local_model_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"Model downloaded to {local_model_path}")
                    except Exception as alt_download_error:
                        print(f"Alternative download also failed: {alt_download_error}")
                        print("Please download the model manually or check your internet connection.")
                        raise RuntimeError(f"Failed to download YOLO model: {download_error}")

            # All classes are loaded by default, but we can filter them later
            # The classes are:
            # 0: person
            # 1: bicycle
            # 2: car
            # 3: motorcycle
            # 4: airplane
            # 5: bus
            # see https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
            #
            # Arguments: https://docs.ultralytics.com/modes/predict/#inference-sources
            try:
                self.model = YOLO(local_model_path)
                print(f"YOLOv11-{self.model_size} model loaded successfully")
            except Exception as model_load_error:
                print(f"Failed to load model from {local_model_path}: {model_load_error}")
                print("Trying to load model directly from ultralytics...")
                try:
                    # Try loading directly from ultralytics
                    self.model = YOLO(f'yolo11{self.model_size}.pt')
                    print(f"YOLOv11-{self.model_size} model loaded from ultralytics successfully")
                except Exception as direct_load_error:
                    print(f"Failed to load model directly: {direct_load_error}")
                    raise RuntimeError(f"Failed to load YOLO model: {model_load_error}")
                    
        except Exception as e:
            print(f"Error loading YOLOv8 model: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def detect(self, frame, top_n=1):
        """
        Detect objects in a frame.
        
        Args:
            frame: The input frame (numpy array)
            top_n: Number of top detections to return, based on confidence. 
                If top_n=1, only the highest confidence detection is returned.
                If top_n=2, the top 2 detections are returned, and so on.
            
        Returns:
            List of detected objects, each as a dictionary with:
            - 'box': [x, y, width, height]
            - 'confidence': detection confidence
            - 'class_name': class name
            - 'class_id': class ID
        """
        try:
            if self.model is None:
                print("Warning: Model not initialized, returning empty detections")
                return []
            
            # Validate input frame
            if frame is None or frame.size == 0:
                print("Warning: Empty frame provided, returning empty detections")
                return []
            
            # Run YOLOv11 inference
            try:
                results = self.model(frame, 
                                    verbose=False, 
                                    classes=self.classes,
                                    )[0]
            except Exception as inference_error:
                print(f"Error during YOLO inference: {inference_error}")
                print("Returning empty detections")
                return []
            
            # Process detections
            detections = []

            try:
                # Collect all valid detections
                for det in results.boxes.data.cpu().numpy():
                    x1, y1, x2, y2, conf, cls = det

                    # Skip if the confidence is below the threshold
                    if conf < self.confidence_threshold:
                        continue

                    width = x2 - x1
                    height = y2 - y1

                    x = int(x1)
                    y = int(y1)
                    w = int(width)
                    h = int(height)
                    class_id = int(cls)
                    
                    # Safely get class name
                    try:
                        class_name = results.names[int(cls)]
                    except (KeyError, IndexError):
                        class_name = f"class_{class_id}"
                    
                    confidence = float(conf)

                    detection = {
                        'box': [x, y, w, h],
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name
                    }

                    detections.append(detection)

                # Sort detections by confidence, in descending order
                detections.sort(key=lambda x: x['confidence'], reverse=True)

                # If top_n is specified, keep only the top 'n' detections
                if top_n > 0:
                    detections = detections[:top_n]
                    
            except Exception as processing_error:
                print(f"Error processing detection results: {processing_error}")
                return []

            # DEBUG DETECTIONS!
            if self.debug:
                try:
                    # Initialize video writer on first frame
                    self._initialize_video_writer(frame)
                    
                    # Draw detection boxes on frame
                    frame_with_boxes = self._draw_detection_boxes(frame, detections)
                    
                    # Write frame to video
                    if self.debug_video_writer is not None:
                        self.debug_video_writer.write(frame_with_boxes)
                        self.frame_count += 1
                    
                    # Log detection details to text file
                    if detections:
                        # Use the same directory as the input video for debug logs
                        if self.input_video_path:
                            input_dir = os.path.dirname(os.path.abspath(self.input_video_path))
                            debug_folder = os.path.join(input_dir, "debug_logs")
                        else:
                            debug_folder = "debug_logs"
                        
                        os.makedirs(debug_folder, exist_ok=True)
                        for detection in detections:
                            with open(os.path.join(debug_folder, "log1_detections.txt"), "a") as f:
                                f.write(f"Frame {self.frame_count}: Detector Box: {detection['box']} "
                                        f"class_name: {detection['class_name']}, "
                                        f"Confidence: {detection['confidence']}\n")
                except Exception as e:
                    print(f"Error in debug processing: {e}")
                    # Don't fail the entire detection if debug fails

            return detections
            
        except Exception as e:
            print(f"Error in object detection: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Return empty list instead of crashing
            return []
    
    def get_class_names(self):
        """Get list of class names the model can detect."""
        try:
            return self.model.names if self.model else {}
        except Exception as e:
            print(f"Error getting class names: {e}")
            return {}
    
    def __del__(self):
        """Clean up resources."""
        try:
            if self.debug_video_writer is not None:
                self.debug_video_writer.release()
            if self.model is not None:
                del self.model
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {e}") 