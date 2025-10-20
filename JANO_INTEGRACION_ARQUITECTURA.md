# 🔗 JANO EN TU ARQUITECTURA - MAPEO ESPECÍFICO

**Objetivo**: Mostrar EXACTAMENTE cómo JANO se integraría en tu sistema actual

---

## 📦 TU ARQUITECTURA ACTUAL

```
docker-compose.yml
├── postgres (5432)
├── auth_microservice (8001)
├── users_microservice (8006)
├── otp_microservice (8003)
└── configuration_rules_microservice (8004) ← ES JANO
```

---

## 🎯 MAPEO: configuration_rules_microservice → JANO

### LO QUE TIENES:
```
configuration_rules_microservice/
├── main.py
```

### LO QUE DEBERÍA HACER (Convertirse en JANO):
```
configuration_rules_microservice/ (Renombrarlo a JANO o dejar igual)
├── src/
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── validate_token_uc.py ................ NUEVO
│   │   │   ├── authorize_user_uc.py ................ NUEVO
│   │   │   ├── evaluate_security_rules_uc.py ....... NUEVO
│   │   │   ├── check_rate_limiting_uc.py ........... NUEVO
│   │   │   └── log_violation_uc.py ................. NUEVO
│   │   │
│   │   └── dtos/
│   │       ├── validate_request_dto.py ............. NUEVO
│   │       └── validate_response_dto.py ............ NUEVO
│   │
│   ├── core/
│   │   ├── services/
│   │   │   ├── jwt_validator.py .................... NUEVO
│   │   │   ├── authorization_service.py ............ NUEVO
│   │   │   ├── rate_limiter.py ..................... NUEVO
│   │   │   └── cache_service.py .................... NUEVO
│   │   │
│   │   └── ports/
│   │       ├── rule_repository_port.py ............. NUEVO
│   │       └── cache_port.py ....................... NUEVO
│   │
│   └── infrastructure/
│       ├── adapters/
│       │   ├── db/
│       │   │   ├── rule_repository.py .............. NUEVO
│       │   │   ├── user_repository.py .............. NUEVO
│       │   │   └── violation_repository.py ......... NUEVO
│       │   │
│       │   ├── cache/
│       │   │   └── redis_cache.py .................. NUEVO
│       │   │
│       │   └── controllers/
│       │       └── jano_controller.py .............. NUEVO
│       │
│       └── config/
│           └── database_config.py .................. NUEVO
│
├── main.py (Convertir a JANO endpoint)
├── requirements.txt (Agregar librerías)
└── Dockerfile

```

---

## 🔄 CÓMO FLUIRÍA EN TU SISTEMA

### Petición a Users Microservice:

```
CLIENTE
│
├─> POST /api/users
│   Authorization: Bearer eyJhbGc...
│
▼
┌──────────────────────────────────┐
│   Users Microservice (8006)      │
│   main.py / controllers/         │
│   (Recibe petición)              │
│                                  │
│   1. Valida que token existe     │
│   2. Extrae datos de petición    │
│   3. LLAMA A JANO                │
└────────┬─────────────────────────┘
         │
         │ requests.post(
         │   'http://configuration_rules_microservice:8004/api/validate',
         │   json={...}
         │ )
         │
         ▼
┌──────────────────────────────────────────────────────┐
│   configuration_rules_microservice (8004) - JANO     │
│   main.py / controllers/jano_controller.py           │
│                                                      │
│   @app.post('/api/validate')                         │
│   async def validate(request: ValidateRequestDTO):  │
│       # 1. Valida JWT                               │
│       # 2. Autoriza usuario                         │
│       # 3. Evalúa reglas                            │
│       # 4. Retorna autorización                     │
│                                                      │
│   Database calls:                                    │
│   - SELECT FROM siata_auth.users                    │
│   - SELECT FROM siata_auth.auth_tokens              │
│   - SELECT FROM siata_auth.jano_security_rules      │
│   - SELECT FROM siata_auth.module_permissions       │
│   - INSERT INTO siata_auth.jano_rule_violations     │
└────────┬──────────────────────────────────────────────┘
         │
         │ Retorna:
         │ {
         │   "authorized": true,
         │   "user": {...},
         │   "validation_stages": [...]
         │ }
         │
         ▼
┌──────────────────────────────────┐
│   Users Microservice (8006)      │
│                                  │
│   Recibe respuesta de JANO       │
│   ¿authorized === true?          │
│   ✅ YES → Procede               │
│   ❌ NO → Retorna error          │
└──────────────────────────────────┘
```

---

## 🎯 VENTAJAS ESPECÍFICAS PARA TU ARQUITECTURA

### Antes (Sin JANO centralizado):
```
Auth MS → Valida tokens (lógica duplicada)
Users MS → Valida roles (lógica duplicada)
OTP MS → Valida rate limit (lógica duplicada)
Management MS → ¿Qué valida? (Inconsistencia)
```

### Después (Con JANO):
```
Todos los MS → Consultan JANO (Una sola fuente de verdad)
JANO → Valida tokens, roles, rate limit, reglas
BD → Centraliza todas las reglas en jano_security_rules
```

---

---

## 📊 DIAGRAMA FINAL EN TU ARQUITECTURA

```
┌────────────────────────────────────────────────────────────┐
│                  docker-compose.yml                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PostgreSQL (5432)                                  │   │
│  │  ├── siata_auth schema                              │   │
│  │  ├── users, teams, auth_tokens                      │   │
│  │  └── jano_security_rules, jano_rule_violations      │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ▲  ▲  ▲  ▲  ▲                        │
│                       │  │  │  │  │                        │
│     ┌─────────────────┘  │  │  │  └──────────┐             │
│     │                    │  │  │             │             │
│  ┌──┴────────┐  ┌───────┴──┴──┴──────┐  ┌──┴─────────┐     │
│  │  Auth MS  │  │  Users MS   │      │  │  JANO MS  │      │
│  │  (8001)   │  │  (8006)     │      │  │  (8004)   │      │
│  └─────┬─────┘  └──────┬──────┘      │  └─────┬─────┘      │
│        │                │              │        │          │
│        │ Genera tokens  │ Valida       │ Centro            │
│        │                │ peticiones   │ de                │
│        │                ├─────────────→│ Validación        │
│        │                                                   │
│  ┌─────┴─────┐                                             │
│  │  OTP MS   │                                             │
│  │  (8003)   │                                             │
│  └───────────┘                                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```
