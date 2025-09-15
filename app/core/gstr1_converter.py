import pandas as pd
import json
from pathlib import Path
from app.core.common_processors import (convert_column_to_date, load_json_from_path, process_basic_info)

from app.core.common_processors import (flatten_and_normalize_data, simple_dataframe_processor, hsn_summary_processor,
                                        nil_summary_processor, doc_issue_processor, safe_reorder, json_normalize_with_meta,
                                        )

# --- Constants ---
BASE_CONFIG_DIR = Path(__file__).resolve().parents[2] / "resources" / "configs"
STRUCTURE_PATH = BASE_CONFIG_DIR / "gstr1_structure.json"

STRUCTURE_FILE = load_json_from_path(STRUCTURE_PATH)

# BASIC_INFO_KEYS = ["gstin", "fp", "gt", "cur_gt"]

# --- Processor Mapping ---
# Maps processor names from JSON config to actual Python functions
PROCESSOR_MAP = {
    "flatten_and_normalize": flatten_and_normalize_data,
    "simple_dataframe":  simple_dataframe_processor,
    "hsn_summary_processor":  hsn_summary_processor,
    "nil_summary_processor":  nil_summary_processor,
    "doc_issue_processor":  doc_issue_processor,
}

# Sub Process conversion functions

# --- Main Conversion Function ---

def convert_gstr1_json_to_excel(json_path, excel_path, config_path, structure_file=STRUCTURE_FILE):
    """
    Converts a GSTR-1 JSON file to an Excel file.
    """
    # Load the JSON data and check
    data = load_json_from_path(json_path)
    if data is None:
        return (False, "Error reading or parsing JSON file")
    # write basic info file
    process_basic_info(data)
    
    pass

# Deprecated ; will be removed soon
def convert_gstr1_to_excel(json_path, excel_path):
    """
    Reads a GSTR-1 JSON file, processes all its sections based on an external
    JSON configuration, and writes them to separate sheets in an Excel file.
    
    Returns a tuple (success, message).
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return (False, f"Error reading or parsing JSON file: {e}")

    try:
        # Load the processor configuration from the JSON file
        with open(STRUCTURE_PATH, 'r') as f:
            section_processors_config = json.load(f)
    except Exception as e:
        return (False, f"Error reading processor configuration file: {e}")

    try:
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # 1. Create and write the Basic Info sheet
            basic_info_df = create_basic_info_df(data)
            basic_info_df.to_excel(writer, sheet_name='Basic Info', index=False)

            # 2. Process and write each major section based on the config
            for key, config in section_processors_config.items():
                if key in data and data[key]:
                    try:
                        processor_func_name = config.get("processor")

                        if processor_func_name == 'flatten_and_normalize' and 'record_path' in config:
                            # New-style processing for sections like B2B
                            df = json_normalize_with_meta(
                                data[key],
                                record_path=config['record_path'],
                                meta=config['meta']
                            )

                            # Dynamically find rename dictionary
                            rename_key = next((k for k in config if k.startswith('rename_') and k.endswith('_dict')), None)
                            rename_dict = config.get(rename_key, {})
                            order_list = config.get('order_df', [])

                            if rename_dict and order_list:
                                df = safe_reorder(df, rename_dict, order_list)

                            if 'Date' in df.columns:
                                section_df = convert_column_to_date(df, "Date")
                            else:
                                section_df = df
                        else:
                            # Original processing path
                            processor_func = PROCESSOR_MAP.get(processor_func_name)

                            if not processor_func:
                                print(f"Warning: Processor '{processor_func_name}' for section '{key}' is not defined. Skipping.")
                                continue

                            args = config.get("args", {})
                            section_df = processor_func(data[key], **args)

                        if not section_df.empty:
                            section_df.to_excel(writer, sheet_name=config["sheet_name"], index=False)
                    except Exception as e:
                        print(f"Warning: Could not process section '{key}'. Error: {e}")

        return (True, f"Successfully converted {json_path} to {excel_path}")
    except Exception as e:
        return (False, f"Error during Excel conversion: {e}")

# --- Helper Functions ---

def create_basic_info_df(data):
    """
    Extracts the non-nested, basic information from the JSON data.
    """
    info = {key: data.get(key) for key in BASIC_INFO_KEYS if key in data}
    return pd.DataFrame(list(info.items()), columns=['Key', 'Value'])
