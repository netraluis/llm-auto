# 🛠️ Tools Directory

Esta carpeta contiene todas las herramientas/funciones disponibles para el LLM.

## 📁 Estructura

```
tools/
├── __init__.py              # Registro de todas las tools
├── weather_tool.py          # Tool del clima
├── vector_store_tool.py     # Tool de búsqueda en vector store
└── README.md               # Esta guía
```

## ✨ Cómo agregar una nueva tool

### 1. Crea un archivo nuevo

```python
# tools/mi_nueva_tool.py
import json
from typing import Dict, Any

async def mi_nueva_funcion(arguments: Dict[str, Any]) -> str:
    """
    Descripción de lo que hace tu tool
    
    Args:
        arguments: Dict con los parámetros necesarios
        
    Returns:
        JSON string con el resultado
    """
    param1 = arguments.get("param1", "")
    param2 = arguments.get("param2", 0)
    
    # Tu lógica aquí
    resultado = f"Procesado: {param1} con valor {param2}"
    
    return json.dumps({
        "resultado": resultado,
        "status": "success"
    })
```

### 2. Registra la tool en `__init__.py`

```python
from .weather_tool import get_current_weather
from .vector_store_tool import search_vector_store
from .mi_nueva_tool import mi_nueva_funcion  # ← Agregar import

TOOL_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    "search_vector_store": search_vector_store,
    "mi_nueva_funcion": mi_nueva_funcion,  # ← Agregar al mapeo
}
```

### 3. Úsala en el frontend

```typescript
const tools = [
  {
    type: "function",
    function: {
      name: "mi_nueva_funcion",
      description: "Descripción de lo que hace",
      parameters: {
        type: "object",
        properties: {
          param1: {
            type: "string",
            description: "Descripción del parámetro"
          },
          param2: {
            type: "number",
            description: "Descripción del parámetro numérico"
          }
        },
        required: ["param1"]
      }
    }
  }
];
```

## 📝 Tools disponibles

### `get_current_weather`
Obtiene el clima actual de una ubicación.

**Parámetros:**
- `location` (string): Ciudad o ubicación

**Respuesta:**
```json
{
  "location": "Madrid, Spain",
  "temperature": "22°C",
  "condition": "Sunny",
  "humidity": "65%",
  "wind_kph": 15,
  "feels_like": "20°C"
}
```

### `search_vector_store`
Busca documentos similares en el vector store.

**Parámetros:**
- `query` (string): Consulta de búsqueda
- `limit` (number, opcional): Cantidad de resultados (default: 5)

**Respuesta:**
```json
[
  {
    "content": "Contenido del documento...",
    "metadata": { ... },
    "similarity": 0.85
  }
]
```

## 🔒 Buenas prácticas

1. ✅ **Siempre retorna JSON** usando `json.dumps()`
2. ✅ **Maneja errores** con try/catch y retorna error en JSON
3. ✅ **Documenta bien** la función con docstring
4. ✅ **Valida parámetros** antes de usarlos
5. ✅ **Usa async/await** para operaciones I/O
6. ✅ **Tipado claro** con Type hints de Python

## 🚀 Ejemplo completo

```python
# tools/traductor_tool.py
import json
from typing import Dict, Any
import httpx

async def traducir_texto(arguments: Dict[str, Any]) -> str:
    """
    Traduce texto usando una API externa
    
    Args:
        arguments: Dict con 'texto' y 'idioma_destino'
        
    Returns:
        JSON string con la traducción
    """
    texto = arguments.get("texto", "")
    idioma = arguments.get("idioma_destino", "en")
    
    if not texto:
        return json.dumps({"error": "Texto vacío"})
    
    try:
        # Aquí iría tu lógica de traducción
        traduccion = f"[{idioma.upper()}] {texto}"
        
        return json.dumps({
            "texto_original": texto,
            "idioma_destino": idioma,
            "traduccion": traduccion
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error al traducir: {str(e)}"
        })
```

## 📚 Recursos

- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)
- [FastAPI Tools/Functions](https://fastapi.tiangolo.com/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

