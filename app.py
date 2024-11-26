import streamlit as st
import pandas as pd
import os
import json
import secrets
from components.data_processing import process_bank_data
from components.broker import broker_data_process
from components.pdf_processing import process_pdf_bank_data 
from datetime import datetime, timedelta

UPLOAD_DIR = './uploads'
AUTH_FILE = '.streamlit/auth.json'

def force_login_check():
    """Force login check before any operation"""
    if os.path.exists(AUTH_FILE) and verify_auth_file():
        # If valid, rehydrate session state
        load_auth_status()
        return True
    # If auth file is missing or invalid, reset authentication state
    st.session_state.authentication_status = False
    return False


def verify_auth_file():
    """Verify if auth file exists and is valid"""
    try:
        if not os.path.exists(AUTH_FILE):
            return False

        with open(AUTH_FILE, 'r') as f:
            auth_data = json.load(f)

        # Check session validity
        if 'session_start_time' in auth_data:
            session_start_time = datetime.strptime(auth_data['session_start_time'], "%Y-%m-%d %H:%M:%S.%f")
            if datetime.now() - session_start_time > timedelta(hours=8):
                os.remove(AUTH_FILE)
                return False

        required_fields = ['username', 'authentication_status', 'session_id']
        return all(field in auth_data for field in required_fields)
    except Exception as e:
        print(f"Auth verification error: {e}")
        return False


def init_session_state():
    """Initialize session state variables"""
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = False

    # Rehydrate session state from AUTH_FILE if valid
    if verify_auth_file():
        load_auth_status()
    else:
        # Clear session state if the auth file is invalid
        clear_session_state()

    # Initialize other state variables if not present
    state_defaults = {
        'authentication_status': False,
        'username': None,
        'file_data': [],
        'processed_files': [],
        'final_submission_done': False,
        'processed_broker_data': pd.DataFrame(),
        'combined_df': pd.DataFrame(),
        'session_start_time': datetime.now(),
        'session_id': generate_session_id() if 'session_id' not in st.session_state else st.session_state.session_id,
    }

    for key, default in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
    
    for key, default in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
    
    # Load authentication status from file if possible
    load_auth_status()

def authenticate(username, password):
    """Authenticate user"""
    if username == "ravi" and password == "12345":
        st.session_state.authentication_status = True
        st.session_state.username = username
        # Generate a secure, persistent session ID
        st.session_state.session_id = generate_session_id()
        st.session_state.session_start_time = datetime.now()
        save_auth_status()
        return True
    return False

def generate_session_id():
    """Generate a unique and secure session ID"""
    # Use secrets.token_hex for a more secure, persistent session ID
    return secrets.token_hex(16)

def save_auth_status():
    """Save authentication status to file"""
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    auth_data = {
        'username': st.session_state.username,
        'authentication_status': st.session_state.authentication_status,
        'file_data': st.session_state.file_data,
        'session_start_time': str(st.session_state.session_start_time),
        'session_id': st.session_state.session_id
    }
    with open(AUTH_FILE, 'w') as f:
        json.dump(auth_data, f)

def load_auth_status():
    """Load authentication status from file"""
    try:
        if not os.path.exists(AUTH_FILE):
            # Auth file doesn't exist, initialize default state
            st.session_state.authentication_status = False
            st.session_state.username = None
            return

        with open(AUTH_FILE, 'r') as f:
            auth_data = json.load(f)

        # Update session state with loaded data
        st.session_state.authentication_status = auth_data.get('authentication_status', False)
        st.session_state.username = auth_data.get('username')
        st.session_state.file_data = auth_data.get('file_data', [])
        st.session_state.session_id = auth_data.get('session_id')
        st.session_state.session_start_time = datetime.strptime(
            auth_data['session_start_time'], 
            "%Y-%m-%d %H:%M:%S.%f"
        )
    except Exception as e:
        print(f"Error loading auth status: {e}")
        # Reset session state on error
        st.session_state.authentication_status = False
        st.session_state.username = None


def clear_session_state():
    """Clear session state and remove temporary files"""
    # Clear auth file
    try:
        if os.path.exists(AUTH_FILE):
            os.remove(AUTH_FILE)
    except Exception as e:
        print(f"Error removing auth file: {e}")

    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reset authentication status
    st.session_state.authentication_status = False

    # Clear upload directory
    if os.path.exists(UPLOAD_DIR):
        for file in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, file))
            except Exception as e:
                print(f"Error removing file {file}: {e}")

def logout():
    """Handle logout"""
    clear_session_state()
    st.rerun()

def login():
    """Display login form"""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def main():
    st.set_page_config(page_title="File Upload and Analysis System")
    
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not st.session_state.get('authentication_status', False):
        login()
        return
    
    # Rest of your main application logic
    st.title("File Upload and Analysis System")
    
    # Add logout to sidebar
    with st.sidebar:
        st.write(f"Welcome {st.session_state.username}!")
        if st.button("Logout"):
            logout()
    
    # Your existing file upload and processing logic goes here
    upload_and_process_files()

def show_sidebar():
    """Display sidebar with logout option"""
    with st.sidebar:
        st.write(f"Welcome {st.session_state.username}!")
        if st.button("Logout"):
            logout()


def upload_and_process_files():
    """Handle insurance file uploads and processing"""
    st.header("Upload Insurance Files for Analysis")
    uploaded_file = st.file_uploader("Select a file to upload", type=["xlsx", "xls", "pdf", "docx"])
    file_type = st.selectbox("Select the file type", ["Excel", "PDF", "DOCX"])
    
    # Updated list of bank names with new entries
    bank_names = ["Bajaj", "CARE", "Cholamandalam", "FUTURE", "IFFCO", "LIBERTY", 
                  "TATA AIG", "SBI", "HDFC", "RELIANCE", "NATIONAL NEHRU", 
                  "MANIPAL SIGNA", "ICICI", "GO-DIGIT", "The New India Pdf", "United Pdf"]
    
    selected_bank = st.selectbox("Select a Bank", bank_names)

    if st.button("Add File for Analysis"):
        if uploaded_file and file_type:
            process_uploaded_file(uploaded_file, file_type, selected_bank)

    if st.button("Final Submission"):
        combine_and_save_processed_files()

    if st.session_state.final_submission_done:
        handle_broker_file_upload()

def process_uploaded_file(uploaded_file, file_type, selected_bank):
    """Process the uploaded insurance file"""
    file_path = f"./uploads/{uploaded_file.name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        if file_type == "Excel":
            df = pd.read_excel(file_path)
            processed_data = process_bank_data(df, selected_bank)
            st.session_state.processed_files.append(processed_data)
            st.success(f"File '{uploaded_file.name}' processed successfully.")
            st.dataframe(processed_data)
        elif file_type == "PDF":
            processed_data = process_pdf_bank_data(file_path, selected_bank)
            st.session_state.processed_files.append(processed_data)
            st.success(f"File '{uploaded_file.name}' processed and tabular data extracted successfully.")
            st.dataframe(processed_data)
        else:
            st.warning("Only Excel and PDF files are currently supported for processing.")
            return

    except Exception as e:
        st.error(f"Error processing the file: {e}")
def combine_and_save_processed_files():
    """Combine processed files and save the output"""
    if st.session_state.processed_files:
        st.session_state.combined_df = pd.concat(st.session_state.processed_files, ignore_index=True)
        output_path = "./uploads/final_output.xlsx"
        st.session_state.combined_df.to_excel(output_path, index=False)
        st.success(f"All files combined and saved to '{output_path}'.")
        st.dataframe(st.session_state.combined_df)
        st.session_state.final_submission_done = True
    else:
        st.warning("No files have been processed for final submission.")

def handle_broker_file_upload():
    """Handle broker file upload and comparison"""
    st.header("Upload the Broker File for Comparison")
    broker_file = st.file_uploader("Upload the Broker file (Excel only)", type=["xlsx", "xls"])
    if broker_file:
        process_broker_file(broker_file)

def process_broker_file(broker_file):
    """Process the uploaded broker file"""
    broker_path = f"./uploads/{broker_file.name}"
    with open(broker_path, "wb") as f:
        f.write(broker_file.getbuffer())
    try:
        broker_df = pd.read_excel(broker_path)
        processed_broker_data = broker_data_process(broker_df)
        st.session_state.processed_broker_data = processed_broker_data
        st.success("Broker file uploaded successfully.")
        st.dataframe(processed_broker_data)

        if st.button("Process Broker File"):
            perform_final_comparison()
    except Exception as e:
        st.error(f"Error processing the broker file: {e}")

def perform_final_comparison():
    """Perform final comparison between combined and broker data"""
    combined_df = st.session_state.combined_df
    processed_broker_data = st.session_state.processed_broker_data

    if not combined_df.empty and not processed_broker_data.empty:
        # Normalize column names for consistency
        combined_df.columns = combined_df.columns.str.strip().str.upper()
        processed_broker_data.columns = processed_broker_data.columns.str.strip().str.upper()

        # Ensure required columns exist for merging
        required_columns = ['PARSED_POLICY_REFERENCE', 'TOTAL COMMISSION BROKER']
        if all(col in processed_broker_data.columns for col in required_columns) and 'TOTAL COMMISSION' in combined_df.columns:
            # Merge the dataframes
            merged_df = combined_df.merge(
                processed_broker_data,
                how='outer',  # Include unmatched broker records
                on='PARSED_POLICY_REFERENCE',
                suffixes=('', '_BROKER'),
                indicator=True  # Adds a column to indicate source of each row
            )

            # Add 'FOUND' column to indicate match status
            merged_df['FOUND'] = merged_df['_merge'].map({
                'both': 'Matched',
                'left_only': 'Not Found in broker sheet',
                'right_only': 'Not Found in bank sheet'
            })

            # Calculate the 'DIFFERENCE' column
            merged_df['DIFFERENCE'] = merged_df.apply(
                lambda row: (
                    'Positive' if pd.notna(row['TOTAL COMMISSION BROKER']) and pd.notna(row['TOTAL COMMISSION']) and row['TOTAL COMMISSION'] > row['TOTAL COMMISSION BROKER']
                    else 'Negative' if pd.notna(row['TOTAL COMMISSION BROKER']) and pd.notna(row['TOTAL COMMISSION']) and row['TOTAL COMMISSION'] < row['TOTAL COMMISSION BROKER']
                    else 'No Difference' if pd.notna(row['TOTAL COMMISSION BROKER'])
                    else 'N/A'
                ),
                axis=1
            )

            # Calculate the 'DIFFERENCE_AMOUNT' column
            merged_df['DIFFERENCE_AMOUNT'] = merged_df.apply(
                lambda row: (
                    row['TOTAL COMMISSION'] - row['TOTAL COMMISSION BROKER'] if pd.notna(row['TOTAL COMMISSION']) and pd.notna(row['TOTAL COMMISSION BROKER'])
                    else row['TOTAL COMMISSION'] if row['FOUND'] == 'Not Found in broker sheet'
                    else -row['TOTAL COMMISSION BROKER'] if row['FOUND'] == 'Not Found in bank sheet'
                    else 0
                ),
                axis=1
            )

            # Handle entries found only in the broker file
            broker_only_df = merged_df[merged_df['_merge'] == 'right_only'].copy()
            broker_only_df['SOURCE'] = broker_only_df['BANK NAME']  # Retain the bank name from the broker file
            broker_only_df = broker_only_df.drop(columns=['_merge'])  # Drop the merge indicator

            # Handle entries found in both or only in the bank file
            merged_df = merged_df.drop(columns=['_merge'])  # Drop the merge indicator from the main DataFrame

            # Save the results
            output_path = './comparison_results.xlsx'
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                merged_df.to_excel(writer, sheet_name='Final Comparison', index=False)
                broker_only_df.to_excel(writer, sheet_name='Not Found in Bank', index=False)

            # Display success message
            st.success(f"Comparison completed! Results saved to {output_path}")
            st.dataframe(merged_df)
        else:
            missing_cols = set(required_columns + ['TOTAL COMMISSION']) - set(combined_df.columns) - set(processed_broker_data.columns)
            st.error(f"Required columns are missing for merging and processing. Missing columns: {missing_cols}")
    else:
        st.warning("Combined or broker data is empty. Cannot proceed with comparison.")


if __name__ == "__main__":
    main()
