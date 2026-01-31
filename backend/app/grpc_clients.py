import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

GRPC_TARGET = os.getenv("GRPC_TARGET", "ken01.utad.pt:9091")

# Se grpcurl estiver no PATH, deixa assim. Se não estiver, aponta para o executável completo:
# Ex.: r"C:\tools\grpcurl\grpcurl.exe"
GRPCURL_BIN = os.getenv("GRPCURL_BIN", "grpcurl")


class GrpcurlError(RuntimeError):
    pass


# Estrutura esperada:
# backend/
#   app/
#   protos/
#     voter.proto
#     voting.proto
BASE_DIR = Path(__file__).resolve().parents[1]          # .../backend
PROTOS_DIR = BASE_DIR / "protos"                        # .../backend/protos

VOTER_PROTO_NAME = "voter.proto"
VOTING_PROTO_NAME = "voting.proto"


def _run_grpcurl(proto_name: str, full_method: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Invoca grpcurl com -insecure (TLS sem validação de certificado).
    Importante: quando usamos -proto, definimos também -import-path, e executamos com cwd=backend/.
    """
    cmd = [
        GRPCURL_BIN,
        "-insecure",
        "-import-path", str(PROTOS_DIR),
        "-proto", proto_name,
        "-d", "@",
        GRPC_TARGET,
        full_method,
    ]

    stdin = ""
    if payload is not None:
        stdin = json.dumps(payload)

    try:
        p = subprocess.run(
            cmd,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
            cwd=str(BASE_DIR),   # garante que o proto_name é resolvido corretamente
        )
    except FileNotFoundError as e:
        raise GrpcurlError(
            "grpcurl não encontrado. "
            "Define GRPCURL_BIN com o caminho completo para o grpcurl.exe (ou adiciona ao PATH). "
            f"Detalhe: {e}"
        ) from e

    if p.returncode != 0:
        raise GrpcurlError(
            f"Falha grpcurl (code={p.returncode}). "
            f"STDERR: {p.stderr.strip()} | STDOUT: {p.stdout.strip()}"
        )

    out = p.stdout.strip()
    if not out:
        return {}

    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        raise GrpcurlError(f"Resposta grpcurl não é JSON válido: {out}") from e


class RegistrationClient:
    def issue_credential(self, citizen_card_number: str) -> Dict[str, Any]:
        return _run_grpcurl(
            VOTER_PROTO_NAME,
            "voting.VoterRegistrationService/IssueVotingCredential",
            {"citizen_card_number": citizen_card_number},
        )


class VotingClient:
    def get_candidates(self) -> List[Dict[str, Any]]:
        data = _run_grpcurl(
            VOTING_PROTO_NAME,
            "voting.VotingService/GetCandidates",
            {},
        )
        return data.get("candidates", [])

    def vote(self, voting_credential: str, candidate_id: int) -> Dict[str, Any]:
        return _run_grpcurl(
            VOTING_PROTO_NAME,
            "voting.VotingService/Vote",
            {"voting_credential": voting_credential, "candidate_id": candidate_id},
        )

    def get_results(self) -> List[Dict[str, Any]]:
        data = _run_grpcurl(
            VOTING_PROTO_NAME,
            "voting.VotingService/GetResults",
            {},
        )
        return data.get("results", [])
