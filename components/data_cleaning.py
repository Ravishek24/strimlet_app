import pandas as pd

def clean_pdf_data(df, bank_name):
    """Clean the extracted DataFrame based on the bank-specific rules.
    
    Parameters:
    df (pd.DataFrame): The extracted DataFrame from the PDF.
    bank_name (str): The name of the bank to apply specific cleaning rules.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    try:
        # Bank-specific cleaning logic
        if bank_name == "The New India Pdf":
            # Drop rows below the first occurrence of a missing 'Policy Number'
            if 'Policy Number' in df.columns:
                # Find the index of the first row with a missing 'Policy Number'
                invalid_index = df[df['Policy Number'].isna() | (df['Policy Number'].astype(str).str.strip() == "")].index
                if not invalid_index.empty:
                    first_invalid_index = invalid_index[0]
                    # Keep rows above (and including) the first invalid 'Policy Number'
                    df = df.loc[:first_invalid_index - 1]
                    

        elif bank_name == "United Pdf":
            # Remove the top two rows
            df = df.iloc[1:].reset_index(drop=True)
            # Remove the first column
            if not df.empty:
                df = df.iloc[:, 1:]
            df.columns = df.iloc[0]  # Set the first row as the header
            df = df.drop(0).reset_index(drop=True)  # Remove the row that is now the header


        # General cleaning applicable to all banks (if any)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Trim whitespace

        return df

    except Exception as e:
        raise RuntimeError(f"Error cleaning data for {bank_name}: {e}")
