<p align="center">
  <img src="DataSecurity.png" width="200" alt="Data Security Icon">
</p>

<h1 align="center">🔐 Data Security & Version Control Platform</h1>

<p align="center">
  <strong>A premium, robust analysis environment designed for secure data ingestion, interactive editing, and AI-powered versioning.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Security-AES--256-green?style=for-the-badge&logo=google-cloud&logoColor=white" alt="Security">
  <img src="https://img.shields.io/badge/AI-Ollama%20%2F%20OpenAI-blueviolet?style=for-the-badge" alt="AI">
</p>

---

## 📸 Overview

![Hero Image](DataSecurity.png)

> [!IMPORTANT]
> This platform ensures your sensitive spreadsheet data remains protected with advanced tokenization and encryption, while giving you powerful analytical and version control capabilities.

---

## 🌟 Visual Feature Matrix

| Feature | Description | Icon |
| :--- | :--- | :---: |
| **Seamless Ingestion** | Upload CSV/Excel or fetch directly from **Kaggle**. | 📥 |
| **Live Workspace** | Edit data natively in a high-performance grid. | 📊 |
| **AI Versioning** | LLM-generated summaries for every data commit. | 🧠 |
| **Tokenization** | SHA-256 hashing and masking for PII protection. | 🛡️ |
| **Full Encryption** | Industry-standard AES-256 file-level protection. | 🔒 |
| **Time Travel** | Revert workspace to any previous commit instantly. | ⏳ |

---

## 🔄 Data Lifecycle Architecture

```mermaid
graph TD
    A[📥 Ingestion] -->|Local / Kaggle| B{📊 Data Workspace}
    B -->|Interactive Editing| C[🧠 AI Summarizer]
    C -->|Commit / Diff| D[📂 Version Control]
    D -->|Time Travel| B
    B -->|PII Detection| E[🛡️ Tokenization]
    E -->|AES-256| F[🔒 Encrypted Export]
    F -->|Secure .bin| G[🏁 Download]
    style A fill:#1a1a1a,stroke:#3776AB,stroke-width:2px,color:#fff
    style B fill:#1a1a1a,stroke:#FF4B4B,stroke-width:2px,color:#fff
    style C fill:#1a1a1a,stroke:#blueviolet,stroke-width:2px,color:#fff
    style F fill:#1a1a1a,stroke:#green,stroke-width:2px,color:#fff
```

---

## 🚀 Getting Started

### 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/saeedangiz1/data-security-analysis.git
cd "data security, version controll"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the platform
streamlit run app.py
```

---

## ⚙️ Configuration

### 🔗 Kaggle Integration
1. Obtain `kaggle.json` from your [Kaggle Account](https://www.kaggle.com/settings).
2. Paste credentials in the **Settings** tab.

### 🤖 AI Engine
- **Cloud**: OpenAI, Abacus.ai, or Groq (OpenAI-compatible).
- **Local**: [Ollama](https://ollama.com/) (Default: `llama3` on `localhost:11434`).

---

## 🔒 Security Protocol
This application handles encryption keys in **memory only**. 

> [!WARNING]
> Decryption keys are NOT stored persistently. If you lose your key for an encrypted `.bin` file, the data is **permanently unrecoverable**.

---

<p align="center">
  <img src="Background.png" alt="Footer Background" style="border-radius: 15px; opacity: 0.8;">
</p>

<p align="center">
  Built with ❤️ for Data Security Professionals
</p>

