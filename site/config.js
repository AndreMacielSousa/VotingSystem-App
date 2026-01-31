// site/config.js
// Configuração do backend por ambiente:
// - Local (quando corres o frontend em http://127.0.0.1:5500): usa http://127.0.0.1:8000
// - Produção (andremaciel.pt): aponta para um endpoint HTTPS (a definir no Passo 3 para o backend)
/*
(function () {
  const host = window.location.hostname;

  // Ambiente local (localhost/127.0.0.1)
  const isLocal =
    host === "127.0.0.1" ||
    host === "localhost" ||
    host.endsWith(".local");

  // Em produção, idealmente apontar para:
  //  - um subdomínio HTTPS (ex.: https://api.andremaciel.pt)
  //  - ou um caminho proxy no mesmo domínio (ex.: https://andremaciel.pt/IS2026/api)
  const PROD_BACKEND_URL = "https://andremaciel.pt/IS2026/api";

  window.APP_CONFIG = {
    BACKEND_URL: isLocal ? "http://127.0.0.1:8000" : PROD_BACKEND_URL
  };
})();
*/

// site/config.js
// Configuração por ambiente:
// - Local: backend em http://127.0.0.1:8000 (teste completo)
// - Online (andremaciel.pt): sem backend por limitações técnicas do alojamento -> UI informa e aponta para GitHub

(function () {
  const host = window.location.hostname;

  const isLocal =
    host === "127.0.0.1" ||
    host === "localhost";

  window.APP_CONFIG = {
    // Local: backend a correr com uvicorn
    BACKEND_URL: isLocal ? "http://127.0.0.1:8000" : "https://andremaciel.pt",

    // Usado pelo frontend para mostrar a nota online (link “humano”)
    GITHUB_REPO_URL: "https://github.com/AndreMacielSousa/VotingSystem-App",

    // Flag para o UI mostrar um aviso explícito no ambiente online
    IS_ONLINE_DEMO: !isLocal
  };
})();
