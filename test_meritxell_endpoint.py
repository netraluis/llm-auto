"""
Test del endpoint de Meritxell
"""
import asyncio
import httpx

async def test_meritxell_endpoint():
    """Test básico del endpoint de Meritxell"""
    
    async with httpx.AsyncClient() as client:
        # Test 1: Pregunta en catalán
        print("🧪 Test 1: Pregunta en catalán")
        response = await client.post(
            "http://localhost:8000/meritxell/chat",
            json={
                "input_text": "Què és l'Acord d'Associació?"
            },
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {data.get('output_text')[:200]}...\n")
        
        # Test 2: Pregunta en español
        print("🧪 Test 2: Pregunta en español")
        response = await client.post(
            "http://localhost:8000/meritxell/chat",
            json={
                "input_text": "¿Qué ventajas tiene el acuerdo?"
            },
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {data.get('output_text')[:200]}...\n")
        
        # Test 3: Pregunta fuera de scope (debe redirigir)
        print("🧪 Test 3: Pregunta fuera de scope")
        response = await client.post(
            "http://localhost:8000/meritxell/chat",
            json={
                "input_text": "¿Cuál es la capital de Francia?"
            },
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {data.get('output_text')[:200]}...\n")

if __name__ == "__main__":
    print("🚀 Iniciando tests del endpoint de Meritxell\n")
    print("⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:8000\n")
    asyncio.run(test_meritxell_endpoint())
    print("✅ Tests completados")

