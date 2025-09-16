import pandas as pd
import json
import os

# --- Generic Processors ---
def json_normalize_with_meta(json_data: dict, record_path: list, meta: list) -> pd.DataFrame:
    """
    Normalizes a JSON object with a record path and meta information.
    """
    return pd.json_normalize(json_data, record_path=record_path, meta=meta)

def safe_reorder(df: pd.DataFrame, rename_dict: dict, new_order: list) -> pd.DataFrame:
    """
    Safely reorders the columns of a DataFrame after renaming them.

    Args:
        df (pd.DataFrame): The DataFrame whose columns are to be reordered.
        rename_dict (dict): A dictionary mapping existing column names to new names for renaming.
        new_order (list): A list specifying the desired order of columns after renaming.

    Returns:
        pd.DataFrame: The DataFrame with columns renamed and reordered according to new_order. 
                      Columns not present in the DataFrame are ignored; columns not listed in new_order are excluded from the result.
    """
    try:
        # Rename  columns
        df = df.rename(columns=rename_dict, errors='ignore')
        
        # Create safe column order (only include columns that exist)
        safe_order = [col for col in new_order if col in df.columns]
        
        # Reorder columns
        return df[safe_order]
    except Exception as e:
        # Optionally, you can log the error or handle it as needed
        print(f"Error in safe_reorder: {e}")
        return df
    
def split_nested_and_non_nested_keys(json_data: dict) -> tuple:
    """
    Splits the keys of a dictionary into nested (dict or list values) and non-nested keys.

    Args:
        json_data (dict): The dictionary to process.

    Returns:
        tuple: (nested_keys, non_nested_keys)
    """
    nested_keys = []
    non_nested_keys = []

    for key, value in json_data.items():
        if isinstance(value, (dict, list)):
            nested_keys.append(key)
        else:
            non_nested_keys.append(key)
    return nested_keys, non_nested_keys

def convert_column_to_date(df: pd.DataFrame, column_name : str = "Date", date_format: str = None, errors: str = 'coerce') -> pd.DataFrame:
    """
    Converts a DataFrame column to datetime dtype.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to convert.
        date_format (str, optional): The date format to use for parsing. Defaults to None (let pandas infer).
        errors (str, optional): How to handle errors. 'coerce' will set invalid parsing as NaT. Defaults to 'coerce'.

    Returns:
        pd.DataFrame: The DataFrame with the column converted to datetime.
    """
    if column_name in df.columns:
        df[column_name] = pd.to_datetime(df[column_name], format=date_format, errors=errors)
    return df

# json loader function from json path
def load_json_from_path(json_path: str) -> dict:
    """
    Loads a JSON file from the given path.
    """

    if not str(json_path).lower().endswith('.json'):
        print(f"Error in load_json_from_path: The file '{json_path}' is not a JSON file.")
        return None
    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error in load_json_from_path: {e}")
        return None

def process_drop(items: list) -> list:
    """
    items: list of dropped paths (files or directories)
    """
    final_files = []

    for path in items:
        if os.path.isfile(path):
            # Single file
            final_files.append(path)

        elif os.path.isdir(path):
            # Only files directly inside the folder
            for f in os.listdir(path):
                full_path = os.path.join(path, f)
                if os.path.isfile(full_path):
                    final_files.append(full_path)
        else:
            print(f"Skipping unknown path: {path}")

    return final_files
def write_df_to_excel(df, excel_path, sheet_name='Sheet1', index=False, headers = True, startrow=1, startcol=1):
    """
    Writes a pandas DataFrame to an Excel file using xlsxwriter.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        excel_path (str): The path to the Excel file to create.
        sheet_name (str, optional): The name of the sheet. Defaults to 'Sheet1'.
        index (bool, optional): Whether to write row indices. Defaults to False.
    """
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=index, headers=headers, startrow=startrow, startcol=startcol)

def process_basic_info(data, excel_path):
    _ , non_nested_keys  = split_nested_and_non_nested_keys(data)
    
    filtered_data = {k: data[k] for k in non_nested_keys if k in data}
    basic_data_df = pd.DataFrame(filtered_data)
    
    write_df_to_excel(basic_data_df, excel_path, sheet_name="Basic Info", headers=False, startcol=9, startrow=7)

def process_section(data, section_config: dict, excel_path):
    """Process a GST section using the provided config structure."""
    df = json_normalize_with_meta(
        data,
        record_path=section_config.get("record_path"),
        meta=section_config.get("meta")
    )
    
    df = safe_reorder(
        df,
        rename_dict=section_config.get("rename_dict"),
        new_order=section_config.get("order_df")
    )
    
    write_df_to_excel(
        df,
        excel_path,
        sheet_name=section_config.get("sheet_name", "Sheet1")
    )
    
# Deprecated functions below
def process_invoice_items(items_list):
    """
    A common utility to process the 'itms' list found in many GSTR sections.
    It unnests the 'itm_det' dictionary.
    
    Args:
        items_list (list): The list of item objects (e.g., invoice['itms']).
        
    Returns:
        list: A list of dictionaries, where each dictionary is a flattened item.
    """
    processed_items = []
    for item in items_list:
        item_details = item.get('itm_det', {})
        processed_item = {
            'item_number': item.get('num'),
            'taxable_value': item_details.get('txval', 0),
            'rate': item_details.get('rt', 0),
            'igst': item_details.get('iamt', 0),
            'cgst': item_details.get('camt', 0),
            'sgst': item_details.get('samt', 0),
            'cess': item_details.get('csamt', 0)
        }
        processed_items.append(processed_item)
    return processed_items

def flatten_and_normalize_data(section_data, record_key, item_key='inv'):
    """
    A generic function to flatten nested invoice-like structures.
    Handles structures like b2b, cdnr, etc. where there's a list of
    parties, and each party has a list of records (invoices/notes).
    
    Args:
        section_data (list): The list of data for a whole section (e.g., data['b2b']).
        record_key (str): The key for the recipient's identifier (e.g., 'ctin').
        item_key (str): The key for the list of items (e.g., 'inv' for invoices, 'nt' for notes).

    Returns:
        pandas.DataFrame: A flattened and processed DataFrame for the section.
    """
    all_records = []
    for party in section_data:
        party_identifier = party.get(record_key)
        for record in party.get(item_key, []):
            # Base details from the record
            record_details = {
                'recipient_gstin': party_identifier,
                'invoice_or_note_number': record.get('inum') or record.get('nt_num'),
                'date': record.get('idt') or record.get('nt_dt'),
                'total_value': record.get('val'),
            }
            
            # Process the nested items list
            items = process_invoice_items(record.get('itms', []))
            
            # If there are multiple items, create a row for each.
            # If there are no items, create one row with the main details.
            if items:
                for item in items:
                    full_record = record_details.copy()
                    full_record.update(item)
                    all_records.append(full_record)
            else:
                all_records.append(record_details)

    return pd.DataFrame(all_records)

def simple_dataframe_processor(data):
    """
    Simply converts the given data to a DataFrame.
    Used for sections that are already flat lists of records.
    """
    return pd.DataFrame(data)

# --- GSTR-1 Specific Processors ---

def hsn_summary_processor(data):
    """
    Processes the HSN summary section of GSTR-1.
    """
    # The actual data is in a nested 'data' key, and each item has a 'det' key
    hsn_items = [item.get('det', {}) for item in data.get('data', [])]
    return pd.DataFrame(hsn_items)

def nil_summary_processor(data):
    """
    Processes the Nil-rated summary section of GSTR-1.
    """
    # The structure is a list of objects, each with an 'inv' list that contains one object
    nil_items = [item.get('inv', [{}])[0] for item in data]
    return pd.DataFrame(nil_items)

def doc_issue_processor(data):
    """
    Processes the complex 'doc_issue' section of GSTR-1.
    """
    all_docs = []
    # The actual list of documents is nested inside 'doc_det'
    for doc_summary in data.get('doc_det', []):
        all_docs.extend(doc_summary.get('docs', []))
    return pd.DataFrame(all_docs)
