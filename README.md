# EduAttend - Monorepo Hexagonal con Microservicios

EduAttend es un sistema de gestion academica distribuido con arquitectura hexagonal (Ports and Adapters) y enfoque de microservicios.

Servicios incluidos:

- Attendance Service: control de asistencias y reglas de negocio de duplicidad.
- Auth Service: login, refresh token y logout con JWT.
- User Service: gestion de usuarios, perfiles y roles.
- Notification Service: consumo de eventos de faltas y envio de alertas por email.

Persistencia y mensajeria:

- Attendance DB: PostgreSQL (attendance_db)
- Auth DB: PostgreSQL (auth_db)
- User DB: PostgreSQL (user_db)
- Notification DB: PostgreSQL (notifications_db.notification_logs)
- Broker: RabbitMQ

## Arquitectura

```text
Usuario/Cliente (Web/Mobile/Postman)
        |
        | HTTP/JSON
        v
 API Gateway (Flask/Nginx) ---- verifica token ----> Auth Service
        |                                            |
        | si valido                                  | consulta credenciales
        v                                            v
 Attendance Service -----------------------------> User Service
        |                                            |
        | publica evento de faltas (RabbitMQ)        |
        v                                            |
   Exchange: absence_events (direct)                |
        | routing_key=absence_limit                 |
        v                                            |
 Notification Service -------------------------------
        |
        | envia correo SMTP
        v
 Servicio Email Externo
```

## Estructura de monorepo

```text
registro-notas-AH/
├── docker-compose.yml
├── .env.example
├── run.py
└── src/
       ├── attendance_service/
    ├── auth_service/
    ├── user_service/
    └── notification_service/
```

## Requisitos previos

- Docker
- Docker Compose

## Manual de instalacion (paso a paso)

1. Clonar repositorio

```powershell
git clone <url-del-repositorio>
cd registro-notas-AH
```

2. Crear archivo de entorno

```powershell
Copy-Item .env.example .env
```

3. Configurar variables en `.env`

- SMTP_USER
- SMTP_PASSWORD
- JWT_SECRET (recomendado)

4. Construir y levantar servicios

```powershell
docker-compose up --build -d
```

5. Verificar estado

```powershell
docker-compose ps
```

6. (Opcional) Detener y limpiar

```powershell
docker-compose down
```

## Endpoints por servicio

| Servicio | Metodo | Ruta | Descripcion | Requiere auth |
|----------|--------|------|-------------|---------------|
| Attendance | GET | /health | Health check | No |
| Attendance | POST | /api/v1/attendance | Registrar asistencia | Si |
| Attendance | GET | /api/v1/attendance | Listar asistencias | Si |
| Attendance | GET | /api/v1/attendance/{id} | Obtener asistencia por id | Si |
| Attendance | PUT | /api/v1/attendance/{id} | Actualizar asistencia | Si |
| Attendance | DELETE | /api/v1/attendance/{id} | Eliminar asistencia | Si |
| Auth | GET | /health | Health check | No |
| Auth | POST | /auth/login | Iniciar sesion y generar tokens | No |
| Auth | POST | /auth/refresh | Renovar access token | No |
| Auth | POST | /auth/logout | Invalidar refresh token | Si |
| User | GET | /health | Health check | No |
| User | GET | /users | Listar usuarios | Si |
| User | POST | /users | Crear usuario | Si |
| User | GET | /users/{id} | Obtener usuario y perfil | Si |
| User | PUT | /users/{id} | Actualizar usuario | Si |
| User | PUT | /users/{id}/profile | Actualizar perfil | Si |
| User | PUT | /users/{id}/role | Asignar rol | Si |

Puertos:

- Attendance Service: http://localhost:8000
- Auth Service: http://localhost:8001
- User Service: http://localhost:8002

## RabbitMQ Admin

Panel de administracion:

- URL: http://localhost:15672
- Usuario: guest
- Password: guest

## Prueba de flujo completo

1. Crear usuario en Auth DB (si no existe) con password hasheado con bcrypt.
2. Login en Auth Service.

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student1@example.com","password":"123456"}'
```

3. Publicar evento de faltas en RabbitMQ (desde panel o script).

Ejemplo de payload:

```json
{
  "event": "ABSENCE_LIMIT_REACHED",
  "student_id": "student-001",
  "student_email": "student1@example.com",
  "course_id": "MAT101",
  "count": 3,
  "timestamp": "2026-04-20T12:00:00Z"
}
```

4. Verificar que Notification Service procese el evento y envie el correo.
5. Revisar logs en PostgreSQL, tabla notification_logs.

```bash
docker exec -it postgres_notifications psql -U notifications_user -d notifications_db -c "SELECT * FROM notification_logs;"
```

## Notas de diseño

- Domain y Application no dependen de Flask, FastAPI, SQLAlchemy, pika ni smtplib.
- Los protocolos se definen en servicios de dominio.
- El wiring de dependencias se concentra en app.py de cada servicio.
- Los secretos locales viven en .env.
