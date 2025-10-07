# 🛠️ Tools / Function Calling - Quick Start

## ✅ ¿Qué se ha añadido?

Tu API ahora soporta **function calling** (tools) - el LLM puede llamar funciones específicas para obtener información o realizar acciones.

## 📍 Dos Endpoints Disponibles

### 1. `/chat` - Control Manual
- El LLM retorna `tool_calls` que debes ejecutar manualmente
- Tienes control total del flujo
- Ideal para apps que necesitan lógica custom entre tool calls

### 2. `/chat/auto-tools` - Ejecución Automática ⭐
- El servidor ejecuta automáticamente los tools en un loop
- Retorna la respuesta final directamente
- Ideal para la mayoría de casos de uso

## 🚀 Uso Rápido

```bash
curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Qué tiempo hace en Madrid?"}
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
                "description": "Ciudad y país, ej: Madrid, España"
              }
            },
            "required": ["location"]
          }
        }
      }
    ]
  }'
```

## 🔧 Tools Disponibles

### 1. `search_vector_store`
Busca documentos en Supabase vector store
```json
{
  "name": "search_vector_store",
  "parameters": {
    "query": "texto a buscar",
    "limit": 5,
    "assistant_id": "asst_123"
  }
}
```

### 2. `get_current_weather` (demo)
Obtiene clima simulado
```json
{
  "name": "get_current_weather",
  "parameters": {
    "location": "Madrid, España"
  }
}
```

## ➕ Añadir Tus Propias Tools

### Paso 1: Define la tool en tu request
```json
{
  "type": "function",
  "function": {
    "name": "mi_nueva_tool",
    "description": "Descripción clara de qué hace",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {"type": "string", "description": "..."}
      },
      "required": ["param1"]
    }
  }
}
```

### Paso 2: Implementa la ejecución en `main.py`

Edita la función `execute_tool`:

```python
async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "mi_nueva_tool":
        param1 = arguments.get("param1")
        # Tu lógica aquí
        resultado = await mi_funcion(param1)
        return json.dumps(resultado)
    
    # ... resto de tools
```

## 📝 Request Schema

```python
{
  "messages": [
    {
      "role": "user",
      "content": "texto del mensaje",
      "tool_calls": [...],      # opcional
      "tool_call_id": "..."     # opcional (para role="tool")
    }
  ],
  "assistant_id": "asst_123",
  "use_vector_context": true,   # default: true
  "vector_limit": 5,             # default: 5
  "tools": [...],                # opcional
  "tool_choice": "auto"          # "auto" | "none" | {type: "function", function: {name: "..."}}
}
```

## 📊 Response Schema

```python
{
  "response": "respuesta del LLM",
  "context_used": "contexto del vector store o null",
  "tool_calls": [...],           # null si finish_reason != "tool_calls"
  "finish_reason": "stop"        # "stop" | "tool_calls" | "length" | "error"
}
```

## 🧪 Testing

```bash
# Test básico
python test_tools.py

# Test auto-tools
python test_auto_tools.py
```

## 📚 Documentación Completa

- `TOOLS_EXAMPLE.md` - Ejemplos detallados y casos de uso
- `test_tools.py` - Tests del endpoint manual
- `test_auto_tools.py` - Tests del endpoint automático

## 💡 Tips

1. **Descripciones claras**: El LLM usa las descripciones para decidir cuándo usar cada tool
2. **Parameters required**: Asegura que el LLM incluya los parámetros necesarios
3. **Auto-tools recomendado**: Para la mayoría de casos, usa `/chat/auto-tools`
4. **Max iterations**: El auto-loop tiene límite de 5 iteraciones
5. **Combinar con context**: Tools y vector context funcionan juntos perfectamente

## 🎯 Casos de Uso

- ✅ Búsqueda en bases de datos
- ✅ APIs externas (clima, noticias, etc)
- ✅ Cálculos o procesamiento
- ✅ Acciones sobre sistemas externos
- ✅ Validaciones y verificaciones
- ✅ Múltiples fuentes de datos en una respuesta

## ⚠️ Notas Importantes

- El modelo debe soportar function calling (verifica en OpenRouter)
- Tools se ejecutan server-side por seguridad
- Valida siempre los parámetros antes de ejecutar
- Maneja errores en la ejecución de tools
- Considera timeouts para tools que llaman APIs externas

