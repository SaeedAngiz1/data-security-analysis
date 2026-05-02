import requests
import json
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage

def generate_summary(diff_info: dict, provider: str, model_name: str, api_key: str = "", base_url: str = "") -> str:
    """
    Generates a natural language summary of the dataset changes using an LLM.
    """
    system_prompt = "You are a data version control assistant. Describe the changes made to the dataset based on the provided diff information in 1-2 concise sentences."
    user_prompt = f"Here is the diff information: {json.dumps(diff_info, indent=2)}\n\nWhat changed?"

    try:
        if provider.lower() == "openai / standard url":
            # Can be OpenAI, or any OpenAI-compatible API (like Abacus, Groq, etc.)
            if not base_url:
                base_url = "https://api.openai.com/v1" # Default
            
            chat = ChatOpenAI(
                model=model_name, 
                api_key=api_key, 
                base_url=base_url,
                max_tokens=150
            )
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = chat.invoke(messages)
            return response.content
            
        elif provider.lower() == "ollama (local)":
            if not base_url:
                base_url = "http://localhost:11434"
            
            llm = Ollama(model=model_name, base_url=base_url)
            prompt = f"{system_prompt}\n\n{user_prompt}"
            response = llm.invoke(prompt)
            return response
            
        else:
            return "Unsupported provider selected."

    except Exception as e:
        return f"Error generating summary: {str(e)}"
