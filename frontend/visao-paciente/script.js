/*
 * Visão do paciente: uma linha do tempo única com consultas, receitas,
 * exames, internações e cobranças. Os dados vêm de um só endpoint:
 *   GET /visao/pacientes/{id}/linha-do-tempo
 */

const el = (id) => document.getElementById(id);

const TIPOS = {
  consulta:   { rotulo: "Consultas",   icone: "bi-calendar-check" },
  prescricao: { rotulo: "Receitas",    icone: "bi-capsule" },
  exame:      { rotulo: "Exames",      icone: "bi-clipboard2-pulse" },
  internacao: { rotulo: "Internações", icone: "bi-hospital" },
  alta:       { rotulo: "Internações", icone: "bi-box-arrow-right" },
  cobranca:   { rotulo: "Cobranças",   icone: "bi-cash-coin" },
};

const CLASSE_STATUS = {
  realizada: "pill-sucesso", pago: "pill-sucesso", concluido: "pill-sucesso", alta: "pill-sucesso", encerrada: "pill-sucesso",
  agendada: "pill-info", ativa: "pill-info",
  pendente: "pill-alerta",
  cancelada: "pill-critico", cancelado: "pill-critico",
};

let visao = null;
let filtro = "todos";

function moeda(v) {
  return Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function iniciais(nome) {
  return String(nome || "?").split(" ").filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
}

async function iniciar() {
  if (!montarLayout({ ativo: "visao", titulo: "Visão do paciente" })) return;

  try {
    const pacientes = await apiFetch("/pacientes");
    pacientes.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
    el("sel-paciente").innerHTML =
      `<option value="">Selecione um paciente...</option>` +
      pacientes.map((p) => `<option value="${p.id_paciente}">${escapeHtml(p.nome)}</option>`).join("");
  } catch (e) {
    mostrarAviso("Não foi possível carregar os pacientes: " + e.message, "erro");
    return;
  }

  el("sel-paciente").addEventListener("change", (e) => {
    if (e.target.value) carregar(e.target.value);
  });

  // permite abrir direto: visao-paciente/index.html?id=3
  const id = new URLSearchParams(location.search).get("id");
  if (id) {
    el("sel-paciente").value = id;
    carregar(id);
  }
}

async function carregar(id) {
  el("area-visao").innerHTML = `<div class="card vazio">Carregando...</div>`;
  try {
    visao = await apiFetch(`/visao/pacientes/${id}/linha-do-tempo`);
    filtro = "todos";
    desenhar();
  } catch (e) {
    el("area-visao").innerHTML = `<div class="card vazio">${escapeHtml(e.message)}</div>`;
  }
}

function desenhar() {
  const p = visao.paciente;
  const r = visao.resumo;

  const contatos = p.contatos
    .map((c) => `<span><i class="bi ${c.tipo === "email" ? "bi-envelope" : "bi-telephone"}"></i>${escapeHtml(c.valor)}${c.preferencial ? " ★" : ""}</span>`)
    .join("");

  const alertas = [];
  if (r.internado_agora) alertas.push(`<div class="vp-alerta"><i class="bi bi-hospital"></i><strong>Paciente internado agora.</strong></div>`);
  if (r.exames_sem_resultado > 0) alertas.push(`<div class="vp-alerta"><i class="bi bi-hourglass-split"></i>${r.exames_sem_resultado} exame(s) aguardando resultado.</div>`);
  if (r.total_pendente > 0) alertas.push(`<div class="vp-alerta"><i class="bi bi-cash-coin"></i>Cobranças pendentes: <strong>${moeda(r.total_pendente)}</strong>.</div>`);

  el("area-visao").innerHTML = `
    <div class="card vp-cabecalho">
      <div class="vp-avatar">${escapeHtml(iniciais(p.nome))}</div>
      <div class="vp-dados">
        <h2>${escapeHtml(p.nome)}</h2>
        <div class="vp-meta">
          <span><i class="bi bi-person"></i>${p.idade != null ? p.idade + " anos" : "idade não informada"}${p.sexo ? " · " + escapeHtml(p.sexo) : ""}</span>
          <span><i class="bi bi-card-text"></i>CPF ${escapeHtml(formatarCpf(p.cpf))}</span>
          <span><i class="bi bi-droplet"></i>Sangue ${escapeHtml(p.tipo_sangue || "—")}</span>
          <span><i class="bi bi-credit-card-2-front"></i>${p.convenio ? escapeHtml(p.convenio) + (p.numero_carteirinha ? " · " + escapeHtml(p.numero_carteirinha) : "") : "Particular"}</span>
          ${contatos}
        </div>
        ${p.observacoes_prontuario ? `<div class="vp-obs"><strong>Prontuário:</strong> ${escapeHtml(p.observacoes_prontuario)}</div>` : ""}
      </div>
    </div>

    ${alertas.join("")}

    <div class="vp-resumo">
      <div class="card"><div class="n">${r.consultas}</div><div class="r">Consultas</div></div>
      <div class="card"><div class="n">${r.prescricoes}</div><div class="r">Receitas</div></div>
      <div class="card"><div class="n">${r.exames}</div><div class="r">Pedidos de exame</div></div>
      <div class="card"><div class="n">${r.internacoes}</div><div class="r">Internações</div></div>
      <div class="card"><div class="n">${moeda(r.total_cobrado)}</div><div class="r">Total cobrado</div></div>
    </div>

    <div class="vp-filtros" id="filtros"></div>
    <div id="linha-tempo"></div>
  `;

  const grupos = [
    ["todos", "Tudo"], ["consulta", "Consultas"], ["prescricao", "Receitas"],
    ["exame", "Exames"], ["internacao", "Internações"], ["cobranca", "Cobranças"],
  ];
  el("filtros").innerHTML = grupos
    .map(([chave, rotulo]) => `<button data-f="${chave}" class="${chave === filtro ? "ativo" : ""}">${rotulo}</button>`)
    .join("");
  el("filtros").querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => { filtro = b.dataset.f; desenharLinha(); marcarFiltro(); });
  });

  desenharLinha();
}

function marcarFiltro() {
  el("filtros").querySelectorAll("button").forEach((b) => b.classList.toggle("ativo", b.dataset.f === filtro));
}

function desenharLinha() {
  const eventos = visao.eventos.filter((e) => {
    if (filtro === "todos") return true;
    if (filtro === "internacao") return e.tipo === "internacao" || e.tipo === "alta";
    return e.tipo === filtro;
  });

  if (!eventos.length) {
    el("linha-tempo").innerHTML = `<div class="card vazio">Nada registrado nesta categoria.</div>`;
    return;
  }

  el("linha-tempo").innerHTML = `<div class="linha-tempo">` + eventos.map((e) => {
    const tipo = TIPOS[e.tipo] || { icone: "bi-circle" };
    const lista = e.detalhes && e.detalhes.length
      ? `<ul>${e.detalhes.map((d) => `<li>${escapeHtml(d)}</li>`).join("")}</ul>` : "";
    const status = e.status
      ? `<span class="pill ${CLASSE_STATUS[e.status] || "pill-info"}">${escapeHtml(e.status)}</span>` : "";
    const valor = e.valor != null ? `<div class="valor">${moeda(e.valor)}</div>` : "";
    return `
      <div class="evento t-${e.tipo}">
        <div class="marcador"><i class="bi ${tipo.icone}"></i></div>
        <div class="caixa">
          <div class="cima">
            <span class="titulo">${escapeHtml(e.titulo)}</span>
            <span>${status} <span class="data">${e.data ? formatarDataHora(e.data) : "sem data"}</span></span>
          </div>
          ${lista}${valor}
        </div>
      </div>`;
  }).join("") + `</div>`;
}

iniciar();
