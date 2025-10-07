#!/bin/bash

# ============================================================================
# EJEMPLOS DE CURL PARA TOOLS / FUNCTION CALLING
# ============================================================================

echo "🛠️  TOOLS / FUNCTION CALLING - Ejemplos cURL"
echo "================================================"

# ============================================================================
# 1. SIMPLE - Una tool con auto-tools
# ============================================================================

echo -e "\n📝 Ejemplo 1: Simple Weather Query (auto-tools)"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué tiempo hace en Madrid?"
      }
    ],
    "assistant_id": "asst_123",
    "use_vector_context": false,
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

# ============================================================================
# 2. MÚLTIPLES TOOLS con auto-tools
# ============================================================================

echo -e "\n\n📝 Ejemplo 2: Múltiples Tools (auto-tools)"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Busca información sobre Python y dime el clima en Barcelona"
      }
    ],
    "assistant_id": "asst_456",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_vector_store",
          "description": "Busca documentos en el vector store",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "Texto de búsqueda"
              },
              "limit": {
                "type": "integer",
                "description": "Número de resultados"
              },
              "assistant_id": {
                "type": "string",
                "description": "ID del asistente"
              }
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
              "location": {
                "type": "string",
                "description": "Ciudad y país"
              }
            },
            "required": ["location"]
          }
        }
      }
    ]
  }'

# ============================================================================
# 3. CONTROL MANUAL - Primera request con /chat
# ============================================================================

echo -e "\n\n📝 Ejemplo 3: Manual Tool Execution (Paso 1 - Primera request)"
echo "----------------------------------------------------------------"

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué temperatura hace en Sevilla?"
      }
    ],
    "assistant_id": "asst_789",
    "use_vector_context": false,
    "tools": [
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

echo -e "\n\n📝 Ejemplo 3b: Manual Tool Execution (Paso 2 - Con resultado de tool)"
echo "----------------------------------------------------------------------"
echo "NOTA: Reemplaza 'call_abc123' con el ID real del tool_call que recibiste"

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué temperatura hace en Sevilla?"
      },
      {
        "role": "assistant",
        "content": "",
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_current_weather",
              "arguments": "{\"location\": \"Sevilla, España\"}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": "{\"location\": \"Sevilla, España\", \"temperature\": \"25°C\", \"condition\": \"Sunny\"}",
        "tool_call_id": "call_abc123"
      }
    ],
    "assistant_id": "asst_789",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima",
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

# ============================================================================
# 4. FORZAR USO DE TOOL ESPECÍFICA
# ============================================================================

echo -e "\n\n📝 Ejemplo 4: Forzar uso de tool específica"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Dame información"
      }
    ],
    "assistant_id": "asst_101",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {"type": "string"}
            },
            "required": ["location"]
          }
        }
      }
    ],
    "tool_choice": {
      "type": "function",
      "function": {"name": "get_current_weather"}
    }
  }'

# ============================================================================
# 5. SIN TOOLS (tool_choice: "none")
# ============================================================================

echo -e "\n\n📝 Ejemplo 5: Deshabilitar tools (tool_choice: none)"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué tiempo hace en Madrid?"
      }
    ],
    "assistant_id": "asst_202",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Obtiene el clima",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {"type": "string"}
            },
            "required": ["location"]
          }
        }
      }
    ],
    "tool_choice": "none"
  }'

# ============================================================================
# 6. BÚSQUEDA EN VECTOR STORE
# ============================================================================

echo -e "\n\n📝 Ejemplo 6: Búsqueda en Vector Store"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Busca documentos sobre inteligencia artificial"
      }
    ],
    "assistant_id": "asst_303",
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_vector_store",
          "description": "Busca documentos similares en la base de datos",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "Texto de búsqueda"
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
    ]
  }'

# ============================================================================
# 7. CONVERSACIÓN CON CONTEXTO
# ============================================================================

echo -e "\n\n📝 Ejemplo 7: Conversación multi-turno con tools"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hola, ¿qué tal?"
      },
      {
        "role": "assistant",
        "content": "¡Hola! Estoy bien, gracias. ¿En qué puedo ayudarte?"
      },
      {
        "role": "user",
        "content": "¿Qué tiempo hace en Valencia?"
      }
    ],
    "assistant_id": "asst_404",
    "tools": [
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

# ============================================================================
# 8. COMBINACIÓN: Tools + Vector Context
# ============================================================================

echo -e "\n\n📝 Ejemplo 8: Tools + Vector Context juntos"
echo "------------------------------------------------"

curl -X POST http://localhost:8000/chat/auto-tools \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "¿Qué dice la documentación sobre Python y qué tiempo hace en Madrid?"
      }
    ],
    "assistant_id": "asst_505",
    "use_vector_context": true,
    "vector_limit": 3,
    "tools": [
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

echo -e "\n\n✅ Ejemplos completados!"
echo "================================================"

