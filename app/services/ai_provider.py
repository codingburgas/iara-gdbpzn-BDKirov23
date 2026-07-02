import requests
import json
import os
import re
from config import Config


class AIProvider:
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    @staticmethod
    def ask_huggingface(prompt, model="microsoft/DialoGPT-medium"):
        try:
            response = requests.post(
                f"{AIProvider.HUGGINGFACE_API_URL}{model}",
                json={"inputs": prompt, "parameters": {"max_length": 256, "temperature": 0.7}},
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    generated = data[0].get("generated_text", "")
                    reply = generated.replace(prompt, "").strip()
                    return reply if reply else None
            elif response.status_code == 503:
                pass
        except Exception:
            pass
        return None

    @staticmethod
    def ask_gemini(prompt, api_key=None):
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or Config.GEMINI_API_KEY
        if not api_key:
            return None

        system_prompt = (
            "Ти си AI асистент на ГДПБЗН (Главна дирекция пожарна безопасност и защита на населението). "
            "Отговаряй полезно и професионално на български език. "
            "Бъди кратък и практичен — потребителите са пожарникари и спасители в реална работна среда."
        )

        try:
            response = requests.post(
                f"{AIProvider.GEMINI_API_URL}?key={api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"}],
                        "role": "user"
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 512,
                    }
                },
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return text.strip() if text else None
        except Exception:
            pass
        return None

    @staticmethod
    def ask_togetherai(prompt, api_key=None):
        api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            return None

        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistralai/Mistral-7B-Instruct-v0.2",
                    "messages": [
                        {"role": "system", "content": "You are an AI assistant for ГДПБЗН (Bulgarian Fire Safety). Answer in Bulgarian. Be concise and helpful for emergency responders."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 512,
                },
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

    @staticmethod
    def ask_ai(prompt, user_id=None):
        try:
            result = AIProvider.ask_gemini(prompt)
            if result:
                result = re.sub(r'[^\w\s\.,!?\-:;()\n]', '', result)
                return result
        except Exception:
            pass

        if os.environ.get("TOGETHER_API_KEY"):
            try:
                result = AIProvider.ask_togetherai(prompt)
                if result:
                    result = re.sub(r'[^\w\s\.,!?\-:;()\n]', '', result)
                    return result
            except Exception:
                pass

        return None
