from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import streamlit as st
# from webdriver_manager.chrome import ChromeDriverManager


# Service('./chromedriver.exe')
# Function to process the URL
def process_url(url):
    # service=Service(ChromeDriverManager().install())
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options, service=service)
    return driver.get(url)


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

    # You can test the process_url function directly here if needed
    # process_url('https://www.ukg.co.uk/subscription/preferences?hid=CKRNS000004851512')


if __name__ == "__main__":
    main()
