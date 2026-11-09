/*
 * Funções compartilhadas para falar com o backend.
 * Todo módulo do frontend (pacientes, agenda, etc.) deve importar este
 * arquivo com: <script src="../services/api.js"></script>
 */

const API_BASE_URL = "http://127.0.0.1:8000";

// Evita mostrar o aviso de sessão expirada várias vezes quando várias chamadas falham juntas
let sessaoExpiradaTratada = false;

function salvarToken(token) {
  localStorage.setItem("medcenter_token", token);
}

function obterToken() {
  return localStorage.getItem("medcenter_token");
}

function removerToken() {
  localStorage.removeItem("medcenter_token");
}

function estaLogado() {
  return !!obterToken();
}

/**
 * Faz login na API e guarda o token.
 * email/senha -> lança erro se as credenciais estiverem erradas.
 */
async function login(email, senha) {
  const corpo = new URLSearchParams();
  corpo.append("username", email);
  corpo.append("password", senha);

  const resposta = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: corpo,
  });

  if (!resposta.ok) {
    throw new Error("Email ou senha incorretos");
  }

  const dados = await resposta.json();
  salvarToken(dados.access_token);
  return dados;
}

function logout() {
  removerToken();
}

/**
 * Chama qualquer rota da API, já incluindo o token de login quando existir.
 * Uso: const pacientes = await apiFetch("/pacientes");
 *      const novo = await apiFetch("/pacientes", { method: "POST", body: JSON.stringify(dados) });
 */
async function apiFetch(caminho, opcoes = {}) {
  const token = obterToken();
  const cabecalhos = {
    "Content-Type": "application/json",
    ...(opcoes.headers || {}),
  };
  if (token) {
    cabecalhos["Authorization"] = `Bearer ${token}`;
  }

  const resposta = await fetch(`${API_BASE_URL}${caminho}`, {
    ...opcoes,
    headers: cabecalhos,
  });

  // Token vencido ou inválido (ex: a SECRET_KEY do servidor mudou): limpa o login
  // e recarrega a página, que volta para a tela de entrada.
  if (resposta.status === 401 && token) {
    if (!sessaoExpiradaTratada) {
      sessaoExpiradaTratada = true;
      removerToken();
      alert("Sua sessão expirou. Entre novamente.");
      location.reload();
    }
    throw new Error("Sessão expirada. Entre novamente.");
  }

  if (!resposta.ok) {
    const corpoErro = await resposta.json().catch(() => ({}));
    throw new Error(corpoErro.detail || `Erro ${resposta.status} ao chamar ${caminho}`);
  }

  if (resposta.status === 204) return null;
  return resposta.json();
}
