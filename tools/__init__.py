"""
Tools module - Contiene todas las herramientas/funciones disponibles para el LLM

Para agregar una nueva tool:
1. Crea un archivo nuevo en esta carpeta (ej: mi_tool.py)
2. Implementa una función async que reciba arguments: Dict[str, Any]
3. Importa y agrega la función a TOOL_FUNCTIONS
4. Listo! La tool estará disponible automáticamente
"""

from .weather_tool import get_current_weather

# Mapeo de nombres de tools a funciones
TOOL_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    # search_vector_store se maneja aparte en main.py porque necesita assistant_id
}

__all__ = ["TOOL_FUNCTIONS", "get_current_weather"]

