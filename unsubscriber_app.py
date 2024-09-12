import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

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

                    # Wait for a few seconds before navigating to the next URL
                    time.sleep(2)  # Adjust the sleep time as necessary

                except Exception as inner_e:
                    logging.error(f"Error processing {url}: {inner_e}")

            logging.info(f"Batch {batch_num + 1}/{total_batches} completed.\n")

    except Exception as e:
        logging.error("Error:", e)

    finally:
        # Close the browser window
        logging.info('All batches were processed!')
        driver.quit()


def main():
    st.title('URL Processor')

    st.write("Upload an Excel file with a sheet containing the column header 'Preference Center URL'")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Try reading the Excel file
            df = pd.read_excel(uploaded_file, sheet_name=None)  # Read all sheets
            sheet_names = df.keys()
            st.write("Sheets available in the file:", sheet_names)

            # Let the user select which sheet to use
            sheet_name = st.selectbox("Select sheet", sheet_names)
            df = df[sheet_name]
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return

        # Check if the DataFrame is empty or has no columns
        if df.empty:
            st.error("Uploaded Excel file is empty or not formatted correctly.")
            return
        if df.columns.empty:
            st.error("Uploaded Excel file does not contain any columns.")
            return

        st.write("Excel file uploaded successfully!")

        if 'Preference Center URL' in df.columns:
            st.write("Column 'Preference Center URL' found!")

            start_row = st.number_input("Start Row", min_value=0, value=0)
            end_row = st.number_input("End Row", min_value=0, value=len(df), max_value=len(df))

            if st.button('Process URLs'):
                st.write("Processing URLs...")
                process_urls(df, start_row, end_row)
                st.write("Processing complete!")
        else:
            st.error("Excel file must contain the column header 'Preference Center URL'")

