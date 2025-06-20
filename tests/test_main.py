"""
Tests for the main.py script - the core entry point for video processing.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the main module
from main import parse_args, main, process_keyframe


class TestMainArgumentParsing:
    """Test argument parsing functionality."""
    
    def test_parse_args_required_arguments(self):
        """Test that required arguments are properly parsed."""
        test_args = [
            '--input', 'test_video.mp4',
            '--output', 'output_video.mp4'
        ]
        
        with patch.object(sys, 'argv', ['main.py'] + test_args):
            args = parse_args()
            
            assert args.input == 'test_video.mp4'
            assert args.output == 'output_video.mp4'
    
    def test_parse_args_default_values(self):
        """Test that default values are set correctly."""
        test_args = [
            '--input', 'test_video.mp4',
            '--output', 'output_video.mp4'
        ]
        
        with patch.object(sys, 'argv', ['main.py'] + test_args):
            args = parse_args()
            
            # Check default values
            assert args.target_ratio == 9/16
            assert args.max_workers == 4
            assert args.detector == 'yolo'
            assert args.skip_frames == 10
            assert args.conf_threshold == 0.5
            assert args.model_size == 'n'
            assert args.object_classes == [0]
            assert args.track_count == 1
            assert args.padding_ratio == 0.1
            assert args.size_weight == 0.4
            assert args.center_weight == 0.3
            assert args.motion_weight == 0.3
            assert args.history_weight == 0.1
            assert args.saliency_weight == 0.4
            assert args.face_detection is False
            assert args.weighted_center is False
            assert args.blend_saliency is False
            assert args.apply_smoothing is False
            assert args.smoothing_window == 30
            assert args.position_inertia == 0.8
            assert args.size_inertia == 0.9
            assert args.debug is False
    
    def test_parse_args_custom_values(self):
        """Test that custom values override defaults."""
        test_args = [
            '--input', 'test_video.mp4',
            '--output', 'output_video.mp4',
            '--target_ratio', '16/9',
            '--max_workers', '8',
            '--model_size', 's',
            '--conf_threshold', '0.7',
            '--skip_frames', '5',
            '--debug'
        ]
        
        with patch.object(sys, 'argv', ['main.py'] + test_args):
            args = parse_args()
            
            assert args.target_ratio == 16/9
            assert args.max_workers == 8
            assert args.model_size == 's'
            assert args.conf_threshold == 0.7
            assert args.skip_frames == 5
            assert args.debug is True


class TestMainComponentInitialization:
    """Test component initialization in main function."""
    
    @patch('main.VideoProcessor')
    @patch('main.ObjectDetector')
    @patch('main.ObjectTracker')
    @patch('main.CropCalculator')
    @patch('main.CropWindowSmoother')
    def test_main_component_initialization(self, mock_smoother, mock_calculator, 
                                         mock_tracker, mock_detector, mock_processor):
        """Test that all components are initialized with correct parameters."""
        # Create mock arguments
        args = Mock()
        args.input = 'test_video.mp4'
        args.output = 'output_video.mp4'
        args.target_ratio = 16/9
        args.max_workers = 4
        args.conf_threshold = 0.5
        args.model_size = 'n'
        args.object_classes = [0]
        args.debug = False
        args.padding_ratio = 0.1
        args.size_weight = 0.4
        args.center_weight = 0.3
        args.motion_weight = 0.3
        args.history_weight = 0.1
        args.saliency_weight = 0.4
        args.face_detection = False
        args.weighted_center = False
        args.blend_saliency = False
        args.apply_smoothing = False
        args.smoothing_window = 30
        args.position_inertia = 0.8
        args.size_inertia = 0.9
        
        # Mock video processor to return valid video info
        mock_processor_instance = Mock()
        mock_processor_instance.load_video.return_value = {
            'total_frames': 100,
            'fps': 30.0,
            'width': 1920,
            'height': 1080
        }
        mock_processor_instance.cap = Mock()
        mock_processor_instance.cap.read.return_value = (True, Mock())
        mock_processor_instance.cap.set.return_value = True
        mock_processor_instance.generate_output_video.return_value = None
        mock_processor.return_value = mock_processor_instance
        
        # Mock other components
        mock_detector_instance = Mock()
        mock_detector_instance.detect.return_value = []
        mock_detector_instance.finalize_debug_video.return_value = None
        mock_detector.return_value = mock_detector_instance
        
        mock_tracker_instance = Mock()
        mock_tracker_instance.update.return_value = []
        mock_tracker.return_value = mock_tracker_instance
        
        mock_calculator_instance = Mock()
        mock_calculator_instance.calculate.return_value = [0, 0, 1920, 1080]
        mock_calculator.return_value = mock_calculator_instance
        
        mock_smoother_instance = Mock()
        mock_smoother_instance.smooth.return_value = [[0, 0, 1920, 1080]] * 100
        mock_smoother.return_value = mock_smoother_instance
        
        # Call main function
        with patch('main.ThreadPoolExecutor') as mock_executor:
            mock_executor.return_value.__enter__.return_value.submit.return_value.result.return_value = 0
            
            main(args)
            
            # Verify components were initialized with correct parameters
            mock_detector.assert_called_once_with(
                confidence_threshold=0.5,
                model_size='n',
                classes=[0],
                debug=False,
                input_video_path='test_video.mp4'
            )
            
            mock_tracker.assert_called_once_with(
                max_disappeared=30,
                max_distance=50
            )
            
            mock_calculator.assert_called_once_with(
                target_ratio=16/9,
                padding_ratio=0.1,
                size_weight=0.4,
                center_weight=0.3,
                motion_weight=0.3,
                history_weight=0.1,
                saliency_weight=0.4,
                debug=False,
                face_detection=False,
                weighted_center=False,
                blend_saliency=False,
                input_video_path='test_video.mp4'
            )
            
            mock_smoother.assert_called_once_with(
                window_size=30,
                position_inertia=0.8,
                size_inertia=0.9
            )


class TestProcessKeyframe:
    """Test the process_keyframe function."""
    
    def test_process_keyframe_basic(self):
        """Test basic keyframe processing."""
        # Create mock components
        mock_detector = Mock()
        mock_detector.detect.return_value = [
            {'bbox': [100, 100, 200, 200], 'confidence': 0.8, 'class_id': 0}
        ]
        
        mock_tracker = Mock()
        mock_tracker.update.return_value = [
            {'bbox': [100, 100, 200, 200], 'confidence': 0.8, 'class_id': 0}
        ]
        
        # Create mock frame
        mock_frame = Mock()
        
        # Create tracked_objects_by_frame dict
        tracked_objects_by_frame = {}
        
        # Call function
        result = process_keyframe(
            frame_idx=10,
            frame=mock_frame,
            detector=mock_detector,
            tracker=mock_tracker,
            tracked_objects_by_frame=tracked_objects_by_frame,
            track_count=1
        )
        
        # Verify results
        assert result == 10
        assert 10 in tracked_objects_by_frame
        assert len(tracked_objects_by_frame[10]) == 1
        
        # Verify detector and tracker were called
        mock_detector.detect.assert_called_once_with(mock_frame, top_n=1)
        mock_tracker.update.assert_called_once_with(mock_frame, mock_detector.detect.return_value)


class TestMainScriptExecution:
    """Test the main script execution."""
    
    @pytest.mark.integration
    @pytest.mark.requires_video
    def test_main_script_can_run(self, sample_video_path, output_dir):
        """Test that the main script can run without crashing."""
        if not sample_video_path:
            pytest.skip("Sample video not available")
        
        # Create output path
        output_path = os.path.join(output_dir, "test_output.mp4")
        
        # Create test arguments
        args = Mock()
        args.input = sample_video_path
        args.output = output_path
        args.target_ratio = 9/16
        args.max_workers = 1  # Use single worker for testing
        args.conf_threshold = 0.3
        args.model_size = 'n'
        args.object_classes = [0]
        args.debug = False
        args.padding_ratio = 0.1
        args.size_weight = 0.4
        args.center_weight = 0.3
        args.motion_weight = 0.3
        args.history_weight = 0.1
        args.saliency_weight = 0.4
        args.face_detection = False
        args.weighted_center = False
        args.blend_saliency = False
        args.apply_smoothing = False
        args.smoothing_window = 30
        args.position_inertia = 0.8
        args.size_inertia = 0.9
        args.skip_frames = 30  # Process fewer frames for faster testing
        args.track_count = 1
        
        # Test that main function can be called without crashing
        try:
            main(args)
            # If we get here, the script ran successfully
            assert True
        except Exception as e:
            pytest.fail(f"Main script failed to run: {e}")
    
    @pytest.mark.integration
    def test_main_script_argument_validation(self):
        """Test that the main script validates arguments properly."""
        # Test with missing required arguments
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['main.py']):
                parse_args()
        
        # Test with invalid model size
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['main.py', '--input', 'test.mp4', '--output', 'out.mp4', '--model_size', 'invalid']):
                parse_args()
        
        # Test with invalid confidence threshold
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['main.py', '--input', 'test.mp4', '--output', 'out.mp4', '--conf_threshold', '1.5']):
                parse_args()


if __name__ == "__main__":
    pytest.main([__file__]) 