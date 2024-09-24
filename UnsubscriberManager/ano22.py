import pandas as pd
import streamlit as st
from selenium import webdriver
import time
import logging
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_urls(df, start_row, end_row, batch_size, col_name, progress_callback):
    options = webdriver.ChromeOptions()
    options.set_capability(

        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}

    )

    DRIVER_PATH = 'C:/Users/lilyh/Data-Science-Projects/UnsubscriberManager/bin/chromedriver.exe'

    service = ChromeService(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)


    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("window-size=1920,1080")

    # Add a preference to mute audio
    options.add_argument("--mute-audio")



    total_batches = (end_row - start_row) // batch_size + (1 if (end_row - start_row) % batch_size != 0 else 0)
    total_urls = end_row - start_row
    total_urls_processed = 0

    try:
        for batch_num in range(total_batches):
            start_index = start_row + batch_num * batch_size
            end_index = min(start_row + (batch_num + 1) * batch_size, end_row)
            batch_df = df.iloc[start_index:end_index]

            logging.info(f"Processing Batch {batch_num + 1}/{total_batches}")

            for index, row in batch_df.iterrows():
                url_index = start_index + index - start_index + 1
                url = row[col_name]
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'edit-global-unsubscribe1'))
                    )
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    scroll_position = total_height * 0.40
                    driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                    time.sleep(1)
                    checkbox = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'edit-global-unsubscribe1'))
                    )
                    if not checkbox.is_selected():
                        checkbox.click()
                        logging.info(f"Checkbox clicked successfully on {url}")
                    else:
                        logging.info(f"Checkbox already selected on {url}")
                    time.sleep(1)
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'edit-actions-submit'))
                    )
                    submit_button.click()
                    logging.info(f"Button clicked successfully on {url}")
                    total_urls_processed += 1

                    progress_callback(total_urls_processed, total_urls)
                    time.sleep(2)
                except Exception as inner_e:
                    logging.error(f"Error processing {url}: {inner_e}")

            logging.info(f"Batch {batch_num + 1}/{total_batches} completed.\n")

    except Exception as e:
        logging.error(f"Error processing URLs: {traceback.format_exc()}")

    finally:
        driver.quit()
        logging.info(f"Total URLs processed: {total_urls_processed}")
        return total_urls_processed

def upload_page():
    st.title('Unsubscribe Assistant')
    st.info("Upload an Excel file with a sheet containing the column header 'Preference Center URL'")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    with col2:
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, sheet_name=None)
                sheet_names = df.keys()
                sheet_name = st.selectbox("Select sheet", sheet_names)
                df = df[sheet_name]
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                return
        else:
            sheet_name = None

    if uploaded_file and sheet_name:
        if df.empty:
            st.error("Uploaded Excel file is empty or not formatted correctly.")
            return
        if df.columns.empty:
            st.error("Uploaded Excel file does not contain any columns.")
            return

        st.success("Excel file uploaded.")

        st.subheader("Content of the Uploaded Excel File")
        st.dataframe(df)

        st.subheader("Rows to Process")
        col1, col2 = st.columns([1, 1])

        with col1:
            start_row = st.number_input("Start Row", min_value=0, value=0)

        with col2:
            end_row = st.number_input("End Row", min_value=0, value=len(df), max_value=len(df))

        if st.button('Stop Current Process'):
            st.error(f"Stopped.")
            st.stop()

        if st.button('Click to Process URLs'):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(processed, total):
                progress = processed / total
                progress_bar.progress(progress)
                status_text.text(f"Processing {processed} of {total} URLs")

            with st.spinner("Processing URLs..."):
                try:
                    urls_processed = process_urls(df,
                                                  start_row,
                                                  end_row,
                                                  batch_size=10,
                                                  chromedriver_path='./bin/chromedriver.exe',  # Change gecko_path to chromedriver_path
                                                  col_name='Preference Center URL',
                                                  progress_callback=update_progress)
                    st.success(f"Processing complete!")
                except Exception as e:
                    st.error(f"Error during processing: {e}")

def about_page():
    st.title('About')
    st.write("""\
         This application automates the process of unsubscribing users from Company X's promotional emails. 
         You can upload an Excel file containing URLs, and the tool will process these URLs to unsubscribe 
         users efficiently. After noticing a repetitive task that my team members frequently performed, 
         I designed this tool to streamline their workflow and expedite the unsubscribing process.
        """)

    st.subheader('Features')
    st.markdown("""\
    - Upload and select sheets from Excel files
    - Process URLs to interact with web elements
    - Track processing status with logs
    """)
    st.title('Fix List')
    st.write("""\
        - Interrupt the Program (please do not try more than 3 or 4 urls right now, otherwise you will need to restart your laptop)
        - Add other buttons/functions that could be user-friendly
        - stop/pause button
        - silence the pinging
        - ISSUE WITH DRIVER (last step you should do, add stop/pause button, silence ping first)

    """)
    st.title('Contact')
    st.write("""\
        If you have any questions or need support, please contact:

        **Email:** lilynaavhoffman@gmail.com

    """)
    st.success("Developed by: Lily Hoffman")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Upload", "About"])

    if page == "Upload":
        upload_page()
    elif page == "About":
        about_page()

if __name__ == "__main__":
    main()
