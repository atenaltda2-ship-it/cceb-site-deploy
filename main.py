import os

import resend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

load_dotenv()

SMTP_EMAIL_DESTINO = os.getenv("SMTP_EMAIL_DESTINO", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY


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
    params = {
        "from": "CCEB Site <onboarding@resend.dev>",
        "to": [SMTP_EMAIL_DESTINO],
        "subject": f"CCEB — Nova Inscrição: {dados.nome}",
        "text": _formatar_corpo(dados),
    }

    try:
        email_response = resend.Emails.send(params)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar e-mail: {exc}",
        )

    return {"mensagem": "Inscrição recebida com sucesso!"}
