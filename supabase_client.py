from supabase import create_client, Client
from config import Config
import openai
import json

class SupabaseVectorStore:
    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            print("⚠️  Supabase credentials not configured. Please check your .env file.")
            self.client = None
            return
        try:
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Supabase client: {e}")
            print("⚠️  Running in demo mode without Supabase")
            self.client = None
    
    async def generate_embedding(self, text: str):
        """
        Generate embedding for text using OpenAI API
        """
        try:
            if not Config.OPENAI_API_KEY:
                print("⚠️  OpenAI API key not configured for embeddings")
                return None
                
            client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"   ❌ Error generating embedding: {e}")
            return None
    
    async def search_similar_vector(self, query: str, table_name: str = "documents", limit: int = 5):
        """
        Search for similar documents using vector similarity with Supabase's native vector search
        """
        if not self.client:
            print("⚠️  Supabase client not initialized. Returning empty results.")
            return []
        
        print(f"\n🔍 Vector Similarity Search:")
        print(f"   📋 Table: {table_name}")
        print(f"   🔍 Query: {query[:50]}...")
        print(f"   📊 Limit: {limit}")
        
        try:
            # Generate embedding for the query
            print(f"   🚀 Generating embedding for query...")
            query_embedding = await self.generate_embedding(query)
            
            if query_embedding:
                print(f"   ✅ Generated embedding with {len(query_embedding)} dimensions")
                
                try:
                    # Use the RPC function with real embedding
                    response = self.client.rpc(
                        'match_documents',
                        {
                            'query_embedding': query_embedding,
                            'match_count': limit,
                            'filter': {}
                        }
                    ).execute()
                    
                    if response.data:
                        print(f"   ✅ Vector search successful!")
                        for i, doc in enumerate(response.data):
                            content = doc.get("content", "")
                            similarity = doc.get("similarity", doc.get("score", 0))
                            print(f"   📄 Doc {i+1} (similarity: {similarity:.3f}): {content[:50]}...")
                        return response.data
                    else:
                        print(f"   📭 No similar documents found via vector search")
                        
                except Exception as rpc_error:
                    print(f"   ⚠️  RPC function failed: {rpc_error}")
                    print(f"   🔄 Falling back to text-based similarity...")
            else:
                print(f"   ⚠️  Could not generate embedding, falling back to text search...")
            
            # Fallback: get all documents and do text-based similarity
            print(f"   🔍 Checking database for documents...")
            response = self.client.table(table_name).select("*").execute()
            
            print(f"   📊 Database query returned: {len(response.data) if response.data else 0} documents")
            
            if response.data:
                print(f"   📊 Found {len(response.data)} documents, using text-based similarity...")
                # Show first few documents for debugging
                for i, doc in enumerate(response.data[:3]):
                    content = doc.get("content", "")
                    print(f"   📄 Doc {i+1}: {content[:50]}...")
                else:
                    print(f"   📭 No documents found in database")
                    print(f"   💡 Tip: Add some documents first using POST /documents endpoint")
                
                # Do text-based similarity scoring
                scored_docs = []
                query_lower = query.lower()
                query_words = [word for word in query_lower.split() if len(word) > 2]
                
                for doc in response.data:
                    content = doc.get("content", "").lower()
                    
                    # Calculate similarity score
                    score = 0
                    if query_lower in content:
                        score += 1.0  # Exact phrase match
                    
                    word_matches = sum(1 for word in query_words if word in content)
                    if word_matches > 0:
                        score += word_matches / len(query_words) * 0.5  # Word matches
                    
                    if score > 0:
                        doc['similarity'] = score
                        scored_docs.append(doc)
                
                # Sort by similarity score
                scored_docs.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                
                print(f"   ✅ Text similarity found {len(scored_docs)} relevant documents")
                for i, doc in enumerate(scored_docs[:limit]):
                    content = doc.get("content", "")
                    similarity = doc.get("similarity", 0)
                    print(f"   📄 Doc {i+1} (similarity: {similarity:.3f}): {content[:50]}...")
                
                return scored_docs[:limit]
            else:
                print(f"   📭 No documents found in database")
                print(f"   💡 Tip: Add some documents first using POST /documents endpoint")
                return []
                
        except Exception as e:
            print(f"   ❌ Vector search failed: {e}")
            return []

    async def search_similar(self, query: str, table_name: str = "documents", limit: int = 5):
        """
        Search for similar documents using vector similarity with fallback to text search
        """
        if not self.client:
            print("⚠️  Supabase client not initialized. Returning empty results.")
            return []
        
        print(f"\n🔍 Document Search:")
        print(f"   📋 Table: {table_name}")
        print(f"   🔍 Query: {query[:50]}...")
        print(f"   📊 Limit: {limit}")
        
        # First try vector search
        try:
            print(f"   🚀 Attempting vector similarity search...")
            vector_results = await self.search_similar_vector(query, table_name, limit)
            
            if vector_results:
                print(f"   ✅ Vector search successful, returning {len(vector_results)} results")
                return vector_results
            else:
                print(f"   📭 Vector search returned no results, trying fallback...")
                
        except Exception as vector_error:
            print(f"   ⚠️  Vector search failed: {vector_error}")
            print(f"   🔄 Falling back to text search...")
        
        # Fallback to text search
        try:
            print(f"   🔍 Performing text-based search...")
            response = self.client.table(table_name).select("*").execute()
            
            if not response.data:
                print(f"   📭 No documents found in database")
                return []
            
            print(f"   📊 Found {len(response.data)} total documents, filtering by text similarity...")
            
            # Simple text matching as fallback
            filtered_docs = []
            query_lower = query.lower()
            query_words = [word for word in query_lower.split() if len(word) > 2]
            
            for doc in response.data:
                content = doc.get("content", "").lower()
                
                # Check for exact phrase match
                if query_lower in content:
                    filtered_docs.append(doc)
                    print(f"   ✅ Phrase match: {content[:50]}...")
                    continue
                
                # Check for word matches
                word_matches = sum(1 for word in query_words if word in content)
                if word_matches > 0:
                    # Add similarity score for ranking
                    doc['text_similarity'] = word_matches / len(query_words)
                    filtered_docs.append(doc)
                    print(f"   ✅ Word match ({word_matches}/{len(query_words)}): {content[:50]}...")
            
            # Sort by similarity if we have scores
            if filtered_docs and 'text_similarity' in filtered_docs[0]:
                filtered_docs.sort(key=lambda x: x.get('text_similarity', 0), reverse=True)
            
            print(f"   🎯 Text search found {len(filtered_docs)} documents")
            return filtered_docs[:limit]
            
        except Exception as fallback_error:
            print(f"   ❌ Text search also failed: {fallback_error}")
            return []
    
    async def get_document_by_id(self, doc_id: str, table_name: str = "documents"):
        """
        Get a specific document by ID
        """
        if not self.client:
            print("Supabase client not initialized.")
            return None
        try:
            response = self.client.table(table_name).select("*").eq("id", doc_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting document from Supabase: {e}")
            return None
    
    async def list_tables(self):
        """
        List all available tables in the database
        """
        if not self.client:
            print("⚠️  Supabase client not initialized.")
            return []
        
        try:
            # This is a simple way to check tables - we'll try to query information_schema
            print(f"\n📋 Checking available tables...")
            
            # Try to get tables from information_schema
            response = self.client.rpc('get_tables_info').execute()
            if response.data:
                print(f"   📊 Available tables: {response.data}")
                return response.data
            else:
                print(f"   ❌ Could not retrieve table information")
                return []
                
        except Exception as e:
            print(f"   ❌ Error listing tables: {e}")
            return []
    
    async def check_table_structure(self, table_name: str = "documents"):
        """
        Check the structure of a specific table
        """
        if not self.client:
            print("⚠️  Supabase client not initialized.")
            return None
        
        try:
            print(f"\n🔍 Checking table structure for: {table_name}")
            
            # Try to get one row to see the structure
            response = self.client.table(table_name).select("*").limit(1).execute()
            
            if response.data:
                print(f"   ✅ Table exists and has data")
                print(f"   📊 Columns: {list(response.data[0].keys())}")
                print(f"   📄 Sample data: {response.data[0]}")
                return response.data[0]
            else:
                print(f"   📭 Table exists but is empty")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking table structure: {e}")
            return None

    async def insert_document(self, content: str, metadata: dict = None, table_name: str = "documents"):
        """
        Insert a new document into the vector store
        """
        if not self.client:
            print("⚠️  Supabase client not initialized.")
            return None
        
        print(f"\n💾 Inserting document:")
        print(f"   📋 Table: {table_name}")
        print(f"   📝 Content: {content[:50]}...")
        print(f"   🏷️  Metadata: {metadata}")
        
        try:
            data = {
                "content": content,
                "metadata": metadata or {}
            }
            response = self.client.table(table_name).insert(data).execute()
            
            if response.data:
                print(f"   ✅ Document inserted successfully")
                return response.data[0]
            else:
                print(f"   ❌ No data returned from insert")
                return None
                
        except Exception as e:
            print(f"   ❌ Error inserting document to Supabase: {e}")
            return None

# Global instance
vector_store = SupabaseVectorStore()
