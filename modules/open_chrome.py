'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

import os
import subprocess
import requests
from modules.helpers import make_directories
from config.settings import (
    run_in_background, stealth_mode, disable_extensions, safe_mode, 
    file_name, failed_file_name, logs_folder_path, generated_resume_path,
    running_in_actions, downloads_path, is_linux
)
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from webdriver_manager.chrome import ChromeDriverManager

def get_platform():
    """Get the current platform for ChromeDriver download"""
    import platform
    system = platform.system().lower()
    machine = platform.machine()
    if system == "linux":
        return "linux64"
    elif system == "darwin":
        return "mac_arm64" if machine == "arm64" else "mac64"
    elif system == "windows":
        return "win64"
    return "linux64"  # default to linux64

def get_chrome_version():
    """Get installed Chrome version"""
    try:
        # Prioritize actual Chrome installation over Chrome for Testing
        commands = [
            ['/opt/google/chrome/chrome', '--version'],  # Ubuntu default path
            ['/usr/bin/google-chrome', '--version'],     # Alternative Ubuntu path
            ['google-chrome', '--version'],              # Try general command last
        ]
        for cmd in commands:
            try:
                version = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                version = version.decode().strip()
                # Handle version string formats, prioritizing actual Chrome
                if 'Google Chrome' in version and 'Testing' not in version:
                    version = version.split('Google Chrome ')[1]
                    # Extract version using regex
                    import re
                    version_match = re.search(r'(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?', version)
                    if version_match:
                        full_version = version_match.group(0)
                        major_version = version_match.group(1)
                        print_lg(f"Detected Chrome version: {full_version} (Major: {major_version})")
                        return major_version, full_version
            except Exception as e:
                continue
        return None, None
    except Exception as e:
        print_lg(f"Error in get_chrome_version: {e}")
        return None, None

def get_compatible_chromedriver_version(chrome_major_version):
    """Get compatible ChromeDriver version"""
    try:
        print_lg(f"Finding ChromeDriver version for Chrome {chrome_major_version}")
        
        # Try regular ChromeDriver first
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            version = response.text.strip()
            print_lg(f"Found ChromeDriver version: {version}")
            return version, False
        
        # Fall back to Chrome for Testing only if regular ChromeDriver not found
        url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            version = response.text.strip()
            print_lg(f"Found Chrome for Testing version: {version}")
            return version, True
        
        # If no exact match, try previous version with regular ChromeDriver
        prev_version = str(int(chrome_major_version) - 1)
        print_lg(f"No exact match found, trying Chrome version {prev_version}")
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{prev_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            version = response.text.strip()
            print_lg(f"Found ChromeDriver version for previous version: {version}")
            return version, False
            
        print_lg("No compatible ChromeDriver version found")
        return None, False
    except Exception as e:
        print_lg(f"Error finding compatible ChromeDriver version: {e}")
        return None, False

try:
    # Set up directories with proper Linux paths
    driver_dir = os.path.expanduser('~/.local/bin') if is_linux or running_in_actions else os.path.join(os.path.expanduser('~'), '.webdrivers')
    os.makedirs(driver_dir, exist_ok=True)
    os.environ["PATH"] = f"{driver_dir}:{os.environ.get('PATH', '')}"

    # Get Chrome version and compatible chromedriver
    chrome_major_version, chrome_full_version = get_chrome_version()
    if not chrome_major_version:
        raise Exception("Failed to detect Chrome version. Please ensure Chrome is installed.")
    
    chromedriver_version, is_chrome_for_testing = get_compatible_chromedriver_version(chrome_major_version)
    if not chromedriver_version:
        raise Exception(f"Failed to find compatible ChromeDriver version for Chrome {chrome_major_version}")
    
    print_lg(f"Using {'Chrome for Testing' if is_chrome_for_testing else 'ChromeDriver'} version: {chromedriver_version}")
    
    # Download and install correct chromedriver
    platform = get_platform()
    if is_chrome_for_testing:
        driver_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromedriver_version}/{platform}/chromedriver-{platform}.zip"
    else:
        driver_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform}.zip"
    
    # Clean up existing ChromeDriver files
    chromedriver_path = os.path.join(driver_dir, 'chromedriver')
    driver_zip = os.path.join(driver_dir, "chromedriver.zip")
    try:
        if os.path.exists(chromedriver_path):
            os.remove(chromedriver_path)
        if os.path.exists(driver_zip):
            os.remove(driver_zip)
    except:
        pass

    print_lg(f"Downloading ChromeDriver from: {driver_url}")
    r = requests.get(driver_url)
    if r.status_code != 200:
        raise Exception(f"Failed to download ChromeDriver from {driver_url}")
    
    with open(driver_zip, 'wb') as f:
        f.write(r.content)
    
    # Extract with platform-specific paths
    extract_dir = os.path.join(driver_dir, 'temp_extract')
    os.makedirs(extract_dir, exist_ok=True)
    
    # Use proper unzip command with error handling
    unzip_result = os.system(f"cd {extract_dir} && unzip -o {driver_zip}")
    if unzip_result != 0:
        raise Exception("Failed to extract ChromeDriver")
        
    if is_chrome_for_testing:
        copy_result = os.system(f"cp -f {extract_dir}/chromedriver-{platform}/chromedriver {chromedriver_path}")
    else:
        copy_result = os.system(f"cp -f {extract_dir}/chromedriver {chromedriver_path}")
        
    if copy_result != 0:
        raise Exception("Failed to copy ChromeDriver to final location")
        
    chmod_result = os.system(f"chmod +x {chromedriver_path}")
    if chmod_result != 0:
        raise Exception("Failed to set ChromeDriver permissions")
    
    # Clean up temporary files
    try:
        os.system(f"rm -rf {extract_dir}")
        os.remove(driver_zip)
    except Exception as e:
        print_lg(f"Warning: Failed to clean up temporary files: {e}")

    # Configure Chrome options for headless/background operation
    options = uc.ChromeOptions() if stealth_mode else webdriver.ChromeOptions()
    
    if run_in_background or running_in_actions or is_linux:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    
    if disable_extensions:
        options.add_argument("--disable-extensions")
    
    # Set up Chrome preferences
    prefs = {
        "download.default_directory": downloads_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    
    if not stealth_mode:
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    # Use guest profile in headless mode
    if safe_mode or running_in_actions or is_linux:
        print_lg("SAFE MODE: Will login with a guest profile, browsing history will not be saved in the browser!")
        options.add_argument("--guest")
    else:
        profile_dir = find_default_profile_directory()
        if profile_dir and not stealth_mode:
            options.add_argument(f"--user-data-dir={profile_dir}")
        else:
            print_lg("Default profile directory not found. Logging in with a guest profile, Web history will not be saved!")

    # Initialize WebDriver
    if stealth_mode:
        print_lg("Using undetected-chromedriver mode...")
        driver = uc.Chrome(options=options)
    else:
        print_lg("Using standard selenium webdriver...")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)

except Exception as e:
    msg = """Seems like either... 
1. Chrome is already running. 
A. Close all Chrome windows and try again. 
2. Google Chrome or Chromedriver is out dated. 
A. Update browser and Chromedriver (You can run "setup.sh" in /setup folder for Ubuntu to update Chromedriver)! 
3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. 
A. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". 
If issue persists, try Safe Mode. Set, safe_mode = True in config.py"""
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    try:
        driver.quit()
    except NameError:
        exit()

def open_chrome():
    """Initialize Chrome with optimal settings for Ubuntu"""
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        
        # Basic options for stability on Ubuntu
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        if run_in_background or running_in_actions or is_linux:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
        
        if disable_extensions:
            options.add_argument('--disable-extensions')
            
        if safe_mode:
            options.add_argument('--guest')
            
        # Set up downloads directory and other preferences
        prefs = {
            "download.default_directory": downloads_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Use ChromeDriverManager for better compatibility
        service = Service(ChromeDriverManager(cache_valid_range=1).install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Maximize window and set page load timeout
        driver.maximize_window()
        driver.set_page_load_timeout(30)
        
        # Set up WebDriverWait with longer timeout for Ubuntu
        wait = WebDriverWait(driver, 10)
        actions = ActionChains(driver)
        
        print_lg("Chrome started successfully")
        return driver
    except Exception as e:
        print_lg(f"Error starting Chrome: {str(e)}")
        return None

