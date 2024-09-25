from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def process_url():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options, service=Service('./chromedriver.exe'))
    return driver.get("https://www.ukg.co.uk/subscription/preferences?hid=CKRNS000004851512")


def main():
    driver = process_url()
    driver

if __name__ == "__main__":
    main()

