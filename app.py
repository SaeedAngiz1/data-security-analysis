import streamlit as st
import pandas as pd
import io
import os
import sys
import base64

# Add current dir to path to ensure utils imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import security, versioning, kaggle_helper, ai_summarizer

def set_bg_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Initialize Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'llm_config' not in st.session_state:
    st.session_state.llm_config = {
        'provider': 'OpenAI / Standard URL',
        'base_url': '',
        'api_key': '',
        'model': 'gpt-3.5-turbo'
    }
if 'kaggle_config' not in st.session_state:
    st.session_state.kaggle_config = {
        'username': '',
        'key': ''
    }

st.set_page_config(page_title="Data Security Analysis", layout="wide", page_icon="DataSecurity.png")
try:
    set_bg_image("Background.png")
except Exception as e:
    st.warning(f"Could not load background image: {e}")
st.logo("DataSecurity.png")

st.title("Data Security Analysis Platform")
st.markdown("Securely analyze, version-control, and export your spreadsheet data.")

# --- UI Tabs ---
tab_ingest, tab_workspace, tab_history, tab_security, tab_settings, tab_manual = st.tabs([
    "📥 Data Ingestion", 
    "📊 Data Workspace", 
    "🕰️ Version History", 
    "🛡️ Security & Export", 
    "⚙️ Settings",
    "📖 User Manual"
])

# --- Settings Tab ---
with tab_settings:
    st.header("API Configurations")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 AI Summarizer (LLM)")
        provider = st.selectbox("Provider", ["OpenAI / Standard URL", "Ollama (Local)"], 
                                index=["OpenAI / Standard URL", "Ollama (Local)"].index(st.session_state.llm_config['provider']))
        
        base_url = st.text_input("Base URL", value=st.session_state.llm_config['base_url'], help="e.g., https://api.openai.com/v1 or http://localhost:11434")
        
        api_key = ""
        if provider == "OpenAI / Standard URL":
            api_key = st.text_input("API Key", type="password", value=st.session_state.llm_config['api_key'])
            
        model = st.text_input("Model Name", value=st.session_state.llm_config['model'], help="e.g., gpt-4o, llama3")
        
        if st.button("Save LLM Settings"):
            st.session_state.llm_config.update({
                'provider': provider,
                'base_url': base_url,
                'api_key': api_key,
                'model': model
            })
            st.success("LLM settings saved!")

    with col2:
        st.subheader("📈 Kaggle Credentials")
        k_user = st.text_input("Kaggle Username", value=st.session_state.kaggle_config['username'])
        k_key = st.text_input("Kaggle API Key", type="password", value=st.session_state.kaggle_config['key'])
        
        if st.button("Save Kaggle Settings"):
            st.session_state.kaggle_config.update({
                'username': k_user,
                'key': k_key
            })
            kaggle_helper.authenticate_kaggle(k_user, k_key)
            st.success("Kaggle settings saved!")

# --- Data Ingestion Tab ---
with tab_ingest:
    st.header("Import Data")
    
    col_up, col_kag = st.columns(2)
    
    with col_up:
        st.subheader("Upload Local File")
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if st.button("Load Uploaded File"):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    st.session_state.current_df = df
                    st.session_state.history = versioning.init_version_control(df)
                    st.success("File loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
                    
    with col_kag:
        st.subheader("Fetch from Kaggle")
        if not st.session_state.kaggle_config['username'] or not st.session_state.kaggle_config['key']:
            st.warning("Please configure Kaggle credentials in the Settings tab first.")
        else:
            search_query = st.text_input("Search Kaggle Datasets")
            if st.button("Search"):
                with st.spinner("Searching..."):
                    results = kaggle_helper.search_datasets(search_query)
                    if not results.empty:
                        st.dataframe(results)
                        st.session_state.kaggle_search_results = results
                    else:
                        st.info("No datasets found or error occurred.")
            
            if 'kaggle_search_results' in st.session_state and not st.session_state.kaggle_search_results.empty:
                dataset_ref = st.selectbox("Select dataset to download", st.session_state.kaggle_search_results['ref'])
                if st.button("Download & Load"):
                    with st.spinner("Downloading..."):
                        df = kaggle_helper.download_dataset(dataset_ref)
                        if df is not None:
                            st.session_state.current_df = df
                            st.session_state.history = versioning.init_version_control(df)
                            st.success("Dataset loaded successfully!")
                        else:
                            st.error("Failed to load a CSV from the dataset.")

# --- Data Workspace Tab ---
with tab_workspace:
    st.header("Interactive Workspace")
    if st.session_state.current_df is not None:
        st.markdown("Edit the data below. Changes are tracked automatically when you click outside the cell.")
        
        edited_df = st.data_editor(
            st.session_state.current_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="data_editor"
        )
        
        # Check if the dataframe has changed
        if not edited_df.equals(st.session_state.current_df):
            if st.button("Commit Changes"):
                with st.spinner("Generating AI Summary..."):
                    diff = versioning.get_diff(st.session_state.current_df, edited_df)
                    
                    # Generate AI Summary
                    summary = "Manual edit (AI summary unavailable)."
                    if st.session_state.llm_config['model']:
                        llm_sum = ai_summarizer.generate_summary(
                            diff_info=diff,
                            provider=st.session_state.llm_config['provider'],
                            model_name=st.session_state.llm_config['model'],
                            api_key=st.session_state.llm_config['api_key'],
                            base_url=st.session_state.llm_config['base_url']
                        )
                        if "Error" not in llm_sum:
                            summary = llm_sum
                        else:
                            st.warning(llm_sum)
                    
                    st.session_state.history = versioning.commit_changes(
                        st.session_state.history, 
                        edited_df, 
                        description=summary
                    )
                    st.session_state.current_df = edited_df
                    st.success("Changes committed to version history!")
                    st.rerun()
    else:
        st.info("Please ingest data first.")

# --- Version History Tab ---
with tab_history:
    st.header("Version History & AI Summaries")
    if st.session_state.history:
        for commit in reversed(st.session_state.history):
            with st.expander(f"Version {commit['version']} - {commit['timestamp']}"):
                st.write(f"**Summary:** {commit['description']}")
                if commit['diff_summary']:
                    st.json(commit['diff_summary'])
                
                if st.button(f"Revert to Version {commit['version']}", key=f"revert_{commit['version']}"):
                    st.session_state.current_df = commit['dataframe'].copy()
                    st.success(f"Reverted to version {commit['version']}. Please go to the Workspace tab.")
    else:
        st.info("No history available.")

# --- Security & Export Tab ---
with tab_security:
    st.header("Security Center & Export")
    if st.session_state.current_df is not None:
        
        st.subheader("1. Column Tokenization (Masking/Hashing)")
        cols_to_tokenize = st.multiselect("Select columns to tokenize", st.session_state.current_df.columns)
        tok_method = st.radio("Tokenization Method", ["hash", "mask"])
        
        if st.button("Apply Tokenization"):
            df_tok = st.session_state.current_df.copy()
            for col in cols_to_tokenize:
                df_tok = security.tokenize_column(df_tok, col, tok_method)
            st.session_state.current_df = df_tok
            st.session_state.history = versioning.commit_changes(
                st.session_state.history, 
                df_tok, 
                description=f"Applied {tok_method} tokenization to columns: {', '.join(cols_to_tokenize)}"
            )
            st.success("Tokenization applied successfully!")
        
        st.divider()
        
        st.subheader("2. Secure Export (AES Encryption)")
        st.markdown("Download your current dataset fully encrypted. Save the provided key to decrypt it later.")
        
        if 'encryption_key' not in st.session_state:
            st.session_state.encryption_key = security.generate_key()
            
        st.code(st.session_state.encryption_key.decode('utf-8'), language="text")
        st.warning("⚠️ Save this key securely. You will need it to decrypt the file.")
        
        encrypted_bytes = security.encrypt_dataframe(st.session_state.current_df, st.session_state.encryption_key)
        
        st.download_button(
            label="Download Encrypted Dataset",
            data=encrypted_bytes,
            file_name="dataset_encrypted.bin",
            mime="application/octet-stream"
        )
        
        st.divider()
        st.subheader("Standard Export")
        
        csv = st.session_state.current_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Tokenized/Raw Dataset (CSV)",
            data=csv,
            file_name="dataset_export.csv",
            mime="text/csv"
        )
        
    else:
        st.info("Please ingest data first.")

# --- User Manual Tab ---
with tab_manual:
    st.header("📖 Comprehensive User Manual")
    st.markdown("""
    Welcome to the **Data Security Analysis Platform**! This built-in manual will guide you through all the features available to help you securely analyze and manage your spreadsheets.

    ### 1. Initial Setup & Configuration
    Before importing any data, head over to the **⚙️ Settings** tab to configure your external services.
    - **AI Summarizer (LLM)**: We use AI to automatically summarize what changed between edits in your spreadsheet. You can choose to use an external provider (like OpenAI, Groq, Abacus) by providing their Base URL, Model Name, and an API Key. Alternatively, choose **Ollama** if you are running a local, offline AI model for maximum privacy.
    - **Kaggle Configuration**: If you want to download datasets directly from Kaggle, you must provide your Kaggle Username and Kaggle API Key here.

    ### 2. Ingesting Data
    Go to the **📥 Data Ingestion** tab. You have two options:
    - **Local File Upload**: Drag and drop a standard `.csv` or `.xlsx` (Excel) file. The app will immediately load it into memory.
    - **Kaggle Search**: Type a keyword (e.g., "housing prices" or "titanic") and click Search. You will see a list of relevant datasets. Select one from the dropdown and click **Download & Load**. The app will automatically fetch it and load the primary CSV file.

    ### 3. Editing Data & Tracking Changes
    Once data is ingested, go to the **📊 Data Workspace** tab.
    - **Interactive Spreadsheet**: You will see your data presented in an interactive grid. You can double-click any cell to edit it. You can also add or delete rows.
    - **Committing Changes**: After making edits, click outside the cell. The app will detect the change and prompt you with a **Commit Changes** button. When clicked, the app saves this as a new "Version" and uses your configured LLM to generate a plain-text summary of what you just did (e.g., "You modified 3 cells in the Salary column").

    ### 4. Viewing History & Reverting
    Go to the **🕰️ Version History** tab to see your edits.
    - You will see a timeline of all your commits.
    - Expanding a commit shows the exact timestamp, the AI-generated description of the changes, and the raw technical difference (rows added/removed).
    - If you made a mistake, simply click **Revert to Version X** to instantly travel back in time and restore that exact spreadsheet state.

    ### 5. Securing & Exporting Data
    When you are done with your analysis, go to the **🛡️ Security & Export** tab.
    
    #### Tokenizing Columns
    If your dataset contains sensitive PII (Personally Identifiable Information) like Names, Emails, or Social Security Numbers, you can "Tokenize" them before exporting.
    - Select the sensitive columns from the dropdown.
    - Choose **Hash** (one-way cryptographic scramble) or **Mask** (replaces with generic identifiers like `TOKEN_123`).
    - Click **Apply Tokenization**. This change is also tracked in your Version History!

    #### Encrypting for Export
    If you need to securely store or share the entire dataset, use the **Secure Export** feature.
    - The app will generate a unique AES-256 encryption key. 
    - **⚠️ IMPORTANT**: Copy and securely save this key. It is mathematically impossible to decrypt the file without it.
    - Click **Download Encrypted Dataset**. You will receive a `.bin` file.
    
    #### Standard Export
    If you have tokenized your sensitive columns and just want a normal CSV file, use the **Download Tokenized/Raw Dataset** button at the bottom.

    ### Privacy Guarantee
    This application runs entirely on your local machine. Your data is kept in your browser's memory and is **never** saved to a local disk unless you explicitly download it. The only time data leaves your machine is if you configure an external LLM provider to summarize your changes.
    """)
