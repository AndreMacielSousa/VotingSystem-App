import os
import grpc

from . import voter_pb2, voter_pb2_grpc
from . import voting_pb2, voting_pb2_grpc

GRPC_TARGET = os.getenv("GRPC_TARGET", "ken01.utad.pt:9091")


def _channel():
    # Nota: nos testes com grpcurl foi usado -insecure (sem validação TLS).
    # Aqui replicamos o comportamento com canal inseguro.
    return grpc.insecure_channel(GRPC_TARGET)


class RegistrationClient:
    def issue_credential(self, citizen_card_number: str) -> voter_pb2.VoterResponse:
        with _channel() as channel:
            stub = voter_pb2_grpc.VoterRegistrationServiceStub(channel)
            req = voter_pb2.VoterRequest(citizen_card_number=citizen_card_number)
            return stub.IssueVotingCredential(req)


class VotingClient:
    def get_candidates(self) -> voting_pb2.GetCandidatesResponse:
        with _channel() as channel:
            stub = voting_pb2_grpc.VotingServiceStub(channel)
            return stub.GetCandidates(voting_pb2.GetCandidatesRequest())

    def vote(self, voting_credential: str, candidate_id: int) -> voting_pb2.VoteResponse:
        with _channel() as channel:
            stub = voting_pb2_grpc.VotingServiceStub(channel)
            req = voting_pb2.VoteRequest(voting_credential=voting_credential, candidate_id=candidate_id)
            return stub.Vote(req)

    def get_results(self) -> voting_pb2.GetResultsResponse:
        with _channel() as channel:
            stub = voting_pb2_grpc.VotingServiceStub(channel)
            return stub.GetResults(voting_pb2.GetResultsRequest())
