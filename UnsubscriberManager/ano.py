import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options


# Function to test headless Chrome
def test_headless():
    # Set Chrome options for headless mode
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    service = ChromeService(executable_path='./bin/chromedriver')  # Update path to chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open a test URL
        test_url = "https://www.example.com"
        driver.get(test_url)

        # Extract and return the page title
        page_title = driver.title
        return page_title
    except Exception as e:
        return f"Error: {e}"
    finally:
        # Close the browser
        driver.quit()


# Streamlit UI
st.title("Headless Browser Test")

# Button to run the test
if st.button("Run Headless Test"):
    with st.spinner("Running headless test..."):
        result = test_headless()

    # Display the result
    st.write("Test Result:")
    st.success(result if "Error" not in result else result)
