# OTP Microservice - Database Integration

## Overview

El microservicio OTP ha sido actualizado de una implementación mock (almacenamiento en memoria) a una implementación completa con persistencia en base de datos PostgreSQL, siguiendo los principios de arquitectura hexagonal.

## Cambios Principales

### 1. Arquitectura Hexagonal

La implementación sigue estrictamente el patrón de puertos y adaptadores:

```
src/
├── core/
│   ├── domain/          # Entidades de dominio (OTP)
│   └── ports/           # Interfaces (OTPRepositoryPort)
├── application/         # Casos de uso
│   ├── generate_otp_use_case.py
│   └── validate_otp_use_case.py
└── infrastructure/      # Implementaciones concretas
    ├── adapters/
    │   ├── controllers/  # REST controllers
    │   └── db/           # Database adapters
    │       ├── database.py
    │       ├── models.py
    │       └── otp_repository.py
    └── config/
        └── settings.py
```

### 2. Persistencia en Base de Datos

#### Tabla: `siata_auth.otp_codes`

```sql
CREATE TABLE siata_auth.otp_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    code VARCHAR(10) NOT NULL,
    delivery_method VARCHAR(10) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    validated_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE
);
```

#### SQLAlchemy Model

```python
class OTPModel(Base):
    __tablename__ = "otp_codes"
    __table_args__ = {"schema": "siata_auth"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    delivery_method = Column(Enum(DeliveryMethodEnum), nullable=False)
    recipient = Column(String(255), nullable=False)
    status = Column(Enum(OTPStatusEnum), nullable=False, default=OTPStatusEnum.PENDING)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
```

### 3. Repository Pattern

El repositorio implementa la interfaz `OTPRepositoryPort` con los siguientes métodos:

```python
class OTPRepositoryPort(ABC):
    @abstractmethod
    async def save(self, otp: OTP) -> OTP:
        """Guarda un nuevo OTP en la base de datos."""
        pass
    
    @abstractmethod
    async def get_by_id(self, otp_id: UUID) -> Optional[OTP]:
        """Obtiene un OTP por su ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[OTP]:
        """Obtiene todos los OTPs de un usuario."""
        pass
    
    @abstractmethod
    async def update(self, otp: OTP) -> OTP:
        """Actualiza un OTP existente."""
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        """Elimina OTPs expirados."""
        pass
```

### 4. Dependency Injection

FastAPI Depends para inyección de dependencias:

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos."""
    async with DatabaseAdapter.get_session() as session:
        yield session


async def get_otp_repository(
    session: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[OTPRepositoryPort, None]:
    """Proporciona una instancia del repositorio OTP."""
    yield OTPRepository(session)
```

### 5. Configuration Management

Pydantic Settings para configuración:

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://otp_service:password@postgres:5432/auth_login_services"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 3
    OTP_CODE_LENGTH: int = 6
    
    # Development
    DEV_SHOW_OTP_IN_RESPONSE: bool = True
```

## Configuración

### Variables de Entorno

Configurar en `docker-compose.yml`:

```yaml
otp_microservice:
  environment:
    DATABASE_URL: postgresql+asyncpg://otp_service:otp_service_password@postgres:5432/auth_login_services
    OTP_EXPIRY_MINUTES: 5
    OTP_MAX_ATTEMPTS: 3
    OTP_CODE_LENGTH: 6
    DEV_SHOW_OTP_IN_RESPONSE: "true"
    DB_POOL_SIZE: 5
    DB_MAX_OVERFLOW: 10
    DB_ECHO: "false"
```

### Database Initialization

El servicio inicializa automáticamente la conexión a la base de datos en el startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Initializing database connection...")
    DatabaseAdapter.initialize(
        database_url=settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    logger.info("Database connection initialized successfully")
    
    yield
    
    logger.info("Closing database connection...")
    await DatabaseAdapter.close()
    logger.info("Database connection closed")
```

## API Endpoints

### 1. Generate OTP

**POST** `/api/v1/otp/generate`

**Request Body:**
```json
{
  "user_id": "user123",
  "delivery_method": "email",
  "recipient": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP generated and sent successfully",
  "otp_id": "123e4567-e89b-12d3-a456-426614174000",
  "expires_in_minutes": 5,
  "code": "123456"
}
```

### 2. Validate OTP

**POST** `/api/v1/otp/validate`

**Request Body:**
```json
{
  "otp_id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "123456",
  "user_id": "user123"
}
```

**Response (200 OK - Valid):**
```json
{
  "valid": true,
  "message": "OTP validated successfully"
}
```

**Response (200 OK - Invalid):**
```json
{
  "valid": false,
  "message": "Invalid OTP code. 2 attempts remaining."
}
```

**Response (400 Bad Request - Expired):**
```json
{
  "detail": "OTP has expired"
}
```

**Response (400 Bad Request - Max Attempts):**
```json
{
  "detail": "Maximum validation attempts exceeded"
}
```

## Estado de OTP

Los OTPs pueden tener los siguientes estados:

- **PENDING**: OTP creado pero no enviado
- **SENT**: OTP enviado al destinatario
- **VALIDATED**: OTP validado exitosamente
- **EXPIRED**: OTP expirado
- **FAILED**: Falló el envío del OTP

## Métodos de Entrega

- **EMAIL**: Envío por correo electrónico
- **SMS**: Envío por mensaje de texto

## Flujo de Validación

1. **Generación**: Se crea un OTP con estado `PENDING`
2. **Envío**: Se marca como `SENT` con timestamp
3. **Validación**: 
   - Si el código es correcto: estado → `VALIDATED`
   - Si es incorrecto: incrementar `attempts`
   - Si `attempts >= max_attempts`: rechazar validación
   - Si `expires_at < now()`: rechazar como expirado

## Testing

### Tests de Integración

```bash
# Ejecutar tests de integración
cd otp_microservice
pytest test/test_otp_integration.py -v
```

### Tests Manuales

```bash
# Ejecutar script de pruebas manuales
python test/manual_test_otp.py
```

El script de pruebas manuales verifica:
- ✅ Health check
- ✅ Generación de OTP
- ✅ Validación exitosa
- ✅ Validación con código incorrecto
- ✅ Máximo de intentos excedidos
- ✅ Expiración de OTP

## Seguridad

### Database Security

- Usuario de base de datos dedicado: `otp_service`
- Permisos restringidos solo a tabla `siata_auth.otp_codes`
- Passwords deben ser cambiados en producción

### OTP Security

- Códigos aleatorios de 6 dígitos
- Expiración configurable (default: 5 minutos)
- Máximo de intentos configurable (default: 3)
- Timestamps para auditoría
- Limpieza automática de OTPs expirados

## Monitoreo y Logs

El servicio registra:
- Inicialización de base de datos
- Generación de OTPs
- Intentos de validación
- Errores de conexión a BD
- Operaciones de limpieza

```python
logger.info(f"OTP generated for user {user_id}")
logger.warning(f"Invalid OTP validation attempt for {otp_id}")
logger.error(f"Database error: {str(e)}")
```

## Mantenimiento

### Limpieza de OTPs Expirados

Se recomienda ejecutar periódicamente:

```python
deleted_count = await otp_repository.delete_expired()
logger.info(f"Deleted {deleted_count} expired OTPs")
```

Puede implementarse como:
- Cron job
- Background task en FastAPI
- Scheduled task en Kubernetes

## Migración de Mock a Database

### Cambios Realizados

1. ✅ Creado port interface: `OTPRepositoryPort`
2. ✅ Implementado adaptador: `OTPRepository`
3. ✅ Creado modelo SQLAlchemy: `OTPModel`
4. ✅ Configuración con Pydantic Settings
5. ✅ Dependency injection con FastAPI
6. ✅ Actualizados use cases para usar repository
7. ✅ Actualizado controller con DI
8. ✅ Lifecycle management de database
9. ✅ Variables de entorno en docker-compose
10. ✅ Tests de integración

### Beneficios

- ✅ **Persistencia**: OTPs sobreviven reinicios del servicio
- ✅ **Escalabilidad**: Múltiples instancias pueden compartir BD
- ✅ **Auditoría**: Timestamps y estado completo
- ✅ **Confiabilidad**: Transacciones ACID
- ✅ **Testing**: Fácil testing con base de datos de prueba
- ✅ **Arquitectura**: Hexagonal permite cambiar adaptadores fácilmente

## Próximos Pasos

1. Implementar envío real de emails (SMTP)
2. Implementar envío real de SMS
3. Agregar background task para limpieza automática
4. Métricas y monitoring (Prometheus)
5. Rate limiting por usuario
6. Logging estructurado (JSON)

## Referencias

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
