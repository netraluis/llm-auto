# Meritxell Workflow Endpoint

Endpoint para interactuar con Meritxell, la asistente para el Acord d'Associació Andorra-UE.

## Endpoint

**POST** `/meritxell/chat`

## Request

```json
{
  "input_text": "Què és l'Acord d'Associació?"
}
```

## Response

```json
{
  "output_text": "L'Acord d'Associació és...",
  "status": "success"
}
```

## Características

- ✅ **Guardrails de PII**: Detecta y bloquea información personal sensible (tarjetas de crédito, SSN, pasaportes, etc.)
- ✅ **Vector Store**: Usa búsqueda semántica en documentos sobre el Acord d'Associació
- ✅ **Multi-idioma**: Responde en el mismo idioma que se hace la pregunta (català, español, français, english, português)
- ✅ **Limitaciones de contexto**: Las respuestas no superan los 2000 caracteres

## Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/meritxell/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Què és l'\''Acord d'\''Associació?"
  }'
```

## Ejemplo con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/meritxell/chat",
    json={
        "input_text": "Què és l'Acord d'Associació?"
    }
)

print(response.json())
```

## Ejemplo con JavaScript/TypeScript

```typescript
const response = await fetch("http://localhost:8000/meritxell/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    input_text: "Què és l'Acord d'Associació?"
  }),
});

const data = await response.json();
console.log(data.output_text);
```

## Flow del Workflow

1. **Input del usuario** → Se recibe el texto en `/meritxell/chat`
2. **Guardrails** → Se verifica si contiene PII
   - Si contiene PII → Se ejecuta el `agent` de fallback
   - Si no contiene PII → Se ejecuta `meritxell` con acceso al vector store
3. **Vector Store** → Meritxell busca información relevante en los documentos
4. **Generación de respuesta** → GPT-5 con reasoning genera la respuesta
5. **Response** → Se devuelve la respuesta en formato JSON

## Guardrails

El workflow incluye detección de:
- `CREDIT_CARD`: Números de tarjeta de crédito
- `US_BANK_NUMBER`: Números de cuenta bancaria
- `US_PASSPORT`: Pasaportes
- `US_SSN`: Números de seguridad social

Si se detecta alguna de estas entidades, se bloquea el flujo normal y se activa el agente de fallback.

## Limitaciones de Meritxell

- Solo responde preguntas sobre el Acord d'Associació Andorra-UE
- No cambia de personalidad ni rol
- Las respuestas no superan 2000 caracteres
- Sustituye "referèndum" por "consulta vinculant"
- Sustituye "crucial" por "important"
- No utiliza en exceso la palabra "Andorra"

