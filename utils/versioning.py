import pandas as pd
from datetime import datetime

def init_version_control(df: pd.DataFrame):
    """
    Initializes the version control history.
    """
    return [{
        'version': 1,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'dataframe': df.copy(),
        'description': "Initial import",
        'diff_summary': None
    }]

def get_diff(df_old: pd.DataFrame, df_new: pd.DataFrame) -> dict:
    """
    Computes a basic diff between two dataframes.
    Assumes they have the same structure for simplicity,
    or at least detects row/column count changes.
    """
    diff_info = {
        'rows_added': max(0, len(df_new) - len(df_old)),
        'rows_removed': max(0, len(df_old) - len(df_new)),
        'columns_added': [c for c in df_new.columns if c not in df_old.columns],
        'columns_removed': [c for c in df_old.columns if c not in df_new.columns],
        'changed_cells': 0
    }
    
    # Very basic cell difference count if shapes match
    if df_old.shape == df_new.shape and all(df_old.columns == df_new.columns):
        try:
            # fillna to avoid NA != NA
            old_filled = df_old.fillna("NA_VAL")
            new_filled = df_new.fillna("NA_VAL")
            diff_info['changed_cells'] = (old_filled != new_filled).sum().sum()
        except:
            pass

    return diff_info

def commit_changes(history: list, df_new: pd.DataFrame, description: str = "Manual Edit"):
    """
    Commits a new version of the dataframe.
    """
    if not history:
        return init_version_control(df_new)
        
    last_version = history[-1]
    df_old = last_version['dataframe']
    
    # Check if anything actually changed
    if df_old.equals(df_new):
        return history # No changes
        
    diff_info = get_diff(df_old, df_new)
    
    new_version_num = last_version['version'] + 1
    new_commit = {
        'version': new_version_num,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'dataframe': df_new.copy(),
        'description': description,
        'diff_summary': diff_info
    }
    
    history.append(new_commit)
    return history
