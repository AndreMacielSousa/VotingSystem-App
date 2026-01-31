// site/config.js
// Configuração do backend por ambiente:
// - Local (quando corres o frontend em http://127.0.0.1:5500): usa http://127.0.0.1:8000
// - Produção (andremaciel.pt): aponta para um endpoint HTTPS (a definir no Passo 3 para o backend)

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
