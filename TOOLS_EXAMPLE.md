# Tools / Function Calling - Guía de Uso

## Resumen
Ahora puedes usar **function calling** (tools) en tus requests al endpoint `/chat`. El LLM puede decidir cuándo llamar funciones específicas para obtener información o realizar acciones.

## Estructura de una Tool

```json
{
  "type": "function",
  "function": {
    "name": "nombre_de_la_funcion",
    "description": "Descripción clara de qué hace la función",
    "parameters": {
      "type": "object",
      "properties": {
        "parametro1": {
          "type": "string",
          "description": "Descripción del parámetro"
        }
      },
      "required": ["parametro1"]
    }
  }
}
```

## Ejemplo 1: Búsqueda en Vector Store

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Busca información sobre Python en la base de datos"
      }
    ],
    "assistant_id": "asst_123",
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
                "description": "El texto de búsqueda"
              },
              "limit": {
                "type": "integer",
                "description": "Número máximo de resultados"
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
  }'
```

## Ejemplo 2: Función del Clima (Demo)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué tiempo hace en Madrid?"
      }
    ],
    "assistant_id": "asst_123",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima actual de una ubicación",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "La ciudad y país, ej: Madrid, España"
              }
            },
            "required": ["location"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'
```

## Ejemplo 3: Múltiples Tools

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Busca documentos sobre IA y dime el clima en Barcelona"
      }
    ],
    "assistant_id": "asst_123",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_vector_store",
          "description": "Busca documentos en el vector store",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {"type": "string"},
              "assistant_id": {"type": "string"}
            },
            "required": ["query", "assistant_id"]
          }
        }
      },
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima actual",
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
  }'
```

## Flujo Completo con Tool Calls

### 1. Primera Request (Usuario pregunta)
```json
{
  "messages": [
    {"role": "user", "content": "¿Qué tiempo hace en Madrid?"}
  ],
  "tools": [...],
  "assistant_id": "asst_123"
}
```

### 2. Response del LLM (Quiere usar una tool)
```json
{
  "response": "",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "arguments": "{\"location\": \"Madrid, España\"}"
      }
    }
  ],
  "finish_reason": "tool_calls"
}
```

### 3. Segunda Request (Con resultado de la tool)
```json
{
  "messages": [
    {"role": "user", "content": "¿Qué tiempo hace en Madrid?"},
    {
      "role": "assistant",
      "content": "",
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "get_current_weather",
            "arguments": "{\"location\": \"Madrid, España\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": "{\"location\": \"Madrid, España\", \"temperature\": \"22°C\", \"condition\": \"Sunny\"}",
      "tool_call_id": "call_abc123"
    }
  ],
  "tools": [...],
  "assistant_id": "asst_123"
}
```

### 4. Response Final del LLM
```json
{
  "response": "En Madrid hace 22°C y está soleado.",
  "finish_reason": "stop"
}
```

## Tool Choice Options

- `"auto"` (default): El LLM decide si usar tools o no
- `"none"`: No usar tools, solo respuesta de texto
- `{"type": "function", "function": {"name": "search_vector_store"}}`: Forzar uso de una tool específica

## Añadir Nuevas Tools

En `main.py`, modifica la función `execute_tool`:

```python
async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "mi_nueva_tool":
        # Tu lógica aquí
        resultado = await mi_funcion(arguments)
        return json.dumps(resultado)
    # ... otras tools
```

## Response Fields

- `response`: Texto de respuesta del LLM
- `context_used`: Contexto del vector store (si se usó)
- `tool_calls`: Array de tool calls si el LLM quiere usar tools
- `finish_reason`: 
  - `"stop"`: Respuesta completa
  - `"tool_calls"`: LLM quiere usar tools
  - `"length"`: Se alcanzó el límite de tokens
  - `"error"`: Hubo un error

## Endpoint `/chat/auto-tools` - Ejecución Automática

Este endpoint ejecuta automáticamente los tool calls en un loop hasta obtener la respuesta final:

```bash
curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Busca información sobre Python y dime el clima en Madrid"
      }
    ],
    "assistant_id": "asst_123",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_vector_store",
          "description": "Busca documentos en el vector store",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {"type": "string"},
              "assistant_id": {"type": "string"}
            },
            "required": ["query", "assistant_id"]
          }
        }
      },
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima actual",
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
  }'
```

**Ventajas del endpoint auto-tools:**
- ✅ Ejecuta tools automáticamente
- ✅ Loop hasta obtener respuesta final
- ✅ No necesitas manejar el flujo manualmente
- ✅ Respuesta final lista para mostrar al usuario

**Diferencias entre `/chat` y `/chat/auto-tools`:**

| Característica | `/chat` | `/chat/auto-tools` |
|----------------|---------|-------------------|
| Tool execution | Manual (retorna tool_calls) | Automática |
| Iteraciones | 1 request = 1 response | Loop hasta respuesta final |
| Control | Total (cliente maneja loop) | Automático (servidor maneja loop) |
| Uso ideal | Apps con control fino | Apps que quieren respuesta directa |

## Tips

1. **Descripciones claras**: Las descripciones de tools y parámetros deben ser muy claras para que el LLM sepa cuándo usarlas
2. **Validación**: Los parámetros `required` aseguran que el LLM incluya la info necesaria
3. **Loop de tools**: 
   - Usa `/chat/auto-tools` para ejecución automática
   - Usa `/chat` para control manual del loop
4. **Combinación con context**: Puedes usar tools Y context del vector store simultáneamente
5. **Max iterations**: El auto-loop tiene un límite de 5 iteraciones para prevenir loops infinitos

