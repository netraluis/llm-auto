#!/usr/bin/env python3
"""
Script para probar el endpoint /chat con búsqueda vectorial
"""

import asyncio
import httpx
import json

async def test_chat_endpoint():
    """Probar el endpoint /chat con diferentes consultas"""
    
    base_url = "http://localhost:8000"
    
    # Casos de prueba
    test_cases = [
        {
            "name": "Consulta simple",
            "messages": [
                {"role": "user", "content": "¿Qué información tienes sobre inteligencia artificial?"}
            ],
            "use_vector_context": True,
            "vector_limit": 3
        },
        {
            "name": "Consulta específica",
            "messages": [
                {"role": "user", "content": "Háblame sobre machine learning y deep learning"}
            ],
            "use_vector_context": True,
            "vector_limit": 5
        },
        {
            "name": "Consulta sin contexto vectorial",
            "messages": [
                {"role": "user", "content": "¿Cómo estás?"}
            ],
            "use_vector_context": False,
            "vector_limit": 0
        }
    ]
    
    async with httpx.AsyncClient() as client:
        print("🚀 Iniciando pruebas del endpoint /chat")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Prueba {i}: {test_case['name']}")
            print("-" * 30)
            
            try:
                # Hacer la petición
                response = await client.post(
                    f"{base_url}/chat",
                    json=test_case,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Respuesta exitosa")
                    print(f"📝 Respuesta: {data['response'][:100]}...")
                    print(f"📄 Contexto usado: {len(data.get('context_used', ''))} caracteres")
                    if data.get('context_used'):
                        print(f"🔍 Contexto: {data['context_used'][:100]}...")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error en la petición: {e}")
            
            print()

async def test_debug_endpoints():
    """Probar endpoints de debug"""
    
    base_url = "http://localhost:8000"
    
    debug_endpoints = [
        "/debug/supabase-status",
        "/debug/tables", 
        "/documents"
    ]
    
    async with httpx.AsyncClient() as client:
        print("\n🔧 Probando endpoints de debug")
        print("=" * 50)
        
        for endpoint in debug_endpoints:
            print(f"\n📋 Probando: {endpoint}")
            try:
                response = await client.get(f"{base_url}{endpoint}", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Respuesta: {json.dumps(data, indent=2)[:200]}...")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas del sistema RAG")
    print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print()
    
    # Ejecutar pruebas
    asyncio.run(test_chat_endpoint())
    asyncio.run(test_debug_endpoints())
    
    print("\n✅ Pruebas completadas")
