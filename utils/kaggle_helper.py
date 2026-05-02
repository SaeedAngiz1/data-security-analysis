import os
import tempfile
import pandas as pd
import subprocess

def authenticate_kaggle(username: str, key: str):
    """
    Sets up the environment for Kaggle authentication.
    """
    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = key
    # Ensure kaggle package sees these
    return True

def search_datasets(query: str):
    """
    Searches for datasets on Kaggle via CLI to avoid import singleton issues.
    """
    try:
        # kaggle datasets list -s "query" --csv
        result = subprocess.run(
            ['kaggle', 'datasets', 'list', '-s', query, '--csv'], 
            capture_output=True, text=True, check=True
        )
        # Parse CSV output
        import io
        df = pd.read_csv(io.StringIO(result.stdout))
        return df[['ref', 'title', 'size']] if not df.empty else pd.DataFrame()
    except Exception as e:
        print(f"Kaggle search error: {e}")
        return pd.DataFrame()

def download_dataset(dataset_ref: str) -> pd.DataFrame:
    """
    Downloads a dataset and attempts to load the first CSV file found.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', dataset_ref, '-p', temp_dir, '--unzip'],
            check=True, capture_output=True
        )
        
        # Find first CSV
        for file in os.listdir(temp_dir):
            if file.endswith('.csv'):
                return pd.read_csv(os.path.join(temp_dir, file))
        
        return None
    except Exception as e:
        print(f"Kaggle download error: {e}")
        return None
