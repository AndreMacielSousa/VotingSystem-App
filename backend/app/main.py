from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .grpc_clients import RegistrationClient, VotingClient

load_dotenv()

app = FastAPI(title="VotingSystem-App Backend", version="0.1.0")

registration = RegistrationClient()
voting = VotingClient()

# Mitigação local: impedir repetição da mesma credencial neste protótipo
USED_CREDENTIALS = set()


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
    try:
        resp = registration.issue_credential(data.citizen_card_number)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AR: {e}")

    return {
        "is_eligible": resp.is_eligible,
        "voting_credential": resp.voting_credential
    }


@app.get("/candidates")
def candidates():
    try:
        resp = voting.get_candidates()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AV: {e}")

    return {
        "candidates": [{"id": c.id, "name": c.name} for c in resp.candidates]
    }


@app.post("/vote")
def do_vote(data: VoteIn):
    # Bloqueio local para não aceitar “votos repetidos” no protótipo
    if data.voting_credential in USED_CREDENTIALS:
        raise HTTPException(status_code=409, detail="Esta credencial já foi usada nesta aplicação (bloqueio local).")

    try:
        resp = voting.vote(data.voting_credential, data.candidate_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao contactar AV: {e}")

    if resp.success:
        USED_CREDENTIALS.add(data.voting_credential)

    return {"success": resp.success, "message": resp.message}


@app.get("/results")
def results():
    try:
        resp = voting.get_results()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao obter resultados: {e}")

    return {
        "results": [{"id": r.id, "name": r.name, "votes": r.votes} for r in resp.results]
    }
