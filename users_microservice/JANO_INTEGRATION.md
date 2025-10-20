# Users Microservice - JANO Integration

**Status**: ✅ COMPLETED  
**Date**: 2024  
**Version**: 2.1.0  

## Overview

El microservicio de usuarios ha sido actualizado para integrar validación de políticas de seguridad con JANO (Configuration Rules Microservice). Todas las contraseñas y nombres de usuario son validados contra las políticas de seguridad antes de crear usuarios.

## Cambios Implementados

### 📦 Archivos Creados (1)

#### 1. JANO Client
- `src/infrastructure/adapters/jano_client.py` (~250 líneas)
  - **JANOClient**: Cliente HTTP async para comunicación con JANO
  - **JANOValidationError**: Excepción personalizada con violaciones
  - **Métodos**:
    * `validate_password()` - Valida contraseña contra políticas
    * `validate_username()` - Valida nombre de usuario
    * `health_check()` - Verifica disponibilidad de JANO
  - **Global instance**: `jano_client` inicializado en lifespan

### 🔧 Archivos Modificados (4)

#### 1. Create User Use Case
**Archivo**: `src/application/use_cases/create_user_use_case.py`

**Cambios**:
- ✅ Agregado parámetro `jano_client: JANOClient` en constructor
- ✅ Validación de username con JANO (paso 1)
- ✅ Validación de password con JANO (paso 2)
- ✅ Manejo de `JANOValidationError` con violaciones detalladas

**Flujo actualizado**:
```python
1. Validate username → JANO
2. Validate password → JANO (with username context)
3. Check user exists → Database
4. Hash password → BCrypt
5. Create user → Database
```

#### 2. Dependencies
**Archivo**: `src/infrastructure/config/dependencies.py`

**Cambios**:
- ✅ Import de `get_jano_client` y `JANOClient`
- ✅ Actualizado `get_create_user_use_case()`:
  ```python
  jano_client = get_jano_client()
  return CreateUserUseCase(user_repository, password_service, jano_client)
  ```

#### 3. User Controller
**Archivo**: `src/infrastructure/adapters/controllers/user_controller.py`

**Cambios**:
- ✅ Import de `JANOValidationError`
- ✅ Manejo de excepciones en `create_user()`:
  ```python
  except JANOValidationError as e:
      raise HTTPException(
          status_code=400,
          detail={
              "message": e.message,
              "violations": e.violations
          }
      )
  ```

#### 4. Main Application
**Archivo**: `main.py`

**Cambios**:
- ✅ Import de `jano_client_module` y `JANOClient`
- ✅ Inicialización de JANO client en lifespan:
  ```python
  jano_service_url = os.getenv("JANO_SERVICE_URL", "http://jano_microservice:8005")
  jano_client_module.jano_client = JANOClient(
      base_url=jano_service_url,
      timeout=5.0,
      application_id="users_service"
  )
  ```
- ✅ Health check de JANO en startup
- ✅ Cierre de cliente en shutdown

#### 5. Docker Compose
**Archivo**: `docker-compose.yml`

**Cambios**:
- ✅ Agregada variable de entorno `JANO_SERVICE_URL`
- ✅ Agregada dependencia de `jano_microservice`

### 📝 Archivos de Testing (1)

- `test/manual_test_users_jano.py` (~330 líneas)
  - 6 tests de integración
  - Autenticación como ROOT
  - Validación de passwords JANO-compliant
  - Validación de rechazo por políticas
  - Test de duplicados

## Validaciones JANO

### Password Validation

El cliente JANO valida contraseñas contra las siguientes políticas:

1. **Longitud mínima**: 8 caracteres (configurable)
2. **Complejidad requerida**:
   - Al menos 1 mayúscula
   - Al menos 1 minúscula
   - Al menos 1 número
   - Al menos 1 carácter especial
3. **Patrones prohibidos**:
   - No puede contener el username
   - No puede ser una contraseña común
4. **Historial**: No puede reutilizar contraseñas recientes

### Username Validation

El cliente JANO valida usernames contra:

1. **Longitud**: 3-50 caracteres (configurable)
2. **Caracteres permitidos**: Alfanuméricos y guion bajo
3. **Patrones**: No puede contener palabras reservadas

## API Changes

### POST /api/users (Create User)

**Request** (sin cambios):
```json
{
  "username": "newuser",
  "email": "newuser@siata.gov.co",
  "password": "SecureP@ss123",
  "name": "New",
  "last_name": "User",
  "role": "USER",
  "team_name": "Development"
}
```

**Response 201 - Success** (sin cambios):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "newuser",
  "email": "newuser@siata.gov.co"
}
```

**Response 400 - JANO Validation Failed** (NUEVO):
```json
{
  "detail": {
    "message": "Password does not meet security requirements: ...",
    "violations": [
      "Password must be at least 8 characters long",
      "Password must contain at least one uppercase letter",
      "Password must contain at least one special character"
    ]
  }
}
```

**Response 409 - Duplicate User**:
```json
{
  "detail": "Username or email already exists"
}
```

## Configuration

### Environment Variables

```yaml
# docker-compose.yml - users_microservice
environment:
  # Database
  DATABASE_URL: postgresql+asyncpg://admin:password@postgres:5432/auth_login_services
  
  # Services
  AUTH_SERVICE_URL: http://auth_microservice:8001
  JANO_SERVICE_URL: http://jano_microservice:8005  # NEW
  
  # Service
  SERVICE_PORT: 8006

depends_on:
  postgres:
    condition: service_healthy
  jano_microservice:  # NEW
    condition: service_started
```

### JANO Client Configuration

```python
JANOClient(
    base_url="http://jano_microservice:8005",
    timeout=5.0,  # 5 seconds
    application_id="users_service"  # Identifies this service in JANO
)
```

## Error Handling

### JANO Service Unavailable

Si JANO no está disponible durante el startup:
- ⚠️  Warning logged
- ✅ Service continúa arrancando
- ❌ Creación de usuarios fallará con error de timeout

### JANO Validation Timeout

```python
try:
    is_valid, violations = await jano_client.validate_password(...)
except JANOValidationError as e:
    # e.message: "Password validation service timeout"
    # e.violations: ["Service temporarily unavailable"]
```

### JANO Communication Error

```python
try:
    is_valid, violations = await jano_client.validate_password(...)
except JANOValidationError as e:
    # e.message: "Unable to validate password"
    # e.violations: ["Service communication error"]
```

## Testing

### Manual Tests

```bash
# Asegurar que los servicios estén corriendo
docker-compose up -d postgres jano_microservice auth_microservice users_microservice

# Ejecutar tests
cd users_microservice
python test/manual_test_users_jano.py
```

### Expected Test Results

1. ✅ Health Check
2. ✅ Create User with Valid Password (JANO compliant)
3. ✅ Get User by ID
4. ✅ Weak Password Rejection (JANO validation)
5. ✅ Invalid Username Rejection (JANO validation)
6. ✅ Duplicate User Rejection

### Test Scenarios

#### Scenario 1: Valid Password
```python
{
  "username": "testuser001",
  "password": "SecureP@ss123",  # ✅ Meets all requirements
  ...
}
# Expected: 201 Created
```

#### Scenario 2: Weak Password
```python
{
  "username": "weakuser001",
  "password": "weak",  # ❌ Too short, no uppercase, no special char
  ...
}
# Expected: 400 Bad Request with JANO violations
```

#### Scenario 3: Invalid Username
```python
{
  "username": "ab",  # ❌ Too short (< 3 chars)
  "password": "ValidP@ss123",
  ...
}
# Expected: 400 Bad Request with JANO violations
```

## Security Benefits

### Before JANO Integration
- ❌ No password policy enforcement
- ❌ Weak passwords accepted
- ❌ No username validation
- ❌ Inconsistent security across services

### After JANO Integration
- ✅ Centralized password policies
- ✅ Strong passwords enforced
- ✅ Username validation
- ✅ Consistent security rules
- ✅ Configurable policies
- ✅ Audit trail via JANO

## BCrypt Password Hashing

El microservicio utiliza BCrypt para hashing de contraseñas:

```python
class BcryptPasswordService(PasswordServicePort):
    def __init__(self, rounds: int = 12):
        self.rounds = rounds  # Cost factor
    
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
```

**Características**:
- ✅ BCrypt con rounds=12 (configurable)
- ✅ Salt automático por hash
- ✅ Resistente a ataques de fuerza bruta
- ✅ Timing attack resistant

## ROOT-Only Access

Todas las operaciones de usuarios requieren rol ROOT:

```python
@router.post(
    "",
    dependencies=[Depends(require_root_role)],  # ROOT only
)
async def create_user(...):
    ...
```

**Endpoints Protegidos**:
- ✅ `POST /api/users` - Create user
- ✅ `GET /api/users/{user_id}` - Get user
- ✅ `PUT /api/users/{user_id}` - Update user
- ✅ `PATCH /api/users/{user_id}/disable` - Disable user
- ✅ `PATCH /api/users/{user_id}/enable` - Enable user

**Endpoints Internos** (sin autenticación):
- `/internal/users/validate-credentials` - Para auth_microservice
- `/internal/users/validate-credentials-email` - Para auth_microservice
- `/internal/users/{user_id}` - Para auth_microservice

## Integration Flow

```
┌─────────────────┐
│  ROOT Client    │
│ (with JWT)      │
└────────┬────────┘
         │
         │ POST /api/users
         │ {username, password, ...}
         ▼
┌─────────────────────────────┐
│  Users Microservice         │
│                             │
│  1. Auth Middleware         │
│     └─> Verify ROOT role    │
│                             │
│  2. Create User Use Case    │
│     ├─> Validate username ──┼──┐
│     │                       │  │
│     ├─> Validate password ──┼──┤
│     │                       │  │
│     ├─> Check duplicates    │  │
│     ├─> Hash password       │  │
│     └─> Save to DB          │  │
└─────────────────────────────┘  │
                                 │
         ┌───────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  JANO Microservice          │
│                             │
│  - Validate username        │
│  - Validate password        │
│  - Check policies           │
│  - Return violations        │
└─────────────────────────────┘
```

## Monitoring & Logging

El servicio registra:

```python
# Startup
logger.info(f"JANO client initialized with URL: {jano_service_url}")
logger.info("✅ JANO service is available")

# Validation
logger.debug(f"Validating username with JANO: {username}")
logger.debug(f"Validating password with JANO for user: {username}")

# Success
logger.info(f"User created successfully: {username} (id={user_id}) [JANO validated]")

# Failures
logger.warning(f"Username validation failed: {username}. Violations: {violations}")
logger.warning(f"Password validation failed: {username}. Violations: {violations}")

# Errors
logger.error(f"JANO password validation timeout after {timeout}s")
logger.error(f"JANO password validation HTTP error: {error}")
```

## Próximos Pasos

- [ ] Implementar cambio de contraseña con validación JANO
- [ ] Validar contraseñas en update de usuario
- [ ] Agregar rate limiting para creación de usuarios
- [ ] Métricas de validaciones JANO (Prometheus)
- [ ] Dashboard de políticas de seguridad
- [ ] Tests de integración automatizados

## Referencias

- **JANO Client**: `src/infrastructure/adapters/jano_client.py`
- **Create User Use Case**: `src/application/use_cases/create_user_use_case.py`
- **User Controller**: `src/infrastructure/adapters/controllers/user_controller.py`
- **Manual Tests**: `test/manual_test_users_jano.py`
- **Password Service**: `src/infrastructure/adapters/services/password_service.py`

---

**Integration Status**: ✅ COMPLETED  
**Next Task**: Task 7 - Implementar management_application_microservice
