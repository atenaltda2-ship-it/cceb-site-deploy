import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL_REMETENTE = os.getenv("SMTP_EMAIL_REMETENTE", "")
SMTP_SENHA_APP = os.getenv("SMTP_SENHA_APP", "")
SMTP_EMAIL_DESTINO = os.getenv("SMTP_EMAIL_DESTINO", "")


class FormularioInscricao(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    nascimento: str
    restricao: str = "Nenhuma restrição"
    atividade: list[str] = []
    obs: str | None = None


app = FastAPI(title="CCEB - API de Inscrição")

origins_env = os.getenv("ALLOWED_ORIGINS")
allowed_origins = (
    [o.strip() for o in origins_env.split(",") if o.strip()]
    if origins_env
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


def _formatar_corpo(dados: FormularioInscricao) -> str:
    atividades = ", ".join(dados.atividade) if dados.atividade else "Nenhuma selecionada"
    return (
        f"Nova inscrição recebida no CCEB:\n"
        f"\n"
        f"Nome: {dados.nome}\n"
        f"E-mail: {dados.email}\n"
        f"Telefone: {dados.telefone}\n"
        f"Data de Nascimento: {dados.nascimento}\n"
        f"Restrição Alimentar: {dados.restricao}\n"
        f"Atividades de Interesse: {atividades}\n"
        f"Observações: {dados.obs or '—'}\n"
    )


@app.post("/enviar-inscricao")
async def enviar_inscricao(dados: FormularioInscricao):
    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL_REMETENTE
    msg["To"] = SMTP_EMAIL_DESTINO
    msg["Subject"] = f"CCEB — Nova Inscrição: {dados.nome}"
    msg.attach(MIMEText(_formatar_corpo(dados), "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL_REMETENTE, SMTP_SENHA_APP)
            server.sendmail(SMTP_EMAIL_REMETENTE, SMTP_EMAIL_DESTINO, msg.as_string())
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar e-mail: {exc}",
        )

    return {"mensagem": "Inscrição recebida com sucesso!"}
