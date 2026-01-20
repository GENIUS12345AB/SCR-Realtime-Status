from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.logger import log, NOTSET
import json
import re
import os
import platform

os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_LOG'] = str(NOTSET)

class SCRScraper:
    def __init__(self):
        # Open Configuration file
        with open('config.json') as f:
            config = json.load(f)

        # Create Driver
        log.info("Starting Selenium Webdriver")
        service = Service(ChromeDriverManager(
            driver_version=config['settings']['driver_version'],
            latest_release_url="https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE").install())
        options = Options()
        if config['settings']['headless']:
            options.add_argument("--headless")
        if platform.system() == "Linux":
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
        driver = webdriver.Chrome(service=service, options=options) 
        log.debug("Selenium Started")

        # Start process
        driver.get("https://roblox.com")
        wait = WebDriverWait(driver, 10)

        # Load Cookies
        for cookie in config['cookies']['roblox']:
            driver.add_cookie(cookie)

        # Open SCR Auth
        log.info("Starting Auth Flow")
        driver.get(config['settings']['url'])

        # Approve Login
        ContinueApp = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Continue']")
            )
        )
        ContinueApp.click()
        ConfirmPrompt = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Confirm and Give Access']")
            )
        )
        ConfirmPrompt.click()
        log.info("Login Complete!")
        
        self.driver = driver

        # Defaults
        self.headcode = None
        self.unit_number = None
        self.next_stop_msg = None
        self.current_status = None
        self.destinaton = None
        self.activity_type = None
        self.station = None
        self.group = None
        self.platforms = None
        self.trains_dispatched = None


    def UpdateLiveActivity(self):
        try:
            def read_element(value, xpath):
                try:
                    return self.driver.find_element(By.XPATH, xpath).text.strip().replace("Stepford United Football Club", "Stepford UFC")
                except:
                    return value
            
            def existing_element(xpath):
                try:
                    self.driver.find_element(By.XPATH, xpath)
                    return True
                except:
                    return False

            try:     
                activity_type_class = self.driver.find_element(
                    By.ID, 
                    "currentActivityDropdown"
                    ).get_attribute("class")
            except:
                # Sometimes website fails to load dropdown menu, use as backup
                try:
                    activity_type_class = self.driver.find_element(
                        By.XPATH,
                        "//div[contains(@class,'card') and contains(@class,'mb-4') and contains(@class,'border-1')]"
                        ).get_attribute("class")
                except:
                    activity_type_class = "primary"

            # Driver Role
            if "drivers" in activity_type_class:
                self.activity_type = "Driving"  
                self.headcode = read_element(self.headcode, "//span[contains(@class, 'badge')]")
                self.unit_number = read_element(self.unit_number, "//*[contains(text(), 'Unit')]")
                self.next_stop_msg = read_element(self.next_stop_msg, "//*[contains(text(), 'The next stop is')]")
                self.current_status = read_element(self.current_status, "//*[contains(text(), 'En-route')]")
                self.current_status = read_element(self.current_status, "//*[contains(text(), 'Loading at')]")
                self.current_status = read_element(self.current_status, "//*[contains(text(), 'Terminating at')]")
                self.current_status = read_element(self.current_status, "//*[contains(text(), 'Terminated at')]")
                self.destinaton = read_element(self.destinaton, "//div[contains(@class, 'fs-5')]/text()[contains(., ' to ')]/following-sibling::a[1]")
            
            # Dispatcher Role
            elif "dispatchers" in activity_type_class:
                self.activity_type = "Dispatching"
                if existing_element("//*[contains(text(), 'Nothing to see here!')]"):
                    self.current_status = "Selecting a station"
                else:
                    self.station = read_element(self.station, "//div[contains(@class,'fs-4')]//a")
                    self.platforms = read_element(self.current_status, "//span[preceding-sibling::text()[contains(., 'Platforms')]]")
                    group_text = read_element(self.group, "//span[contains(., 'Dispatching trains')]")
                    if group_text:
                        self.group = re.search(r"\b(\d+)\b", group_text).group(1)
                    try:
                        rows = self.driver.find_element(By.CSS_SELECTOR, "table.transport-timeline.m-4").find_elements(By.TAG_NAME, "tr")
                        if rows:
                            self.trains_dispatched = len(rows) - 1
                    except:
                        pass

            # Guard Role
            elif "guards" in activity_type_class:
                self.activity_type = "Guarding"
                if existing_element("//*[contains(text(), 'Nothing to see here!')]"):
                    self.current_status = "Selecting a train"
                else:
                    self.headcode = read_element(self.headcode, "//span[contains(@class, 'badge')]")
                    self.current_status = read_element(self.current_status, "//*[contains(text(), 'En-route')]")
                    self.current_status = read_element(self.current_status, "//*[contains(text(), 'Loading at')]")
                    self.current_status = read_element(self.current_status, "//*[contains(text(), 'Terminating at')]")
                    self.destinaton = read_element(self.destinaton, "//div[contains(@class, 'fs-5')]/text()[contains(., ' to ')]/following-sibling::a[1]")
            
            # Signaller Role
            elif "signallers" in activity_type_class:
                self.activity_type = "Signalling"

            # Main Menu / No Role
            elif "primary" in activity_type_class:
                self.activity_type = "Menu"

        except Exception as e:
            pass

    def close(self):
        if self.driver:
            self.driver.quit()
