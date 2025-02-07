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

def clean_and_trim_policy_number(policy):
    """
    Clean and trim policy numbers by:
    1. Removing extra trailing digits beyond 9 digits.
    2. Zero-padding to ensure consistent 9-digit format.
    3. Removing non-numeric characters.
    """
    if pd.isna(policy):
        return None

    # Convert to string and remove non-numeric characters
    policy_str = ''.join(filter(str.isdigit, str(policy)))

    # Trim to the first 9 digits if longer, or pad with zeros if shorter
    if len(policy_str) > 9:
        policy_str = policy_str[:9]
    policy_str = policy_str.zfill(9)

    return policy_str


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
            # Read the file directly and pass it to process_bank_data for further processing
            df = pd.read_excel(file_path)
            processed_data = process_bank_data(df, selected_bank)
            st.session_state.processed_files.append(processed_data)
            st.success(f"File '{uploaded_file.name}' processed successfully.")
            st.dataframe(processed_data)
        
        elif file_type == "PDF":
            # Process PDF file
            processed_data = process_pdf_bank_data(file_path, selected_bank)
            st.session_state.processed_files.append(processed_data)
            st.success(f"File '{uploaded_file.name}' processed and tabular data extracted successfully.")
            st.dataframe(processed_data)
        
        else:
            # Unsupported file type
            st.warning("Only Excel and PDF files are currently supported for processing.")
            return

    except Exception as e:
        # Handle any errors during file processing
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
        # Read the broker file into a DataFrame
        broker_df = pd.read_excel(broker_path)

        # Pass the raw broker DataFrame directly to broker_data_process
        processed_broker_data = broker_data_process(broker_df)

        # Save the processed data to session state
        st.session_state.processed_broker_data = processed_broker_data

        # Notify the user and display the processed DataFrame
        st.success("Broker file uploaded successfully.")
        st.dataframe(processed_broker_data)

        # Trigger the final comparison if the button is pressed
        if st.button("Process Broker File"):
            perform_final_comparison()

    except Exception as e:
        # Handle any errors during file processing
        st.error(f"Error processing the broker file: {e}")



def normalize_column_names(df):
    """Normalize column names: strip whitespace and convert to uppercase"""
    return df.rename(columns=lambda x: str(x).strip().upper())

def preprocess_dataframe(df):
    """Clean and preprocess dataframe values"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df

def map_bank_names(bank_name):
    """Map short bank names to full names"""
    bank_map = {
        "BAJAJ": "BAJAJ ALLIANZ GENERAL INSURANCE COMPANY LIMITED",
        "CARE": "CARE HEALTH INSURANCE LIMITED",
        "CHOLAMANDALAM": "CHOLAMANDALAM MS GENERAL INSURANCE COMPANY LIMITED",
        "FUTURE": "FUTURE GENERALI INDIA INSURANCE COMPANY LIMITED",
        "IFFCO": "IFFCO TOKIO GENERAL INSURANCE COMPANY LIMITED",
        "LIBERTY": "LIBERTY GENERAL INSURANCE LIMITED",
        "GO-DIGIT": "GO DIGIT GENERAL INSURANCE LIMITED",
        "HDFC": "HDFC ERGO GENERAL INSURANCE COMPANY LIMITED",
        "ICICI": "ICICI LOMBARD GENERAL INSURANCE COMPANY LIMITED",
        "MANIPAL SIGNA": "MANIPALCIGNA HEALTH INSURANCE COMPANY LIMITED",
        "NATIONAL NEHRU": "NATIONAL INSURANCE COMPANY LIMITED",
        "RELIANCE": "RELIANCE GENERAL INSURANCE COMPANY LIMITED",
        "SBI": "SBI GENERAL INSURANCE COMPANY LIMITED",
        "TATA AIG": "TATA AIG GENERAL INSURANCE COMPANY LIMITED",
        "UNITED PDF": "UNITED INDIA INSURANCE COMPANY LIMITED"
    }
    return bank_map.get(bank_name.upper(), bank_name)

def standardize_endorsement_values(df):
    """Standardize endorsement-related values"""
    if 'INSNATURE' in df.columns:
        df = df.rename(columns={'INSNATURE': 'INSURANCE_NATURE'})
    if 'INSURANCE NATURE' in df.columns:
        df = df.rename(columns={'INSURANCE NATURE': 'INSURANCE_NATURE'})
    
    if 'INSURANCE_NATURE' in df.columns:
        replacements = {
            'ENDORSMENT': 'ENDORSEMENT',
            'Endorsment': 'ENDORSEMENT',
            'endorsment': 'ENDORSEMENT',
            'ENDO': 'ENDORSEMENT'
        }
        df['INSURANCE_NATURE'] = df['INSURANCE_NATURE'].replace(replacements)
    return df

def normalize_premium_columns(df):
    """Normalize premium-related columns"""
    premium_column_mappings = {
        'APPLICABLE_PREMIUM_AMOUNT': 'PREMIUM_AMOUNT',
        'PREMIUM_FOR_PAYOUTS': 'PREMIUM_AMOUNT',
        'TOTAL PREMIUM': 'PREMIUM_AMOUNT',
        'TOTALPREMIUM': 'PREMIUM_AMOUNT',
        'ODPREMIUMPREMIUM': 'PREMIUM_AMOUNT'
    }
    
    for old_col, new_col in premium_column_mappings.items():
        if old_col in df.columns:
            df[new_col] = pd.to_numeric(df[old_col], errors='coerce')
            
    return df

def normalize_customer_names(df):
    """Normalize customer name columns"""
    customer_column_mappings = {
        'INSURED_CUSTOMER_NAME': 'CUSTOMER_NAME',
        'CUSTOMER NAME': 'CUSTOMER_NAME',
        'CNAME': 'CUSTOMER_NAME',
        'CUSTOMERNAME': 'CUSTOMER_NAME'
    }
    
    for old_col, new_col in customer_column_mappings.items():
        if old_col in df.columns:
            df[new_col] = df[old_col].str.strip().str.upper()
    
    return df

def perform_final_comparison():
    try:
        # Get combined bank and broker data from session state
        combined_df = st.session_state.combined_df.copy()
        broker_df = st.session_state.processed_broker_data.copy()

        if combined_df.empty or broker_df.empty:
            st.error("One or both datasets are empty. Cannot proceed with comparison.")
            return

        # Normalize column names for consistency
        combined_df.columns = combined_df.columns.str.strip().str.upper()
        broker_df.columns = broker_df.columns.str.strip().str.upper()

        # Debug: Check column names
        st.write("Combined DataFrame columns:", combined_df.columns.tolist())
        st.write("Broker DataFrame columns:", broker_df.columns.tolist())

        # Ensure PARSED_POLICY_NUMBER_BANK exists
        if 'PARSED_POLICY_NUMBER_BANK' not in combined_df.columns:
            st.error("PARSED_POLICY_NUMBER_BANK column is missing in Combined DataFrame.")
            return

        # Map the SOURCE column in the bank data to broker bank names
        combined_df['SOURCE_MAPPED'] = combined_df['SOURCE'].apply(map_bank_names)

        # Filter broker data to include only banks listed in the mapped source column of combined_df
        relevant_banks = combined_df['SOURCE_MAPPED'].unique()
        st.write("Relevant Banks after Mapping:", relevant_banks)
        filtered_broker_df = broker_df[broker_df['BANK NAME'].isin(relevant_banks)]

        # Split broker data into endorsement and regular policies
        endorsement_broker = filtered_broker_df[filtered_broker_df['INSURANCE NATURE'] == 'Endorsment']
        regular_broker = filtered_broker_df[filtered_broker_df['INSURANCE NATURE'] != 'Endorsment']

        # Match regular policies on policy number (PARSED_POLICY_NUMBER)
        merged_regular = pd.merge(
            regular_broker,
            combined_df,
            left_on='PARSED_POLICY_REFERENCE',
            right_on='PARSED_POLICY_NUMBER_BANK',
            how='left',
            suffixes=('_BROKER', '_BANK'),
            indicator=True
        )

        # Match endorsement policies on customer name and premium
        merged_endorsement = pd.merge(
            endorsement_broker,
            combined_df,
            left_on=['CUSTOMER NAME', 'TOTAL PREMIUM'],
            right_on=['CUSTOMER NAME', 'PREMIUM BANK'],
            how='left',
            suffixes=('_BROKER', '_BANK'),
            indicator=True
        )

        # Combine the results
        merged_df = pd.concat([merged_regular, merged_endorsement], ignore_index=True)

        # Add FOUND column based on the _merge column
        merged_df['FOUND'] = merged_df['_merge'].map({
            'both': 'Matched',
            'left_only': 'Not Found in Bank',
            'right_only': 'Not Found in Broker'
        })

        # Calculate the DIFF column (difference in commissions)
        merged_df['DIFFERENCE'] = merged_df.apply(
            lambda row: (
                row['TOTAL COMMISSION BROKER'] - row['TOTAL COMMISSION']
                if pd.notna(row['TOTAL COMMISSION BROKER']) and pd.notna(row['TOTAL COMMISSION'])
                else 0
            ),
            axis=1
        )

        # Drop unnecessary columns
        merged_df.drop(columns=['_merge', 'SOURCE_MAPPED'], inplace=True)

        # Save the final merged data to an Excel file
        output_path = './comparison_results.xlsx'
        merged_df.to_excel(output_path, index=False)

        # Display the results in Streamlit
        st.success(f"Comparison completed successfully! Results saved to {output_path}")
        st.dataframe(merged_df)

        # Display summary statistics
        display_results_summary(merged_df)

    except Exception as e:
        st.error(f"An error occurred during comparison: {str(e)}")







def calculate_commission_difference(row):
    """Calculate commission difference between bank and broker records"""
    if row['FOUND'] == 'Matched':
        bank_commission = row.get('TOTAL COMMISSION', 0) or 0
        broker_commission = row.get('TOTAL COMMISSION BROKER', 0) or 0
        return float(bank_commission) - float(broker_commission)
    elif row['FOUND'] == 'Not Found in Broker':
        return float(row.get('TOTAL COMMISSION', 0) or 0)
    else:
        return -float(row.get('TOTAL COMMISSION BROKER', 0) or 0)

def display_results_summary(merged_df):
    """Display summary statistics of the comparison results."""
    total_records = len(merged_df)
    matched = len(merged_df[merged_df['FOUND'] == 'Matched'])
    not_in_bank = len(merged_df[merged_df['FOUND'] == 'Not Found in Bank'])
    not_in_broker = len(merged_df[merged_df['FOUND'] == 'Not Found in Broker'])

    st.write("Comparison Summary:")
    st.write(f"Total Records: {total_records}")
    st.write(f"Matched Records: {matched}")
    st.write(f"Records Not Found in Bank: {not_in_bank}")
    st.write(f"Records Not Found in Broker: {not_in_broker}")










if __name__ == "__main__":
    main()
