import pandas as pd
import streamlit as st

def process_bank_data(df, bank_name):
    """Process data based on the selected bank's specific logic."""
    # Define a common naming scheme for columns
    standard_columns = {
        "reference": "Policy Reference",
        "customer_name": "Customer Name",
        "commission": "Total Commission"
    }

    if bank_name == "Bajaj":
        if 'POLICY_REFERENCE' in df.columns:
            filtered_df = df[df['POLICY_REFERENCE'].notna()]
            selected_columns = filtered_df[['POLICY_REFERENCE', 'CUSTOMER NAME ', 'TOTAL COMMISSION']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'Bajaj'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "CARE":
        if 'Policy No' in df.columns:
            filtered_df = df[df['Policy No'].notna()]
            selected_columns = filtered_df[['Policy No', 'Customer Name', 'Total Amount']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'CARE'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "Cholamandalam":
        if 'POLICY_NO' in df.columns:
            filtered_df = df[df['POLICY_NO'].notna()]
            selected_columns = filtered_df[['POLICY_NO', 'INSURED_NAME', 'Total Payout']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'Cholamandalam'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "FUTURE":
        if 'POLICY_NO' in df.columns:
            filtered_df = df[df['POLICY_NO'].notna()]
            selected_columns = filtered_df[['POLICY_NO', 'COMBINE_CLIENT_NAME', 'Com+Payout']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'FUTURE'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "IFFCO":
        if 'Policy number' in df.columns:
            filtered_df = df[df['Policy number'].notna()]
            selected_columns = filtered_df[['Policy number', 'Client Name', 'Total Eligible']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'IFFCO'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "LIBERTY":
        if 'POLICY/ENDORSEMENT NO.' in df.columns:
            filtered_df = df[df['POLICY/ENDORSEMENT NO.'].notna()]
            selected_columns = filtered_df[['POLICY/ENDORSEMENT NO.', 'INSURED NAME', 'TOTAL COMMISSION']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'LIBERTY'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "GO-DIGIT":
        if 'policy number' in df.columns:
            filtered_df = df[df['policy number'].notna()]
            selected_columns = filtered_df[['policy number', 'policy holder', 'IRDA_AMT']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'GO-DIGIT'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "HDFC":
        if 'Certificate_Num' in df.columns:
            filtered_df = df[df['Certificate_Num'].notna()]
            selected_columns = filtered_df[['Certificate_Num', 'Customer_Name', 'TOTAL_COMM']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'HDFC'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "ICICI":
        if 'POL_NUM_TXT' in df.columns:
            filtered_df = df[df['POL_NUM_TXT'].notna()]
            
            selected_columns = filtered_df[['POL_NUM_TXT', 'INSURED_CUSTOMER_NAME', 'ACTUAL_COMMISSION']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'ICICI'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "MANIPAL SIGNA":
        if 'Policy Number' in df.columns:
            filtered_df = df[df['Policy Number'].notna()]
            selected_columns = filtered_df[['Policy Number', 'Proposer Name', 'Commission']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'MANIPAL SIGNA'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "NATIONAL NEHRU":
        if 'Policy No' in df.columns:
            filtered_df = df[df['Policy No'].notna()]
            selected_columns = filtered_df[['Policy No', 'Insured Name', 'Commission Amount']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'NATIONAL NEHRU'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "RELIANCE":
        if 'PolicyNumber' in df.columns:
            filtered_df = df[df['PolicyNumber'].notna()]
            selected_columns = filtered_df[['PolicyNumber', 'InsuredName', 'FinalIRDAComm']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'RELIANCE'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()
        
    elif bank_name == "SBI":
        if 'Policy No' in df.columns:
            filtered_df = df[df['Policy No'].notna()]
            selected_columns = filtered_df[['Policy No', 'Insured Name', 'Total Commission']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'SBI'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()
        
    elif bank_name == "TATA AIG":
        if 'policy_no' in df.columns:
            filtered_df = df[df['policy_no'].notna()]
            selected_columns = filtered_df[['policy_no', 'clientname', 'Commission ']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'TATA AIG'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    elif bank_name == "The New India Pdf":
        if 'policy number' in df.columns:
            filtered_df = df[df['policy number'].notna()]
            possible_insured_columns = ['insured name', 'insuredname']
            insured_column = next((col for col in df.columns if col in possible_insured_columns), None)
            if insured_column:
                selected_columns = filtered_df[['policy number', insured_column, 'brokerage']].copy()
                selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
                selected_columns.loc[:, 'Source'] = 'The New India Pdf'
                selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
                return selected_columns
            else:
                st.warning("No valid 'Insured Name' column found.")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    elif bank_name == "United Pdf":
        if 'Policy/ Endt number' in df.columns:
            filtered_df = df[df['Policy/ Endt number'].notna()]
            selected_columns = filtered_df[['Policy/ Endt number', 'Insured Name', 'Commission Amount']].copy()
            selected_columns.columns = [standard_columns["reference"], standard_columns["customer_name"], standard_columns["commission"]]
            selected_columns.loc[:, 'Source'] = 'United Pdf'
            selected_columns.loc[:, 'Parsed_POLICY_REFERENCE'] = selected_columns[standard_columns["reference"]].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return selected_columns
        else:
            return pd.DataFrame()

    else:
        if 'POLICY_REFERENCE' in df.columns:
            filtered_df = df[df['POLICY_REFERENCE'].notna()]
            filtered_df['Cleaned_POLICY_REFERENCE'] = filtered_df['POLICY_REFERENCE'].str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            return filtered_df
        else:
            return pd.DataFrame()