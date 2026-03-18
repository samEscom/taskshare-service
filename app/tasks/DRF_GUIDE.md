# Guía Rápida: Django REST Framework (DRF)

Esta guía resume los conceptos clave para construir APIs con DRF, enfocándose en la diferencia entre vistas y el manejo de acciones asíncronas con Celery.

## 1. Request Flow (Flujo de Petición)
El camino que sigue un dato desde que llega hasta que se guarda:
1. **Request (JSON):** El cliente envía datos.
2. **URLs (`urls.py`):** Dirigen la petición al recurso correcto.
3. **View (`views.py`):** Contiene la lógica de negocio y decide qué hacer.
4. **Serializer (`serializers.py`):** 
   - *Deserialización:* Valida el JSON y lo convierte en un objeto de base de datos.
   - *Serialización:* Convierte el objeto de base de datos a JSON para la respuesta.
5. **Response (JSON):** Se envía el resultado al cliente.

---

## 2. ModelViewSet vs APIView

### ModelViewSet (El "Atajo Inteligente")
- **Propósito:** Operaciones CRUD estándar (List, Create, Retrieve, Update, Delete).
- **Ventaja:** Con ~3 líneas de código obtienes 5 endpoints automáticos.
- **Cuándo usar:** Cuando solo necesitas exponer una tabla de base de datos de forma estándar.

### APIView (El "Control Total")
- **Propósito:** Lógicas personalizadas que no encajan en un CRUD (ej. procesos de pago, reportes complejos).
- **Ventaja:** Tienes control total sobre cada método HTTP (`get`, `post`, `put`, `delete`).
- **Cuándo usar:** Cuando la lógica es muy distinta a "guardar o leer de una tabla".

---

## 3. Acciones Extra: El Decorador `@action`
Si ya usas un `ModelViewSet`, no necesitas cambiar a `APIView` para agregar una lógica especial. Puedes usar `@action`.

- **Uso:** Se agrega como un método dentro del `ModelViewSet`.
- **Ejemplo Real:** "Compartir una tarea" (`POST /tasks/123/share/`).
- **Ventaja:** DRF se encarga de buscar el objeto por ti (`self.get_object()`). Si el ID no existe en tus tareas, devuelve un 404 automáticamente.

```python
@action(detail=True, methods=['post'])
def share(self, request, pk=None):
    task = self.get_object() # Obtiene la tarea actual
    user_id = request.data.get('user_id')
    # Lógica para guardar en tabla intermedia...
    return Response({"message": "Shared!"}, status=201)
```

---

## 4. Integración con Celery (Workers)
Para tareas pesadas o lentas (enviar emails, procesar imágenes, compartir), el flujo ideal es:

1. **Vista:** Recibe la petición.
2. **Validación:** Verifica que el ID existe.
3. **Queue (Handoff):** Envía el trabajo al worker con `.delay()`.
4. **Respuesta Rápida:** La API responde un código `202 Accepted` de inmediato.
5. **Worker:** Ejecuta la tarea en segundo plano sin bloquear la API.

> [!IMPORTANT]
> **Redis vs Postgres para Reintentos:**
> Para "intentos de envío" (counters), es mejor dejar que Celery lo maneje en **Redis**.
> - **Celery native retries:** Usa el decorador `@task(bind=True, max_retries=5)`.
> - **Eficiencia:** Evitas escribir en Postgres cada vez que algo falla temporalmente.
> - **Persistencia:** Solo guardamos en Postgres lo que debe durar para siempre (como quién compartió la tarea).

### Código de Ejemplo: Implementación
**1. Definir la tarea (`tasks.py`):**
En lugar de procesarlo en la vista, se registra en Celery:
```python
from celery import shared_task
import time

@shared_task(bind=True, max_retries=5)
def send_email(self, user_id, task_id):
    try:
        # Lógica pesada, red, o lenta...
        time.sleep(2) 
        return True
    except Exception as exc:
        # Celery vuelve a encolarlo inteligentemente (Exponential Backoff)
        self.retry(exc=exc, countdown=5 ** self.request.retries)
```

**2. Enviar a la cola (`views.py`):**
Nunca uses `send_email(user_id, task_id)` directamente, ya que eso congelaría la API esos 2 segundos (o lo que tarde). **Siempre usa `.delay()`:**
```python
# Manda el trabajo a Redis y continúa a la siguiente línea al instante
send_email.delay(user_id=1, task_id="uuid-123")

# Responde al cliente de volada
return Response({"message": "Correo encolado"}, status=201)
```

---

## 5. Autenticación y Usuarios (JWT)

Para este proyecto, usamos **SimpleJWT** para manejar la seguridad. Aquí los dos flujos principales:

### Registro de Usuario (`POST /auth/register/`)
- **Cómo funciona:** Es una mezcla de definición propia.
  - El **Serializer** (`UserSerializer`) usa `User.objects.create_user` para encriptar la contraseña.
  - La **Vista** (`UserRegistrationView`) usa `generics.CreateAPIView` que ya sabe cómo guardar datos.
- **Deducción:** Swagger lo muestra porque detecta la ruta en `urls.py` vinculada a una vista de DRF.

### Login / Obtención de Token (`POST /auth/login/`)
- **Cómo funciona:** Usamos `TokenObtainPairView` de la librería SimpleJWT.
- **La "Magia":** Esta vista ya viene programada. Al recibir `username` y `password`:
  1. Valida contra la tabla `auth_user`.
  2. Genera un **Access Token** (llave de corto plazo para peticiones).
  3. Genera un **Refresh Token** (llave de largo plazo para renovar el access).
- **Uso:** El cliente debe guardar el `access` token y enviarlo en cada petición protegida en el header: 
  `Authorization: Bearer <TOKEN>`

### Protección de Endpoints
Para bloquear un recurso, usamos `permission_classes = [IsAuthenticated]` en la vista. Esto obliga a DRF a verificar que el token enviado sea válido antes de ejecutar cualquier lógica.

---

## 6. Personalización de Lógica (Overrides)

En un `ModelViewSet`, puedes modificar el comportamiento estándar sobrescribiendo sus métodos:

### Filtrado por Dueño (`get_queryset`)
Para evitar que un usuario vea los datos de otro, sobrescribimos el método que obtiene la lista:
```python
def get_queryset(self):
    return Task.objects.filter(created_by=self.request.user)
```

### Borrado Lógico (`destroy`)
Si no quieres borrar el registro de la DB sino solo marcarlo como inactivo:
```python
def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    instance.is_active = False
    instance.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
```

### Auditoría Automática (`perform_create` / `perform_update`)
Permiten inyectar datos (como el usuario que edita o la fecha) justo antes de guardar:
```python
def perform_update(self, serializer):
    serializer.save(updated_by=self.request.user, updated_at=timezone.now())
```
