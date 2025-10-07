# 📊 Tools Metadata - Información de Ejecución

## ✨ Nueva Funcionalidad

El endpoint `/chat/auto-tools` ahora retorna **metadata detallada** sobre la ejecución:
- ✅ Número de iteraciones realizadas
- ✅ Lista de tools ejecutadas con sus argumentos
- ✅ Preview de los resultados

## 📋 Response Schema

```typescript
{
  "response": string,           // Respuesta final del LLM
  "context_used": string | null, // Contexto del vector store
  "tool_calls": null,            // Siempre null en auto-tools
  "finish_reason": string,       // "stop" | "tool_calls" | "length" | "error"
  
  // 🆕 Nuevo metadata
  "iterations": number | null,   // Número de iteraciones realizadas
  "tools_executed": [            // Lista de tools ejecutadas
    {
      "tool_name": string,       // Nombre de la tool
      "arguments": object,       // Argumentos usados
      "result_preview": string   // Preview del resultado (max 200 chars)
    }
  ] | null
}
```

## 🎯 Ejemplo de Response

### Request
```bash
curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Busca información sobre Netra"}
    ],
    "assistant_id": "general",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_vector_store",
          "description": "Busca documentos",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {"type": "string"}
            },
            "required": ["query"]
          }
        }
      }
    ]
  }'
```

### Response (Antes - sin metadata)
```json
{
  "response": "Netra es un ingeniero mecánico formado en la UPC...",
  "context_used": null,
  "tool_calls": null,
  "finish_reason": "stop"
}
```

### Response (Ahora - con metadata) ✨
```json
{
  "response": "Netra es un ingeniero mecánico formado en la UPC que se encarga del desarrollo del chatbot y de la construcción de las interfaces técnicas necesarias para las soluciones de la empresa...",
  "context_used": null,
  "tool_calls": null,
  "finish_reason": "stop",
  
  "iterations": 2,
  "tools_executed": [
    {
      "tool_name": "search_vector_store",
      "arguments": {
        "query": "Netra",
        "limit": 5
      },
      "result_preview": "[{\"id\": 123, \"content\": \"Netra es ingeniero mecánico...\", \"similarity\": 0.95}]"
    }
  ]
}
```

## 📊 Casos de Uso

### 1. Debugging
```typescript
const response = await fetch('/chat/auto-tools', {...});
const data = await response.json();

if (data.iterations > 3) {
  console.log('⚠️ Muchas iteraciones:', data.iterations);
  console.log('Tools ejecutadas:', data.tools_executed);
}
```

### 2. Analytics
```typescript
// Trackear qué tools se usan más
const toolsUsed = data.tools_executed?.map(t => t.tool_name) || [];
analytics.track('chat_completed', {
  iterations: data.iterations,
  tools_used: toolsUsed,
  finish_reason: data.finish_reason
});
```

### 3. UI/UX - Mostrar Progreso
```typescript
// Mostrar al usuario qué se hizo
if (data.tools_executed && data.tools_executed.length > 0) {
  const toolsInfo = data.tools_executed
    .map(t => `• Búsqueda: "${t.arguments.query}"`)
    .join('\n');
    
  console.log('Información obtenida de:');
  console.log(toolsInfo);
}
```

### 4. Logs y Monitoreo
```typescript
logger.info('Chat completed', {
  user_id: userId,
  iterations: data.iterations,
  tools_count: data.tools_executed?.length || 0,
  finish_reason: data.finish_reason,
  response_length: data.response.length
});
```

## 🔍 Interpretación del Metadata

### `iterations`
- **1**: Respuesta directa sin tools
- **2**: Una tool ejecutada + respuesta final
- **3+**: Múltiples tools o re-intentos
- **5**: Máximo alcanzado (posible problema)

### `tools_executed`
- **null**: No se ejecutaron tools
- **[...]**: Lista ordenada de ejecución

### `finish_reason`
- **"stop"**: Completado correctamente ✅
- **"tool_calls"**: Solo en `/chat`, nunca en `/chat/auto-tools`
- **"length"**: Max iterations o tokens alcanzados ⚠️
- **"error"**: Error en la ejecución ❌

## 💡 Tips

### 1. Monitorear Iterations
```python
if response.iterations >= 4:
    # Tal vez la tool definition no es clara
    # O el LLM está haciendo búsquedas redundantes
    logger.warning(f"High iterations: {response.iterations}")
```

### 2. Optimizar Tools
```python
# Analizar qué se busca para mejorar la tool
for tool in response.tools_executed:
    if tool.tool_name == "search_vector_store":
        query = tool.arguments.get("query")
        # Analizar patterns de búsqueda
```

### 3. Detectar Problemas
```python
if response.finish_reason == "length":
    # Loop infinito o problema con tools
    print("Max iterations reached!")
    print("Tools executed:", response.tools_executed)
```

## 📝 Response Examples

### Sin Tools
```json
{
  "response": "Hola, ¿cómo puedo ayudarte?",
  "iterations": 1,
  "tools_executed": null,
  "finish_reason": "stop"
}
```

### Una Tool
```json
{
  "response": "El clima en Madrid es...",
  "iterations": 2,
  "tools_executed": [
    {
      "tool_name": "get_current_weather",
      "arguments": {"location": "Madrid"},
      "result_preview": "{\"temperature\": \"22°C\", \"condition\": \"Sunny\"}"
    }
  ],
  "finish_reason": "stop"
}
```

### Múltiples Tools
```json
{
  "response": "He encontrado información sobre Python y el clima en Barcelona...",
  "iterations": 3,
  "tools_executed": [
    {
      "tool_name": "search_vector_store",
      "arguments": {"query": "Python"},
      "result_preview": "[{\"id\": 1, \"content\": \"Python es...\"}]"
    },
    {
      "tool_name": "get_current_weather",
      "arguments": {"location": "Barcelona"},
      "result_preview": "{\"temperature\": \"20°C\"}"
    }
  ],
  "finish_reason": "stop"
}
```

### Max Iterations
```json
{
  "response": "Max iterations reached. Unable to complete request.",
  "iterations": 5,
  "tools_executed": [
    {"tool_name": "search_vector_store", ...},
    {"tool_name": "search_vector_store", ...},
    {"tool_name": "search_vector_store", ...},
    {"tool_name": "search_vector_store", ...}
  ],
  "finish_reason": "length"
}
```

## 🚀 Frontend Integration

### React Hook
```typescript
interface ChatMetadata {
  iterations?: number;
  toolsExecuted?: Array<{
    tool_name: string;
    arguments: any;
    result_preview: string;
  }>;
}

function useChatWithMetadata() {
  const [metadata, setMetadata] = useState<ChatMetadata>({});
  
  const sendMessage = async (content: string) => {
    const response = await fetch('/chat/auto-tools', {...});
    const data = await response.json();
    
    setMetadata({
      iterations: data.iterations,
      toolsExecuted: data.tools_executed
    });
    
    return data.response;
  };
  
  return { sendMessage, metadata };
}
```

### Display Component
```tsx
function ChatMetadata({ metadata }: { metadata: ChatMetadata }) {
  if (!metadata.iterations) return null;
  
  return (
    <div className="metadata">
      <p>Iteraciones: {metadata.iterations}</p>
      {metadata.toolsExecuted && (
        <details>
          <summary>Tools ejecutadas ({metadata.toolsExecuted.length})</summary>
          <ul>
            {metadata.toolsExecuted.map((tool, i) => (
              <li key={i}>
                <strong>{tool.tool_name}</strong>
                <pre>{JSON.stringify(tool.arguments, null, 2)}</pre>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
```

## 🎓 Resumen

El metadata te permite:
- 🔍 **Debugging**: Ver exactamente qué pasó
- 📊 **Analytics**: Trackear uso de tools
- 🎨 **UX**: Mostrar progreso al usuario
- ⚡ **Optimización**: Identificar cuellos de botella
- 🐛 **Troubleshooting**: Diagnosticar problemas

**El endpoint `/chat` NO tiene este metadata** - solo `/chat/auto-tools` porque solo ahí el backend ejecuta el loop completo.

