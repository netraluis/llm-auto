from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

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

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_vector_context: bool = True
    vector_limit: int = 5

class ChatResponse(BaseModel):
    response: str
    context_used: Optional[str] = None

# Main endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal que integra OpenRouter con Supabase vector store
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
                    limit=request.vector_limit
                )
                
                if similar_docs:
                    # Combine context from similar documents
                    context = "\n".join([doc.get("content", "") for doc in similar_docs[:3]])
        
        print(f"\n🔍 Context found: {len(context) if context else 0} characters")
        if context:
            print(f"📄 Context preview: {context[:100]}...")
        
        # Convert messages to the format expected by OpenRouter
        openrouter_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in request.messages
        ]
        
        print(f"\n💬 Messages to send ({len(openrouter_messages)} messages):")
        for i, msg in enumerate(openrouter_messages):
            print(f"  {i+1}. [{msg['role'].upper()}]: {msg['content'][:50]}...")
        
        # Call OpenRouter with context
        print(f"\n🚀 Calling OpenRouter...")
        response = await openrouter_client.chat_completion(
            messages=openrouter_messages,
            context=context
        )
        
        print(f"\n✅ OpenRouter response ({len(response) if response else 0} characters):")
        print(f"📝 Response preview: {response[:100] if response else 'No response'}...")
        return ChatResponse(
            response=response,
            context_used=context
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
