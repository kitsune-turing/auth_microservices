# 🔐 JANO - MICROSERVICIO CENTRALIZADO DE VALIDACIÓN

**Concepto**: Un único microservicio que valida autenticación y autorización para TODOS los otros microservicios.

---

## 📊 ARQUITECTURA ACTUAL vs PROPUESTA

### ❌ ACTUAL (Validación Distribuida - NO ÓPTIMO)
```
┌─────────────────────────┐
│   Auth Microservice     │
│  - Genera JWT           │
│  - OTP validation       │
│  - Tokens               │
└──────────┬──────────────┘

┌─────────────────────────┐
│   Users Microservice    │
│  - Credenciales         │
│  - JANO rules?          │
│  - Rate limiting?       │
└──────────┬──────────────┘

┌─────────────────────────┐
│   OTP Microservice      │
│  - OTP codes            │
│  - Validación?          │
│  - Rate limiting?       │
└──────────┬──────────────┘

┌─────────────────────────┐
│   Management App MS     │
│  - ¿Cómo valida?        │
│  - ¿Qué reglas?         │
│  - ¿Rate limit?         │
└─────────────────────────┘

❌ PROBLEMA: Cada servicio hace su propia validación
❌ PROBLEMA: No hay consistencia de reglas
❌ PROBLEMA: Duplicación de lógica
❌ PROBLEMA: Difícil mantener
```

---

### ✅ PROPUESTA (JANO Centralizado)

```
┌────────────────────────────────────────────────────────────────┐
│                  JANO MICROSERVICE (Central)                   │
│                        (Puerto 8002)                           │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  VALIDACIÓN DE TOKENS & AUTORIZACIÓN                    │  │
│  │  - Valida JWT con firmas públicas                       │  │
│  │  - Verifica roles y permisos                            │  │
│  │  - Evalúa reglas de seguridad                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  REGLAS DE SEGURIDAD (jano_security_rules)              │  │
│  │  - Rate limiting (requests por minuto)                  │  │
│  │  - IP whitelist                                         │  │
│  │  - MFA policies                                         │  │
│  │  - Password policies                                    │  │
│  │  - Session expiry                                       │  │
│  │  - Command execution rules                              │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  CACHÉ DE PERMISOS & GRUPOS                             │  │
│  │  - Cache de usuario + roles + grupos (10 min)           │  │
│  │  - Cache de restricciones por recurso                   │  │
│  │  - Cache de aplicaciones y módulos                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AUDITORÍA & LOGGING                                    │  │
│  │  - Registro de violaciones (jano_rule_violations)       │  │
│  │  - Logs de acceso negado                                │  │
│  │  - Estadísticas de seguridad                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
   ▲            ▲            ▲           
   │ Valida     │ Valida     │ Valida  
┌──┴──┐      ┌──┴──┐      ┌──┴──┐    
│Auth │      │Users│      │ OTP │     
│(8001)     │(8006)      │(8003)     
└─────┘      └─────┘      └─────┘     
```

---

## 🔄 FLUJO DE VALIDACIÓN EN JANO

### Cuando CUALQUIER microservicio recibe una petición:

```
1. Petición llega al Microservicio
   └─> GET /api/users/1
       Headers: Authorization: Bearer eyJhbGc...

2. Microservicio (Auth, Users, OTP, etc.) llama a JANO
   └─> POST http://jano_microservice:8002/api/validate
       {
         "token": "eyJhbGc...",
         "endpoint": "/api/users/1",
         "method": "GET",
         "ip_address": "192.168.1.100",
         "user_agent": "Mozilla/5.0...",
         "request_data": {...}
       }

3. JANO valida en ESTE ORDEN:
   
   ✅ ETAPA 1: AUTENTICACIÓN
      └─> ¿El token es válido?
          - Verifica firma del JWT
          - Comprueba que no esté expirado
          - Verifica que no esté revocado
      
      Si ✅ Continúa a ETAPA 2
      Si ❌ Retorna 401 Unauthorized

   ✅ ETAPA 2: AUTORIZACIÓN (URL + Método)
      └─> ¿El usuario puede acceder a este endpoint?
          - Lee tabla: jano_security_rules (restricciones)
          - Mapea URL: /api/users/* 
          - Valida método: GET
          - Verifica grupos del usuario
      
      Si ✅ Continúa a ETAPA 3
      Si ❌ Retorna 403 Forbidden

   ✅ ETAPA 3: EVALUACIÓN DE REGLAS DE SEGURIDAD
      └─> Rate limiting
          - ¿Qué IP? → ¿Cuántas requests en el último minuto?
          - Si >= 100 req/min → BLOQUEA
          - Registra violación en: jano_rule_violations
      
      └─> Otras validaciones
          - ¿IP en whitelist?
          - ¿Comando permitido para este rol?
          - ¿Cartera de clientes?
          - ¿Nivel de seguridad?
      
      Si ✅ Continúa a ETAPA 4
      Si ❌ Retorna 429 Too Many Requests o 403 Forbidden

   ✅ ETAPA 4: RETORNA PERMISO AL MICROSERVICIO
      └─> Retorna JSON con permisos validados:
          {
            "authorized": true,
            "user": {
              "user_id": "78de8e0b-...",
              "username": "juan.perez",
              "email": "juan.perez@siata.gov.co",
              "role": "user_siata",
              "groups": ["hidrologia", "development"],
              "permissions": ["read", "write"]
            },
            "validation": {
              "stage_1_authentication": "PASS",
              "stage_2_authorization": "PASS",
              "stage_3_rules": "PASS"
            },
            "metadata": {
              "token_expires_at": "2025-10-19T23:00:00Z",
              "cached": true,
              "cache_ttl": 600
            }
          }

4. Microservicio recibe respuesta
   └─> Si authorized === true
       ├─> Continúa con la lógica de negocio
       ├─> Accede a la BD
       ├─> Procesa la petición
       └─> Retorna respuesta al cliente
   
   └─> Si authorized === false
       ├─> Retorna error (401, 403, 429)
       └─> NO accede a la BD
```

---

## 📋 ENDPOINTS DE JANO

### 1. **POST /api/validate** (Principal)
**Propósito**: Validar token y autorización

```
Petición:
POST http://jano_microservice:8002/api/validate
{
  "token": "eyJhbGc...",
  "endpoint": "/api/users/1",
  "method": "GET",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "request_data": {} (opcional)
}

Respuesta ✅ (Autorizado):
{
  "authorized": true,
  "user": {
    "user_id": "...",
    "username": "juan.perez",
    "role": "user_siata",
    "groups": ["hidrologia"],
    "permissions": ["read", "write"]
  },
  "validation_stages": [
    {"stage": "authentication", "result": "PASS"},
    {"stage": "authorization", "result": "PASS"},
    {"stage": "rules_evaluation", "result": "PASS"}
  ]
}

Respuesta ❌ (No autorizado):
{
  "authorized": false,
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "100 requests per minute exceeded",
  "retry_after": 45
}
```

### 2. **POST /api/validate-command** (Para comandos complejos)
**Propósito**: Validar ejecución de comandos específicos

```
Petición:
POST http://jano_microservice:8002/api/validate-command
{
  "token": "eyJhbGc...",
  "command": "task.save",
  "resource": "/api/tasks",
  "ip_address": "192.168.1.100"
}

Respuesta:
{
  "authorized": true,
  "command": "task.save",
  "restrictions_matched": {
    "rule": "COMMAND_RULE_001",
    "allowed_roles": ["root", "user_siata"],
    "allowed_commands": ["*"]
  }
}
```

### 3. **GET /api/rules** (Consultar reglas)
**Propósito**: Obtener todas las reglas de seguridad

```
GET http://jano_microservice:8002/api/rules

Respuesta:
{
  "rules": [
    {
      "rule_id": "...",
      "rule_name": "Rate limiting de API",
      "rule_type": "rate_limit",
      "config": {
        "requests_per_minute": 100,
        "burst_size": 150
      },
      "severity": "high",
      "is_active": true
    },
    ...
  ]
}
```

### 4. **POST /api/violations** (Log de violaciones)
**Propósito**: Registrar violaciones de seguridad

```
POST http://jano_microservice:8002/api/violations
{
  "user_id": "...",
  "rule_id": "...",
  "violation_type": "RATE_LIMIT_EXCEEDED",
  "endpoint": "/api/data/stations",
  "ip_address": "203.0.113.42",
  "was_blocked": true
}

Respuesta:
{
  "violation_id": "...",
  "recorded_at": "2025-10-19T23:00:00Z"
}
```

### 5. **GET /api/cache-status** (Estado del caché)
**Propósito**: Monitoreo

```
GET http://jano_microservice:8002/api/cache-status

Respuesta:
{
  "cache": {
    "total_entries": 543,
    "memory_usage_mb": 12.5,
    "hit_rate": 0.87,
    "ttl_seconds": 600
  }
}
```

---

## 🏗️ ESTRUCTURA INTERNA DE JANO

```
jano_microservice/
├── src/
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── validate_request_dto.py
│   │   │   ├── validate_response_dto.py
│   │   │   └── rule_dto.py
│   │   └── use_cases/
│   │       ├── validate_token_use_case.py
│   │       ├── authorize_user_use_case.py
│   │       ├── evaluate_security_rules_use_case.py
│   │       ├── check_rate_limiting_use_case.py
│   │       └── log_violation_use_case.py
│   │
│   ├── core/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── user_entity.py
│   │   │   │   ├── token_entity.py
│   │   │   │   ├── rule_entity.py
│   │   │   │   └── violation_entity.py
│   │   │   └── exceptions/
│   │   │       └── jano_exceptions.py
│   │   │
│   │   ├── ports/
│   │   │   ├── token_validation_port.py
│   │   │   ├── user_repository_port.py
│   │   │   ├── rule_repository_port.py
│   │   │   └── cache_port.py
│   │   │
│   │   ├── services/
│   │   │   ├── jwt_validator_service.py (valida tokens)
│   │   │   ├── authorization_service.py (valida permisos)
│   │   │   ├── rate_limiter_service.py (rate limiting)
│   │   │   ├── cache_service.py (caché centralizado)
│   │   │   └── rule_evaluator_service.py (evalúa reglas)
│   │   │
│   │   └── utils/
│   │       ├── token_parser.py
│   │       ├── rule_matcher.py (regex para URL)
│   │       └── permission_checker.py
│   │
│   └── infrastructure/
│       ├── adapters/
│       │   ├── db/
│       │   │   ├── user_repository.py (lee de siata_auth.users)
│       │   │   ├── rule_repository.py (lee de jano_security_rules)
│       │   │   ├── violation_repository.py (escribe en jano_rule_violations)
│       │   │   └── token_repository.py (lee de auth_tokens)
│       │   │
│       │   ├── cache/
│       │   │   ├── redis_cache_adapter.py
│       │   │   └── in_memory_cache_adapter.py
│       │   │
│       │   └── controllers/
│       │       └── jano_controller.py
│       │
│       └── config/
│           ├── database_config.py
│           ├── cache_config.py
│           └── security_config.py
│
├── main.py
├── requirements.txt
└── Dockerfile
```

---

## 🔄 FLUJO ENTRE MICROSERVICIOS Y JANO

### Ejemplo: Petición a Users Microservice

```
CLIENTE
│
├─> POST /api/users/1
│   Headers: Authorization: Bearer eyJhbGc...
│
▼
┌─────────────────────────────┐
│  Users Microservice (8006)  │
│  (Recibe petición)          │
└──────────┬──────────────────┘
           │
           │ (ANTES de procesar)
           │ Llama a JANO
           ▼
┌─────────────────────────────┐
│  JANO Microservice (8002)   │
│  POST /api/validate         │
│  {                          │
│    "token": "eyJhbGc...",  │
│    "endpoint": "/api/users" │
│    "method": "POST",        │
│    "ip_address": "192..." │
│  }                          │
└──────────┬──────────────────┘
           │
           │ VALIDA:
           │ 1. Token JWT válido? ✅
           │ 2. Usuario autorizado? ✅
           │ 3. Rate limit ok? ✅
           │ 4. Otras reglas? ✅
           │
           │ Retorna:
           ▼
    {
      "authorized": true,
      "user": {...},
      "validation_stages": [...]
    }
           │
           │
           ▼
┌─────────────────────────────┐
│  Users Microservice (8006)  │
│  (Recibe respuesta de JANO) │
│  authorized === true?       │
└──────────┬──────────────────┘
           │
     ✅ YES │
           │ Continúa con lógica de negocio
           │ - Accede a BD
           │ - Procesa datos
           │ - Retorna respuesta
           ▼
    RESPUESTA AL CLIENTE
    {
      "user_id": 1,
      "name": "Juan",
      "email": "juan@..."
    }
```

---

## 💾 TABLAS QUE USA JANO

### Desde `siata_auth` schema:

1. **users** (lee)
   - Obtiene roles, grupos, permisos

2. **auth_tokens** (lee)
   - Valida que el token existe y no esté revocado

3. **jano_security_rules** (lee)
   - Obtiene reglas de seguridad configuradas

4. **jano_rule_violations** (escribe)
   - Registra violaciones cuando alguien intenta acceder sin permisos

5. **sessions** (lee)
   - Valida sesiones activas

6. **teams** (lee)
   - Obtiene grupos del usuario

7. **applications** (lee)
   - Valida aplicaciones autorizadas

8. **modules** (lee)
   - Valida acceso a módulos

9. **module_permissions** (lee)
   - Obtiene permisos específicos por rol/equipo

---

## ⚡ CACHÉ EN JANO (CRÍTICO)

```
┌────────────────────────────────────────────────┐
│         CACHÉ DE JANO (10 minutos TTL)         │
├────────────────────────────────────────────────┤
│                                                │
│ Clave: user:{user_id}                         │
│ Valor:                                        │
│ {                                             │
│   "user_id": "...",                          │
│   "username": "juan",                        │
│   "role": "user_siata",                      │
│   "groups": ["hidrologia", "dev"],           │
│   "permissions": ["read", "write"],          │
│   "cached_at": 2025-10-19T23:00:00,          │
│   "expires_at": 2025-10-19T23:10:00          │
│ }                                             │
│                                               │
│ Clave: rule:{rule_id}                         │
│ Valor: {...regla configurada...}             │
│                                               │
│ Clave: rate_limit:{ip}                        │
│ Valor: {requests: 95, window_end: ...}       │
│                                               │
│ Clave: endpoint:{endpoint}:{method}          │
│ Valor: {matched_rule_id: "...", ...}         │
│                                               │
└────────────────────────────────────────────────┘

IMPORTANTE:
- Si cambias un usuario de grupo → espera 10 min
- Si cambias una regla → espera 10 min
- Si cambias permisos → espera 10 min
- Por eso Caroline menciona el cache en su explicación
```

---

## 🔌 CÓMO LOS OTROS MICROSERVICIOS INTEGRAN JANO

### En cada microservicio (Auth, Users, OTP, Management):

```python
# En el controlador o middleware

from requests import post

class AuthMiddleware:
    async def __call__(self, request):
        # 1. Obtener token del header
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        # 2. LLAMAR A JANO para validar
        response = post(
            "http://jano_microservice:8002/api/validate",
            json={
                "token": token,
                "endpoint": request.url.path,
                "method": request.method,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "request_data": request.body
            },
            timeout=5
        )
        
        # 3. Evaluar respuesta
        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        
        validation_result = response.json()
        
        # 4. Si está autorizado, continuar
        if validation_result["authorized"]:
            # Pasar información del usuario al request
            request.state.user = validation_result["user"]
            request.state.permissions = validation_result["user"]["permissions"]
            return await request.next()
        else:
            return JSONResponse(
                status_code=403,
                content={"error": "Unauthorized"}
            )
```

---

## 📈 VENTAJAS DE JANO CENTRALIZADO

| Aspecto | Actual (Distribuido) | Con JANO (Centralizado) |
|--------|----------------------|------------------------|
| **Consistencia** | ❌ Cada MS valida diferente | ✅ Una única fuente de verdad |
| **Mantenimiento** | ❌ Actualizar reglas en N MS | ✅ Cambiar en 1 lugar (JANO) |
| **Caché** | ❌ Caché duplicado | ✅ Caché centralizado (10min) |
| **Rate limiting** | ❌ Por MS | ✅ Global por IP |
| **Auditoría** | ❌ Dispersa | ✅ Centralizada en jano_rule_violations |
| **Performance** | ❌ Más lento (validaciones distribuidas) | ✅ Rápido (caché compartido) |
| **Escalabilidad** | ❌ Difícil agregar nuevas reglas | ✅ Fácil (solo en JANO) |
| **Seguridad** | ❌ Vulnerable a bypasses | ✅ Más seguro (punto único) |

---

## 🚀 IMPLEMENTACIÓN PASO A PASO

### Paso 1: Crear `configuration_rules_microservice`
```
Hacer un nuevo microservicio que sea JANO
Puerto: 8002
```

### Paso 2: En cada MS (Auth, Users, OTP, Management)
```python
# En middleware o en el inicio de cada endpoint
1. Extraer token del header
2. Llamar a JANO con: token, endpoint, método, IP
3. Si JANO retorna authorized=true → continuar
4. Si no → retornar error 401/403/429
```

### Paso 3: Configurar en docker-compose.yml
```yaml
jano_microservice:
  build: ./configuration_rules_microservice
  ports:
    - "8002:8002"
  depends_on:
    - postgres
    - auth_microservice
  environment:
    - DATABASE_URL=postgresql://...
    - CACHE_TYPE=redis  # o in-memory
    - JWT_PUBLIC_KEY=...
```

### Paso 4: Actualizar reglas en BD
```sql
-- Insertar en jano_security_rules
INSERT INTO jano_security_rules (...) VALUES (...);

-- Insertar en module_permissions
INSERT INTO module_permissions (...) VALUES (...);
```

---

## 📊 DIAGRAMA DE CAPAS

```
┌─────────────────────────────────────────────┐
│         CLIENTE (Frontend/App)              │
└────────────────────┬────────────────────────┘
                     │
                     │ HTTP Request
                     │ + JWT Token
                     ▼
┌─────────────────────────────────────────────┐
│  Auth MS │ Users MS │ OTP MS │ Mgmt MS     │
│  (8001)  │  (8006)  │ (8003) │   (8005)    │
│                                             │
│  Cada MS envía petición a JANO              │
│  (Antes de procesar)                        │
└────────────┬────────────┬────────┬──────────┘
             │            │        │
             │ Valida     │ Valida │ Valida
             │            │        │
             └────┬───────┴────┬───┘
                  │            │
                  ▼            ▼
        ┌─────────────────────────────┐
        │   JANO Microservice (8002)  │
        │   - JWT validation          │
        │   - Authorization           │
        │   - Rate limiting           │
        │   - Auditoría               │
        │   - Caché (10 min)          │
        └────────────┬────────────────┘
                     │
                     │ Lee/Escribe
                     ▼
        ┌─────────────────────────────┐
        │     PostgreSQL (siata_auth)  │
        │                             │
        │  - users                    │
        │  - auth_tokens              │
        │  - jano_security_rules      │
        │  - jano_rule_violations     │
        │  - sessions                 │
        │  - teams                    │
        │  - module_permissions       │
        │  - applications             │
        │  - modules                  │
        └─────────────────────────────┘
```

---

## 🎯 CONFIGURACIÓN DE REGLAS EN JANO

### Ejemplo de Regla: Rate Limiting
```sql
INSERT INTO jano_security_rules (
  rule_name,
  rule_type,
  rule_code,
  description,
  rule_config,
  severity,
  priority,
  is_active,
  applies_to_roles
) VALUES (
  'Rate limiting de API',
  'rate_limit',
  'RATE_LIMIT_001',
  'Máximo 100 requests por minuto por IP',
  '{
    "requests_per_minute": 100,
    "burst_size": 150,
    "block_duration_minutes": 15
  }',
  'high',
  120,
  true,
  NULL  -- Aplica a todos los roles
);
```

### Ejemplo de Regla: Authorization por Endpoint
```sql
INSERT INTO jano_security_rules (
  rule_name,
  rule_type,
  rule_code,
  description,
  rule_config,
  severity,
  applies_to_endpoints
) VALUES (
  'Acceso a /api/tasks',
  'authorization',
  'AUTH_ENDPOINT_001',
  'Solo root y user_siata pueden acceder a /api/tasks',
  '{
    "endpoint": "/api/tasks",
    "method": "GET",
    "allowed_roles": ["root", "user_siata"],
    "required_groups": []
  }',
  'high',
  NULL,
  '{/api/tasks*}'
);
```

---

## 🔐 FLUJO COMPLETO DETALLADO

```
CLIENTE envía:
GET /api/users/1
Authorization: Bearer eyJhbGc...
IP: 192.168.1.100

│
▼
USERS MICROSERVICE (8006)
├─> Intercepta petición
├─> Extrae token: eyJhbGc...
├─> Extrae endpoint: /api/users/1
├─> Extrae IP: 192.168.1.100
├─> LLAMA A JANO:
│   POST http://jano_microservice:8002/api/validate
│   {
│     "token": "eyJhbGc...",
│     "endpoint": "/api/users/1",
│     "method": "GET",
│     "ip_address": "192.168.1.100",
│     "user_agent": "Mozilla/..."
│   }
│
▼
JANO MICROSERVICE (8002)
├─> ETAPA 1: VALIDA TOKEN
│   ├─> Decodifica JWT
│   ├─> Verifica firma contra public key
│   ├─> Comprueba exp (no esté expirado)
│   ├─> Consulta BD: ¿está revocado?
│   └─> ✅ PASS
│
├─> ETAPA 2: VALIDA AUTORIZACIÓN
│   ├─> Consulta jano_security_rules
│   ├─> Busca regla que mapee: /api/users/* + GET
│   ├─> Obtiene user_id del token
│   ├─> Consulta usuarios: role y grupos
│   ├─> Valida: ¿rol/grupos coinciden con regla?
│   └─> ✅ PASS
│
├─> ETAPA 3: EVALÚA REGLAS ADICIONALES
│   ├─> Rate limit:
│   │   ├─> Consulta caché: rate_limit:192.168.1.100
│   │   ├─> Si no existe → crea: {"requests": 1, "window_end": T+60s}
│   │   ├─> Si existe → incrementa: {"requests": 96, "window_end": T+30s}
│   │   ├─> ¿96 < 100? → ✅ OK
│   │
│   ├─> IP whitelist: (si está configurada)
│   │   ├─> ¿192.168.1.100 en whitelist?
│   │   └─> ✅ OK
│   │
│   ├─> MFA required:
│   │   ├─> ¿Usuario es root?
│   │   ├─> ¿Tiene MFA habilitado?
│   │   └─> ✅ OK
│   │
│   └─> Otras reglas...
│
├─> ✅ RETORNA AL USERS MS:
│   {
│     "authorized": true,
│     "user": {
│       "user_id": "78de8e0b-...",
│       "username": "juan.perez",
│       "email": "juan.perez@siata.gov.co",
│       "role": "user_siata",
│       "groups": ["hidrologia"],
│       "permissions": ["read", "write"]
│     },
│     "validation_stages": [
│       {"stage": "authentication", "result": "PASS"},
│       {"stage": "authorization", "result": "PASS"},
│       {"stage": "rules", "result": "PASS"}
│     ]
│   }
│
▼
USERS MICROSERVICE (8006) - Continúa
├─> Recibe respuesta de JANO
├─> ¿authorized === true? → ✅ YES
├─> Procede con lógica de negocio
├─> Consulta BD: SELECT * FROM users WHERE user_id = 1
├─> Retorna datos al cliente
│
▼
CLIENTE recibe:
{
  "user_id": 1,
  "name": "Juan Pérez",
  "email": "juan.perez@siata.gov.co",
  "role": "user_siata"
}
```

---

## 🎓 RESUMEN EN PUNTOS CLAVE

✅ **JANO es un microservicio independiente** que:
1. Valida JWT tokens
2. Verifica autorización (roles, permisos, grupos)
3. Evalúa reglas de seguridad
4. Implementa rate limiting
5. Registra violaciones
6. Cachea decisiones (10 minutos)

✅ **Todos los MS consultan a JANO** antes de procesar:
- Auth MS → Consulta JANO
- Users MS → Consulta JANO
- OTP MS → Consulta JANO
- Management MS → Consulta JANO

✅ **Las reglas se configuran en 1 solo lugar**: Base de datos

✅ **El caché es compartido**: 10 minutos TTL

✅ **Es transversal y reutilizable**: Se aplica a todo

---

**Esto es exactamente lo que Carolina explicaba en su presentación** 🎯

Se puede implementar como `configuration_rules_microservice` que actúe como **JANO centralizado**.
