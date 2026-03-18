# Guía de Interacción API para Automatización

Sigue este orden para tus Goroutines o scripts de prueba:

## 1. Registro de Usuarios (`Register`)
Crea al menos dos usuarios para probar la funcionalidad de compartir.

- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/app/tasks/auth/register/` (o la ruta configurada en tu `urls.py`)
- **Body (JSON):** 
  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "password123"
  }
  ```

## 2. Obtención de Token (`Login`)
Obtén el JWT necesario para las peticiones protegidas.

- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/auth/login/`
- **Body (JSON):** 
  ```json
  {
    "username": "user1",
    "password": "password123"
  }
  ```
- **Respuesta:** Captura el valor de `"access"`.

## 3. Creación de Tareas (`Create`)
- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/tasks/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body (JSON):** 
  ```json
  {
    "name": "Nueva Tarea",
    "description": "Detalles de la tarea"
  }
  ```
- **Respuesta:** Guarda el `"id"` (UUID) devuelto.

## 4. Compartir Tarea (`Share`)
- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/tasks/<task_uuid>/share/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body (JSON):** 
  ```json
  {
    "user_id": <id_del_receptor>
  }
  ```

---
> [!NOTE]
> Los IDs de usuario (`user_id`) son numéricos por defecto en Django (1, 2, 3...). Las tareas usan `UUID` (strings).
