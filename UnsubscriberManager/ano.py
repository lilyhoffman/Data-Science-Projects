from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# Set Chrome options
options = Options()

# Add headless argument to run browser without GUI
options.add_argument("--headless")

# Additional options to avoid issues
options.add_argument("--disable-gpu")  # Disable GPU acceleration (recommended for headless)
options.add_argument("--no-sandbox")  # Sandbox issues can cause crashes
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems in containers

# Initialize the Chrome WebDriver
service = ChromeService(executable_path='./bin/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

# Open a URL
driver.get("https://www.google.com")

# Print the page title (to check if it's working)
print(driver.title)

# Close the browser
driver.quit()
