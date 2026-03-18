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
- **Caso de uso:** "Compartir una tarea" (`POST /tasks/123/share/`).
- **Ventaja:** Sigues teniendo acceso automático al objeto (`self.get_object()`) sin tener que buscarlo manualmente por ID.

---

## 4. Integración con Celery (Workers)
Para tareas pesadas o lentas (enviar emails, procesar imágenes, compartir), el flujo ideal es:

1. **Vista:** Recibe la petición.
2. **Validación:** Verifica que el ID existe.
3. **Queue (Handoff):** Envía el trabajo al worker con `.delay()`.
4. **Respuesta Rápida:** La API responde un código `202 Accepted` de inmediato.
5. **Worker:** Ejecuta la tarea en segundo plano sin bloquear la API.

> [!TIP]
> Mantén tus vistas "delgadas" (lean). La lógica pesada siempre debe vivir en el Serializer o, mejor aún, en un Worker de Celery si es asíncrona.
