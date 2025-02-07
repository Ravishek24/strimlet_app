import pandas as pd
import streamlit as st

def process_bank_data(df, bank_name):
    """Process data based on the selected bank's specific logic."""
    # Define standard column names
    standard_columns = {
        "reference": "Policy Reference",
        "customer_name": "Customer Name",
        "commission": "Total Commission",
        "premium": "Premium Bank"  # New column for Premium Amount
    }

    # Bank-specific configurations
    bank_config = {
        "Bajaj": {"columns": ['POLICY_REFERENCE', 'CUSTOMER NAME ', 'TOTAL COMMISSION', 'NET PREMIUM'], "source": "Bajaj"},
        "CARE": {"columns": ['Policy No', 'Customer Name', 'Total Amount', 'Premium'], "source": "CARE"},
        "Cholamandalam": {"columns": ['POLICY_NO', 'INSURED_NAME', 'Total Payout', 'NET_PREMIUM'], "source": "Cholamandalam"},
        "FUTURE": {"columns": ['POLICY_NO', 'COMBINE_CLIENT_NAME', 'Com+Payout', 'GWP'], "source": "FUTURE"},
        "LIBERTY": {"columns": ['POLICY/ENDORSEMENT NO.', 'INSURED NAME', 'TOTAL COMMISSION', 'GWP'], "source": "LIBERTY"},
        "GO-DIGIT": {"columns": ['policy number', 'policy holder', 'IRDA_AMT', 'net premium'], "source": "GO-DIGIT"},
        "HDFC": {"columns": ['Certificate_Num', 'Customer_Name', 'TOTAL_COMM', 'GWP'], "source": "HDFC"},
        "ICICI": {"columns": ['POL_NUM_TXT', 'INSURED_CUSTOMER_NAME', 'ACTUAL_COMMISSION', 'PREMIUM_FOR_PAYOUTS'], "source": "ICICI"},
        "MANIPAL SIGNA": {"columns": ['Policy Number', 'Proposer Name', 'Commission', 'Base Premium'], "source": "MANIPAL SIGNA"},
        "NATIONAL NEHRU": {"columns": ['Policy No', 'Insured Name', 'Commission Amount', 'Premium Amount'], "source": "NATIONAL NEHRU"},
        "RELIANCE": {"columns": ['PolicyNumber', 'InsuredName', 'FinalIRDAComm', 'PremiumAmount'], "source": "RELIANCE"},
        "SBI": {"columns": ['Policy No', 'Insured Name', 'Total Commission', 'Gross Written Premium'], "source": "SBI"},
        "TATA AIG": {"columns": ['policy_no', 'clientname', 'Commission ', 'premiumamount'], "source": "TATA AIG"},
        "The New India Pdf": {"columns": ['Policy Number', 'Brokerage'], "source": "The New India Pdf"},
        "United Pdf": {"columns": ['Policy/ Endt number', 'Insured Name', 'Commission Amount'], "source": "United Pdf"}
    }

    # Validate if bank is supported
    if bank_name not in bank_config:
        st.warning(f"Bank '{bank_name}' is not supported.")
        return pd.DataFrame()

    # Get the configuration for the selected bank
    config = bank_config[bank_name]

    # Validate required columns
    try:
        validate_columns(df, config['columns'])
    except ValueError as e:
        st.error(str(e))
        return pd.DataFrame()

    # Process the data
    return process_specific_bank(df, config, standard_columns)

def validate_columns(df, required_columns):
    """Validate that required columns exist in the DataFrame."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

def process_specific_bank(df, config, standard_columns):
    """Process data for a specific bank."""
    filtered_df = df[df[config['columns'][0]].notna()]
    validate_columns(filtered_df, config['columns'])  # Validate columns dynamically
    selected_columns = filtered_df[config['columns']].copy()

    # Rename columns based on the configuration
    if len(config['columns']) == 4:
        selected_columns.columns = [
            standard_columns["reference"],
            standard_columns["customer_name"],
            standard_columns["commission"],
            standard_columns["premium"]
        ]
    else:
        selected_columns.columns = [
            standard_columns["reference"],
            standard_columns["customer_name"],
            standard_columns["commission"]
        ]

    # Convert all premium amounts to positive
    if "Premium Bank" in selected_columns.columns:
        selected_columns["Premium Bank"] = selected_columns["Premium Bank"].abs()

    # Add metadata and clean policy references
    selected_columns.loc[:, 'Source'] = config['source']
    selected_columns.loc[:, 'Parsed_POLICY_NUMBER_BANK'] = (
        selected_columns[standard_columns["reference"]]
        .astype(str)
        .str.replace(r'[^a-zA-Z0-9]', '', regex=True)
    )

    # Keep only the first occurrence of each Parsed_POLICY_NUMBER_BANK
    selected_columns = selected_columns.drop_duplicates(subset=['Parsed_POLICY_NUMBER_BANK'], keep='first')

    return selected_columns
