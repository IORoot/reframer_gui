"""
Tests for the ffmpeg_manager.py module.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Import the ffmpeg manager
from ffmpeg_manager import get_ffmpeg_path, download_ffmpeg, FFmpegManager


class TestFFmpegManagerInitialization:
    """Test FFmpegManager initialization."""
    
    def test_ffmpeg_manager_init(self):
        """Test FFmpegManager initialization."""
        manager = FFmpegManager()
        
        assert manager.ffmpeg_dir is not None
        assert isinstance(manager.ffmpeg_dir, Path)
        assert manager.ffmpeg_path is not None
        assert isinstance(manager.ffmpeg_path, Path)
    
    def test_ffmpeg_manager_custom_dir(self):
        """Test FFmpegManager initialization with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FFmpegManager(ffmpeg_dir=temp_dir)
            
            assert manager.ffmpeg_dir == Path(temp_dir)
            assert manager.ffmpeg_path == Path(temp_dir) / "ffmpeg"


class TestFFmpegManagerPathDetection:
    """Test FFmpeg path detection functionality."""
    
    @patch('ffmpeg_manager.shutil.which')
    def test_detect_system_ffmpeg_success(self, mock_which):
        """Test successful detection of system FFmpeg."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        manager = FFmpegManager()
        result = manager.detect_system_ffmpeg()
        
        assert result == '/usr/bin/ffmpeg'
        mock_which.assert_called_once_with('ffmpeg')
    
    @patch('ffmpeg_manager.shutil.which')
    def test_detect_system_ffmpeg_not_found(self, mock_which):
        """Test detection when system FFmpeg is not found."""
        mock_which.return_value = None
        
        manager = FFmpegManager()
        result = manager.detect_system_ffmpeg()
        
        assert result is None
        mock_which.assert_called_once_with('ffmpeg')
    
    @patch('ffmpeg_manager.subprocess.run')
    def test_verify_ffmpeg_success(self, mock_run):
        """Test successful FFmpeg verification."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ffmpeg version 4.2.7"
        
        manager = FFmpegManager()
        result = manager.verify_ffmpeg('/usr/bin/ffmpeg')
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('ffmpeg_manager.subprocess.run')
    def test_verify_ffmpeg_failure(self, mock_run):
        """Test FFmpeg verification failure."""
        mock_run.return_value.returncode = 1
        
        manager = FFmpegManager()
        result = manager.verify_ffmpeg('/usr/bin/ffmpeg')
        
        assert result is False
        mock_run.assert_called_once()
    
    @patch('ffmpeg_manager.subprocess.run')
    def test_verify_ffmpeg_timeout(self, mock_run):
        """Test FFmpeg verification timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(['ffmpeg', '-version'], 10)
        
        manager = FFmpegManager()
        result = manager.verify_ffmpeg('/usr/bin/ffmpeg')
        
        assert result is False


class TestFFmpegManagerDownload:
    """Test FFmpeg downloading functionality."""
    
    @patch('ffmpeg_manager.requests.get')
    @patch('ffmpeg_manager.zipfile.ZipFile')
    def test_download_ffmpeg_success(self, mock_zipfile, mock_get):
        """Test successful FFmpeg download."""
        # Mock the download response
        mock_response = Mock()
        mock_response.content = b'fake_ffmpeg_content'
        mock_get.return_value = mock_response
        
        # Mock the zip file
        mock_zip = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FFmpegManager(ffmpeg_dir=temp_dir)
            
            # Test download
            result = manager.download_ffmpeg()
            
            # Verify download was attempted
            mock_get.assert_called()
            mock_zipfile.assert_called()
            
            # Verify result
            assert result is True
    
    @patch('ffmpeg_manager.requests.get')
    def test_download_ffmpeg_network_error(self, mock_get):
        """Test FFmpeg download with network error."""
        mock_get.side_effect = Exception("Network error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FFmpegManager(ffmpeg_dir=temp_dir)
            
            # Test download
            result = manager.download_ffmpeg()
            
            # Verify result
            assert result is False
    
    @patch('ffmpeg_manager.requests.get')
    @patch('ffmpeg_manager.zipfile.ZipFile')
    def test_download_ffmpeg_extraction_error(self, mock_zipfile, mock_get):
        """Test FFmpeg download with extraction error."""
        # Mock the download response
        mock_response = Mock()
        mock_response.content = b'fake_ffmpeg_content'
        mock_get.return_value = mock_response
        
        # Mock the zip file to raise an exception
        mock_zipfile.side_effect = Exception("Extraction error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FFmpegManager(ffmpeg_dir=temp_dir)
            
            # Test download
            result = manager.download_ffmpeg()
            
            # Verify result
            assert result is False


class TestFFmpegManagerGetPath:
    """Test get_ffmpeg_path functionality."""
    
    @patch('ffmpeg_manager.FFmpegManager')
    def test_get_ffmpeg_path_system_available(self, mock_manager_class):
        """Test get_ffmpeg_path when system FFmpeg is available."""
        # Mock the manager
        mock_manager = Mock()
        mock_manager.detect_system_ffmpeg.return_value = '/usr/bin/ffmpeg'
        mock_manager.verify_ffmpeg.return_value = True
        mock_manager_class.return_value = mock_manager
        
        # Test get_ffmpeg_path
        result = get_ffmpeg_path()
        
        # Verify result
        assert result == '/usr/bin/ffmpeg'
        
        # Verify manager was called correctly
        mock_manager.detect_system_ffmpeg.assert_called_once()
        mock_manager.verify_ffmpeg.assert_called_once_with('/usr/bin/ffmpeg')
    
    @patch('ffmpeg_manager.FFmpegManager')
    def test_get_ffmpeg_path_download_required(self, mock_manager_class):
        """Test get_ffmpeg_path when download is required."""
        # Mock the manager
        mock_manager = Mock()
        mock_manager.detect_system_ffmpeg.return_value = None  # No system FFmpeg
        mock_manager.verify_ffmpeg.return_value = True
        mock_manager.download_ffmpeg.return_value = True
        mock_manager.ffmpeg_path = '/tmp/ffmpeg/ffmpeg'
        mock_manager_class.return_value = mock_manager
        
        # Test get_ffmpeg_path
        result = get_ffmpeg_path()
        
        # Verify result
        assert result == '/tmp/ffmpeg/ffmpeg'
        
        # Verify manager was called correctly
        mock_manager.detect_system_ffmpeg.assert_called_once()
        mock_manager.download_ffmpeg.assert_called_once()
        mock_manager.verify_ffmpeg.assert_called_once_with('/tmp/ffmpeg/ffmpeg')
    
    @patch('ffmpeg_manager.FFmpegManager')
    def test_get_ffmpeg_path_download_failed(self, mock_manager_class):
        """Test get_ffmpeg_path when download fails."""
        # Mock the manager
        mock_manager = Mock()
        mock_manager.detect_system_ffmpeg.return_value = None  # No system FFmpeg
        mock_manager.download_ffmpeg.return_value = False  # Download failed
        mock_manager_class.return_value = mock_manager
        
        # Test get_ffmpeg_path
        with pytest.raises(RuntimeError, match="Failed to download FFmpeg"):
            get_ffmpeg_path()
        
        # Verify manager was called correctly
        mock_manager.detect_system_ffmpeg.assert_called_once()
        mock_manager.download_ffmpeg.assert_called_once()


class TestFFmpegManagerPlatformDetection:
    """Test platform-specific functionality."""
    
    @patch('ffmpeg_manager.platform.system')
    @patch('ffmpeg_manager.platform.machine')
    def test_get_download_url_macos(self, mock_machine, mock_system):
        """Test download URL generation for macOS."""
        mock_system.return_value = 'Darwin'
        mock_machine.return_value = 'x86_64'
        
        manager = FFmpegManager()
        url = manager.get_download_url()
        
        assert 'macos' in url.lower()
        assert 'x86_64' in url
    
    @patch('ffmpeg_manager.platform.system')
    @patch('ffmpeg_manager.platform.machine')
    def test_get_download_url_windows(self, mock_machine, mock_system):
        """Test download URL generation for Windows."""
        mock_system.return_value = 'Windows'
        mock_machine.return_value = 'AMD64'
        
        manager = FFmpegManager()
        url = manager.get_download_url()
        
        assert 'windows' in url.lower()
        assert 'amd64' in url
    
    @patch('ffmpeg_manager.platform.system')
    @patch('ffmpeg_manager.platform.machine')
    def test_get_download_url_linux(self, mock_machine, mock_system):
        """Test download URL generation for Linux."""
        mock_system.return_value = 'Linux'
        mock_machine.return_value = 'x86_64'
        
        manager = FFmpegManager()
        url = manager.get_download_url()
        
        assert 'linux' in url.lower()
        assert 'x86_64' in url
    
    @patch('ffmpeg_manager.platform.system')
    def test_get_download_url_unsupported_platform(self, mock_system):
        """Test download URL generation for unsupported platform."""
        mock_system.return_value = 'UnsupportedOS'
        
        manager = FFmpegManager()
        
        with pytest.raises(NotImplementedError, match="Unsupported platform"):
            manager.get_download_url()


class TestFFmpegManagerIntegration:
    """Integration tests for FFmpegManager."""
    
    @pytest.mark.integration
    def test_ffmpeg_manager_full_workflow(self):
        """Test the full FFmpegManager workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FFmpegManager(ffmpeg_dir=temp_dir)
            
            # Test system detection
            system_ffmpeg = manager.detect_system_ffmpeg()
            
            # If system FFmpeg is available, test verification
            if system_ffmpeg:
                is_valid = manager.verify_ffmpeg(system_ffmpeg)
                assert isinstance(is_valid, bool)
            
            # Test that manager can be created without errors
            assert manager.ffmpeg_dir == Path(temp_dir)
            assert manager.ffmpeg_path == Path(temp_dir) / "ffmpeg"
    
    @pytest.mark.integration
    def test_get_ffmpeg_path_integration(self):
        """Test get_ffmpeg_path integration."""
        try:
            # This should either return a valid path or raise an exception
            ffmpeg_path = get_ffmpeg_path()
            
            # If we get here, we should have a valid path
            assert isinstance(ffmpeg_path, str)
            assert len(ffmpeg_path) > 0
            
            # Test that the path exists (if it's a local path)
            if os.path.exists(ffmpeg_path):
                assert os.path.isfile(ffmpeg_path)
                
        except RuntimeError as e:
            # It's okay if FFmpeg is not available and download fails
            assert "Failed to download FFmpeg" in str(e)


class TestFFmpegManagerErrorHandling:
    """Test error handling in FFmpegManager."""
    
    def test_ffmpeg_manager_invalid_directory(self):
        """Test FFmpegManager with invalid directory."""
        with pytest.raises(ValueError, match="Invalid ffmpeg_dir"):
            FFmpegManager(ffmpeg_dir="/nonexistent/directory")
    
    def test_ffmpeg_manager_permission_error(self):
        """Test FFmpegManager with permission error."""
        # Create a read-only directory
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chmod(temp_dir, 0o444)  # Read-only
            
            try:
                with pytest.raises(PermissionError):
                    FFmpegManager(ffmpeg_dir=temp_dir)
            finally:
                os.chmod(temp_dir, 0o755)  # Restore permissions


if __name__ == "__main__":
    pytest.main([__file__]) 