# Curls para Postman - LLM Auto Backend

## Base URL
```
http://localhost:8000
```

## 1. Health Check
```bash
curl --location 'http://localhost:8000/health' \
--method GET
```

## 2. Create ChatKit Session
```bash
curl --location 'http://localhost:8000/api/chatkit/session' \
--method POST \
--header 'Content-Type: application/json'
```

## 3. Chat Endpoint (Principal)
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "¿Qué es la inteligencia artificial?"
        }
    ],
    "use_vector_context": true,
    "vector_limit": 5
}'
```

## 4. Chat sin contexto del vector store
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "Explícame qué es Python"
        }
    ],
    "use_vector_context": false,
    "vector_limit": 5
}'
```

## 5. Chat con múltiples mensajes (conversación)
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "Hola, ¿cómo estás?"
        },
        {
            "role": "assistant",
            "content": "¡Hola! Estoy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?"
        },
        {
            "role": "user",
            "content": "Cuéntame sobre machine learning"
        }
    ],
    "use_vector_context": true,
    "vector_limit": 3
}'
```

## 6. Obtener documentos del vector store
```bash
curl --location 'http://localhost:8000/documents?limit=10' \
--method GET
```

## 7. Añadir documento al vector store
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "La inteligencia artificial es un campo de la informática que se centra en la creación de sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
    "metadata": {
        "topic": "AI",
        "source": "manual",
        "language": "es"
    }
}'
```

## 8. Añadir documento sin metadata
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Es conocido por su sintaxis simple y legible."
}'
```

## 9. Debug: Verificar estado de Supabase
```bash
curl --location 'http://localhost:8000/debug/supabase-status' \
--method GET
```

## 10. Debug: Listar tablas disponibles
```bash
curl --location 'http://localhost:8000/debug/tables' \
--method GET
```

## 11. Debug: Verificar estructura de tabla
```bash
curl --location 'http://localhost:8000/debug/table-structure/documents' \
--method GET
```

## Ejemplos de respuestas esperadas:

### ChatKit Session Response:
```json
{
    "client_secret": "cs_live_abc123xyz..."
}
```

### Chat Response:
```json
{
    "response": "La inteligencia artificial es...",
    "context_used": "Contexto relevante del vector store si está disponible..."
}
```

### Health Check Response:
```json
{
    "status": "healthy",
    "service": "LLM Auto Backend"
}
```

### Documents Response:
```json
{
    "documents": [
        {
            "id": "uuid-here",
            "content": "contenido del documento...",
            "metadata": {},
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

## Notas para Postman:

1. **Importar**: Copia cada curl y usa "Import" en Postman para crear las requests automáticamente
2. **Variables**: Crea una variable de entorno `base_url` con valor `http://localhost:8000`
3. **Headers**: Asegúrate de que `Content-Type: application/json` esté configurado
4. **Testing**: Usa estos curls para probar que el servidor funciona correctamente

## Flujo de prueba recomendado:

1. Primero ejecuta el health check
2. Luego prueba el chat básico
3. Añade algunos documentos al vector store
4. Prueba el chat con contexto habilitado
5. Verifica que los documentos se guardaron correctamente
