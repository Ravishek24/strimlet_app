import pandas as pd
import re

def clean_pdf_data(df, bank_name):
    """
    Clean the extracted DataFrame based on bank-specific rules.

    Parameters:
    df (pd.DataFrame): The extracted DataFrame from the PDF.
    bank_name (str): The name of the bank to apply specific cleaning rules.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    try:
        print(f"Cleaning data for bank: {bank_name}")
        print("Original DataFrame (First 5 Rows):")
        print(df.head())

        # Bank-specific cleaning logic
        if bank_name == "The New India Pdf":
            # Drop rows where 'Policy Number' is NaN or empty
            df = df.dropna(subset=['Policy Number'])
            df = df[df['Policy Number'].astype(str).str.strip() != ""]
            df = df[~df['Policy Number'].astype(str).str.fullmatch(r'0+')]

            # Select required columns dynamically
            required_columns = {
                'Policy Number': 'Policy Reference',
                'Insured Name': 'Customer Name',
                'Premium': 'Premium Bank',
                'Brokerage': 'Total Commission'
            }

            # Alternative column names to check for 'Insured Name'
            insured_name_alternatives = ['Insured Name', 'INSURED NAME', 'Insured name', 'Customer Name']

            # Find the correct column for 'Insured Name'
            for alt_name in insured_name_alternatives:
                if alt_name in df.columns:
                    required_columns[alt_name] = 'Customer Name'
                    break  # Stop searching once a match is found

            # Select the available columns
            available_columns = {col: new_col for col, new_col in required_columns.items() if col in df.columns}
            df = df[list(available_columns.keys())]

            # Rename columns to new names
            df = df.rename(columns=available_columns)

            # Add Source column with the bank name
            df['Source'] = "New India"

            # Parse Policy Reference
            def parse_policy_reference(policy):
                # Remove everything except numbers
                policy_str = ''.join(filter(str.isdigit, str(policy)))
                # Remove digits after the last set of five zeros
                parsed_policy = re.sub(r'0{5}\d{1,3}$', '00000', policy_str)
                return parsed_policy

            df['PARSED_POLICY_REFERENCE'] = df['Policy Reference'].apply(parse_policy_reference)

            # Drop rows where the parsed policy reference is empty
            df = df[df['PARSED_POLICY_REFERENCE'].str.strip() != ""]

            print("Cleaned DataFrame (First 5 Rows):")
            print(df.head())

            return df


        elif bank_name == "United Pdf":
            # Ensure the table has at least 2 rows for cleaning
            if df.shape[0] < 2:
                raise ValueError("The table does not have enough rows to extract headers.")

            # Set the second row as header and drop the first two rows
            df.columns = df.iloc[1].fillna("Unnamed").tolist()
            df = df.iloc[2:].reset_index(drop=True)

            # Deduplicate column names
            seen = {}
            unique_headers = []
            for col in df.columns:
                if col in seen:
                    seen[col] += 1
                    unique_headers.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    unique_headers.append(col)
            df.columns = unique_headers

            # Extract required columns
            required_columns = {
                'Policy/ Endt number': 'Policy Reference',
                'Insured Name': 'Customer Name',
                'ELG Premium Amount': 'Premium Bank',
                'Commission Amount': 'Total Commission'
            }
            df = df[list(required_columns.keys())]

            # Rename columns to new names
            df = df.rename(columns=required_columns)

            # Add Source column with the bank name
            df['Source'] = "United"

            # Parse Policy Reference
            def parse_policy_reference(policy):
                # Remove everything after '/' including the slash
                parsed_policy = re.sub(r"/.*", "", str(policy))
                # Ensure it's alphanumeric
                if re.match(r'^[a-zA-Z0-9]+$', parsed_policy):
                    return parsed_policy
                return None  # Invalid policy number

            df['PARSED_POLICY_REFERENCE'] = df['Policy Reference'].apply(parse_policy_reference)

            # Remove rows with invalid or missing Parsed Policy Reference
            df = df.dropna(subset=['PARSED_POLICY_REFERENCE'])

            # Clean numeric columns
            def clean_numeric(value):
                # Remove commas and whitespace, and convert to numeric
                if isinstance(value, str):
                    value = value.replace(",", "").strip()
                return pd.to_numeric(value, errors='coerce')

            df['Premium Bank'] = df['Premium Bank'].apply(clean_numeric).fillna(0)
            df['Total Commission'] = df['Total Commission'].apply(clean_numeric).fillna(0)

            print("Data After Cleaning Numeric Columns (First 5 Rows):")
            print(df[['Premium Bank', 'Total Commission']].head())

            # Group by Parsed Policy Reference and aggregate values
            df = df.groupby(['PARSED_POLICY_REFERENCE', 'Customer Name', 'Source'], as_index=False).agg({
                'Premium Bank': 'sum',
                'Total Commission': 'sum',
                'Policy Reference': 'first'  # Keep one policy reference
            })

            # Rearrange columns
            df = df[[
                'Policy Reference',
                'Customer Name',
                'Premium Bank',
                'Total Commission',
                'Source',
                'PARSED_POLICY_REFERENCE'
            ]]

            print("Cleaned DataFrame (First 5 Rows):")
            print(df.head())

            return df


        else:
            print(f"No specific cleaning rules defined for bank: {bank_name}")

        # General cleaning: Trim whitespace and handle empty cells
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Trim strings
        df = df.replace('', pd.NA)  # Replace empty strings with NaN for consistency
        df = df.dropna(how='all')  # Drop rows where all elements are NaN

        return df

    except Exception as e:
        raise RuntimeError(f"Error cleaning data for {bank_name}: {e}")
