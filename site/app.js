// site/app.js

const BACKEND_URL = (window.APP_CONFIG && window.APP_CONFIG.BACKEND_URL)
  ? window.APP_CONFIG.BACKEND_URL.replace(/\/+$/, "")
  : "http://127.0.0.1:8000";

const els = {
  backendUrl: document.getElementById("backend-url"),

  pillReg: document.getElementById("pill-reg"),
  pillVote: document.getElementById("pill-vote"),
  pillRes: document.getElementById("pill-res"),

  cc: document.getElementById("cc"),
  btnRegister: document.getElementById("btn-register"),
  btnClear: document.getElementById("btn-clear"),
  regMsg: document.getElementById("reg-msg"),

  candidate: document.getElementById("candidate"),
  cred: document.getElementById("cred"),
  btnLoadCandidates: document.getElementById("btn-load-candidates"),
  btnVote: document.getElementById("btn-vote"),
  voteMsg: document.getElementById("vote-msg"),

  btnResults: document.getElementById("btn-results"),
  resMsg: document.getElementById("res-msg"),
  resTable: document.getElementById("res-table"),
  resTbody: document.getElementById("res-tbody"),
};

const state = {
  credential: null,
  hasVoted: false,
  candidates: [],
};

function setMsg(el, kind, text) {
  el.classList.remove("ok", "warn", "err");
  if (kind) el.classList.add(kind);
  el.textContent = text;
}

function setStepPills() {
  // Registo fica OK se há credencial
  els.pillReg.classList.toggle("ok", !!state.credential);
  els.pillReg.classList.toggle("active", !state.credential);

  // Votação ativa se há credencial e ainda não votou
  const voteActive = !!state.credential && !state.hasVoted;
  els.pillVote.classList.toggle("active", voteActive);
  els.pillVote.classList.toggle("ok", !!state.credential && state.hasVoted);

  // Apuramento sempre disponível
  els.pillRes.classList.add("active");
}

function saveSession() {
  sessionStorage.setItem("vs_credential", state.credential || "");
  sessionStorage.setItem("vs_hasVoted", state.hasVoted ? "1" : "0");
}

function loadSession() {
  const cred = sessionStorage.getItem("vs_credential") || "";
  const hv = sessionStorage.getItem("vs_hasVoted") === "1";
  state.credential = cred || null;
  state.hasVoted = hv;
}

function syncUI() {
  els.backendUrl.textContent = BACKEND_URL;

  els.cred.value = state.credential || "";
  els.btnLoadCandidates.disabled = !state.credential;
  els.candidate.disabled = !state.credential;

  const canVote =
    !!state.credential &&
    !state.hasVoted &&
    !!els.candidate.value;

  els.btnVote.disabled = !canVote;

  if (state.hasVoted) {
    setMsg(els.voteMsg, "ok", "Voto já submetido nesta sessão. Para nova simulação, limpe a sessão.");
  }

  setStepPills();
}

async function apiGet(path) {
  const url = `${BACKEND_URL}${path}`;
  const res = await fetch(url, { method: "GET" });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.detail ? String(data.detail) : `Erro HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

async function apiPost(path, body) {
  const url = `${BACKEND_URL}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.detail ? String(data.detail) : `Erro HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function isLikelyCC(value) {
  return /^[0-9]{6,12}$/.test(value.trim());
}

async function doRegister() {
  const cc = els.cc.value.trim();
  if (!isLikelyCC(cc)) {
    setMsg(els.regMsg, "warn", "Introduza um número válido (apenas dígitos).");
    return;
  }

  setMsg(els.regMsg, null, "A emitir credencial...");
  try {
    const r = await apiPost("/register", { citizen_card_number: cc });

    if (r.is_eligible === true && r.voting_credential) {
      state.credential = r.voting_credential;
      state.hasVoted = false;
      saveSession();
      setMsg(els.regMsg, "ok", `Eleitor elegível. Credencial emitida: ${r.voting_credential}`);
      setMsg(els.voteMsg, null, "Carregue candidatos e submeta o voto.");
    } else {
      state.credential = null;
      state.hasVoted = false;
      saveSession();
      setMsg(els.regMsg, "warn", "Eleitor não elegível (mock). Repita com outro número.");
    }
  } catch (e) {
    setMsg(els.regMsg, "err", `Falha no registo: ${e.message}`);
  } finally {
    syncUI();
  }
}

async function loadCandidates() {
  setMsg(els.voteMsg, null, "A carregar candidatos...");
  try {
    const r = await apiGet("/candidates");
    const list = Array.isArray(r.candidates) ? r.candidates : [];
    state.candidates = list;

    // preencher select
    els.candidate.innerHTML = "";
    const opt0 = document.createElement("option");
    opt0.value = "";
    opt0.textContent = "(selecionar candidato)";
    els.candidate.appendChild(opt0);

    for (const c of list) {
      const opt = document.createElement("option");
      opt.value = String(c.id);
      opt.textContent = `${c.id} — ${c.name}`;
      els.candidate.appendChild(opt);
    }

    setMsg(els.voteMsg, "ok", `Candidatos carregados: ${list.length}.`);
  } catch (e) {
    setMsg(els.voteMsg, "err", `Falha ao obter candidatos: ${e.message}`);
  } finally {
    syncUI();
  }
}

async function doVote() {
  if (!state.credential) {
    setMsg(els.voteMsg, "warn", "Sem credencial. Faça primeiro o registo.");
    return;
  }
  if (state.hasVoted) {
    setMsg(els.voteMsg, "warn", "Voto já submetido nesta sessão.");
    return;
  }
  const candidateId = Number(els.candidate.value);
  if (!candidateId) {
    setMsg(els.voteMsg, "warn", "Selecione um candidato.");
    return;
  }

  setMsg(els.voteMsg, null, "A submeter voto...");
  try {
    const r = await apiPost("/vote", {
      voting_credential: state.credential,
      candidate_id: candidateId,
    });

    if (r.success === true) {
      state.hasVoted = true;
      saveSession();
      setMsg(els.voteMsg, "ok", r.message || "Voto aceite.");
    } else {
      setMsg(els.voteMsg, "warn", r.message || "Voto recusado.");
    }
  } catch (e) {
    setMsg(els.voteMsg, "err", `Falha ao votar: ${e.message}`);
  } finally {
    syncUI();
  }
}

function renderResults(rows) {
  els.resTbody.innerHTML = "";
  for (const r of rows) {
    const tr = document.createElement("tr");

    const tdId = document.createElement("td");
    tdId.textContent = String(r.id ?? "");
    const tdName = document.createElement("td");
    tdName.textContent = String(r.name ?? "");
    const tdVotes = document.createElement("td");
    tdVotes.textContent = String(r.votes ?? "");

    tr.appendChild(tdId);
    tr.appendChild(tdName);
    tr.appendChild(tdVotes);
    els.resTbody.appendChild(tr);
  }
}

async function loadResults() {
  setMsg(els.resMsg, null, "A obter resultados...");
  try {
    const r = await apiGet("/results");
    const rows = Array.isArray(r.results) ? r.results : [];
    renderResults(rows);

    els.resTable.style.display = rows.length ? "table" : "none";
    setMsg(els.resMsg, "ok", `Resultados carregados: ${rows.length} candidatos.`);
  } catch (e) {
    els.resTable.style.display = "none";
    setMsg(els.resMsg, "err", `Falha ao obter resultados: ${e.message}`);
  } finally {
    syncUI();
  }
}

function clearSession() {
  sessionStorage.removeItem("vs_credential");
  sessionStorage.removeItem("vs_hasVoted");
  state.credential = null;
  state.hasVoted = false;
  state.candidates = [];
  els.candidate.innerHTML = `<option value="">(carregar candidatos)</option>`;
  setMsg(els.regMsg, null, "Sessão limpa. Pode iniciar novo registo.");
  setMsg(els.voteMsg, null, "Sem ações de votação.");
  setMsg(els.resMsg, null, "Sem resultados carregados.");
  els.resTable.style.display = "none";
  syncUI();
}

// Eventos
els.btnRegister.addEventListener("click", doRegister);
els.btnLoadCandidates.addEventListener("click", loadCandidates);
els.btnVote.addEventListener("click", doVote);
els.btnResults.addEventListener("click", loadResults);
els.btnClear.addEventListener("click", clearSession);

els.candidate.addEventListener("change", () => syncUI());

document.addEventListener("DOMContentLoaded", () => {
  loadSession();
  syncUI();

  // Se houver credencial, sugerir carregar candidatos
  if (state.credential && !state.hasVoted) {
    setMsg(els.regMsg, "ok", "Credencial encontrada na sessão. Pode carregar candidatos e votar.");
    setMsg(els.voteMsg, null, "Carregue candidatos e submeta o voto.");
  }
});
