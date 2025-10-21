# API SIATA - Comandos CURL para Autenticación y Creación de Usuarios

Este documento contiene los comandos CURL necesarios para:
1. Ingresar como root (obtener OTP y verificarlo)
2. Crear usuario external sin team_id
3. Crear usuario root sin team_id
4. Crear usuario user_siata con team_id

## Variables Globales

```bash
AUTH_URL="http://localhost:8001"
USERS_URL="http://localhost:8006"
TEAM_ID="329454c0-c6cb-411b-80f6-2e196bff1947"
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
  }'
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
  }'
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
  }'
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
  }'
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


## 6. MODIFICAR USUARIO (Actualizar información)

**Endpoint:** `PUT /api/users/{user_id}`

Requiere: JWT Token (Bearer Token) y rol ROOT

```bash
# Primero obtener el user_id del usuario que queremos modificar
USER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

curl -X PUT "${USERS_URL}/api/users/${USER_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "name": "Nombre Actualizado",
    "last_name": "Apellido Actualizado",
    "email": "nuevo.email@siata.gov.co"
  }'
```

**Response esperado:**
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "username": "usuario_externo",
  "email": "nuevo.email@siata.gov.co",
  "name": "Nombre Actualizado",
  "last_name": "Apellido Actualizado",
  "role": "external",
  "status": "pending_activation"
}
```

**Notas:**
- Todos los campos son opcionales
- Solo se actualizan los campos enviados
- El email debe ser único
- No se puede cambiar `username`, `role` o `team_id` en este endpoint

---

## 7. LISTAR TODOS LOS USUARIOS

**Endpoint:** `GET /api/users`

Requiere: JWT Token (Bearer Token) y rol ROOT

```bash
# Listar usuarios con paginación (página 1, 10 usuarios por página)
curl -X GET "${USERS_URL}/api/users?page=1&size=10" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**Con filtros opcionales:**

```bash
# Listar solo usuarios activos
curl -X GET "${USERS_URL}/api/users?page=1&size=10&active_only=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

# Listar solo usuarios con rol específico
curl -X GET "${USERS_URL}/api/users?page=1&size=10&role=user_siata" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

# Combinación de filtros
curl -X GET "${USERS_URL}/api/users?page=1&size=10&role=external&active_only=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**Response esperado:**
```json
{
  "items": [
    {
      "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "username": "usuario_externo",
      "email": "usuario.externo@example.com",
      "name": "Usuario",
      "last_name": "Externo",
      "role": "external",
      "status": "active"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 10,
  "pages": 2
}
```

**Parámetros de Paginación:**
- `page`: Número de página (comienza en 1). Default: 1
- `size`: Cantidad de usuarios por página (máximo 100). Default: 10
- `role`: Filtrar por rol (external, root, user_siata, admin). Opcional
- `active_only`: Si es `true`, solo retorna usuarios activos. Default: false

---

## 8. DESHABILITAR USUARIO

**Endpoint:** `PATCH /api/users/{user_id}/disable`

Requiere: JWT Token (Bearer Token) y rol ROOT

```bash
# Obtener el user_id del usuario a deshabilitar
USER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

curl -X PATCH "${USERS_URL}/api/users/${USER_ID}/disable" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**Response esperado:**
```json
{
  "message": "User xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx disabled successfully",
  "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "inactive"
}
```

**Notas:**
- El usuario deshabilitado tendrá status `inactive`
- No podrá ingresar al sistema
- Se puede reactivar usando el endpoint `/enable`

---

## 9. HABILITAR USUARIO

**Endpoint:** `PATCH /api/users/{user_id}/enable`

Requiere: JWT Token (Bearer Token) y rol ROOT

```bash
# Obtener el user_id del usuario a habilitar
USER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

curl -X PATCH "${USERS_URL}/api/users/${USER_ID}/enable" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**Response esperado:**
```json
{
  "message": "User xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx enabled successfully",
  "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "active"
}
```

**Notas:**
- El usuario habilitado tendrá status `active`
- Podrá ingresar al sistema nuevamente
- Se puede deshabilitar usando el endpoint `/disable`

---
