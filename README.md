# Una pregunta especial

Aplicación full stack construida con FastAPI, HTML, CSS y JavaScript. Solicita un
correo, presenta la pregunta y, al aceptar, envía una notificación a
`saulofct222@gmail.com` y una confirmación separada a la persona que respondió.
El despliegue usa `requirements-invitation.txt` para instalar únicamente las
dependencias de esta aplicación, sin cargar los módulos analíticos del proyecto.

## Ejecutar localmente

1. Copia los valores de `.env.example` a tu archivo `.env` existente.
2. Configura `SMTP_USERNAME`, `SMTP_FROM_EMAIL` y `SMTP_PASSWORD`.
3. Inicia la aplicación:

```powershell
.\.venv\Scripts\uvicorn.exe app.invitation_main:app --reload
```

4. Abre `http://127.0.0.1:8000`.

Para Gmail, `SMTP_PASSWORD` debe ser una contraseña de aplicación, no la
contraseña normal de la cuenta. La cuenta debe tener habilitada la verificación
en dos pasos.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_invitation -v
```

Las pruebas simulan el envío, por lo que no mandan correos reales.

## Desplegar en Render

1. Publica el proyecto en un repositorio de GitHub.
2. En Render, crea un Blueprint y selecciona el repositorio. Render detectará
   `render.yaml`.
3. Ingresa los secretos solicitados: `SMTP_USERNAME`, `SMTP_PASSWORD` y
   `SMTP_FROM_EMAIL`.
4. Finaliza el despliegue y abre la URL `onrender.com` asignada.

El plan gratuito de Render puede suspender el servicio después de un periodo sin
tráfico, por lo que la primera apertura posterior puede tardar alrededor de un
minuto. No guardes contraseñas reales en `.env.example`, GitHub ni `render.yaml`.
