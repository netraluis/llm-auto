# ChatKit Session Endpoint

## Endpoint: POST /api/chatkit/session

Crea una nueva sesión de ChatKit con OpenAI.

### Descripción

Este endpoint permite crear una sesión de ChatKit que puede ser utilizada para interacciones con el modelo de OpenAI. La sesión devuelve un `client_secret` que puede ser utilizado en el cliente para autenticar las peticiones.

### Request

**Método:** `POST`

**URL:** `/api/chatkit/session`

**Headers:**
```
Content-Type: application/json
```

**Body:** No requiere body

### Response

**Success (200):**
```json
{
  "client_secret": "cs_live_..."
}
```

**Error (500):**
```json
{
  "detail": "Error creating ChatKit session: [error message]"
}
```

### Ejemplo de uso

#### cURL

```bash
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Content-Type: application/json"
```

#### Python

```python
import requests

response = requests.post("http://localhost:8000/api/chatkit/session")
data = response.json()

print(f"Client Secret: {data['client_secret']}")
```

#### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/chatkit/session', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log('Client Secret:', data.client_secret);
```

### Configuración requerida

Asegúrate de tener configurada la variable de entorno `OPENAI_API_KEY` en tu archivo `.env`:

```bash
OPENAI_API_KEY=sk-...
```

### Notas

- El `client_secret` retornado es necesario para autenticar las peticiones del cliente con ChatKit
- La sesión tiene una duración limitada según las políticas de OpenAI
- Este endpoint requiere que tengas una API key válida de OpenAI con acceso a ChatKit

### Testing

Para probar el endpoint:

```bash
# Iniciar el servidor
uvicorn main:app --reload

# En otra terminal, hacer la petición
curl -X POST http://localhost:8000/api/chatkit/session
```

### Integración con el frontend

Una vez obtenido el `client_secret`, puedes usarlo en tu frontend para inicializar el cliente de ChatKit:

```typescript
import { ChatKit } from '@openai/chatkit';

// Obtener el client_secret del backend
const response = await fetch('http://localhost:8000/api/chatkit/session', {
  method: 'POST'
});
const { client_secret } = await response.json();

// Inicializar ChatKit
const chatkit = new ChatKit({
  clientSecret: client_secret
});
```
