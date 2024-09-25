from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import streamlit as st
import os

# Function to process the URL
def process_url(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # Path to chromedriver (ensure it's executable and in the correct location)
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver")

    # Set up the service for ChromeDriver
    service = Service(chromedriver_path)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the URL
    driver.get(url)

# Function to handle file upload and process URL (add URL input in Streamlit)
def upload_page():
    st.title('Unsubscribe Assistant')
    st.info("Upload an Excel file with a sheet containing the column header 'Preference Center URL'")

    # You can add an input box or file uploader here if needed. Here's an example of a URL input:
    url = st.text_input('Enter the URL you want to process', 'https://www.example.com')

    if st.button('Process URL'):
        process_url(url)
        st.success(f"Processed URL: {url}")

# Main function
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Upload", "About"])

    if page == "Upload":
        upload_page()
    elif page == "About":
        st.write("This is the 'About' page.")

if __name__ == "__main__":
    main()
