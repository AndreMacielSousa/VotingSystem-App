# Voting System (gRPC) — Aplicação Web (Tarefa 3)

Este repositório contém uma aplicação web simples que implementa o processo de votação em **3 fases** (Registo → Votação → Apuramento), consumindo serviços **gRPC remotos** disponibilizados para o trabalho final.

A aplicação **não implementa** os serviços gRPC; atua como **cliente gRPC** e orquestra o processo descrito no enunciado.

---

## 1. Serviços gRPC consumidos

Endpoint:
- `ken01.utad.pt:9091`

Contratos (ficheiros `.proto` neste repositório):
- `Protos/voter.proto`
  - `voting.VoterRegistrationService/IssueVotingCredential`
  - Campos principais: `citizen_card_number`, `is_eligible`, `voting_credential`
- `Protos/voting.proto`
  - `voting.VotingService/GetCandidates`
  - `voting.VotingService/Vote`
  - `voting.VotingService/GetResults`
  - Campos principais: `voting_credential`, `candidate_id`, `success`, `message`, `results`

---

## 2. Processo implementado (3 fases)

### Fase 1 — Registo
1. O utilizador introduz o número de Cartão de Cidadão (`citizen_card_number`).
2. A aplicação invoca `IssueVotingCredential`.
3. Se `is_eligible = true`, guarda a `voting_credential` na sessão e avança para a Fase 2.
4. Caso contrário, bloqueia o avanço.

### Fase 2 — Votação
1. A aplicação invoca `GetCandidates` e apresenta a lista.
2. O utilizador seleciona o candidato (por `id`).
3. A aplicação invoca `Vote` com `{voting_credential, candidate_id}`.
4. Se o voto for aceite (`success = true`), a aplicação marca o estado `has_voted = true`.

> Nota de robustez (baseada nos testes da Tarefa 2):  
> o mock aceita reutilização da mesma credencial. Por esse motivo, a aplicação implementa um bloqueio local por sessão após um voto aceite.

### Fase 3 — Apuramento
1. A aplicação invoca `GetResults`.
2. Apresenta resultados agregados (`candidato`, `votos`).

---

## 3. Requisitos

- Python 3.11+ (recomendado)
- Dependências em `requirements.txt`

---

## 4. Instalação e execução local

### 4.1 Criar ambiente virtual
```powershell
python -m venv .venv
.\.venv\Scripts\activate

```

### 4.2 Instalar dependências
```powershell
pip install -r requirements.txt
```

### 4.3 Executar
```powershell
python app.py
```

Aceder em: http://127.0.0.1:5000

### 5. Testes rápidos com grpcurl (validação do endpoint)
Executar a partir de uma pasta que contenha Protos/.

### 5.1 Emitir credencial
```powershell
'{"citizen_card_number":"123456789"}' | grpcurl -insecure -proto Protos/voter.proto -d "@" ken01.utad.pt:9091 voting.VoterRegistrationService/IssueVotingCredential

```
### 5.2 Obter candidatos
```powershell
grpcurl -insecure -proto Protos/voting.proto ken01.utad.pt:9091 voting.VotingService/GetCandidates
```

### 5.3 Votar (exemplo)
```powershell
'{"voting_credential":"CRED-ABC-123","candidate_id":1}' | grpcurl -insecure -proto Protos/voting.proto -d "@" ken01.utad.pt:9091 voting.VotingService/Vote
```
### 5.4 Obter resultados
```powershell
grpcurl -insecure -proto Protos/voting.proto ken01.utad.pt:9091 voting.VotingService/GetResults
```

## 6. Deploy e publicação

### Publicação em andremaciel.pt/IS2026

## 7. Estrutura do projeto

```cpp
VotingSystem-App/
├─ app.py
├─ grpc_clients.py
├─ Protos/
├─ templates/
├─ static/
├─ requirements.txt
├─ Procfile
└─ README.md
```

## Links

- Repositório: https://github.com/AndreMacielSousa/VotingSystem-App
- Página pública (docente): https://andremaciel.pt/IS2026/
- Aplicação em execução: (a preencher após deploy)

## 8. Autor

Andre Sousa — MEIW / UAb-UTAD




