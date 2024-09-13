import pandas as pd
import streamlit as st
from selenium import webdriver
import time
import logging
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_urls(df, start_row, end_row, batch_size=10, gecko_path='C:/Program Files/geckodriver.exe',
                 col_name='Preference Center URL'):
    # Create a new Firefox WebDriver instance with headless option
    options = Options()
    options.add_argument("--headless")  # Run Firefox in headless mode

    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=options)

    # Define total batches needed
    total_batches = (end_row - start_row) // batch_size + (1 if (end_row - start_row) % batch_size != 0 else 0)

    # Counter for URLs processed
    total_urls_processed = 0

    try:
        for batch_num in range(total_batches):
            start_index = start_row + batch_num * batch_size
            end_index = min(start_row + (batch_num + 1) * batch_size, end_row)

            # Get the batch of URLs
            batch_df = df.iloc[start_index:end_index]

            logging.info(f"Processing Batch {batch_num + 1}/{total_batches}")

            for index, row in batch_df.iterrows():
                url = row[col_name]
                try:
                    # Navigate to the webpage
                    driver.get(url)

                    # Wait for the page to load completely
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'edit-global-unsubscribe1'))
                    )

                    # Get the height of the entire page
                    total_height = driver.execute_script("return document.body.scrollHeight")

                    # Calculate the scroll position to bring the checkbox closer to the middle-bottom
                    scroll_position = total_height * 0.40  # Adjust this proportion as needed

                    # Scroll to the calculated position
                    driver.execute_script(f"window.scrollTo(0, {scroll_position});")

                    # Optionally, wait for a few seconds to ensure the page has scrolled
                    time.sleep(1)  # Adjust the sleep time as necessary

                    # Wait for the checkbox to be present and interactable
                    checkbox = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'edit-global-unsubscribe1'))
                    )

                    # Check if the checkbox is not already selected
                    if not checkbox.is_selected():
                        checkbox.click()
                        logging.info(f"Checkbox clicked successfully on {url}")
                    else:
                        logging.info(f"Checkbox already selected on {url}")

                    # Wait for a brief moment to ensure the click is registered
                    time.sleep(1)  # Adjust the sleep time as necessary

                    # Wait for the submit button to be present and interactable
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'edit-actions-submit'))
                    )
                    submit_button.click()
                    logging.info(f"Button clicked successfully on {url}")

                    # Update the counter for processed URLs
                    total_urls_processed += 1

                    # Wait for a few seconds before navigating to the next URL
                    time.sleep(2)  # Adjust the sleep time as necessary

                except Exception as inner_e:
                    logging.error(f"Error processing {url}: {inner_e}")

            logging.info(f"Batch {batch_num + 1}/{total_batches} completed.\n")

    except Exception as e:
        logging.error("Error:", e)

    finally:
        # Close the browser window
        driver.quit()
        # Log the total number of URLs processed
        logging.info(f"Total URLs processed: {total_urls_processed}")

    # Return the number of URLs processed
    return total_urls_processed


def upload_page():
    st.title('UKG Unsubscribe Assistant')
    # st.write("Automates the process of unsubscribing users from UKG promotional emails.")
    st.info("Upload an Excel file with a sheet containing the column header 'Preference Center URL'")

    # Layout for file uploader and sheet selector with wider column for file uploader
    col1, col2 = st.columns([2, 1])  # Wider column for file uploader

    with col1:
        # File Uploader
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    with col2:
        if uploaded_file:
            try:
                # Read Excel File
                df = pd.read_excel(uploaded_file, sheet_name=None)  # Read all sheets
                sheet_names = df.keys()

                # Sheet Selector
                sheet_name = st.selectbox("Select sheet", sheet_names)
                df = df[sheet_name]
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                return
        else:
            sheet_name = None

    # Check DataFrame Validity
    if uploaded_file and sheet_name:
        if df.empty:
            st.error("Uploaded Excel file is empty or not formatted correctly.")
            return
        if df.columns.empty:
            st.error("Uploaded Excel file does not contain any columns.")
            return

        st.success("Excel file uploaded.")

        # Display DataFrame in a separate section
        st.subheader("Content of the Uploaded Excel File")
        st.dataframe(df)

        # Layout for Start Row and End Row inputs next to each other
        st.subheader("Rows to Process")
        col1, col2 = st.columns([1, 1])  # Equal width columns

        with col1:
            start_row = st.number_input("Start Row", min_value=0, value=0)

        with col2:
            end_row = st.number_input("End Row", min_value=0, value=len(df), max_value=len(df))

        if st.button('Process URLs'):
            with st.spinner("Processing URLs..."):
                urls_processed = process_urls(df, start_row, end_row)
            st.success(f"Processing complete! Total URLs processed: {urls_processed}")



def about_page():
    st.title('About')
    st.write("""
        This application automates the process of unsubscribing users from UKG promotional emails. 
        You can upload an Excel file containing URLs, and the tool will process these URLs to 
        unsubscribe users efficiently. It is designed to streamline the workflow for the Marketing 
        Operations Team and expedite the unsubscribing process.
        """)

    st.subheader('Features')
    st.markdown("""
    - Upload and select sheets from Excel files
    - Process URLs to interact with web elements
    - Track processing status with logs
    """)
    st.title('Fix List')
    st.write("""
        - Interrupt the Program (please do not try more than 3 or 4 urls right now, otherwise you will need to restart your laptop)
        - Add other buttons/functions that could be user-friendly

    """)
    st.title('Contact')
    st.write("""
        If you have any questions or need support, please contact:

        **Email:** lily.hoffman@ukg.com

    """)
    st.success("Developed by: Lily Hoffman (Marketing Operations Intern)")


def main():
    st.sidebar.image(image="ukg.webp", use_column_width=True)
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Upload", "About"])


    # Show the selected page
    if page == "Upload":
        upload_page()
    elif page == "About":
        about_page()


if __name__ == "__main__":
    main()
