# JANO Security Framework Microservice

## 🛡️ Descripción

**JANO** es el framework de seguridad centralizado que define y aplica las políticas de seguridad globales del sistema SIATA. Implementa validaciones de autenticación, autorización, rate limiting, políticas de contraseñas, sesiones y MFA.

## 🏗️ Arquitectura

Implementado con **Arquitectura Hexagonal (Puertos y Adaptadores)**:

```
configuration_rules_microservice/
├── src/
│   ├── core/                    # Capa de dominio
│   │   ├── domain/
│   │   │   ├── entity/         # Entidades: SecurityRule, RuleViolation
│   │   │   └── exceptions/     # Excepciones del dominio
│   │   ├── ports/              # Interfaces (puertos)
│   │   └── services/           # Servicios del dominio
│   ├── application/             # Capa de aplicación
│   │   ├── dtos/               # Data Transfer Objects
│   │   └── use_cases/          # Casos de uso
│   └── infrastructure/          # Capa de infraestructura
│       ├── adapters/
│       │   ├── controllers/    # Controllers REST
│       │   └── db/             # Adaptadores de BD
│       ├── config/             # Configuración
│       └── middleware/         # Middleware
├── main.py
├── Dockerfile
└── requirements.txt
```

## 🔐 Funcionalidades

### 1. Gestión de Reglas de Seguridad (CRUD)

#### Tipos de Reglas:
- **authentication**: Reglas de autenticación
- **authorization**: Reglas de autorización
- **rate_limit**: Límites de requests
- **ip_whitelist**: Listas blancas de IPs
- **password_policy**: Políticas de contraseñas
- **session_policy**: Políticas de sesiones
- **mfa_policy**: Políticas de MFA

#### Endpoints:
- `POST /api/rules` - Crear regla (ROOT only)
- `GET /api/rules/{rule_id}` - Obtener regla
- `GET /api/rules` - Listar reglas
- `PUT /api/rules/{rule_id}` - Actualizar regla (ROOT only)
- `DELETE /api/rules/{rule_id}` - Eliminar regla (ROOT only)

### 2. Validaciones de Seguridad

#### Endpoints:
- `POST /api/validate/request` - Validar request completo
- `POST /api/validate/password` - Validar contraseña
- `POST /api/validate/session` - Validar sesión
- `POST /api/validate/mfa` - Validar requerimiento MFA

## 📊 Modelos de Datos

### SecurityRule

```json
{
  "rule_id": "uuid",
  "rule_name": "Password Policy",
  "rule_type": "password_policy",
  "rule_code": "PASSWORD_POLICY_001",
  "description": "Enforce strong passwords",
  "rule_config": {
    "min_length": 8,
    "require_uppercase": true,
    "require_lowercase": true,
    "require_numbers": true,
    "require_special": true
  },
  "severity": "high",
  "priority": 100,
  "is_active": true,
  "applies_to_roles": ["root", "user_siata"],
  "applies_to_endpoints": ["/api/auth/*"]
}
```

### ValidationResult

```json
{
  "is_valid": false,
  "should_block": true,
  "violated_rules": [...],
  "violations": [...],
  "warnings": ["Password too weak"],
  "metadata": {}
}
```

## 🚀 Uso

### Crear Regla de Contraseña

```bash
curl -X POST http://localhost:8004/api/rules \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Strong Password Policy",
    "rule_type": "password_policy",
    "rule_code": "PWD_POLICY_001",
    "description": "Passwords must be strong",
    "rule_config": {
      "min_length": 8,
      "require_uppercase": true,
      "require_lowercase": true,
      "require_numbers": true,
      "require_special": true
    },
    "severity": "high",
    "priority": 100
  }'
```

### Validar Contraseña

```bash
curl -X POST http://localhost:8004/api/validate/password \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MyP@ssw0rd"
  }'
```

### Validar Request

```bash
curl -X POST http://localhost:8004/api/validate/request \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "uuid",
    "user_role": "root",
    "endpoint": "/api/users",
    "ip_address": "192.168.1.100"
  }'
```

## 🔧 Configuración

### Variables de Entorno

```env
# Service
SERVICE_PORT=8004
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://jano_service:password@postgres:5432/auth_login_services

# Auth Service
AUTH_SERVICE_URL=http://auth_microservice:8001

# CORS
CORS_ORIGINS=["*"]
```

## 🐳 Docker

### Build

```bash
docker build -t jano_microservice .
```

### Run

```bash
docker run -p 8004:8004 \
  -e DATABASE_URL=postgresql+asyncpg://jano_service:password@postgres:5432/auth_login_services \
  -e AUTH_SERVICE_URL=http://auth_microservice:8001 \
  jano_microservice
```

## 📝 Reglas Pre-configuradas

El sistema viene con 5 reglas pre-configuradas (ver `database/schema.sql`):

1. **PASSWORD_POLICY_001**: Contraseñas seguras
2. **AUTH_RATE_LIMIT_001**: Límite de intentos de login
3. **MFA_POLICY_001**: MFA obligatorio para ROOT
4. **SESSION_POLICY_001**: Expiración de sesiones
5. **RATE_LIMIT_001**: Rate limiting general

## 🔗 Integración con Otros Microservicios

### Auth Microservice
- Valida contraseñas antes de crear/actualizar usuarios
- Verifica políticas MFA
- Valida sesiones activas

### Users Microservice
- Aplica políticas de autorización (solo ROOT)

### OTP Microservice
- Verifica políticas MFA

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=src tests/
```

## 📚 API Documentation

Una vez levantado el servicio, acceder a:

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc
- **OpenAPI JSON**: http://localhost:8004/openapi.json

## 🔒 Seguridad

- Solo usuarios con rol **ROOT** pueden crear/modificar/eliminar reglas
- Todos los endpoints requieren autenticación JWT (excepto health checks)
- Las validaciones se ejecutan en orden de prioridad
- Las violaciones se registran en la base de datos

## 📊 Monitoreo

### Health Check

```bash
curl http://localhost:8004/health
```

Respuesta:
```json
{
  "status": "healthy",
  "service": "JANO Security Framework",
  "version": "1.0.0",
  "database": "connected"
}
```

## 🛠️ Desarrollo

### Requisitos
- Python 3.11+
- PostgreSQL 16+
- pip

### Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

## 📄 Licencia

Propiedad de SIATA - Sistema de Alerta Temprana de Medellín

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Mantenedor**: Equipo SIATA
