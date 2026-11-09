/*
 * Layout compartilhado das telas dos módulos: menu lateral, topo,
 * modal e avisos. Assim cada página só precisa escrever o próprio conteúdo.
 *
 * Como usar numa página que fica dentro de uma pasta (ex: pacientes/index.html):
 *
 *   <body>
 *     <div id="conteudo-pagina"> ...o conteúdo da página... </div>
 *     <script src="../services/api.js"></script>
 *     <script src="../services/layout.js"></script>
 *     <script> montarLayout({ ativo: "pacientes", titulo: "Pacientes" }); </script>
 *   </body>
 */

const ITENS_MENU = [
  { chave: "dashboard", rotulo: "Dashboard", icone: "bi-grid", href: "index.html" },
  { chave: "pacientes", rotulo: "Pacientes", icone: "bi-people", href: "pacientes/index.html" },
  { chave: "medicos", rotulo: "Médicos", icone: "bi-person-badge", href: "agenda/index.html#medicos" },
  { chave: "agenda", rotulo: "Agendamentos", icone: "bi-calendar3", href: "agenda/index.html" },
  { chave: "resultados", rotulo: "Resultados", icone: "bi-file-earmark-text", href: "farmacia-exames/index.html" },
  { chave: "financeiro", rotulo: "Financeiro", icone: "bi-bar-chart", href: "financeiro/index.html" },
  { chave: "convenios", rotulo: "Convênios", icone: "bi-credit-card-2-front", href: "pacientes/index.html#convenios" },
];

// ---------- Utilitários ----------
function escapeHtml(valor) {
  const trocas = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(valor ?? "").replace(/[&<>"']/g, (c) => trocas[c]);
}

function formatarData(iso) {
  if (!iso) return "—";
  const [ano, mes, dia] = String(iso).split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarDataHora(iso) {
  if (!iso) return "—";
  const hora = String(iso).split("T")[1];
  return hora ? `${formatarData(iso)} ${hora.slice(0, 5)}` : formatarData(iso);
}

function formatarCpf(cpf) {
  const numeros = String(cpf ?? "").replace(/\D/g, "");
  if (numeros.length !== 11) return cpf || "—";
  return numeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

function hojeISO() {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  const dia = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-${dia}`;
}

function lerPerfilDoToken() {
  try {
    const base64 = obterToken().split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64)).perfil || "usuário";
  } catch (e) {
    return "usuário";
  }
}

// ---------- Layout ----------
function marcarMenuAtivo(chave) {
  document.querySelectorAll(".sidebar nav a").forEach((a) => {
    a.classList.toggle("ativo", a.dataset.chave === chave);
  });
}

function montarLayout({ ativo, titulo, raiz = ".." }) {
  if (!estaLogado()) {
    location.href = `${raiz}/index.html`;
    return false;
  }

  const perfil = lerPerfilDoToken();
  const itens = ITENS_MENU.map(
    (i) =>
      `<a href="${raiz}/${i.href}" data-chave="${i.chave}" class="${i.chave === ativo ? "ativo" : ""}">` +
      `<i class="bi ${i.icone}"></i> ${i.rotulo}</a>`
  ).join("");

  const casca = document.createElement("div");
  casca.className = "layout";
  casca.innerHTML = `
    <aside class="sidebar">
      <div class="marca">
        <div class="icone"><i class="bi bi-hospital"></i></div>
        <div>
          <div class="nome">MedCenter</div>
          <div class="subtitulo">Hospital Geral</div>
        </div>
      </div>
      <nav>${itens}</nav>
      <div class="rodape-usuario">
        <div class="avatar-circulo">${escapeHtml(perfil.slice(0, 2).toUpperCase())}</div>
        <div>
          <div class="nome">Usuário logado</div>
          <div class="email">perfil: ${escapeHtml(perfil)}</div>
        </div>
      </div>
    </aside>
    <div class="conteudo">
      <header class="topo">
        <div>
          <h1 id="titulo-pagina">${escapeHtml(titulo)}</h1>
          <p class="data-hoje" id="data-hoje"></p>
        </div>
        <div class="topo-acoes">
          <button class="botao botao-secundario botao-sm" id="btn-sair">Sair</button>
        </div>
      </header>
      <div class="pagina" id="area-pagina"></div>
    </div>`;

  const conteudo = document.getElementById("conteudo-pagina");
  document.body.prepend(casca);
  document.getElementById("area-pagina").appendChild(conteudo);

  document.getElementById("data-hoje").textContent = new Date().toLocaleDateString("pt-BR", {
    weekday: "long", day: "2-digit", month: "long", year: "numeric",
  });
  document.getElementById("btn-sair").addEventListener("click", () => {
    logout();
    location.href = `${raiz}/index.html`;
  });

  const avisos = document.createElement("div");
  avisos.id = "toasts";
  document.body.appendChild(avisos);

  return true;
}

// ---------- Avisos ----------
function mostrarAviso(texto, tipo = "sucesso") {
  const aviso = document.createElement("div");
  aviso.className = `toast toast-${tipo}`;
  aviso.textContent = texto;
  document.getElementById("toasts").appendChild(aviso);
  setTimeout(() => aviso.remove(), 4000);
}

// ---------- Modal ----------
function fecharModal() {
  const atual = document.getElementById("modal-fundo");
  if (atual) atual.remove();
}

function mostrarErroModal(mensagem) {
  const caixa = document.getElementById("modal-erro");
  if (!caixa) return;
  caixa.textContent = mensagem;
  caixa.style.display = "block";
}

/*
 * Abre um modal. Se "aoSalvar" for informado, aparece o botão Salvar:
 * ele chama aoSalvar(corpoDoModal); se der erro (throw new Error("..."))
 * a mensagem aparece no modal; se não der erro, o modal fecha sozinho.
 * Retorna o elemento do corpo do modal, para ligar eventos nos campos.
 */
function abrirModal(titulo, corpoHtml, opcoes = {}) {
  const { textoSalvar = "Salvar", aoSalvar = null, largura = "520px" } = opcoes;
  fecharModal();

  const fundo = document.createElement("div");
  fundo.className = "modal-fundo";
  fundo.id = "modal-fundo";
  fundo.innerHTML = `
    <div class="modal-caixa" style="max-width:${largura}">
      <div class="modal-topo">
        <h2>${escapeHtml(titulo)}</h2>
        <button type="button" class="modal-x" aria-label="Fechar">&times;</button>
      </div>
      <div class="modal-corpo">${corpoHtml}</div>
      <div class="modal-erro" id="modal-erro" style="display:none;"></div>
      <div class="modal-rodape">
        <button type="button" class="botao botao-secundario" data-acao="cancelar">${aoSalvar ? "Cancelar" : "Fechar"}</button>
        ${aoSalvar ? `<button type="button" class="botao botao-primario" data-acao="salvar">${escapeHtml(textoSalvar)}</button>` : ""}
      </div>
    </div>`;
  document.body.appendChild(fundo);

  fundo.addEventListener("click", (e) => { if (e.target === fundo) fecharModal(); });
  fundo.querySelector(".modal-x").addEventListener("click", fecharModal);
  fundo.querySelector('[data-acao="cancelar"]').addEventListener("click", fecharModal);

  const corpo = fundo.querySelector(".modal-corpo");
  const botaoSalvar = fundo.querySelector('[data-acao="salvar"]');
  if (botaoSalvar) {
    botaoSalvar.addEventListener("click", async () => {
      botaoSalvar.disabled = true;
      document.getElementById("modal-erro").style.display = "none";
      try {
        await aoSalvar(corpo);
        fecharModal();
      } catch (erro) {
        mostrarErroModal(erro.message);
        botaoSalvar.disabled = false;
      }
    });
  }
  return corpo;
}
