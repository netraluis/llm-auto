# LLM Auto Backend

Backend simple con Python que integra OpenRouter con Supabase Vector Store.

## Características

- **FastAPI**: Framework web moderno y rápido
- **OpenRouter**: Integración con múltiples modelos de LLM
- **Supabase**: Vector store para búsqueda semántica
- **Endpoints RESTful**: API simple y documentada

## Configuración

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura las variables de entorno:
```bash
cp env.example .env
```

Edita el archivo `.env` con tus credenciales:
- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_KEY`: Clave anónima de Supabase
- `OPENROUTER_API_KEY`: Tu API key de OpenRouter
- `OPENROUTER_MODEL`: Modelo a usar (opcional, por defecto llama-3.1-8b-instruct)

## Uso

### Ejecutar el servidor:
```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Documentación automática:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST `/chat`
Endpoint principal que integra OpenRouter con el vector store.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "¿Qué es la inteligencia artificial?"}
  ],
  "use_vector_context": true,
  "vector_limit": 5
}
```

**Response:**
```json
{
  "response": "La inteligencia artificial es...",
  "context_used": "Contexto relevante del vector store..."
}
```

### GET `/health`
Verifica el estado del servicio.

### GET `/documents`
Obtiene documentos del vector store.

### POST `/documents`
Añade un nuevo documento al vector store.

## Estructura del Proyecto

```
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración y variables de entorno
├── supabase_client.py     # Cliente para Supabase vector store
├── openrouter_client.py   # Cliente para OpenRouter API
├── requirements.txt       # Dependencias Python
└── env.example           # Ejemplo de variables de entorno
```

## Notas

- Asegúrate de tener una tabla en Supabase con columnas `content` y `metadata`
- El vector store busca documentos similares basándose en el contenido
- El contexto del vector store se añade automáticamente a las consultas de OpenRouter