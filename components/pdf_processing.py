import pdfplumber
import pandas as pd
from components.data_cleaning import clean_pdf_data

def process_pdf_bank_data(pdf_path, bank_name):
    """
    Extract tabular data from a PDF, clean it based on bank-specific rules, and return as a DataFrame.

    Parameters:
    pdf_path (str): Path to the PDF file.
    bank_name (str): The name of the bank to apply specific cleaning rules.

    Returns:
    pd.DataFrame: Cleaned DataFrame containing extracted tabular data from the PDF.
    """
    try:
        # Extract tabular data using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table_num, table in enumerate(tables, start=1):
                    if table:  # Check for non-empty tables
                        print(f"Page {page_num}, Table {table_num}: Extracted {len(table)} rows.")
                        all_tables.extend(table)

        # Ensure tables were extracted
        if not all_tables:
            raise ValueError("No tables found in the PDF.")

        # Normalize rows to ensure consistent column lengths
        max_cols = max(len(row) for row in all_tables if row)
        normalized_table = [
            row + [''] * (max_cols - len(row)) for row in all_tables
        ]
        df = pd.DataFrame(normalized_table)

        print("Extracted DataFrame (Before Cleaning):")
        print(df.head())

        # Validate and assign headers
        headers = df.iloc[0].fillna("").tolist()
        headers = [f"Unnamed_{i}" if not col or col.strip() == "" else col for i, col in enumerate(headers)]

        # Deduplicate headers by appending a counter to duplicates
        seen = {}
        unique_headers = []
        for col in headers:
            if col in seen:
                seen[col] += 1
                unique_headers.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                unique_headers.append(col)

        # Assign unique headers
        df.columns = unique_headers
        df = df.drop(0).reset_index(drop=True)

        print("DataFrame After Header Assignment:")
        print(df.head())

        # Clean the data using bank-specific rules
        cleaned_df = clean_pdf_data(df, bank_name)

        print("Cleaned DataFrame (After Cleaning):")
        print(cleaned_df.head())

        return cleaned_df

    except Exception as e:
        raise RuntimeError(f"Error processing PDF file: {e}")
