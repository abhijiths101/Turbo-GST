import pandas as pd
import json
import os
from . import common_processors

# --- Constants ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'configs', 'gstr2_processors.json')
BASIC_INFO_KEYS = ["gstin", "fp", "gt", "cur_gt"]

# --- Processor Mapping ---
# Maps processor names from JSON config to actual Python functions
PROCESSOR_MAP = {
    "flatten_and_normalize": common_processors.flatten_and_normalize_data,
    "simple_dataframe": common_processors.simple_dataframe_processor,
}

# --- Main Conversion Function ---

def convert_gstr2_to_excel(json_path, excel_path):
    """
    Reads a GSTR-2A/B JSON file, processes all its sections based on an external
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
        with open(CONFIG_PATH, 'r') as f:
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
                        processor_func = PROCESSOR_MAP.get(processor_func_name)
                        
                        if not processor_func:
                            print(f"Warning: Processor '{processor_func_name}' for section '{key}' is not defined. Skipping.")
                            continue

                        # Get arguments for the processor, if any
                        args = config.get("args", {})
                        
                        # Call the processor with the data and arguments
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
