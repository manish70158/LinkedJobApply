'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla
'''

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import (
    run_in_background, disable_extensions, safe_mode, 
    downloads_path
)
from modules.helpers import print_lg

def open_chrome():
    """Initialize Chrome browser using webdriver_manager"""
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        
        # Basic options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if run_in_background:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        
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
        
        # Use webdriver_manager to handle chromedriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set up common driver utilities
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        actions = ActionChains(driver)
        
        print_lg("Chrome started successfully")
        return driver
    except Exception as e:
        print_lg(f"Error starting Chrome: {str(e)}")
        return None

# Initialize the WebDriver instance
try:
    driver = open_chrome()
    if driver is None:
        raise Exception("Failed to initialize Chrome")
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
except Exception as e:
    print_lg(f"Failed to initialize Chrome: {str(e)}")
    raise

