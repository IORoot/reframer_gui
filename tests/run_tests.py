left -- richardparsons@daleuw.com
andrewbruce@daleuw.com

owen 

#!/usr/bin/env python3
"""
Test runner script for Reframer GUI backend tests.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type='all', coverage=False, verbose=False, parallel=False, output_format='text'):
    """
    Run the test suite with specified options.
    
    Args:
        test_type (str): Type of tests to run ('all', 'unit', 'integration', 'fast')
        coverage (bool): Whether to generate coverage report
        verbose (bool): Whether to run tests in verbose mode
        parallel (bool): Whether to run tests in parallel
        output_format (str): Output format ('text', 'html', 'json')
    """
    
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory
    cmd.append(str(test_dir))
    
    # Add markers based on test type
    if test_type == 'unit':
        cmd.extend(['-m', 'unit'])
    elif test_type == 'integration':
        cmd.extend(['-m', 'integration'])
    elif test_type == 'fast':
        cmd.extend(['-m', 'not slow'])
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=python', '--cov-report=html', '--cov-report=term'])
    
    # Add verbose flag
    if verbose:
        cmd.append('-v')
    
    # Add parallel execution
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    # Add output format
    if output_format == 'html':
        cmd.extend(['--html=test_results.html', '--self-contained-html'])
    elif output_format == 'json':
        cmd.extend(['--json-report', '--json-report-file=test_results.json'])
    
    # Add additional options
    cmd.extend([
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings',  # Disable warnings
    ])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Test type: {test_type}")
    print(f"Coverage: {coverage}")
    print(f"Verbose: {verbose}")
    print(f"Parallel: {parallel}")
    print(f"Output format: {output_format}")
    print("-" * 50)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run Reframer GUI backend tests')
    
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'unit', 'integration', 'fast'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests in verbose mode'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['text', 'html', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install test dependencies before running tests'
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        test_requirements = Path(__file__).parent / 'requirements-test.txt'
        if test_requirements.exists():
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(test_requirements)
            ], check=True)
            print("Test dependencies installed successfully!")
        else:
            print("Warning: requirements-test.txt not found")
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose,
        parallel=args.parallel,
        output_format=args.output
    )
    
    # Print summary
    print("-" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main() 