import os
import sys
import subprocess
import venv
import platform
from pathlib import Path

def get_app_path():
    """Get the path to the application's resources directory."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        if platform.system() == 'Darwin':  # macOS
            return Path(os.path.dirname(sys.executable)).parent / 'Resources'
        elif platform.system() == 'Windows':
            return Path(os.path.dirname(sys.executable))
        else:  # Linux
            return Path(os.path.dirname(sys.executable))
    else:
        # Running in normal Python environment
        return Path(__file__).parent

def create_venv(venv_path):
    """Create a virtual environment if it doesn't exist."""
    try:
        # Check if venv exists but is incomplete
        if venv_path.exists():
            python_exe = get_python_executable(venv_path)
            if not python_exe.exists():
                print(f"Found incomplete virtual environment at {venv_path}")
                print("Removing incomplete virtual environment...")
                import shutil
                shutil.rmtree(venv_path)
                print("Incomplete virtual environment removed")
        
        if not venv_path.exists():
            print("Creating virtual environment...")
            print(f"Target directory: {venv_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Directory writable: {os.access(os.getcwd(), os.W_OK)}")
            
            # Ensure parent directory exists
            venv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to create the venv with explicit error handling
            try:
                print("Attempting to create virtual environment...")
                venv.create(venv_path, with_pip=True)
                print("Virtual environment created successfully!")
                
                # Verify the venv was created properly
                if not venv_path.exists():
                    raise RuntimeError("Virtual environment directory was not created")
                
                # Check for essential directories
                required_dirs = ['bin', 'lib', 'include']
                for req_dir in required_dirs:
                    if not (venv_path / req_dir).exists():
                        raise RuntimeError(f"Required directory '{req_dir}' was not created")
                
                # Check for Python executable
                python_exe = get_python_executable(venv_path)
                if not python_exe.exists():
                    raise RuntimeError(f"Python executable not found at {python_exe}")
                
                print("Virtual environment structure verified successfully!")
                
            except Exception as venv_error:
                print(f"Built-in venv failed, trying alternative method...")
                print(f"Error: {venv_error}")
                
                # Clean up any partial creation
                if venv_path.exists():
                    import shutil
                    shutil.rmtree(venv_path)
                    print("Cleaned up partial virtual environment")
                
                # Try alternative method using subprocess
                try:
                    print("Attempting to create virtual environment using python -m venv...")
                    import subprocess
                    result = subprocess.run([
                        sys.executable, '-m', 'venv', str(venv_path), '--upgrade-deps'
                    ], capture_output=True, text=True, check=True)
                    print("Virtual environment created using subprocess method!")
                    
                    # Verify again
                    if not venv_path.exists():
                        raise RuntimeError("Virtual environment directory was not created")
                    
                    python_exe = get_python_executable(venv_path)
                    if not python_exe.exists():
                        raise RuntimeError(f"Python executable still not found at {python_exe}")
                    
                    print("Alternative virtual environment creation successful!")
                    
                except Exception as alt_error:
                    print(f"Alternative method also failed: {alt_error}")
                    raise RuntimeError(f"All virtual environment creation methods failed. Original error: {venv_error}, Alternative error: {alt_error}")
        else:
            print(f"Virtual environment already exists at: {venv_path}")
        
        # List contents of venv directory for debugging
        if venv_path.exists():
            print(f"Contents of {venv_path}:")
            for item in venv_path.iterdir():
                print(f"  {item}")
            if (venv_path / 'bin').exists():
                print(f"Contents of {venv_path}/bin:")
                for item in (venv_path / 'bin').iterdir():
                    print(f"  {item}")
        
        # Verify the virtual environment was created properly
        python_exe = get_python_executable(venv_path)
        if not python_exe.exists():
            print(f"Error: Python executable not found at {python_exe}")
            print("Virtual environment creation may have failed")
            return False
        
        print(f"Virtual environment verified: {python_exe}")
        return True
        
    except Exception as e:
        print(f"Exception during virtual environment creation: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_python_executable(venv_path):
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == 'Windows':
        return venv_path / 'Scripts' / 'python.exe'
    return venv_path / 'bin' / 'python'

def get_fallback_python_executable():
    """Get a fallback Python executable from known system locations."""
    if platform.system() == 'Darwin':  # macOS
        # Common macOS Python locations
        fallback_paths = [
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            '/opt/homebrew/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.9/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',
            '/Library/Developer/CommandLineTools/usr/bin/python3',
            '/System/Library/Frameworks/Python.framework/Versions/3.9/bin/python3',
            '/System/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',
            '/System/Library/Frameworks/Python.framework/Versions/3.11/bin/python3'
        ]
    elif platform.system() == 'Windows':
        fallback_paths = [
            'python',
            'python3',
            'C:\\Python39\\python.exe',
            'C:\\Python310\\python.exe',
            'C:\\Python311\\python.exe'
        ]
    else:  # Linux
        fallback_paths = [
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            '/opt/python3/bin/python3',
            'python3'
        ]
    
    # Check each fallback path
    for path in fallback_paths:
        try:
            if platform.system() == 'Windows' and not path.endswith('.exe'):
                # On Windows, try to find the executable
                result = subprocess.run(['where', path], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return path
            else:
                # On Unix-like systems, check if file exists and is executable
                if os.path.exists(path) and os.access(path, os.X_OK):
                    return path
        except Exception:
            continue
    
    # If no fallback found, return the current Python executable
    return sys.executable

def install_requirements(venv_path):
    """Install required packages in the virtual environment."""
    # Try virtual environment Python first, fallback to system Python if needed
    python_exe = get_python_executable(venv_path)
    
    # If virtual environment Python doesn't exist, use fallback
    if not python_exe.exists():
        print(f"Virtual environment Python not found at {python_exe}")
        print("Using fallback Python executable...")
        python_exe = get_fallback_python_executable()
        print(f"Using fallback Python: {python_exe}")
    
    # Look for requirements.txt in the same directory as setup.py
    requirements_path = get_app_path() / 'requirements.txt'
    
    if not requirements_path.exists():
        print("Error: requirements.txt not found!")
        print(f"Looking for requirements.txt at: {requirements_path}")
        return False

    print("Installing required packages...")
    try:
        subprocess.run([
            str(python_exe),
            '-m', 'pip', 'install',
            '--upgrade', 'pip'
        ], check=True)
        
        subprocess.run([
            str(python_exe),
            '-m', 'pip', 'install',
            '-r', str(requirements_path)
        ], check=True)
        
        print("Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def setup():
    """Main setup function."""
    app_path = get_app_path()
    venv_path = app_path / 'python' / 'venv'
    
    print(f"App path: {app_path}")
    print(f"Venv path: {venv_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Is frozen: {getattr(sys, 'frozen', False)}")
    
    # Create virtual environment
    if not create_venv(venv_path):
        print("Failed to create virtual environment")
        return False
    
    # Install requirements
    if install_requirements(venv_path):
        # Create a marker file to indicate successful setup
        (venv_path / '.setup_complete').touch()
        return True
    return False

if __name__ == '__main__':
    success = setup()
    sys.exit(0 if success else 1) 