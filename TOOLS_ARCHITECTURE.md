# 🏗️ Arquitectura de Tools - Explicación Visual

## 📊 Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. FRONTEND/CLIENTE                                             │
│    (Aquí defines QUÉ tools están disponibles)                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ POST /chat/auto-tools
                           │ {
                           │   "messages": [...],
                           │   "tools": [              ← DEFINICIÓN
                           │     {
                           │       "type": "function",
                           │       "function": {
                           │         "name": "get_current_weather",
                           │         "description": "...",
                           │         "parameters": {...}
                           │       }
                           │     }
                           │   ]
                           │ }
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. BACKEND - main.py (chat_auto_tools_endpoint)                 │
│    Recibe las tools y las pasa a OpenRouter                     │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Pasa tools al LLM
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. LLM (via OpenRouter)                                          │
│    Lee las definiciones de tools y decide:                      │
│    "Necesito llamar get_current_weather con location=Madrid"    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Retorna tool_calls: [
                           │   {
                           │     "id": "call_123",
                           │     "function": {
                           │       "name": "get_current_weather",
                           │       "arguments": '{"location": "Madrid"}'
                           │     }
                           │   }
                           │ ]
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BACKEND - main.py (execute_tool)                             │
│    AQUÍ ejecutas la lógica de cada tool                         │
│                                                                  │
│    if tool_name == "get_current_weather":      ← EJECUCIÓN     │
│        location = arguments.get("location")                     │
│        # Llamar API real, DB, etc                               │
│        return json.dumps(resultado)                             │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Retorna resultado al LLM
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. LLM (via OpenRouter)                                          │
│    Lee el resultado y genera respuesta final:                   │
│    "En Madrid hace 22°C y está soleado"                         │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Response final
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. FRONTEND/CLIENTE                                             │
│    Recibe: "En Madrid hace 22°C y está soleado"                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Ubicación de las Tools

### ❌ Las tools NO están aquí:
- No hay un archivo `tools.py`
- No hay una configuración central
- No hay un registro de tools

### ✅ Las tools ESTÁN aquí:

#### 1. **DEFINICIÓN** → Request del cliente
```json
// En tu frontend, Postman, cURL, etc
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "nombre_tool",
        "description": "qué hace",
        "parameters": {...}
      }
    }
  ]
}
```

**📁 Ejemplos:** 
- `TOOLS_CURL_EXAMPLES.sh` - ejemplos cURL
- `frontend_integration_example.ts` - ejemplos TypeScript
- `test_tools.py` - ejemplos Python

#### 2. **EJECUCIÓN** → `main.py` función `execute_tool`
```python
# Líneas 54-88 en main.py

async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "search_vector_store":
        # ← Lógica de búsqueda
        results = await vector_store.search_similar(...)
        return json.dumps(results)
    
    elif tool_name == "get_current_weather":
        # ← Lógica del clima (simulada)
        return json.dumps({...})
    
    # AÑADE AQUÍ TUS NUEVAS TOOLS
    elif tool_name == "mi_nueva_tool":
        result = await mi_funcion(...)
        return json.dumps(result)
```

## 📝 Tools Actualmente Implementadas

| Tool Name | Ubicación Ejecución | Qué Hace |
|-----------|---------------------|----------|
| `search_vector_store` | `main.py:58-68` | Busca en Supabase vector store |
| `get_current_weather` | `main.py:70-78` | Simula respuesta de clima |

## ➕ Cómo Añadir una Nueva Tool

### Ejemplo: Tool para buscar usuarios

**Paso 1 - Define en el request:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "buscar_usuario",
        "description": "Busca un usuario por email",
        "parameters": {
          "type": "object",
          "properties": {
            "email": {
              "type": "string",
              "description": "Email del usuario"
            }
          },
          "required": ["email"]
        }
      }
    }
  ]
}
```

**Paso 2 - Implementa en main.py:**
```python
async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    # ... tools existentes ...
    
    elif tool_name == "buscar_usuario":
        email = arguments.get("email")
        
        # Tu lógica - por ejemplo, buscar en DB
        usuario = await db.get_user_by_email(email)
        
        if usuario:
            return json.dumps({
                "nombre": usuario.nombre,
                "email": usuario.email,
                "activo": usuario.activo
            })
        else:
            return json.dumps({"error": "Usuario no encontrado"})
```

## 🔑 Conceptos Clave

1. **Definición vs Ejecución:**
   - **Definición** = Metadatos (nombre, descripción, parámetros) → En REQUEST
   - **Ejecución** = Código que realmente hace el trabajo → En `execute_tool`

2. **El LLM NO ejecuta las tools:**
   - El LLM lee las definiciones y decide CUÁNDO llamarlas
   - Tu backend ejecuta el código real
   - El LLM lee el resultado y genera la respuesta final

3. **Flexible:**
   - Puedes enviar diferentes tools en cada request
   - No necesitas registrar tools previamente
   - El LLM decide dinámicamente cuáles usar

## 📚 Archivos de Referencia

| Archivo | Qué Contiene |
|---------|--------------|
| `main.py:54-88` | **Ejecución** de tools |
| `TOOLS_README.md` | Guía rápida |
| `TOOLS_EXAMPLE.md` | Ejemplos detallados |
| `TOOLS_CURL_EXAMPLES.sh` | Ejemplos cURL ejecutables |
| `frontend_integration_example.ts` | Ejemplos para frontend |
| `test_tools.py` | Tests Python |

## 🎓 En Resumen

```
TU REQUEST              →  Defines QUÉ tools existen
       ↓
LLM (OpenRouter)        →  Decide CUÁNDO llamarlas
       ↓
execute_tool (main.py)  →  Ejecuta la LÓGICA real
       ↓
LLM (OpenRouter)        →  Genera RESPUESTA final
       ↓
TU FRONTEND             →  Recibe respuesta
```

**Las tools NO están "pre-definidas" en ningún lado.** 
Tú las defines dinámicamente en cada request, y tu backend decide cómo ejecutarlas.

