#!/usr/bin/env python3
"""
Script para agregar documentos de muestra a la base de datos
"""

import asyncio
import httpx
import json

async def add_sample_documents():
    """Agregar documentos de muestra para probar el RAG"""
    
    base_url = "http://localhost:8000"
    
    sample_documents = [
        {
            "content": "Netra es una empresa de tecnología especializada en inteligencia artificial y machine learning. Desarrollamos soluciones innovadoras para automatización de procesos empresariales.",
            "metadata": {"category": "empresa", "topic": "netra"}
        },
        {
            "content": "La inteligencia artificial (IA) es una rama de las ciencias de la computación que se ocupa de la creación de sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
            "metadata": {"category": "tecnologia", "topic": "inteligencia_artificial"}
        },
        {
            "content": "Machine Learning es un subcampo de la inteligencia artificial que permite a las máquinas aprender y mejorar automáticamente a partir de la experiencia sin ser programadas explícitamente.",
            "metadata": {"category": "tecnologia", "topic": "machine_learning"}
        },
        {
            "content": "Deep Learning es una técnica de machine learning que utiliza redes neuronales artificiales con múltiples capas para modelar y entender datos complejos.",
            "metadata": {"category": "tecnologia", "topic": "deep_learning"}
        },
        {
            "content": "Los algoritmos de procesamiento de lenguaje natural (NLP) permiten a las máquinas entender, interpretar y generar lenguaje humano de manera natural.",
            "metadata": {"category": "tecnologia", "topic": "nlp"}
        }
    ]
    
    async with httpx.AsyncClient() as client:
        print("📚 Agregando documentos de muestra...")
        print("=" * 50)
        
        for i, doc in enumerate(sample_documents, 1):
            print(f"\n📄 Documento {i}: {doc['content'][:50]}...")
            
            try:
                response = await client.post(
                    f"{base_url}/documents",
                    json=doc,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Documento agregado exitosamente")
                    print(f"   ID: {result.get('document', {}).get('id', 'N/A')}")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error agregando documento: {e}")
        
        print(f"\n🔍 Verificando documentos en la base de datos...")
        try:
            response = await client.get(f"{base_url}/documents?limit=10")
            if response.status_code == 200:
                data = response.json()
                docs = data.get('documents', [])
                print(f"✅ Base de datos contiene {len(docs)} documentos")
                for i, doc in enumerate(docs[:3]):
                    content = doc.get("content", "")
                    print(f"   📄 Doc {i+1}: {content[:50]}...")
            else:
                print(f"❌ Error verificando documentos: {response.text}")
        except Exception as e:
            print(f"❌ Error verificando: {e}")

if __name__ == "__main__":
    print("📚 Agregando documentos de muestra para probar RAG")
    print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print()
    
    asyncio.run(add_sample_documents())
    
    print("\n✅ Proceso completado")
    print("Ahora puedes probar el endpoint /chat con consultas como:")
    print("- '¿Qué es Netra?'")
    print("- 'Háblame sobre inteligencia artificial'")
    print("- '¿Qué es machine learning?'")
