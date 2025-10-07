"""
Test del endpoint /chat/auto-tools que ejecuta tools automáticamente
"""
import httpx
import json
import asyncio

async def test_auto_tools():
    """Test del endpoint con ejecución automática de tools"""
    print("\n🧪 Test: Auto-Tools Endpoint")
    print("=" * 60)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Qué tiempo hace en Barcelona? Y también busca información sobre Python"
            }
        ],
        "assistant_id": "asst_auto_123",
        "use_vector_context": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Obtiene el clima actual de una ubicación específica",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "La ciudad y país, por ejemplo: Barcelona, España"
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_vector_store",
                    "description": "Busca documentos similares en el vector store de Supabase",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "El texto de búsqueda"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Número máximo de resultados",
                                "default": 5
                            },
                            "assistant_id": {
                                "type": "string",
                                "description": "ID del asistente"
                            }
                        },
                        "required": ["query", "assistant_id"]
                    }
                }
            }
        ],
        "tool_choice": "auto"
    }
    
    print("\n📤 Enviando request a /chat/auto-tools...")
    print(f"📝 Pregunta: {payload['messages'][0]['content']}")
    print(f"🔧 Tools disponibles: {len(payload['tools'])}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat/auto-tools",
                json=payload,
                timeout=60.0  # Más tiempo para el loop
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Response exitoso:")
                print(f"   📊 Finish reason: {result.get('finish_reason')}")
                print(f"   📝 Response: {result.get('response')[:200]}...")
                print(f"\n📥 Full Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"📝 {response.text}")
                
        except httpx.TimeoutException:
            print("\n⏱️  Timeout - el loop puede estar tomando mucho tiempo")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

async def test_auto_tools_simple():
    """Test simple con una sola tool"""
    print("\n🧪 Test: Auto-Tools Simple (solo clima)")
    print("=" * 60)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Qué temperatura hace en Madrid?"
            }
        ],
        "assistant_id": "asst_simple_123",
        "use_vector_context": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Obtiene el clima actual",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Ciudad y país"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat/auto-tools",
                json=payload,
                timeout=60.0
            )
            
            result = response.json()
            print(f"\n✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

async def compare_endpoints():
    """Comparar /chat vs /chat/auto-tools"""
    print("\n🧪 Test: Comparación /chat vs /chat/auto-tools")
    print("=" * 60)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Qué tiempo hace en Sevilla?"
            }
        ],
        "assistant_id": "asst_compare_123",
        "use_vector_context": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Obtiene el clima",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        # Test /chat (manual)
        print("\n1️⃣  Testing /chat (manual tool execution):")
        response1 = await client.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=30.0
        )
        result1 = response1.json()
        print(f"   📝 tool_calls present: {result1.get('tool_calls') is not None}")
        print(f"   📝 finish_reason: {result1.get('finish_reason')}")
        
        # Test /chat/auto-tools
        print("\n2️⃣  Testing /chat/auto-tools (automatic):")
        response2 = await client.post(
            "http://localhost:8000/chat/auto-tools",
            json=payload,
            timeout=60.0
        )
        result2 = response2.json()
        print(f"   📝 tool_calls present: {result2.get('tool_calls') is not None}")
        print(f"   📝 finish_reason: {result2.get('finish_reason')}")
        print(f"   💬 response: {result2.get('response')[:150]}...")

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 TESTING AUTO-TOOLS ENDPOINT")
    print("=" * 60)
    
    try:
        await test_auto_tools_simple()
        await asyncio.sleep(1)
        
        await test_auto_tools()
        await asyncio.sleep(1)
        
        await compare_endpoints()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

