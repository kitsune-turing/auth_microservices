# API SIATA - Comandos CURL para Autenticación y Creación de Usuarios

Este documento contiene los comandos CURL necesarios para:
1. Ingresar como root (obtener OTP y verificarlo)
2. Crear usuario external sin team_id
3. Crear usuario root sin team_id
4. Crear usuario user_siata con team_id

## Variables Globales

```bash
# Base URLs
AUTH_URL="http://localhost:8001"
USERS_URL="http://localhost:8006"

# Team ID para usuarios user_siata
TEAM_ID="329454c0-c6cb-411b-80f6-2e196bff1947"

# Credenciales root
ROOT_EMAIL="admin@siata.gov.co"
ROOT_PASSWORD="Admin123!"
```

---

## 1. LOGIN - Obtener OTP

**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST "${AUTH_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@siata.gov.co",
    "password": "Admin123!"
  }' | jq .
```

**Response esperado:**
```json
{
  "otp_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "otp_code": "123456"
}
```

**Guardar para el siguiente paso:**
```bash
OTP_ID="<otp_id del response>"
OTP_CODE="<otp_code del response>"
```

---

## 2. VERIFY OTP - Obtener JWT Token

**Endpoint:** `POST /api/auth/verify-login`

Usa el `OTP_ID` y `OTP_CODE` del paso anterior.

```bash
curl -X POST "${AUTH_URL}/api/auth/verify-login" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_id": "'"${OTP_ID}"'",
    "otp_code": "'"${OTP_CODE}"'"
  }' | jq .
```

**Response esperado:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Guardar para los siguientes pasos:**
```bash
ACCESS_TOKEN="<access_token del response>"
```

---

## 3. CREAR USUARIO EXTERNAL (sin team_id)

**Endpoint:** `POST /api/users`

Requiere: JWT Token (Bearer Token)

```bash
curl -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_externo",
    "email": "usuario.externo@example.com",
    "password": "ExternalPass@123",
    "name": "Usuario",
    "last_name": "Externo",
    "role": "external"
  }' | jq .
```

**Response esperado:**
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "username": "usuario_externo",
  "email": "usuario.externo@example.com",
  "name": "Usuario",
  "last_name": "Externo",
  "role": "external",
  "status": "pending_activation"
}
```

**Notas:**
- El `team_id` NO se envía (no se requiere para rol external)
- El usuario se crea con status `pending_activation`

---

## 4. CREAR USUARIO ROOT (sin team_id)

**Endpoint:** `POST /api/users`

Requiere: JWT Token (Bearer Token)

```bash
curl -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_root",
    "email": "usuario.root@siata.gov.co",
    "password": "RootPass@123",
    "name": "Administrador",
    "last_name": "Root",
    "role": "root"
  }' | jq .
```

**Response esperado:**
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "username": "usuario_root",
  "email": "usuario.root@siata.gov.co",
  "name": "Administrador",
  "last_name": "Root",
  "role": "root",
  "status": "pending_activation"
}
```

**Notas:**
- El `team_id` NO se envía (no se requiere para rol root)
- El usuario se crea con status `pending_activation`

---

## 5. CREAR USUARIO USER_SIATA (con team_id)

**Endpoint:** `POST /api/users`

Requiere: JWT Token (Bearer Token)

```bash
curl -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_meteorologo",
    "email": "usuario.meteorologo@siata.gov.co",
    "password": "MeteoPass@123",
    "name": "Meteorólogo",
    "last_name": "SIATA",
    "role": "user_siata",
    "team_id": "329454c0-c6cb-411b-80f6-2e196bff1947"
  }' | jq .
```

**Response esperado:**
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "username": "usuario_meteorologo",
  "email": "usuario.meteorologo@siata.gov.co",
  "name": "Meteorólogo",
  "last_name": "SIATA",
  "role": "user_siata",
  "team_id": "329454c0-c6cb-411b-80f6-2e196bff1947",
  "status": "pending_activation"
}
```

**Notas:**
- El `team_id` ES REQUERIDO para rol user_siata
- El `team_id` debe ser válido (debe existir en la tabla de teams)
- El usuario se crea con status `pending_activation`

---

## Validación de Restricciones por Rol

### External
- ✓ No requiere `team_id`
- ✓ Puede ser null

### Root
- ✓ No requiere `team_id`
- ✓ Puede ser null

### User_SIATA
- ✗ Requiere `team_id` (obligatorio)
- ✗ No puede ser null
- ✗ Debe ser un UUID válido existente

### Admin
- ✓ No requiere `team_id`
- ✓ Puede ser null

---

## Script Bash Completo

Si prefieres ejecutar todo en un script bash:

```bash
#!/bin/bash

# Variables
AUTH_URL="http://localhost:8001"
USERS_URL="http://localhost:8006"
TEAM_ID="329454c0-c6cb-411b-80f6-2e196bff1947"

# 1. LOGIN
echo "1. Ingresando como root..."
LOGIN_RESPONSE=$(curl -s -X POST "${AUTH_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@siata.gov.co",
    "password": "Admin123!"
  }')

OTP_ID=$(echo $LOGIN_RESPONSE | jq -r '.otp_id')
OTP_CODE=$(echo $LOGIN_RESPONSE | jq -r '.otp_code')
echo "OTP ID: $OTP_ID"
echo "OTP CODE: $OTP_CODE"

# 2. VERIFY OTP
echo -e "\n2. Verificando OTP..."
AUTH_RESPONSE=$(curl -s -X POST "${AUTH_URL}/api/auth/verify-login" \
  -H "Content-Type: application/json" \
  -d '{
    "otp_id": "'"${OTP_ID}"'",
    "otp_code": "'"${OTP_CODE}"'"
  }')

ACCESS_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.access_token')
echo "Token obtenido (primeros 50 caracteres): ${ACCESS_TOKEN:0:50}..."

# 3. CREATE EXTERNAL USER
echo -e "\n3. Creando usuario EXTERNAL..."
EXTERNAL=$(curl -s -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_externo",
    "email": "usuario.externo@example.com",
    "password": "ExternalPass@123",
    "name": "Usuario",
    "last_name": "Externo",
    "role": "external"
  }')

echo $EXTERNAL | jq .

# 4. CREATE ROOT USER
echo -e "\n4. Creando usuario ROOT..."
ROOT=$(curl -s -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_root",
    "email": "usuario.root@siata.gov.co",
    "password": "RootPass@123",
    "name": "Administrador",
    "last_name": "Root",
    "role": "root"
  }')

echo $ROOT | jq .

# 5. CREATE USER_SIATA
echo -e "\n5. Creando usuario USER_SIATA..."
USER_SIATA=$(curl -s -X POST "${USERS_URL}/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "username": "usuario_meteorologo",
    "email": "usuario.meteorologo@siata.gov.co",
    "password": "MeteoPass@123",
    "name": "Meteorólogo",
    "last_name": "SIATA",
    "role": "user_siata",
    "team_id": "'"${TEAM_ID}"'"
  }')

echo $USER_SIATA | jq .

echo -e "\n✓ Flujo completado exitosamente"
```

---

## Troubleshooting

### Error: "Invalid token"
- Verificar que el token no haya expirado (válido por 30 minutos)
- Obtener un nuevo token ejecutando nuevamente los pasos 1 y 2

### Error: "User not found"
- Verificar las credenciales root (`admin@siata.gov.co` / `Admin123!`)

### Error: "Email already in use"
- Usar emails únicos para cada usuario
- Cambiar el dominio o añadir timestamp

### Error: "Invalid team_id"
- Verificar que el team_id sea un UUID válido
- Verificar que el team exista en la tabla de teams

### Error: "Unauthorized (401)"
- Verificar que el token sea incluido en el header `Authorization: Bearer {token}`
- Verificar que el formato sea exactamente: `Bearer {token}` (con espacio)

