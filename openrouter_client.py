import httpx
from typing import List, Dict, Any
from config import Config

class OpenRouterClient:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def chat_completion(self, messages: List[Dict[str, str]], context: str = None) -> str:
        """
        Send a chat completion request to OpenRouter
        """
        try:
            # Add context if provided
            if context:
                system_message = {
                    "role": "system", 
                    "content": f"Context from vector store: {context}"
                }
                messages = [system_message] + messages
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",  # Optional: replace with your domain
                "X-Title": "LLM Auto Backend"  # Optional: replace with your app name
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            print(f"\n🌐 OpenRouter Request Details:")
            print(f"   📍 URL: {self.base_url}/chat/completions")
            print(f"   🤖 Model: {self.model}")
            print(f"   🔑 API Key: {self.api_key[:20]}..." if self.api_key else "   ❌ No API key")
            print(f"   📊 Messages: {len(messages)} messages")
            print(f"   🔧 Max tokens: {payload['max_tokens']}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                print(f"\n📡 OpenRouter Response:")
                print(f"   📊 Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Success!")
                else:
                    print(f"   ❌ Error response: {response.text[:200]}...")
                
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"   📝 Response length: {len(content)} characters")
                print(f"   💬 Response preview: {content[:100]}...")
                return content
                
        except httpx.HTTPStatusError as e:
            print(f"\n❌ HTTP Error calling OpenRouter:")
            print(f"   📊 Status: {e.response.status_code}")
            print(f"   📝 Error: {e.response.text}")
            return f"HTTP Error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            print(f"\n❌ General Error calling OpenRouter:")
            print(f"   🚨 Error: {e}")
            return f"Error: {str(e)}"

# Global instance
openrouter_client = OpenRouterClient()
