#!/usr/bin/env python3

import platform
import os
import subprocess
import sys

def run_command(command, shell=False):
    """Run a command and return its output and status"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed with exit code {e.returncode}:\n{e.stderr}"
    except Exception as e:
        return False, str(e)

def run_setup():
    system = platform.system().lower()
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\nDetected operating system: {system}")
    print(f"Setup directory: {setup_dir}\n")
    
    if system == "linux":
        setup_script = os.path.join(setup_dir, "setup-ubuntu.sh")
        print("Linux detected, running Ubuntu setup script...")
        
        # Make script executable
        success, output = run_command(["sudo", "chmod", "+x", setup_script])
        if not success:
            print(f"Failed to make setup script executable: {output}")
            return False
            
        # Run setup script
        success, output = run_command(["sudo", setup_script])
        if not success:
            print(f"Setup script failed: {output}")
            return False
    
    elif system == "darwin":  # macOS
        setup_script = os.path.join(setup_dir, "setup-mac.sh")
        print("macOS detected, running macOS setup script...")
        
        # Make script executable
        success, output = run_command(["chmod", "+x", setup_script])
        if not success:
            print(f"Failed to make setup script executable: {output}")
            return False
            
        # Run setup script
        success, output = run_command([setup_script])
        if not success:
            print(f"Setup script failed: {output}")
            return False
    
    elif system == "windows":
        setup_script = os.path.join(setup_dir, "windows-setup.bat")
        print("Windows detected, running Windows setup script...")
        
        success, output = run_command(setup_script, shell=True)
        if not success:
            print(f"Setup script failed: {output}")
            return False
    
    else:
        print(f"Unsupported operating system: {system}")
        return False
    
    print("\nSetup completed successfully!")
    return True

if __name__ == "__main__":
    try:
        if run_setup():
            print("\nSetup completed successfully!")
            print("You can now run the LinkedIn Auto Job Applier using 'python runAiBot.py'")
            sys.exit(0)
        else:
            print("\nSetup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        sys.exit(1)