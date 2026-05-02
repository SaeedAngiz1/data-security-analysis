import pandas as pd
import hashlib
import os
import io
from cryptography.fernet import Fernet

def generate_key():
    """Generates a new Fernet encryption key."""
    return Fernet.generate_key()

def encrypt_dataframe(df: pd.DataFrame, key: bytes) -> bytes:
    """
    Encrypts a Pandas DataFrame using AES (Fernet).
    Serializes the dataframe to CSV, then encrypts it.
    """
    f = Fernet(key)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    encrypted_data = f.encrypt(csv_bytes)
    return encrypted_data

def decrypt_dataframe(encrypted_data: bytes, key: bytes) -> pd.DataFrame:
    """
    Decrypts encrypted data back into a Pandas DataFrame.
    """
    f = Fernet(key)
    decrypted_bytes = f.decrypt(encrypted_data)
    csv_buffer = io.StringIO(decrypted_bytes.decode('utf-8'))
    df = pd.read_csv(csv_buffer)
    return df

def tokenize_column(df: pd.DataFrame, column_name: str, method: str = 'hash') -> pd.DataFrame:
    """
    Tokenizes a specific column in the dataframe.
    method can be 'hash' (SHA-256) or 'mask' (replace with generic tokens).
    """
    df_copy = df.copy()
    if column_name not in df_copy.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    if method == 'hash':
        # Apply SHA-256 hash to string representation of the value
        df_copy[column_name] = df_copy[column_name].apply(
            lambda x: hashlib.sha256(str(x).encode('utf-8')).hexdigest()[:16] # Shortened for readability
        )
    elif method == 'mask':
        # Mask with generic token
        df_copy[column_name] = df_copy[column_name].apply(
            lambda x: f"TOKEN_{hash(str(x)) % 1000000}"
        )
    else:
        raise ValueError("Invalid method. Choose 'hash' or 'mask'.")
    
    return df_copy
