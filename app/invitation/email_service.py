import asyncio
import html
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class EmailConfigurationError(RuntimeError):
    """Raised when the selected email provider is not configured."""


async def _send_acceptance_emails_brevo(participant_email: str) -> None:
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    sender = os.getenv("BREVO_SENDER_EMAIL", "").strip()
    sender_name = os.getenv("BREVO_SENDER_NAME", "Una pregunta especial").strip()
    target_email = os.getenv("TARGET_EMAIL", "saulofct222@gmail.com").strip()

    if not api_key or not sender:
        raise EmailConfigurationError(
            "BREVO_API_KEY y BREVO_SENDER_EMAIL deben estar configurados."
        )

    safe_participant = html.escape(participant_email)
    messages = [
        {
            "sender": {"name": sender_name, "email": sender},
            "to": [{"email": target_email}],
            "replyTo": {"email": participant_email},
            "subject": f"¡Dijo que sí! Respuesta de {participant_email}",
            "textContent": (
                "La respuesta fue aceptada.\n\n"
                f"Correo de quien respondió: {participant_email}\n"
                "Respuesta: Sí, quiero ser tu novia."
            ),
            "htmlContent": f"""
            <div style="font-family:Georgia,serif;max-width:560px;margin:auto;padding:32px;
                        color:#3f2928;background:#fffaf5;border:1px solid #ead8cc;border-radius:18px">
              <p style="color:#b9504e;letter-spacing:.12em;text-transform:uppercase">Respuesta recibida</p>
              <h1 style="font-size:32px;margin:8px 0 18px">¡Dijo que sí!</h1>
              <p style="font-size:17px;line-height:1.6">La invitación fue aceptada por
                 <strong>{safe_participant}</strong>.</p>
              <p style="font-size:17px;line-height:1.6"><strong>Respuesta:</strong>
                 Sí, quiero ser tu novia.</p>
            </div>
            """,
        },
        {
            "sender": {"name": sender_name, "email": sender},
            "to": [{"email": participant_email}],
            "subject": "Nuestra historia comienza aquí",
            "textContent": (
                "Tu respuesta fue enviada correctamente.\n\n"
                "Gracias por decir que sí. Este es el comienzo de algo muy bonito."
            ),
            "htmlContent": """
            <div style="font-family:Georgia,serif;max-width:560px;margin:auto;padding:32px;
                        color:#3f2928;background:#fffaf5;border:1px solid #ead8cc;border-radius:18px">
              <p style="color:#b9504e;letter-spacing:.12em;text-transform:uppercase">Confirmación</p>
              <h1 style="font-size:32px;margin:8px 0 18px">Nuestra historia comienza aquí</h1>
              <p style="font-size:17px;line-height:1.6">Tu respuesta fue enviada correctamente.</p>
              <p style="font-size:17px;line-height:1.6">Gracias por decir que sí.
                 Este es el comienzo de algo muy bonito.</p>
            </div>
            """,
        },
    ]

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        for message in messages:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers=headers,
                json=message,
            )
            response.raise_for_status()


def _build_message(
    *,
    sender: str,
    sender_name: str,
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
    reply_to: str | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = f"{sender_name} <{sender}>"
    message["To"] = recipient
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def _send_acceptance_emails_sync(participant_email: str) -> None:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_FROM_EMAIL", username).strip()
    sender_name = os.getenv("SMTP_FROM_NAME", "Una pregunta especial").strip()
    target_email = os.getenv("TARGET_EMAIL", "saulofct222@gmail.com").strip()

    if not username or not password or not sender:
        raise EmailConfigurationError(
            "SMTP_USERNAME, SMTP_PASSWORD y SMTP_FROM_EMAIL deben estar configurados."
        )

    safe_participant = html.escape(participant_email)
    owner_message = _build_message(
        sender=sender,
        sender_name=sender_name,
        recipient=target_email,
        subject=f"¡Dijo que sí! Respuesta de {participant_email}",
        text_body=(
            "La respuesta fue aceptada.\n\n"
            f"Correo de quien respondió: {participant_email}\n"
            "Respuesta: Sí, quiero ser tu novia."
        ),
        html_body=f"""
        <div style="font-family:Georgia,serif;max-width:560px;margin:auto;padding:32px;
                    color:#3f2928;background:#fffaf5;border:1px solid #ead8cc;border-radius:18px">
          <p style="color:#b9504e;letter-spacing:.12em;text-transform:uppercase">Respuesta recibida</p>
          <h1 style="font-size:32px;margin:8px 0 18px">¡Dijo que sí!</h1>
          <p style="font-size:17px;line-height:1.6">La invitación fue aceptada por
             <strong>{safe_participant}</strong>.</p>
          <p style="font-size:17px;line-height:1.6"><strong>Respuesta:</strong>
             Sí, quiero ser tu novia.</p>
        </div>
        """,
        reply_to=participant_email,
    )

    participant_message = _build_message(
        sender=sender,
        sender_name=sender_name,
        recipient=participant_email,
        subject="Nuestra historia comienza aquí",
        text_body=(
            "Tu respuesta fue enviada correctamente.\n\n"
            "Gracias por decir que sí. Este es el comienzo de algo muy bonito."
        ),
        html_body="""
        <div style="font-family:Georgia,serif;max-width:560px;margin:auto;padding:32px;
                    color:#3f2928;background:#fffaf5;border:1px solid #ead8cc;border-radius:18px">
          <p style="color:#b9504e;letter-spacing:.12em;text-transform:uppercase">Confirmación</p>
          <h1 style="font-size:32px;margin:8px 0 18px">Nuestra historia comienza aquí</h1>
          <p style="font-size:17px;line-height:1.6">Tu respuesta fue enviada correctamente.</p>
          <p style="font-size:17px;line-height:1.6">Gracias por decir que sí.
             Este es el comienzo de algo muy bonito.</p>
        </div>
        """,
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)
        server.send_message(owner_message)
        server.send_message(participant_message)


async def send_acceptance_emails(participant_email: str) -> None:
    """Use Brevo over HTTPS in hosting, with SMTP as the local fallback."""
    if os.getenv("BREVO_API_KEY", "").strip():
        await _send_acceptance_emails_brevo(participant_email)
        return
    await asyncio.to_thread(_send_acceptance_emails_sync, participant_email)
