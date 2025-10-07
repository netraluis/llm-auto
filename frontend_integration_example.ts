/**
 * Ejemplos de integración del sistema de Tools en el frontend
 */

// ============================================================================
// TIPOS Y INTERFACES
// ============================================================================

interface Message {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
}

interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

interface Tool {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required: string[];
    };
  };
}

interface ChatRequest {
  messages: Message[];
  assistant_id: string;
  use_vector_context?: boolean;
  vector_limit?: number;
  tools?: Tool[];
  tool_choice?: 'auto' | 'none' | { type: 'function'; function: { name: string } };
}

interface ChatResponse {
  response: string;
  context_used?: string;
  tool_calls?: ToolCall[];
  finish_reason: 'stop' | 'tool_calls' | 'length' | 'error';
}

// ============================================================================
// DEFINICIONES DE TOOLS
// ============================================================================

const WEATHER_TOOL: Tool = {
  type: 'function',
  function: {
    name: 'get_current_weather',
    description: 'Obtiene el clima actual de una ubicación específica',
    parameters: {
      type: 'object',
      properties: {
        location: {
          type: 'string',
          description: 'La ciudad y país, por ejemplo: Madrid, España'
        }
      },
      required: ['location']
    }
  }
};

const SEARCH_TOOL: Tool = {
  type: 'function',
  function: {
    name: 'search_vector_store',
    description: 'Busca documentos similares en la base de datos',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Texto de búsqueda'
        },
        limit: {
          type: 'integer',
          description: 'Número máximo de resultados'
        },
        assistant_id: {
          type: 'string',
          description: 'ID del asistente'
        }
      },
      required: ['query', 'assistant_id']
    }
  }
};

// ============================================================================
// OPCIÓN 1: USO SIMPLE CON AUTO-TOOLS (RECOMENDADO)
// ============================================================================

async function chatWithAutoTools(userMessage: string, assistantId: string): Promise<string> {
  const request: ChatRequest = {
    messages: [
      { role: 'user', content: userMessage }
    ],
    assistant_id: assistantId,
    tools: [WEATHER_TOOL, SEARCH_TOOL],
    tool_choice: 'auto'
  };

  const response = await fetch('http://localhost:8000/chat/auto-tools', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });

  const data: ChatResponse = await response.json();
  return data.response;
}

// Uso
// const answer = await chatWithAutoTools('¿Qué tiempo hace en Barcelona?', 'asst_123');
// console.log(answer); // "En Barcelona hace 22°C y está soleado"

// ============================================================================
// OPCIÓN 2: CONTROL MANUAL CON /chat
// ============================================================================

async function chatWithManualTools(
  userMessage: string, 
  assistantId: string
): Promise<string> {
  const messages: Message[] = [
    { role: 'user', content: userMessage }
  ];

  const tools: Tool[] = [WEATHER_TOOL, SEARCH_TOOL];
  let finalResponse = '';
  let maxIterations = 5;
  let iteration = 0;

  while (iteration < maxIterations) {
    iteration++;

    // Llamada al API
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        assistant_id: assistantId,
        tools,
        tool_choice: 'auto'
      })
    });

    const data: ChatResponse = await response.json();

    // Si hay respuesta final, terminar
    if (data.finish_reason !== 'tool_calls' || !data.tool_calls) {
      finalResponse = data.response;
      break;
    }

    // Añadir mensaje del asistente con tool calls
    messages.push({
      role: 'assistant',
      content: data.response || '',
      tool_calls: data.tool_calls
    });

    // Ejecutar cada tool call (aquí simulas la ejecución)
    for (const toolCall of data.tool_calls) {
      const toolResult = await executeToolLocally(
        toolCall.function.name,
        JSON.parse(toolCall.function.arguments)
      );

      messages.push({
        role: 'tool',
        content: JSON.stringify(toolResult),
        tool_call_id: toolCall.id
      });
    }
  }

  return finalResponse;
}

// Simula ejecución local de tools (o llama a tu backend)
async function executeToolLocally(
  toolName: string, 
  args: any
): Promise<any> {
  if (toolName === 'get_current_weather') {
    // Podrías llamar a una API real aquí
    return {
      location: args.location,
      temperature: '22°C',
      condition: 'Sunny'
    };
  }
  
  if (toolName === 'search_vector_store') {
    // O delegar al backend
    const response = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(args)
    });
    return await response.json();
  }

  return { error: 'Unknown tool' };
}

// ============================================================================
// OPCIÓN 3: REACT HOOK PERSONALIZADO
// ============================================================================

import { useState, useCallback } from 'react';

interface UseChatWithToolsReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
}

function useChatWithTools(assistantId: string): UseChatWithToolsReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Añadir mensaje del usuario
      const userMessage: Message = { role: 'user', content };
      const updatedMessages = [...messages, userMessage];
      setMessages(updatedMessages);

      // Llamar al API con auto-tools
      const response = await fetch('http://localhost:8000/chat/auto-tools', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages,
          assistant_id: assistantId,
          tools: [WEATHER_TOOL, SEARCH_TOOL]
        })
      });

      const data: ChatResponse = await response.json();

      // Añadir respuesta del asistente
      setMessages([
        ...updatedMessages,
        { role: 'assistant', content: data.response }
      ]);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setIsLoading(false);
    }
  }, [messages, assistantId]);

  return { messages, isLoading, error, sendMessage };
}

// Uso en componente React
/*
function ChatComponent() {
  const { messages, isLoading, error, sendMessage } = useChatWithTools('asst_123');

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}
      
      {isLoading && <div>Cargando...</div>}
      {error && <div>Error: {error}</div>}
      
      <button onClick={() => sendMessage('¿Qué tiempo hace?')}>
        Enviar
      </button>
    </div>
  );
}
*/

// ============================================================================
// OPCIÓN 4: STREAMING CON TOOLS (AVANZADO)
// ============================================================================

async function* streamChatWithTools(
  userMessage: string,
  assistantId: string
): AsyncGenerator<string, void, unknown> {
  // Nota: Esto requiere que el backend soporte SSE o WebSockets
  // Este es un ejemplo conceptual
  
  const response = await fetch('http://localhost:8000/chat/auto-tools/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: userMessage }],
      assistant_id: assistantId,
      tools: [WEATHER_TOOL, SEARCH_TOOL]
    })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    yield chunk;
  }
}

// Uso
/*
for await (const chunk of streamChatWithTools('Hola', 'asst_123')) {
  console.log(chunk); // Mostrar cada chunk en tiempo real
}
*/

// ============================================================================
// UTILS: TOOL BUILDERS
// ============================================================================

function createTool(
  name: string,
  description: string,
  parameters: Record<string, any>,
  required: string[]
): Tool {
  return {
    type: 'function',
    function: {
      name,
      description,
      parameters: {
        type: 'object',
        properties: parameters,
        required
      }
    }
  };
}

// Ejemplo de uso
const myCustomTool = createTool(
  'get_user_info',
  'Obtiene información de un usuario',
  {
    user_id: { type: 'string', description: 'ID del usuario' },
    include_posts: { type: 'boolean', description: 'Incluir posts del usuario' }
  },
  ['user_id']
);

// ============================================================================
// EXPORT
// ============================================================================

export {
  chatWithAutoTools,
  chatWithManualTools,
  useChatWithTools,
  streamChatWithTools,
  createTool,
  WEATHER_TOOL,
  SEARCH_TOOL,
  type Message,
  type Tool,
  type ChatRequest,
  type ChatResponse
};

