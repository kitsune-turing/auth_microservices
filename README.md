# Sistema de Autenticación y Gestión de Usuarios - SIATA

Sistema de microservicios para autenticación, autorización y gestión de usuarios desarrollado con arquitectura hexagonal.

## 🏗️ Arquitectura

- **auth_microservice**: Autenticación JWT con OTP y gestión de sesiones
- **users_microservice**: CRUD de usuarios con autorización basada en roles
- **otp_microservice**: Generación y validación de códigos OTP
- **management_application_microservice**: Gestión de aplicaciones
- **management_module_microservice**: Gestión de módulos

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose
- PowerShell (Windows)

### Iniciar Servicios

```powershell
# Opción 1: Script automatizado
.\inicio.ps1

# Opción 2: Manual
docker-compose up -d
```

### Verificar Salud

```powershell
# Auth Microservice
Invoke-RestMethod http://localhost:8001/health

# Users Microservice
Invoke-RestMethod http://localhost:8006/health

# OTP Microservice
Invoke-RestMethod http://localhost:8003/health
```

## 📚 Documentación

- [Guía de Inicio Rápido](INICIO_RAPIDO.md)
- [Comandos de Prueba](COMANDOS_RAPIDOS_PRUEBA.md)
- [Guía de Verificación](GUIA_VERIFICACION_TOKENS_DB.md)
- [Resumen de Implementación](RESUMEN_IMPLEMENTACION_TOKENS.md)
- [Resumen Ejecutivo](RESUMEN_EJECUTIVO.md)

## 🔑 Características Principales

### Auth Microservice
- ✅ Login con email/password + OTP
- ✅ Tokens JWT (access + refresh)
- ✅ Almacenamiento de tokens en PostgreSQL
- ✅ Gestión de sesiones con IP y User-Agent
- ✅ Revocación de tokens en logout
- ✅ Validación de tokens para otros microservicios

### Users Microservice
- ✅ CRUD de usuarios
- ✅ Autorización basada en roles (ROOT)
- ✅ Validación de credenciales
- ✅ Integración con auth_microservice

### OTP Microservice
- ✅ Generación de códigos OTP
- ✅ Validación de códigos
- ✅ Modo MOCK para desarrollo

## 🗄️ Base de Datos

**PostgreSQL 15**
- `auth_tokens`: Almacenamiento de JWT con metadatos
- `sessions`: Registro de sesiones activas
- `users`: Información de usuarios
- Índices optimizados para consultas frecuentes

## 🔒 Seguridad

- JWT con UUID-based `jti` para tracking
- Tokens almacenados en BD para revocación
- Autenticación de dos factores (OTP)
- Autorización basada en roles (ROOT, EXTERNAL, USER_SIATA)
- Sesiones rastreables con IP y User-Agent
- CORS configurado

## 🛠️ Tecnologías

- **Backend**: FastAPI + Python 3.11
- **ORM**: SQLAlchemy 2.0 (async)
- **Base de Datos**: PostgreSQL 15 + asyncpg
- **Autenticación**: JWT (python-jose)
- **Contenedores**: Docker + Docker Compose
- **Arquitectura**: Hexagonal/Clean Architecture

## 📝 Variables de Entorno

### auth_microservice/.env
```env
JWT_SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql+asyncpg://admin:secure_password_123@auth_login_services_db:5432/auth_login_services
USERS_SERVICE_URL=http://users_microservice:8006
OTP_SERVICE_URL=http://otp_microservice:8003
CORS_ORIGINS=["*"]
```

### users_microservice/.env
```env
DATABASE_URL=postgresql://admin:secure_password_123@auth_login_services_db:5432/auth_login_services
AUTH_SERVICE_URL=http://auth_microservice:8001
```

## 🧪 Pruebas

```powershell
# Crear usuario ROOT
$createUser = @{
    username = "admin"
    email = "admin@siata.gov.co"
    password = "Admin123!"
    name = "Admin"
    last_name = "SIATA"
    role = "root"
    is_active = $true
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8006/api/users" -Method Post -Body $createUser -ContentType "application/json"

# Login
$login = @{
    email = "admin@siata.gov.co"
    password = "Admin123!"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" -Method Post -Body $login -ContentType "application/json"

# Verificar OTP (ver logs)
docker logs otp_microservice --tail 5

# Completar login
$verify = @{
    email = "admin@siata.gov.co"
    otp_code = "123456"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/auth/verify-login" -Method Post -Body $verify -ContentType "application/json"
```

## 📊 Endpoints Principales

### Auth Microservice (8001)
- `POST /api/auth/login` - Iniciar login
- `POST /api/auth/verify-login` - Verificar OTP y obtener tokens
- `POST /api/auth/refresh-token` - Renovar access token
- `POST /api/auth/logout` - Cerrar sesión
- `POST /api/auth/validate-token` - Validar token JWT
- `GET /health` - Estado del servicio

### Users Microservice (8006)
- `POST /api/users` - Crear usuario (requiere ROOT)
- `GET /api/users/{user_id}` - Obtener usuario (requiere ROOT)
- `POST /api/users/validate-credentials` - Validar credenciales
- `GET /health` - Estado del servicio

### OTP Microservice (8003)
- `POST /api/otp/generate` - Generar OTP
- `POST /api/otp/validate` - Validar OTP
- `GET /health` - Estado del servicio

## 🐳 Docker

```bash
# Construir servicios
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir un servicio específico
docker-compose build --no-cache auth_microservice
```

## 📦 Estructura del Proyecto

```
login_system_services/
├── auth_microservice/          # Autenticación JWT
│   ├── src/
│   │   ├── application/        # Casos de uso
│   │   ├── domain/             # Entidades y lógica de negocio
│   │   └── infrastructure/     # Adaptadores y controladores
│   ├── Dockerfile
│   └── requirements.txt
├── users_microservice/         # Gestión de usuarios
├── otp_microservice/           # OTP
├── docker-compose.yml
└── README.md
```

## 👥 Roles y Permisos

- **root**: Acceso completo al sistema, puede crear/modificar usuarios
- **user_siata**: Usuario interno de SIATA
- **external**: Usuario externo con acceso limitado

## 🔍 Verificación en Base de Datos

```powershell
# Conectar a PostgreSQL
docker exec -it auth_login_services_db psql -U admin -d auth_login_services

# Ver tokens
SELECT id, user_id, token_type, created_at, revoked FROM auth_tokens;

# Ver sesiones
SELECT id, user_id, ip_address, created_at, active FROM sessions;

# Ver usuarios
SELECT id, username, email, role FROM users;
```

## 🚨 Troubleshooting

Ver [INICIO_RAPIDO.md](INICIO_RAPIDO.md) sección de troubleshooting.

## 📄 Licencia

SIATA - Sistema de Alerta Temprana de Medellín y el Valle de Aburrá

## 🤝 Contribución

Este proyecto utiliza arquitectura hexagonal y sigue principios SOLID.
