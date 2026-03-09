# Guía del Sistema Para Dummies

## 1. Qué hace este proyecto
Este proyecto intenta responder a una pregunta simple:

> "Si entra un mensaje de Telegram, ¿parece normal o parece una amenaza?"

Para responderla, el sistema hace cuatro cosas:
1. recibe el mensaje;
2. lo pasa por un modelo de IA;
3. guarda una evidencia técnica mínima de lo que ha pasado;
4. enseña el resultado en una API, en un dashboard y en Grafana.

## 2. Cómo fluye un mensaje
Imagina este camino:

`Telegram -> bot -> modelo IA -> MongoDB -> API -> dashboard/Grafana`

Más despacio:
- Telegram entrega un mensaje al bot.
- El bot limpia el texto y calcula su hash.
- El modelo estima una probabilidad de amenaza.
- El bot decide `0` o `1` usando un umbral.
- MongoDB guarda la traza técnica mínima.
- La API publica resultados por `run_id`.
- React y Grafana enseñan esos resultados.

## 3. Qué guarda realmente MongoDB
Aquí se aplicó la idea más importante del cambio:

> guardar lo mínimo necesario para poder explicar la decisión.

Por defecto se guarda:
- `run_id`: qué ejecución produjo ese resultado;
- `message_id`: identificador técnico del mensaje;
- `user_hash` y `chat_hash`: versiones pseudonimizadas de usuario y chat;
- `msg_sha256`: huella del contenido;
- `pred`: decisión final (`0` benigno, `1` amenaza);
- `score_1`: probabilidad estimada de amenaza;
- `latency_ms`: cuánto tardó la inferencia;
- `created_at_utc`: cuándo ocurrió;
- `hf_model`, `model_source`, `device`: con qué se ejecutó.

Por defecto **no** se guarda:
- `msg_original`;
- `msg_limpio`;
- `tokens`.

## 4. Por qué no se guarda el mensaje original siempre
Porque el mensaje original puede contener datos personales o sensibles.

La tutora tenía razón aquí: para un TFG defendible no basta con que "funcione"; también tiene que quedar claro que:
- no guardas más de lo que necesitas;
- no dejas abiertos datos sensibles sin justificación;
- puedes explicar la trazabilidad sin romper privacidad.

Por eso se decidió:
- dejar `msg_original=false` por defecto;
- usar `msg_sha256` para demostrar integridad;
- usar hashes para usuario y chat;
- dejar una retención limitada por TTL en Mongo.

## 5. Qué significa `run_id`
`run_id` es el identificador de una ejecución concreta.

Sirve para unir:
- las métricas offline,
- la matriz de confusión,
- el análisis por umbral,
- y los mensajes asociados a esa misma ejecución.

Antes había una incoherencia: algunos endpoints usaban `run_id`, pero ciertos CSV se leían de forma global desde `reports/`.

Ahora la idea correcta es:
- cada ejecución vive en `reports/runs/<run_id>/`;
- la API busca los artefactos de ese run;
- `reports/` solo mantiene una copia rápida del último resultado.

## 6. Por qué el umbral es `0.05`
El modelo devuelve una probabilidad.

Después hace falta decidir:
- si esa probabilidad ya cuenta como amenaza,
- o si todavía no.

Ese punto de corte es el umbral.

### Qué pasa si el umbral es bajo
- detectas más amenazas;
- también saltan más falsas alarmas.

### Qué pasa si el umbral es alto
- reduces falsas alarmas;
- también dejas escapar amenazas.

Se ha mantenido `THRESHOLD=0.05` porque el proyecto está planteado como sistema de detección temprana.

La lógica es:
- en ciberseguridad preventiva suele ser peor dejar pasar una amenaza real;
- aceptar algo más de ruido puede ser razonable si luego un humano revisa.

Eso no significa que `0.05` sea "el mejor umbral universal".
Significa que es el mejor **para este objetivo operativo**.

## 7. Entonces, ¿para qué sirve `threshold_analysis.csv`?
Sirve para demostrar que la elección del umbral no es caprichosa.

Ese archivo compara varios umbrales y enseña:
- precisión,
- recall,
- F1,
- accuracy.

Con eso puedes decir:
- "si quiero detectar mucho, uso 0.05";
- "si quiero equilibrio, me voy a 0.45 o 0.50".

Es una decisión técnica explicada, no una intuición.

## 8. Qué métricas importan aquí
### Accuracy
Porcentaje total de aciertos.

Problema:
- puede sonar bien aunque falle justo en lo importante.

### Precision
De todo lo que el sistema marcó como amenaza, cuánto era verdad.

### Recall
De todas las amenazas reales, cuántas consiguió detectar.

### F1
Un equilibrio entre precision y recall.

### Idea simple
- si te importa no molestar, miras más precision;
- si te importa no dejar escapar amenazas, miras más recall.

Aquí se prioriza recall, sin dejar de reportar el resto.

## 9. Qué cambió en seguridad
### MongoDB
Antes:
- se publicaba puerto.

Ahora:
- solo queda accesible dentro de la red Docker.

### API
Antes:
- los `GET` quedaban abiertos.

Ahora:
- todos requieren `X-API-Key`.

### CORS
Antes:
- se permitía `*`.

Ahora:
- solo orígenes locales explícitos.

### Grafana
Antes:
- acceso anónimo activo.

Ahora:
- autenticación obligatoria.

## 10. Cómo explicarlo en una defensa
Versión corta:

> "El sistema clasifica mensajes de Telegram con un modelo binario, guarda solo evidencia mínima y pseudonimizada para trazabilidad, versiona los artefactos por ejecución con `run_id`, y protege la explotación mediante API key, CORS restringido y Grafana sin acceso anónimo."

Versión todavía más simple:

> "No solo intento acertar; intento acertar dejando pruebas técnicas suficientes y sin guardar más datos de los necesarios."

## 11. Qué queda como decisión de diseño
- Raspberry Pi queda como trabajo futuro, no como prioridad inmediata.
- El núcleo ahora es seguridad mínima, coherencia del `run_id` y defensa técnica sólida.
- Si en el futuro hace falta más forense, se puede activar el guardado opcional de texto original, pero ya sería una decisión explícita y justificada.
