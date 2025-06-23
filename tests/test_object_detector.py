"""
Tests for the object_detector.py module.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile

# Import the object detector
from object_detector import ObjectDetector


class TestObjectDetectorInitialization:
    """Test ObjectDetector initialization."""
    
    def test_object_detector_init_defaults(self):
        """Test ObjectDetector initialization with default parameters."""
        detector = ObjectDetector()
        
        assert detector.confidence_threshold == 0.5
        assert detector.model_size == 'n'
        assert detector.classes == [0]
        assert detector.debug is False
        assert detector.input_video_path is None
    
    def test_object_detector_init_custom_params(self):
        """Test ObjectDetector initialization with custom parameters."""
        detector = ObjectDetector(
            confidence_threshold=0.7,
            model_size='s',
            classes=[0, 1, 2],
            debug=True,
            input_video_path='test_video.mp4'
        )
        
        assert detector.confidence_threshold == 0.7
        assert detector.model_size == 's'
        assert detector.classes == [0, 1, 2]
        assert detector.debug is True
        assert detector.input_video_path == 'test_video.mp4'
    
    @patch('object_detector.YOLO')
    def test_object_detector_model_loading(self, mock_yolo):
        """Test that YOLO model is loaded correctly."""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        detector = ObjectDetector(model_size='n')
        
        # Verify YOLO was called with correct model name
        mock_yolo.assert_called_once_with('yolov8n.pt')
        assert detector.model == mock_model
    
    @patch('object_detector.YOLO')
    def test_object_detector_different_model_sizes(self, mock_yolo):
        """Test loading different YOLO model sizes."""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        # Test different model sizes
        sizes = ['n', 's', 'm', 'l', 'x']
        expected_models = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
        
        for size, expected_model in zip(sizes, expected_models):
            mock_yolo.reset_mock()
            detector = ObjectDetector(model_size=size)
            mock_yolo.assert_called_once_with(expected_model)


class TestObjectDetectorDetection:
    """Test object detection functionality."""
    
    @patch('object_detector.YOLO')
    def test_detect_basic(self, mock_yolo):
        """Test basic object detection."""
        # Create mock model and results
        mock_model = Mock()
        mock_results = Mock()
        mock_results[0].boxes.data = np.array([
            [100, 100, 200, 200, 0.8, 0],  # x1, y1, x2, y2, conf, class_id
            [300, 300, 400, 400, 0.6, 1]   # x1, y1, x2, y2, conf, class_id
        ])
        mock_model.return_value = [mock_results]
        mock_yolo.return_value = mock_model
        
        # Create detector
        detector = ObjectDetector(
            confidence_threshold=0.5,
            classes=[0, 1]
        )
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect(frame, top_n=2)
        
        # Verify results
        assert len(detections) == 2
        assert detections[0]['bbox'] == [100, 100, 200, 200]
        assert detections[0]['confidence'] == 0.8
        assert detections[0]['class_id'] == 0
        assert detections[1]['bbox'] == [300, 300, 400, 400]
        assert detections[1]['confidence'] == 0.6
        assert detections[1]['class_id'] == 1
    
    @patch('object_detector.YOLO')
    def test_detect_confidence_filtering(self, mock_yolo):
        """Test that detections are filtered by confidence threshold."""
        # Create mock model and results
        mock_model = Mock()
        mock_results = Mock()
        mock_results[0].boxes.data = np.array([
            [100, 100, 200, 200, 0.8, 0],  # High confidence
            [300, 300, 400, 400, 0.3, 1]   # Low confidence (should be filtered)
        ])
        mock_model.return_value = [mock_results]
        mock_yolo.return_value = mock_model
        
        # Create detector with high confidence threshold
        detector = ObjectDetector(confidence_threshold=0.5, classes=[0, 1])
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect(frame, top_n=10)
        
        # Verify only high confidence detection is returned
        assert len(detections) == 1
        assert detections[0]['confidence'] == 0.8
    
    @patch('object_detector.YOLO')
    def test_detect_class_filtering(self, mock_yolo):
        """Test that detections are filtered by class."""
        # Create mock model and results
        mock_model = Mock()
        mock_results = Mock()
        mock_results[0].boxes.data = np.array([
            [100, 100, 200, 200, 0.8, 0],  # Class 0 (person)
            [300, 300, 400, 400, 0.7, 2]   # Class 2 (car) - should be filtered
        ])
        mock_model.return_value = [mock_results]
        mock_yolo.return_value = mock_model
        
        # Create detector that only tracks class 0
        detector = ObjectDetector(confidence_threshold=0.5, classes=[0])
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect(frame, top_n=10)
        
        # Verify only class 0 detection is returned
        assert len(detections) == 1
        assert detections[0]['class_id'] == 0
    
    @patch('object_detector.YOLO')
    def test_detect_top_n_limiting(self, mock_yolo):
        """Test that top_n parameter limits the number of detections."""
        # Create mock model and results with many detections
        mock_model = Mock()
        mock_results = Mock()
        mock_results[0].boxes.data = np.array([
            [100, 100, 200, 200, 0.9, 0],  # Highest confidence
            [200, 200, 300, 300, 0.8, 0],  # Second highest
            [300, 300, 400, 400, 0.7, 0],  # Third highest
            [400, 400, 500, 500, 0.6, 0],  # Fourth highest
        ])
        mock_model.return_value = [mock_results]
        mock_yolo.return_value = mock_model
        
        # Create detector
        detector = ObjectDetector(confidence_threshold=0.5, classes=[0])
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection with top_n=2
        detections = detector.detect(frame, top_n=2)
        
        # Verify only top 2 detections are returned
        assert len(detections) == 2
        assert detections[0]['confidence'] == 0.9  # Highest confidence first
        assert detections[1]['confidence'] == 0.8  # Second highest confidence
    
    @patch('object_detector.YOLO')
    def test_detect_no_detections(self, mock_yolo):
        """Test detection when no objects are found."""
        # Create mock model with no detections
        mock_model = Mock()
        mock_results = Mock()
        mock_results[0].boxes.data = np.array([])  # No detections
        mock_model.return_value = [mock_results]
        mock_yolo.return_value = mock_model
        
        # Create detector
        detector = ObjectDetector()
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect(frame, top_n=10)
        
        # Verify empty list is returned
        assert len(detections) == 0


class TestObjectDetectorDebug:
    """Test debug functionality."""
    
    @patch('object_detector.YOLO')
    @patch('object_detector.cv2.VideoWriter')
    @patch('object_detector.os.makedirs')
    def test_debug_video_creation(self, mock_makedirs, mock_video_writer, mock_yolo):
        """Test debug video creation when debug mode is enabled."""
        # Create mock model
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        # Create mock video writer
        mock_writer = Mock()
        mock_video_writer.return_value = mock_writer
        
        # Create detector with debug enabled
        detector = ObjectDetector(
            debug=True,
            input_video_path='test_video.mp4'
        )
        
        # Verify debug directory was created
        mock_makedirs.assert_called()
        
        # Verify video writer was created
        mock_video_writer.assert_called()
        
        # Test finalize_debug_video
        detector.finalize_debug_video()
        mock_writer.release.assert_called_once()
    
    @patch('object_detector.YOLO')
    def test_debug_disabled(self, mock_yolo):
        """Test that debug functionality is disabled when debug=False."""
        # Create mock model
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        # Create detector with debug disabled
        detector = ObjectDetector(debug=False)
        
        # Verify debug attributes are None
        assert detector.debug_video_path is None
        assert detector.debug_writer is None
        
        # Test finalize_debug_video (should not crash)
        detector.finalize_debug_video()


class TestObjectDetectorErrorHandling:
    """Test error handling in ObjectDetector."""
    
    @patch('object_detector.YOLO')
    def test_model_loading_error(self, mock_yolo):
        """Test handling of model loading errors."""
        # Make YOLO raise an exception
        mock_yolo.side_effect = Exception("Model loading failed")
        
        # Test that exception is raised
        with pytest.raises(Exception, match="Model loading failed"):
            ObjectDetector()
    
    @patch('object_detector.YOLO')
    def test_detection_error(self, mock_yolo):
        """Test handling of detection errors."""
        # Create mock model that raises exception
        mock_model = Mock()
        mock_model.side_effect = Exception("Detection failed")
        mock_yolo.return_value = mock_model
        
        # Create detector
        detector = ObjectDetector()
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test that detection error is handled
        with pytest.raises(Exception, match="Detection failed"):
            detector.detect(frame)


if __name__ == "__main__":
    pytest.main([__file__]) 