from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from src.logger import log
import json


def create_configuration():
    log.info("Starting configuration generator, Please login with your roblox account.")
    # Setup webdriver
    driver = webdriver.Chrome() 
    driver.get("https://stepfordcountyrailway.co.uk/authentication/login")
    wait = WebDriverWait(driver, 3000)

    # Wait for user to finish logging in
    wait.until(EC.url_matches("https://stepfordcountyrailway.co.uk"))

    # Find Userid
    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "userDropdown")
        )
    )
    dropdown.click()
    userid = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[.//text()[normalize-space()='My Stats']]")
        )
    ).get_attribute("href").rstrip("/").split("/")[-1]

    # Extract cookies
    driver.get("https://roblox.com")
    roblox_cookies = driver.get_cookies()

    # Close driver
    try:
        driver.quit()
    except:
        pass

    config = {
        "settings": {
            "url": f"https://stepfordcountyrailway.co.uk/Players/{userid}/CurrentActivity",
            "clientid": 1224018767584034816,
            "headless": True,
            "driver_version": None
        },
        "cookies": {
            "roblox": roblox_cookies,
            }
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    log.info("Configuration File Generated!")


if __name__ == "__main__":
    create_configuration()


    