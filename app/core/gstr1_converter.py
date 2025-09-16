import pandas as pd
from pathlib import Path
from app.core.common_processors import (
    load_json_from_path,
    json_normalize_with_meta,
    safe_reorder,
    convert_column_to_date,
    split_nested_and_non_nested_keys
)

# --- Constants ---
BASE_CONFIG_DIR = Path(__file__).resolve().parents[2] / "resources" / "configs"
STRUCTURE_PATH = BASE_CONFIG_DIR / "gstr1_structure.json"

STRUCTURE_FILE = load_json_from_path(STRUCTURE_PATH)

# --- Main Conversion Function ---

def convert_gstr1_json_to_excel(json_path, excel_path,structure_file=STRUCTURE_FILE):
    """
    Converts a GSTR-1 JSON file to an Excel file based on a structure config.
    """
    data = load_json_from_path(json_path)
    if data is None:
        return (False, "Error reading or parsing JSON file")

    if structure_file is None:
        return (False, "Error reading or parsing structure JSON file")

    try:
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # 1. Create and write the Basic Info sheet
            _, non_nested_keys = split_nested_and_non_nested_keys(data)
            basic_info_data = {k: data[k] for k in non_nested_keys if k in data}
            if basic_info_data:
                basic_info_df = pd.DataFrame(list(basic_info_data.items()), columns=['Key', 'Value'])
                basic_info_df.to_excel(writer, sheet_name='Basic Info', index=False)

            # 2. Process and write each major section based on the config
            for section_key, config in structure_file.items():
                if section_key in data and data[section_key]:
                    try:
                        # Use the generic processor for all sections
                        df = json_normalize_with_meta(
                            data[section_key],
                            record_path=config.get("record_path"),
                            meta=config.get("meta")
                        )

                        if df.empty:
                            continue

                        rename_dict = config.get("rename_dict", {})
                        order_list = config.get("order_df", [])

                        if rename_dict and order_list:
                            df = safe_reorder(df, rename_dict, order_list)

                        if 'Date' in df.columns:
                            df = convert_column_to_date(df, "Date")

                        if not df.empty:
                            df.to_excel(writer, sheet_name=config.get("sheet_name", section_key), index=False)
                    except Exception as e:
                        print(f"Warning: Could not process section '{section_key}'. Error: {e}")

        return (True, f"Successfully converted {json_path} to {excel_path}")
    except Exception as e:
        return (False, f"Error during Excel conversion: {e}")
