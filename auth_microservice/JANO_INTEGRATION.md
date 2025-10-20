# 🔄 Auth Microservice - JANO Integration

Este documento detalla la integración del **JANO Security Framework** en el `auth_microservice` para validaciones de seguridad centralizadas.

## 📋 Cambios Realizados

### 1. ✅ Nuevo Cliente JANO

**Archivo**: `src/infrastructure/adapters/services/jano_client.py`

Cliente HTTP para comunicarse con JANO microservice y validar:
- ✅ **Políticas de contraseñas** (complejidad, longitud, caracteres)
- ✅ **Rate limiting** (límite de requests por IP)
- ✅ **Validación de sesiones** (timeout de inactividad/absoluto)
- ✅ **Requisitos MFA** (basado en rol)

```python
# Métodos implementados:
- validate_password(password: str) -> Dict
- validate_request(user_id, role, endpoint, method, ip_address, user_agent) -> Dict
- validate_session(user_id, role, session_created_at, last_activity_at) -> Dict
- validate_mfa_requirement(user_id, role) -> Dict
```

### 2. ✅ Nuevo Port Interface

**Archivo**: `src/domain/ports/jano_service_port.py`

Port abstracto para JANO siguiendo arquitectura hexagonal:
```python
class JANOServicePort(ABC):
    @abstractmethod
    async def validate_password(password: str) -> Dict[str, Any]
    
    @abstractmethod
    async def validate_request(...) -> Dict[str, Any]
    
    @abstractmethod
    async def validate_session(...) -> Dict[str, Any]
    
    @abstractmethod
    async def validate_mfa_requirement(...) -> Dict[str, Any]
```

### 3. ✅ Nuevas Excepciones

**Archivo**: `src/domain/exceptions/auth_exceptions.py`

Nuevas excepciones para manejo de errores de JANO:

```python
# AUTH_103 - JANO Service Unavailable
class JANOServiceUnavailableException(AuthException):
    status_code = 503
    message = "JANO service unavailable"

# AUTH_901 - Password Policy Violation
class PasswordPolicyViolationException(AuthException):
    status_code = 400
    message = "Password policy violation"
    violations: list  # Lista de violaciones específicas

# AUTH_901 - Rate Limit Exceeded
class RateLimitExceededException(AuthException):
    status_code = 429
    message = "Rate limit exceeded"
```

### 4. ✅ Integración en Login Flow

**Archivo**: `src/application/use_cases/login_init_use_case.py`

El use case de login ahora incluye validación de JANO:

**Flujo Actualizado**:
```
1. Cliente → POST /auth/login { email, password }
2. ⭐ NUEVO: Validar rate limiting via JANO
   - Endpoint: POST /api/validate/request
   - Bloquea si excede límite (default: 5 intentos)
3. Validar credenciales via users_microservice
4. Generar OTP via otp_microservice
5. Retornar { otp_id, message, masked_email }
```

**Cambios en el código**:
```python
class LoginInitUseCase:
    def __init__(
        self,
        users_service: UsersServicePort,
        otp_service: OTPServicePort,
        jano_service: JANOServicePort,  # ⭐ NUEVO
    ):
        ...
    
    async def execute(
        self,
        request: LoginRequest,
        ip_address: str = "0.0.0.0",     # ⭐ NUEVO
        user_agent: str = "Unknown",      # ⭐ NUEVO
    ) -> LoginInitResponse:
        # ⭐ NUEVO: Rate limiting check
        rate_limit_result = await self.jano_service.validate_request(
            user_id="anonymous",
            role="anonymous",
            endpoint="/auth/login",
            method="POST",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        if rate_limit_result.get("should_block", False):
            raise RateLimitExceededException(...)
        
        # Resto del flujo...
```

### 5. ✅ Actualización de Controller

**Archivo**: `src/infrastructure/adapters/controllers/auth_controller.py`

El endpoint ahora extrae información del request HTTP:

```python
@router.post("/login")
async def login(
    request: LoginRequest,
    http_request: Request,  # ⭐ NUEVO: FastAPI Request
) -> LoginInitResponse:
    # ⭐ NUEVO: Extraer info del cliente
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)
    
    # ⭐ NUEVO: Crear cliente JANO
    jano_service = JANOServiceClient()
    
    use_case = LoginInitUseCase(
        users_service=UsersServiceClient(),
        otp_service=OTPServiceClient(),
        jano_service=jano_service,  # ⭐ NUEVO
    )
    
    result = await use_case.execute(
        request=request,
        ip_address=ip_address,  # ⭐ NUEVO
        user_agent=user_agent,  # ⭐ NUEVO
    )
    
    return result
```

### 6. ✅ Configuración Actualizada

**Archivo**: `src/infrastructure/config/settings.py`

Nueva configuración para JANO:

```python
class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # ⭐ NUEVO: JANO Configuration
    JANO_SERVICE_URL: str = Field(
        default="http://jano_microservice:8005",
        description="JANO security microservice URL"
    )
    JANO_SERVICE_TIMEOUT: int = Field(
        default=10,
        description="JANO service timeout in seconds"
    )
```

### 7. ✅ Docker Compose Actualizado

**Archivo**: `docker-compose.yml`

Auth microservice ahora depende de JANO:

```yaml
auth_microservice:
  environment:
    JANO_SERVICE_URL: http://jano_microservice:8005  # ⭐ NUEVO
    DATABASE_URL: postgresql+asyncpg://auth_service:auth_service_password@postgres:5432/auth_login_services
  depends_on:
    postgres:
      condition: service_healthy
    users_microservice:
      condition: service_started
    otp_microservice:
      condition: service_started
    jano_microservice:  # ⭐ NUEVO
      condition: service_started
```

## 🔄 Flujo Completo de Login con JANO

```mermaid
sequenceDiagram
    participant Client
    participant Auth as Auth Service
    participant JANO as JANO Service
    participant Users as Users Service
    participant OTP as OTP Service
    
    Client->>Auth: POST /auth/login { email, password }
    Auth->>JANO: POST /api/validate/request (rate limit check)
    
    alt Rate limit exceeded
        JANO-->>Auth: { should_block: true, violations: [...] }
        Auth-->>Client: 429 Rate Limit Exceeded
    else Rate limit OK
        JANO-->>Auth: { should_block: false }
        Auth->>Users: POST /api/users/validate-credentials
        
        alt Invalid credentials
            Users-->>Auth: 401 Invalid Credentials
            Auth-->>Client: 401 Invalid Credentials
        else Valid credentials
            Users-->>Auth: 200 { id, email, role, ... }
            Auth->>OTP: POST /api/otp/generate { user_id, email }
            OTP-->>Auth: 200 { otp_id, message }
            Auth-->>Client: 200 { otp_id, masked_email, ... }
        end
    end
```

## 🧪 Testing

### Test Manual con Curl

```bash
# 1. Login normal (dentro del rate limit)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@siata.gov.co",
    "password": "Admin123!"
  }'

# Respuesta esperada: 200 OK con OTP enviado

# 2. Exceder rate limit (5+ intentos en 1 minuto)
for i in {1..6}; do
  curl -X POST http://localhost:8001/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{ "email": "test@test.com", "password": "wrong" }'
done

# Respuesta esperada en intento 6: 429 Rate Limit Exceeded
```

### Test de Password Validation

```bash
# Validar contraseña directamente con JANO
curl -X POST http://localhost:8005/api/validate/password \
  -H "Content-Type: application/json" \
  -d '{ "password": "weak" }'

# Respuesta esperada:
# {
#   "is_valid": false,
#   "violated_rules": [
#     {
#       "rule_name": "PASSWORD_POLICY_001",
#       "message": "Password must be at least 8 characters",
#       "severity": "critical"
#     },
#     {
#       "rule_name": "PASSWORD_POLICY_001",
#       "message": "Password must contain uppercase letters",
#       "severity": "critical"
#     }
#   ]
# }
```

## 🚨 Manejo de Errores

### Graceful Degradation

Si JANO no está disponible:
- ✅ El login **continúa funcionando** (degradación elegante)
- ⚠️ Se registra warning en logs
- ❌ No se bloquea el rate limiting

```python
try:
    rate_limit_result = await self.jano_service.validate_request(...)
except Exception as e:
    logger.warning(f"JANO rate limit check failed: {e}. Continuing without rate limit validation.")
    # Continuar con el login
```

### Excepciones Manejadas

| Exception | Status Code | Descripción |
|-----------|-------------|-------------|
| `RateLimitExceededException` | 429 | Demasiados intentos de login |
| `PasswordPolicyViolationException` | 400 | Contraseña no cumple políticas |
| `JANOServiceUnavailableException` | 503 | JANO no disponible |

## 📊 Métricas y Logs

### Logs Generados

```
INFO - Login init attempt for email: admin@siata.gov.co
DEBUG - Rate limit check for IP 192.168.1.100: OK
INFO - Credentials valid for user: 123e4567-e89b-12d3-a456-426614174000
INFO - OTP sent to email for user: 123e4567-e89b-12d3-a456-426614174000
```

### Logs de Rate Limit Excedido

```
WARNING - Rate limit exceeded for IP 192.168.1.100: [{'rule_name': 'AUTH_RATE_LIMIT_001', ...}]
```

## 🔐 Reglas JANO Aplicadas

El auth_microservice se beneficia de estas reglas pre-configuradas en JANO:

1. **AUTH_RATE_LIMIT_001**: Máximo 5 intentos de login por minuto por IP
2. **PASSWORD_POLICY_001**: Contraseña mínimo 8 caracteres, mayúsculas, minúsculas, números, especiales
3. **MFA_POLICY_001**: MFA obligatorio para rol `root`
4. **SESSION_POLICY_001**: Sesiones expiran a los 30 minutos de inactividad

## 🎯 Próximos Pasos

- [ ] Integrar validación de sesión en token refresh
- [ ] Validar password policy en registro de usuarios
- [ ] Agregar JANO validation en todos los endpoints protegidos
- [ ] Implementar dashboard de violaciones JANO
- [ ] Agregar métricas de Prometheus para rate limiting

## 📚 Referencias

- [JANO Microservice README](../configuration_rules_microservice/README.md)
- [Database Schema](../database/README.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)

---

**Última Actualización**: 2025-10-18  
**Versión**: 1.0.0  
**Estado**: ✅ Integración Completa
