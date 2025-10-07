# Añadir Documentos de Prueba

Ejecuta estos curls en orden para añadir documentos de ejemplo a tu tabla:

## 1. Documento sobre Inteligencia Artificial
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "La inteligencia artificial es un campo de la informática que se centra en la creación de sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
    "metadata": {
        "topic": "AI",
        "language": "es",
        "category": "technology"
    }
}'
```

## 2. Documento sobre Python
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Es conocido por su sintaxis simple y legible.",
    "metadata": {
        "topic": "Programming",
        "language": "es",
        "category": "technology"
    }
}'
```

## 3. Documento sobre Machine Learning
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "Machine Learning es una rama de la inteligencia artificial que permite a las máquinas aprender y mejorar automáticamente a partir de la experiencia.",
    "metadata": {
        "topic": "ML",
        "language": "es",
        "category": "technology"
    }
}'
```

## 4. Documento sobre FastAPI
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "FastAPI es un framework web moderno y rápido para construir APIs con Python, basado en estándares abiertos.",
    "metadata": {
        "topic": "Web Development",
        "language": "es",
        "category": "technology"
    }
}'
```

## 5. Documento sobre Supabase
```bash
curl --location 'http://localhost:8000/documents' \
--header 'Content-Type: application/json' \
--data '{
    "content": "Supabase es una plataforma backend como servicio que proporciona una base de datos PostgreSQL, autenticación y almacenamiento.",
    "metadata": {
        "topic": "Backend",
        "language": "es",
        "category": "technology"
    }
}'
```

## Después de añadir los documentos, verifica:

### Verificar que se guardaron:
```bash
curl --location 'http://localhost:8000/documents'
```

### Verificar estructura de tabla:
```bash
curl --location 'http://localhost:8000/debug/table-structure/documents'
```

### Probar chat con contexto:
```bash
curl --location 'http://localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "¿Qué es Python?"
        }
    ],
    "use_vector_context": true,
    "vector_limit": 3,
    "assistant_id: xxxx
}'
```

Esto debería devolver una respuesta que incluya información sobre Python del vector store.
