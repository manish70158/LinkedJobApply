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
    running_in_actions, downloads_path
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

def get_compatible_chromedriver_version(chrome_major_version):
    try:
        # Try Chrome for Testing first
        url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            return response.text.strip(), True
            
        # Fall back to regular ChromeDriver
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            return response.text.strip(), False
            
        # Try previous versions
        for version in range(int(chrome_major_version)-1, int(chrome_major_version)-5, -1):
            url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}"
            response = requests.get(url)
            if response.status_code == 200 and not "Error" in response.text:
                return response.text.strip(), False
    except:
        pass
    return None, False

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
        # Try different commands for different platforms
        commands = [
            ['google-chrome', '--version'],  # Ubuntu/Linux
            ['google-chrome-stable', '--version'],  # Alternative Linux name
            ['chrome', '--version'],
            ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version']
        ]
        for cmd in commands:
            try:
                version = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                version = version.decode().strip()
                # Handle Ubuntu-style version string
                if 'Google Chrome' in version:
                    version = version.split('Google Chrome ')[1]
                version = version.split()[0]  # Get first word in case of extra text
                major_version = version.split('.')[0]
                return major_version, version
            except:
                continue
        return None, None
    except:
        return None, None

try:
    # Check for existing Chrome instances and create lock file in /tmp for Ubuntu
    lock_file = '/tmp/chrome.lock' if os.name == 'posix' else os.path.join(os.path.expanduser('~'), '.chrome_lock')
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except:
            raise Exception("Chrome appears to be already running. Please close all Chrome windows and try again.")
    
    # Create lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    # Set up directories with proper Linux paths
    make_directories([file_name, failed_file_name, logs_folder_path+"/screenshots", default_resume_path, generated_resume_path+"/temp", downloads_path])

    # Set up local driver directory in ~/.local/bin for Ubuntu
    if os.name == 'posix':
        driver_dir = os.path.expanduser('~/.local/bin')
    else:
        driver_dir = os.path.join(os.path.expanduser('~'), '.webdrivers')
    os.makedirs(driver_dir, exist_ok=True)
    os.environ["PATH"] = f"{driver_dir}:{os.environ.get('PATH', '')}"

    # Get Chrome version and compatible chromedriver
    chrome_major_version, chrome_full_version = get_chrome_version()
    if chrome_major_version:
        print_lg(f"Detected Chrome version: {chrome_full_version} (Major: {chrome_major_version})")
        chromedriver_version, is_chrome_for_testing = get_compatible_chromedriver_version(chrome_major_version)
        if chromedriver_version:
            print_lg(f"Using {'Chrome for Testing' if is_chrome_for_testing else 'ChromeDriver'} version: {chromedriver_version}")
            os.environ["CHROMEDRIVER_VERSION"] = chromedriver_version
            
            # Download and install correct chromedriver
            try:
                platform = get_platform()
                if is_chrome_for_testing:
                    driver_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromedriver_version}/{platform}/chromedriver-{platform}.zip"
                else:
                    driver_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform}.zip"
                
                driver_zip = os.path.join(driver_dir, "chromedriver.zip")
                print_lg(f"Downloading ChromeDriver from: {driver_url}")
                r = requests.get(driver_url)
                with open(driver_zip, 'wb') as f:
                    f.write(r.content)
                
                # Extract with platform-specific paths
                if platform == "linux64":
                    os.system(f"cd {driver_dir} && unzip -o chromedriver.zip && chmod +x chromedriver")
                else:
                    os.system(f"cd {driver_dir} && unzip -o chromedriver.zip")
                
                if os.path.exists(driver_zip):
                    os.remove(driver_zip)
            except Exception as e:
                print_lg(f"Error downloading ChromeDriver: {e}")

    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    
    # Configure Chrome for headless/background operation
    if run_in_background or running_in_actions:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # Required for running Chrome as root in Ubuntu
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
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

    # Use guest profile in Ubuntu for stability
    if safe_mode or running_in_actions:
        print_lg("SAFE MODE: Will login with a guest profile, browsing history will not be saved in the browser!")
    else:
        profile_dir = find_default_profile_directory()
        if profile_dir and not stealth_mode:
            options.add_argument(f"--user-data-dir={profile_dir}")
        else:
            print_lg("Default profile directory not found. Logging in with a guest profile, Web history will not be saved!")

    if stealth_mode:
        print_lg("Using undetected-chromedriver mode...")
        driver = uc.Chrome(options=options)
    else:
        print_lg("Using standard selenium webdriver...")
        chromedriver_path = os.path.join(driver_dir, 'chromedriver')
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)

except Exception as e:
    # Remove lock file on error
    try:
        os.remove(lock_file)
    except:
        pass
    
    msg = """Seems like either... 

1. Chrome is already running. 
A. Close all Chrome windows and try again. 

2. Google Chrome or Chromedriver is out dated. 
A. Update browser and Chromedriver (You can run "setup.sh" in /setup folder for Ubuntu to update Chromedriver)! 

3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. 
A. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". 

If issue persists, try Safe Mode. Set, safe_mode = True in config.py"""
    if isinstance(e, TimeoutError):
        msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    try:
        driver.quit()
    except NameError:
        exit()

def open_chrome():
    options = webdriver.ChromeOptions()
    if run_in_background:
        options.add_argument('--headless')
    if disable_extensions:
        options.add_argument('--disable-extensions')
    if safe_mode:
        options.add_argument('--guest')
    
    # Set up Chrome service using webdriver-manager
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        print("Chrome started successfully")
        return driver
    except Exception as e:
        print(f"Error starting Chrome: {str(e)}")
        return None

