from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os


from .grpc_clients import RegistrationClient, VotingClient, GrpcurlError

load_dotenv()

app = FastAPI(title="VotingSystem-App Backend", version="0.2.1")

# -----------------------------
# CORS (Cross-Origin Resource Sharing)
# Necessário para permitir que o frontend (origem diferente) consuma a API.
# -----------------------------
allowed_origins = [
    # Desenvolvimento local (frontend)
    "http://127.0.0.1:5500",
    "http://localhost:5500",

    # Se testares o frontend noutro porto local
    "http://127.0.0.1:5173",
    "http://localhost:5173",

    # Produção (frontend publicado)
    "https://andremaciel.pt",
    "https://www.andremaciel.pt",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


registration = RegistrationClient()
voting = VotingClient()

# Mitigação local: impedir repetição da mesma credencial neste protótipo
USED_CREDENTIALS = set()


def _get(resp: dict, *keys, default=None):
    """
    Obtém a primeira chave existente em 'resp' (para suportar snake_case e lowerCamelCase),
    devolvendo 'default' se nenhuma existir.
    """
    for k in keys:
        if k in resp:
            return resp[k]
    return default


class RegisterIn(BaseModel):
    citizen_card_number: str = Field(min_length=1)


class VoteIn(BaseModel):
    voting_credential: str = Field(min_length=1)
    candidate_id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register")
def register(data: RegisterIn):
    """
    Fase 1 — Registo:
    Recebe citizen_card_number e obtém voting_credential via serviço AR (grpcurl).
    """
    try:
        resp = registration.issue_credential(data.citizen_card_number)
    except GrpcurlError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AR (grpcurl): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no registo: {e}")

    # Suporta snake_case e lowerCamelCase (Protobuf JSON mapping)
    is_eligible = bool(_get(resp, "is_eligible", "isEligible", default=False))
    voting_credential = _get(resp, "voting_credential", "votingCredential", default="")

    return {
        "is_eligible": is_eligible,
        "voting_credential": voting_credential,
    }


@app.get("/candidates")
def candidates():
    """
    Fase 2 (parte i) — Listagem de candidatos:
    Obtém a lista de candidatos via serviço AV (grpcurl).
    """
    try:
        resp = voting.get_candidates()  # lista de dicts: [{"id":..., "name":...}, ...]
    except GrpcurlError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AV (grpcurl): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao obter candidatos: {e}")

    return {"candidates": resp}


@app.post("/vote")
def do_vote(data: VoteIn):
    """
    Fase 2 (partes ii–iii) — Submissão de voto:
    Submete o voto com voting_credential e candidate_id.
    Inclui bloqueio local para evitar repetição da credencial no protótipo.
    """
    if data.voting_credential in USED_CREDENTIALS:
        raise HTTPException(
            status_code=409,
            detail="Esta credencial já foi usada nesta aplicação (bloqueio local do protótipo).",
        )

    try:
        resp = voting.vote(data.voting_credential, data.candidate_id)
    except GrpcurlError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AV (grpcurl): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao submeter voto: {e}")

    # Suporta snake_case e lowerCamelCase
    success = bool(_get(resp, "success", default=False))
    message = str(_get(resp, "message", default=""))

    if success:
        USED_CREDENTIALS.add(data.voting_credential)

    return {"success": success, "message": message}


@app.get("/results")
def results():
    """
    Fase 3 — Apuramento:
    Obtém resultados agregados via serviço AV (grpcurl).
    """
    try:
        resp = voting.get_results()  # lista de dicts: [{"id":..., "name":..., "votes":...}, ...]
    except GrpcurlError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao obter resultados (grpcurl): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao obter resultados: {e}")

    return {"results": resp}
