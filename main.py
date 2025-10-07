from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import httpx

from config import Config
from supabase_client import vector_store
from openrouter_client import openrouter_client

# Initialize FastAPI app
app = FastAPI(
    title="LLM Auto Backend",
    description="Backend que integra OpenRouter con Supabase Vector Store",
    version="1.0.0"
)

# Validate configuration on startup
@app.on_event("startup")
async def startup_event():
    try:
        Config.validate()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        raise

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

class ToolDefinition(BaseModel):
    type: str = "function"
    function: Dict[str, Any]

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_vector_context: bool = True
    vector_limit: int = 5
    assistant_id: str
    tools: Optional[List[ToolDefinition]] = None
    tool_choice: Optional[str] = "auto"  # "auto", "none", or specific tool

class ToolExecutionLog(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result_preview: str

class ChatResponse(BaseModel):
    response: str
    context_used: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: Optional[str] = None
    # Metadata para auto-tools
    iterations: Optional[int] = None
    tools_executed: Optional[List[ToolExecutionLog]] = None

# Tool execution functions
async def execute_tool(tool_name: str, arguments: Dict[str, Any], assistant_id: str = None) -> str:
    """
    Execute a tool based on its name
    """
    if tool_name == "search_vector_store":
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
    
    elif tool_name == "get_current_weather":
        location = arguments.get("location", "")
        
        if not Config.WEATHER_API_KEY:
            # Fallback a simulación si no hay API key
            return json.dumps({
                "location": location,
                "temperature": "22°C",
                "condition": "Sunny",
                "humidity": "65%",
                "note": "Using simulated data - no API key configured"
            })
        
        try:
            # Llamada real a WeatherAPI.com
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.weatherapi.com/v1/current.json",
                    params={
                        "key": Config.WEATHER_API_KEY,
                        "q": location,
                        "aqi": "no"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return json.dumps({
                        "location": f"{data['location']['name']}, {data['location']['country']}",
                        "temperature": f"{data['current']['temp_c']}°C",
                        "condition": data['current']['condition']['text'],
                        "humidity": f"{data['current']['humidity']}%",
                        "wind_kph": data['current']['wind_kph'],
                        "feels_like": f"{data['current']['feelslike_c']}°C"
                    })
                else:
                    return json.dumps({
                        "error": f"Weather API error: {response.status_code}",
                        "location": location
                    })
                    
        except Exception as e:
            return json.dumps({
                "error": f"Failed to fetch weather: {str(e)}",
                "location": location
            })
    
    # 👇 AÑADE TUS NUEVAS TOOLS AQUÍ
    # elif tool_name == "mi_nueva_tool":
    #     param1 = arguments.get("param1")
    #     # Tu lógica aquí
    #     result = await mi_funcion(param1)
    #     return json.dumps(result)
    
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

# Main endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal que integra OpenRouter con Supabase vector store
    Soporta function calling / tools
    """
    try:
        context = None
        
        # Get context from vector store if requested
        if request.use_vector_context and request.messages:
            # Use the last user message for context search
            last_message = request.messages[-1].content if request.messages[-1].role == "user" else ""
            
            if last_message:
                # Search for similar documents in vector store
                similar_docs = await vector_store.search_similar(
                    query=last_message,
                    limit=request.vector_limit,
                    assistant_id=request.assistant_id
                )
                
                if similar_docs:
                    # Combine context from similar documents
                    context = "\n".join([doc.get("content", "") for doc in similar_docs[:3]])
        
        print(f"\n🔍 Context found: {len(context) if context else 0} characters")
        if context:
            print(f"📄 Context preview: {context[:100]}...")
        
        # Convert messages to the format expected by OpenRouter
        openrouter_messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            openrouter_messages.append(message_dict)
        
        print(f"\n💬 Messages to send ({len(openrouter_messages)} messages):")
        for i, msg in enumerate(openrouter_messages):
            content_preview = str(msg.get('content', ''))[:50] if msg.get('content') else 'N/A'
            print(f"  {i+1}. [{msg['role'].upper()}]: {content_preview}...")
        
        # Prepare tools for OpenRouter
        tools = None
        if request.tools:
            tools = [tool.dict() for tool in request.tools]
        
        # Call OpenRouter with context and tools
        print(f"\n🚀 Calling OpenRouter...")
        if tools:
            print(f"🔧 Tools enabled: {len(tools)} tools")
        
        response_data = await openrouter_client.chat_completion(
            messages=openrouter_messages,
            context=context,
            tools=tools,
            tool_choice=request.tool_choice
        )
        
        # Check if response contains tool calls
        finish_reason = response_data.get("finish_reason", "stop")
        tool_calls = response_data.get("tool_calls")
        response_content = response_data.get("content", "")
        
        print(f"\n✅ OpenRouter response:")
        print(f"   📝 Finish reason: {finish_reason}")
        print(f"   🔧 Tool calls: {len(tool_calls) if tool_calls else 0}")
        
        # If there are tool calls, we might want to execute them automatically
        # or return them to the client to handle
        if tool_calls and finish_reason == "tool_calls":
            print(f"\n🔨 Processing tool calls...")
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                print(f"   🔹 Executing: {tool_name} with {arguments}")
        
        return ChatResponse(
            response=response_content,
            context_used=context,
            tool_calls=tool_calls,
            finish_reason=finish_reason
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Auto-loop endpoint with automatic tool execution
@app.post("/chat/auto-tools", response_model=ChatResponse)
async def chat_auto_tools_endpoint(request: ChatRequest):
    """
    Endpoint que ejecuta automáticamente los tool calls en un loop
    hasta que el LLM dé una respuesta final
    """
    try:
        context = None
        max_iterations = 5  # Prevenir loops infinitos
        iteration = 0
        tools_executed_log = []  # Log de tools ejecutadas
        
        # Get initial context if requested
        if request.use_vector_context and request.messages:
            last_message = request.messages[-1].content if request.messages[-1].role == "user" else ""
            if last_message:
                similar_docs = await vector_store.search_similar(
                    query=last_message,
                    limit=request.vector_limit,
                    assistant_id=request.assistant_id
                )
                if similar_docs:
                    context = "\n".join([doc.get("content", "") for doc in similar_docs[:3]])
        
        # Working messages list
        messages = [msg.dict() for msg in request.messages]
        tools = [tool.dict() for tool in request.tools] if request.tools else None
        
        print(f"\n🔄 Starting auto-tool loop...")
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔁 Iteration {iteration}/{max_iterations}")
            
            # Call OpenRouter
            response_data = await openrouter_client.chat_completion(
                messages=messages,
                context=context if iteration == 1 else None,  # Context only on first call
                tools=tools,
                tool_choice=request.tool_choice
            )
            
            finish_reason = response_data.get("finish_reason", "stop")
            tool_calls = response_data.get("tool_calls")
            content = response_data.get("content", "")
            
            # If no tool calls, we're done
            if finish_reason != "tool_calls" or not tool_calls:
                print(f"✅ Final response (finish_reason: {finish_reason})")
                return ChatResponse(
                    response=content,
                    context_used=context,
                    tool_calls=None,
                    finish_reason=finish_reason,
                    iterations=iteration,
                    tools_executed=tools_executed_log if tools_executed_log else None
                )
            
            # Add assistant message with tool calls
            assistant_msg = {
                "role": "assistant",
                "content": content or "",
                "tool_calls": tool_calls
            }
            messages.append(assistant_msg)
            
            print(f"🔧 Executing {len(tool_calls)} tool call(s)...")
            
            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                tool_call_id = tool_call["id"]
                
                print(f"   ⚙️  {tool_name}({arguments})")
                
                # Execute tool with assistant_id from request
                tool_result = await execute_tool(tool_name, arguments, request.assistant_id)
                
                # Log tool execution
                tools_executed_log.append(ToolExecutionLog(
                    tool_name=tool_name,
                    arguments=arguments,
                    result_preview=tool_result[:200] if len(tool_result) > 200 else tool_result
                ))
                
                # Add tool response message
                tool_msg = {
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call_id
                }
                messages.append(tool_msg)
                
                print(f"   ✓ Result: {tool_result[:100]}...")
        
        # Max iterations reached
        print(f"⚠️  Max iterations ({max_iterations}) reached")
        return ChatResponse(
            response="Max iterations reached. Unable to complete request.",
            context_used=context,
            tool_calls=None,
            finish_reason="length",
            iterations=max_iterations,
            tools_executed=tools_executed_log if tools_executed_log else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LLM Auto Backend"}

# Additional endpoints for vector store management
@app.get("/documents")
async def get_documents(limit: int = 10):
    """Get documents from vector store"""
    try:
        docs = await vector_store.search_similar("", limit=limit)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

@app.post("/documents")
async def add_document(request: DocumentRequest):
    """Add a new document to vector store"""
    try:
        doc = await vector_store.insert_document(request.content, request.metadata)
        return {"document": doc, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Debug endpoints
@app.get("/debug/tables")
async def debug_tables():
    """Debug: List available tables"""
    try:
        tables = await vector_store.list_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/table-structure/{table_name}")
async def debug_table_structure(table_name: str):
    """Debug: Check table structure"""
    try:
        structure = await vector_store.check_table_structure(table_name)
        return {"table": table_name, "structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/supabase-status")
async def debug_supabase_status():
    """Debug: Check Supabase connection status"""
    try:
        status = {
            "client_initialized": vector_store.client is not None,
            "supabase_url": Config.SUPABASE_URL[:30] + "..." if Config.SUPABASE_URL else None,
            "supabase_key": Config.SUPABASE_KEY[:20] + "..." if Config.SUPABASE_KEY else None
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
