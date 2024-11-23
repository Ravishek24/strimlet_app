import pdfplumber
from components.data_cleaning import clean_pdf_data 
from components.data_processing import process_bank_data
import pandas as pd

def process_pdf_bank_data(pdf_path, bank_name):
    """Extract tabular data from a PDF, clean it, and process based on bank."""
    try:
        # Extract tabular data using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:  # Check for non-empty tables
                        all_tables.extend(table)

        # Create a DataFrame from the extracted data
        if not all_tables:
            raise ValueError("No tables found in the PDF.")

        df = pd.DataFrame(all_tables)

        # Optional: If the first row contains headers, set it as the DataFrame header
        df.columns = df.iloc[0]  # Set first row as header if applicable
        df = df.drop(0)  # Remove the first row if used as header
        df = df.reset_index(drop=True)  # Reset index

        # Clean the data
        cleaned_df = clean_pdf_data(df, bank_name)

        # Call process_bank_data() to process the cleaned data based on bank-specific rules
        processed_data = process_bank_data(cleaned_df, bank_name)
        return processed_data

    except Exception as e:
        raise RuntimeError(f"Error processing PDF file: {e}")