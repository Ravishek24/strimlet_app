import pandas as pd

def broker_data_process(df):
    # Filtering the DataFrame based on the conditions
    filtered_df = df

    # Selecting specific columns and renaming to match the structure of the concatenated insurance file
    selected_columns = filtered_df[['PolicyNumber', 'p_insurerName', 'cName', 'odPremium', 'TpPremium', 'commisionRate', 'NetCommision']].copy()
    selected_columns.columns = ['POLICY_REFERENCE', 'Bank Name', 'CUSTOMER NAME', 'OD PREMIUM', 'TP PREMIUM', 'COMMISSION RATE', 'TOTAL COMMISSION BROKER']  # Rename to match the insurance data

    # Adding a new column with a default value
    selected_columns.loc[:, 'Source'] = 'BROKER'

    # Ensure POLICY_REFERENCE is treated as a string
    selected_columns['POLICY_REFERENCE'] = selected_columns['POLICY_REFERENCE'].astype(str)

    # Parsing POLICY_REFERENCE: Special conditions for specific banks
    selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns.apply(
        lambda row: 
        # Special condition for GO-DIGIT
        row['POLICY_REFERENCE'].split('/')[0].strip() if row['Bank Name'] == 'GO DIGIT GENERAL INSURANCE LIMITED' else
        # Special condition for TATA AIG GENERAL INSURANCE COMPANY LIMITED
        (row['POLICY_REFERENCE'][:10] if len(row['POLICY_REFERENCE']) > 10 else row['POLICY_REFERENCE']) 
        if row['Bank Name'] == 'TATA AIG GENERAL INSURANCE COMPANY LIMITED' else 
        # General condition for other banks
        row['POLICY_REFERENCE'], axis=1
    )

    # Clean up Parsed_POLICY_REFERENCE to retain only alphanumeric characters for all banks
    selected_columns['Parsed_POLICY_REFERENCE'] = selected_columns['Parsed_POLICY_REFERENCE'].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)

    return selected_columns
