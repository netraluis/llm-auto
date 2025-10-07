import json
from typing import Dict, Any
from supabase_client import vector_store


async def search_vector_store(arguments: Dict[str, Any], assistant_id: str = None) -> str:
    """
    Busca en el vector store documentos similares a una consulta
    
    Args:
        arguments: Dict con 'query' (str) y 'limit' (int) opcional
        assistant_id: ID del asistente para filtrar resultados
        
    Returns:
        JSON string con los documentos encontrados
    """
    query = arguments.get("query", "")
    limit = arguments.get("limit", 5)
    # Usar el assistant_id del request, no del LLM
    search_assistant_id = assistant_id or arguments.get("assistant_id", "")
    
    results = await vector_store.search_similar(
        query=query,
        limit=limit,
        assistant_id=search_assistant_id
    )
    return json.dumps(results)

