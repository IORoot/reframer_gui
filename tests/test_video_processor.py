"""
Tests for the video_processor.py module.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
import shutil

# Import the video processor
from video_processor import VideoProcessor


class TestVideoProcessorInitialization:
    """Test VideoProcessor initialization."""
    
    def test_video_processor_init(self):
        """Test VideoProcessor initialization."""
        processor = VideoProcessor()
        
        assert processor.cap is None
        assert processor.output_writer is None
    
    def test_video_processor_context_manager(self):
        """Test VideoProcessor as context manager."""
        with VideoProcessor() as processor:
            assert processor.cap is None
            assert processor.output_writer is None


class TestVideoProcessorVideoLoading:
    """Test video loading functionality."""
    
    @patch('video_processor.cv2.VideoCapture')
    def test_load_video_success(self, mock_video_capture):
        """Test successful video loading."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 300,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        
        mock_video_capture.return_value = mock_cap
        
        # Create processor and load video
        processor = VideoProcessor()
        video_info = processor.load_video('test_video.mp4')
        
        # Verify video capture was created
        mock_video_capture.assert_called_once_with('test_video.mp4')
        
        # Verify video info
        assert video_info['total_frames'] == 300
        assert video_info['fps'] == 30.0
        assert video_info['width'] == 1920
        assert video_info['height'] == 1080
        
        # Verify cap is set
        assert processor.cap == mock_cap
    
    @patch('video_processor.cv2.VideoCapture')
    def test_load_video_failure(self, mock_video_capture):
        """Test video loading failure."""
        # Create mock video capture that fails to open
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        # Create processor and attempt to load video
        processor = VideoProcessor()
        
        with pytest.raises(ValueError, match="Could not open video file"):
            processor.load_video('nonexistent_video.mp4')
    
    @patch('video_processor.cv2.VideoCapture')
    def test_load_video_file_not_found(self, mock_video_capture):
        """Test video loading when file doesn't exist."""
        # Make VideoCapture raise an exception
        mock_video_capture.side_effect = Exception("File not found")
        
        # Create processor and attempt to load video
        processor = VideoProcessor()
        
        with pytest.raises(Exception, match="File not found"):
            processor.load_video('nonexistent_video.mp4')


class TestVideoProcessorFrameReading:
    """Test frame reading functionality."""
    
    @patch('video_processor.cv2.VideoCapture')
    def test_read_frame_success(self, mock_video_capture):
        """Test successful frame reading."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480
        }.get(prop, 0)
        mock_cap.read.return_value = (True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))
        
        mock_video_capture.return_value = mock_cap
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Read frame
        ret, frame = processor.cap.read()
        
        # Verify frame was read
        assert ret is True
        assert frame is not None
        assert frame.shape == (480, 640, 3)
    
    @patch('video_processor.cv2.VideoCapture')
    def test_read_frame_end_of_video(self, mock_video_capture):
        """Test frame reading at end of video."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480
        }.get(prop, 0)
        mock_cap.read.return_value = (False, None)  # End of video
        
        mock_video_capture.return_value = mock_cap
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Read frame
        ret, frame = processor.cap.read()
        
        # Verify end of video
        assert ret is False
        assert frame is None


class TestVideoProcessorOutputGeneration:
    """Test output video generation functionality."""
    
    @patch('video_processor.cv2.VideoCapture')
    @patch('video_processor.cv2.VideoWriter')
    def test_generate_output_video(self, mock_video_writer, mock_video_capture):
        """Test output video generation."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        
        # Create mock frames
        mock_frames = []
        for i in range(100):
            frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            mock_frames.append(frame)
        
        mock_cap.read.side_effect = [(True, frame) for frame in mock_frames] + [(False, None)]
        
        mock_video_capture.return_value = mock_cap
        
        # Create mock video writer
        mock_writer = Mock()
        mock_video_writer.return_value = mock_writer
        mock_writer.isOpened.return_value = True
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Create crop windows (simple center crop for testing)
        crop_windows = []
        for i in range(100):
            # Center crop: x=480, y=270, w=960, h=540
            crop_windows.append([480, 270, 960, 540])
        
        # Generate output video
        processor.generate_output_video(
            output_path='test_output.mp4',
            crop_windows=crop_windows,
            fps=30.0
        )
        
        # Verify video writer was created
        mock_video_writer.assert_called_once()
        
        # Verify frames were written
        assert mock_writer.write.call_count == 100
        
        # Verify writer was released
        mock_writer.release.assert_called_once()
    
    @patch('video_processor.cv2.VideoCapture')
    @patch('video_processor.cv2.VideoWriter')
    def test_generate_output_video_writer_failure(self, mock_video_writer, mock_video_capture):
        """Test output video generation when writer fails to open."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        
        mock_video_capture.return_value = mock_cap
        
        # Create mock video writer that fails to open
        mock_writer = Mock()
        mock_writer.isOpened.return_value = False
        mock_video_writer.return_value = mock_writer
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Create crop windows
        crop_windows = [[480, 270, 960, 540]] * 100
        
        # Test that exception is raised
        with pytest.raises(ValueError, match="Could not open output video file"):
            processor.generate_output_video(
                output_path='test_output.mp4',
                crop_windows=crop_windows,
                fps=30.0
            )
    
    @patch('video_processor.cv2.VideoCapture')
    @patch('video_processor.cv2.VideoWriter')
    def test_generate_output_video_crop_validation(self, mock_video_writer, mock_video_capture):
        """Test crop window validation in output generation."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        
        mock_video_capture.return_value = mock_cap
        
        # Create mock video writer
        mock_writer = Mock()
        mock_writer.isOpened.return_value = True
        mock_video_writer.return_value = mock_writer
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Test with invalid crop window (negative coordinates)
        invalid_crop_windows = [[-10, -10, 100, 100]] * 100
        
        with pytest.raises(ValueError, match="Invalid crop window"):
            processor.generate_output_video(
                output_path='test_output.mp4',
                crop_windows=invalid_crop_windows,
                fps=30.0
            )
        
        # Test with invalid crop window (out of bounds)
        out_of_bounds_crop_windows = [[2000, 2000, 100, 100]] * 100
        
        with pytest.raises(ValueError, match="Crop window out of bounds"):
            processor.generate_output_video(
                output_path='test_output.mp4',
                crop_windows=out_of_bounds_crop_windows,
                fps=30.0
            )


class TestVideoProcessorCleanup:
    """Test cleanup functionality."""
    
    @patch('video_processor.cv2.VideoCapture')
    def test_cleanup(self, mock_video_capture):
        """Test cleanup of video processor."""
        # Create mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480
        }.get(prop, 0)
        
        mock_video_capture.return_value = mock_cap
        
        # Create processor and load video
        processor = VideoProcessor()
        processor.load_video('test_video.mp4')
        
        # Verify cap is set
        assert processor.cap is not None
        
        # Cleanup
        processor.cleanup()
        
        # Verify cap was released
        mock_cap.release.assert_called_once()
        assert processor.cap is None
    
    def test_cleanup_no_cap(self):
        """Test cleanup when no video is loaded."""
        processor = VideoProcessor()
        
        # Cleanup should not crash
        processor.cleanup()
        assert processor.cap is None


class TestVideoProcessorIntegration:
    """Integration tests for VideoProcessor."""
    
    @pytest.mark.integration
    @pytest.mark.requires_video
    def test_full_video_processing(self, sample_video_path, output_dir):
        """Test full video processing pipeline."""
        if not sample_video_path:
            pytest.skip("Sample video not available")
        
        # Create output path
        output_path = os.path.join(output_dir, "test_output.mp4")
        
        # Create processor
        processor = VideoProcessor()
        
        try:
            # Load video
            video_info = processor.load_video(sample_video_path)
            
            # Verify video info
            assert video_info['total_frames'] > 0
            assert video_info['fps'] > 0
            assert video_info['width'] > 0
            assert video_info['height'] > 0
            
            # Create simple crop windows (center crop)
            crop_windows = []
            for i in range(video_info['total_frames']):
                # Simple center crop
                crop_width = video_info['width'] // 2
                crop_height = video_info['height'] // 2
                x = (video_info['width'] - crop_width) // 2
                y = (video_info['height'] - crop_height) // 2
                crop_windows.append([x, y, crop_width, crop_height])
            
            # Generate output video
            processor.generate_output_video(
                output_path=output_path,
                crop_windows=crop_windows,
                fps=video_info['fps']
            )
            
            # Verify output file was created
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
        finally:
            # Cleanup
            processor.cleanup()


if __name__ == "__main__":
    pytest.main([__file__]) 