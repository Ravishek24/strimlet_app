import re

def broker_data_process(df):
    # Filtering the DataFrame based on the conditions
    filtered_df = df

    # Selecting specific columns and renaming to match the structure of the concatenated insurance file
    selected_columns = filtered_df[['PolicyNumber', 'p_insurerName', 'cName', 'odPremium', 'TpPremium', 'commisionRate', 'NetCommision', 'insNature', 'TotalPremium']].copy()
    selected_columns.columns = [
        'POLICY_REFERENCE', 'Bank Name', 'CUSTOMER NAME', 'OD PREMIUM', 'TP PREMIUM',
        'COMMISSION RATE', 'TOTAL COMMISSION BROKER', 'INSURANCE NATURE', 'TOTAL PREMIUM'
    ]

    # Convert 'TOTAL COMMISSION BROKER' and premiums to positive values
    selected_columns['TOTAL COMMISSION BROKER'] = selected_columns['TOTAL COMMISSION BROKER'].abs()
    selected_columns['OD PREMIUM'] = selected_columns['OD PREMIUM'].abs()
    selected_columns['TP PREMIUM'] = selected_columns['TP PREMIUM'].abs()
    selected_columns['TOTAL PREMIUM'] = selected_columns['TOTAL PREMIUM'].abs()

    # Adding a new column with a default value
    selected_columns.loc[:, 'Source'] = 'BROKER'

    # Ensure POLICY_REFERENCE is treated as a string and strip leading/trailing spaces
    selected_columns['POLICY_REFERENCE'] = selected_columns['POLICY_REFERENCE'].astype(str).str.strip()

    # Parsing POLICY_REFERENCE: Special conditions for specific banks
    def parse_policy_reference(row):
        policy_number = row['POLICY_REFERENCE']
        bank_name = row['Bank Name']

        if bank_name == 'GO DIGIT GENERAL INSURANCE LIMITED':
            # Remove everything after '/'
            return policy_number.split('/')[0].strip()

        elif bank_name == 'TATA AIG GENERAL INSURANCE COMPANY LIMITED':
            # Remove the first 0 if the policy number starts with it
            if policy_number.startswith('0'):
                policy_number = policy_number[1:]
            # Keep only the first 10 characters
            return policy_number[:10] if len(policy_number) > 10 else policy_number

        elif bank_name == 'THE NEW INDIA ASSURANCE COMPANY LIMITED':
            # Remove the last 3 digits if policy number ends with 8 zeros + 3 digits
            if re.search(r'0{8}\d{3}$', policy_number):
                return policy_number[:-3]  # Remove last 3 digits
            return policy_number  # Keep as is if condition isn't met

        else:
            return policy_number  # Default case

    # Apply the parsing function
    selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns.apply(parse_policy_reference, axis=1)

    # Clean up Parsed_POLICY_REFERENCE to retain only alphanumeric characters for all banks
    selected_columns['Parsed_POLICY_REFERENCE'] = selected_columns['Parsed_POLICY_REFERENCE'].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)

    return selected_columns
