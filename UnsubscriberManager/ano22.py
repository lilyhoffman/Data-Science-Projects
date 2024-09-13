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
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_urls(df, start_row, end_row, batch_size, gecko_path, col_name, progress_callback, pause_event):
    options = Options()
    options.add_argument("--headless")
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=options)

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

                    # Check if process is paused
                    if pause_event['paused']:
                        while pause_event['paused']:
                            time.sleep(1)

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
    st.title('UKG Unsubscribe Assistant')
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

        # Initialize session state variables for pause/resume
        if 'paused' not in st.session_state:
            st.session_state.paused = False
        if 'process_started' not in st.session_state:
            st.session_state.process_started = False

        if st.button('Start/Resume Processing'):
            st.session_state.process_started = True
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(processed, total):
                progress = processed / total
                progress_bar.progress(progress)
                status_text.text(f"Processing {processed} of {total} URLs")

            def pause_process():
                st.session_state.paused = True

            def resume_process():
                st.session_state.paused = False

            if st.session_state.process_started:
                with st.spinner("Processing URLs..."):
                    try:
                        urls_processed = process_urls(df, start_row, end_row, batch_size=10,
                                                      gecko_path='C:/Program Files/geckodriver.exe',
                                                      col_name='Preference Center URL',
                                                      progress_callback=update_progress,
                                                      pause_event={'paused': st.session_state.paused})
                        st.success(f"Processing complete!")
                    except Exception as e:
                        st.error(f"Error during processing: {e}")

        if st.session_state.process_started:
            if st.button('Pause Processing'):
                pause_process()

            if st.button('Resume Processing'):
                resume_process()


def main():
    st.sidebar.image(image="ukg.webp", use_column_width=True)
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Upload", "About"])

    if page == "Upload":
        upload_page()
    elif page == "About":
        about_page()


def about_page():
    st.title('About')
    st.write("""\
        This application automates the process of unsubscribing users from UKG promotional emails. 
        You can upload an Excel file containing URLs, and the tool will process these URLs to 
        unsubscribe users efficiently. It is designed to streamline the workflow for the Marketing 
        Operations Team and expedite the unsubscribing process.
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

    """)
    st.title('Contact')
    st.write("""\
        If you have any questions or need support, please contact:

        **Email:** lily.hoffman@ukg.com

    """)
    st.success("Developed by: Lily Hoffman (Marketing Operations Intern)")


if __name__ == "__main__":
    main()
