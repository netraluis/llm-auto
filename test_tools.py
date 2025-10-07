"""
Script de prueba para demostrar el uso de tools/function calling
"""
import httpx
import json
import asyncio

async def test_weather_tool():
    """Test de la tool de clima"""
    print("\n🧪 Test 1: Weather Tool")
    print("=" * 50)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Qué tiempo hace en Barcelona?"
            }
        ],
        "assistant_id": "asst_test_123",
        "use_vector_context": False,  # No usar vector store para este test
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
            }
        ],
        "tool_choice": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=30.0
        )
        
        result = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(result, indent=2))
        
        if result.get("tool_calls"):
            print(f"\n🔧 Tool calls detected: {len(result['tool_calls'])}")
            for tc in result["tool_calls"]:
                print(f"   - {tc['function']['name']}: {tc['function']['arguments']}")

async def test_vector_store_tool():
    """Test de la tool de búsqueda en vector store"""
    print("\n🧪 Test 2: Vector Store Search Tool")
    print("=" * 50)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Busca información sobre Python en la base de datos"
            }
        ],
        "assistant_id": "asst_test_123",
        "use_vector_context": False,  # Usaremos la tool en lugar del contexto automático
        "tools": [
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
                                "description": "El texto de búsqueda para encontrar documentos similares"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Número máximo de documentos a retornar",
                                "default": 5
                            },
                            "assistant_id": {
                                "type": "string",
                                "description": "ID del asistente para filtrar documentos"
                            }
                        },
                        "required": ["query", "assistant_id"]
                    }
                }
            }
        ],
        "tool_choice": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=30.0
        )
        
        result = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(result, indent=2))

async def test_multiple_tools():
    """Test con múltiples tools disponibles"""
    print("\n🧪 Test 3: Multiple Tools")
    print("=" * 50)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Busca documentos sobre IA y dime el clima en Madrid"
            }
        ],
        "assistant_id": "asst_test_123",
        "use_vector_context": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "search_vector_store",
                    "description": "Busca documentos en el vector store",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Búsqueda"},
                            "assistant_id": {"type": "string", "description": "ID del asistente"}
                        },
                        "required": ["query", "assistant_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Obtiene el clima actual de una ubicación",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "Ciudad y país"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "tool_choice": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=30.0
        )
        
        result = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(result, indent=2))

async def test_forced_tool():
    """Test forzando el uso de una tool específica"""
    print("\n🧪 Test 4: Forced Tool Usage")
    print("=" * 50)
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Dame información"
            }
        ],
        "assistant_id": "asst_test_123",
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
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": "get_current_weather"}
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=30.0
        )
        
        result = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(result, indent=2))

async def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🚀 TESTING TOOLS/FUNCTION CALLING")
    print("=" * 50)
    
    try:
        await test_weather_tool()
        await asyncio.sleep(1)
        
        await test_vector_store_tool()
        await asyncio.sleep(1)
        
        await test_multiple_tools()
        await asyncio.sleep(1)
        
        await test_forced_tool()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

