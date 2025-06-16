import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path
import hashlib

class FFmpegManager:
    def __init__(self):
        self.ffmpeg_dir = self._get_ffmpeg_dir()
        self.ffmpeg_path = self._get_ffmpeg_path()
        
    def _get_ffmpeg_dir(self):
        """Get the directory where ffmpeg should be stored."""
        if getattr(sys, 'frozen', False):
            # Running in a bundle
            if platform.system() == 'Darwin':  # macOS
                bundle_path = Path(os.path.dirname(sys.executable)).parent.parent
                return bundle_path / 'Resources' / 'ffmpeg'
            else:
                return Path(os.path.dirname(sys.executable)) / 'ffmpeg'
        else:
            # Running in development
            return Path(__file__).parent / 'ffmpeg'
    
    def _get_ffmpeg_path(self):
        """Get the path to the ffmpeg executable."""
        if platform.system() == 'Windows':
            return self.ffmpeg_dir / 'ffmpeg.exe'
        else:
            return self.ffmpeg_dir / 'ffmpeg'
    
    def _get_ffmpeg_url(self):
        """Get the appropriate ffmpeg download URL for the current platform (official ffmpeg.org builds)."""
        system = platform.system()
        machine = platform.machine().lower()

        # Official ffmpeg.org builds
        if system == 'Darwin':  # macOS
            # Official builds are universal (arm64 + x86_64) as of 2024
            # https://evermeet.cx/ffmpeg/ is linked from ffmpeg.org for macOS static builds
            return "https://evermeet.cx/ffmpeg/ffmpeg-6.1.1.zip"
        elif system == 'Windows':
            # Official builds: https://www.gyan.dev/ffmpeg/builds/ (linked from ffmpeg.org)
            return "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        elif system == 'Linux':
            # Official static builds: https://johnvansickle.com/ffmpeg/ (linked from ffmpeg.org)
            return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        else:
            raise RuntimeError(f"Unsupported platform: {system} {machine}")
    
    def _download_file(self, url, filepath):
        """Download a file from URL to filepath."""
        print(f"Downloading ffmpeg from {url}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(response, f)
            print("Download completed successfully!")
        except Exception as e:
            print(f"Download failed: {e}")
            raise
    
    def _extract_archive(self, archive_path, extract_to):
        """Extract downloaded archive."""
        print(f"Extracting {archive_path} to {extract_to}...")
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix in ['.xz', '.tar', '.tar.xz', '.tar.gz']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
        print("Extraction completed!")
    
    def _find_ffmpeg_in_extracted(self, extract_dir):
        """Find the ffmpeg executable in the extracted directory."""
        system = platform.system()
        if system == 'Windows':
            for root, dirs, files in os.walk(extract_dir):
                if 'ffmpeg.exe' in files:
                    return Path(root) / 'ffmpeg.exe'
        else:
            for root, dirs, files in os.walk(extract_dir):
                if 'ffmpeg' in files:
                    ffmpeg_path = Path(root) / 'ffmpeg'
                    os.chmod(ffmpeg_path, 0o755)
                    return ffmpeg_path
        raise FileNotFoundError("Could not find ffmpeg executable in extracted archive")
    
    def _check_ffmpeg_works(self, ffmpeg_path):
        """Check if ffmpeg works by running a simple command."""
        try:
            result = subprocess.run([str(ffmpeg_path), '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def install_ffmpeg(self):
        """Download and install ffmpeg if not already present."""
        if self.ffmpeg_path.exists() and self._check_ffmpeg_works(self.ffmpeg_path):
            print(f"FFmpeg already installed and working: {self.ffmpeg_path}")
            return str(self.ffmpeg_path)
        
        # Create ffmpeg directory if it doesn't exist
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
        
        # Get download URL
        url = self._get_ffmpeg_url()
        
        # Download archive
        archive_path = self.ffmpeg_dir / f"ffmpeg_archive{Path(url).suffix}"
        self._download_file(url, archive_path)
        
        # Extract archive
        temp_extract_dir = self.ffmpeg_dir / "temp_extract"
        temp_extract_dir.mkdir(exist_ok=True)
        self._extract_archive(archive_path, temp_extract_dir)
        
        # Find ffmpeg executable in extracted files
        ffmpeg_executable = self._find_ffmpeg_in_extracted(temp_extract_dir)
        
        # Move to final location
        if platform.system() == 'Windows':
            shutil.move(str(ffmpeg_executable), str(self.ffmpeg_path))
        else:
            shutil.move(str(ffmpeg_executable), str(self.ffmpeg_path))
        
        # Clean up
        shutil.rmtree(temp_extract_dir)
        archive_path.unlink()
        
        # Verify installation
        if self._check_ffmpeg_works(self.ffmpeg_path):
            print(f"FFmpeg installed successfully: {self.ffmpeg_path}")
            return str(self.ffmpeg_path)
        else:
            raise RuntimeError("FFmpeg installation failed - executable doesn't work")
    
    def get_ffmpeg_path(self):
        """Get the path to ffmpeg, installing it if necessary."""
        try:
            return self.install_ffmpeg()
        except Exception as e:
            print(f"Failed to install ffmpeg: {e}")
            print("Falling back to system ffmpeg...")
            return 'ffmpeg'  # Fallback to system ffmpeg

# Global instance
_ffmpeg_manager = None

def get_ffmpeg_path():
    """Get the path to ffmpeg, installing it if necessary."""
    global _ffmpeg_manager
    if _ffmpeg_manager is None:
        _ffmpeg_manager = FFmpegManager()
    return _ffmpeg_manager.get_ffmpeg_path() 