/*
 * Tela de Farmácia e Exames: prescrições (com medicamentos), pedidos de exame
 * (com exames), cadastro de medicamentos e de exames.
 * Usa as rotas do módulo farmacia_exames do backend.
 */

let medicamentos = [];
let exames = [];
let atendimentos = [];
let consultas = [];
let pacientes = [];
let prescricoes = [];
let itensPrescricao = [];
let pedidos = [];
let itensPedido = [];
let falhas = [];

const el = (id) => document.getElementById(id);
const CLASSE_STATUS = {
  ativa: "pill-info", concluida: "pill-sucesso", cancelada: "pill-alerta",
  pendente: "pill-alerta", em_andamento: "pill-info", concluido: "pill-sucesso",
};

// ======================= Início =======================
async function iniciar() {
  if (!montarLayout({ ativo: "resultados", titulo: "Farmácia e exames" })) return;

  document.querySelectorAll(".aba").forEach((botao) => {
    botao.addEventListener("click", () => { location.hash = "#" + botao.dataset.aba; });
  });
  window.addEventListener("hashchange", aplicarAba);

  el("btn-nova-prescricao").addEventListener("click", abrirFormPrescricao);
  el("btn-novo-pedido").addEventListener("click", abrirFormPedido);
  el("btn-novo-medicamento").addEventListener("click", () => abrirFormMedicamento());
  el("btn-novo-exame").addEventListener("click", () => abrirFormExame());

  await carregarTudo();
  aplicarAba();
}

function aplicarAba() {
  const hash = location.hash.replace("#", "");
  const aba = ["pedidos", "medicamentos", "exames"].includes(hash) ? hash : "prescricoes";
  ["prescricoes", "pedidos", "medicamentos", "exames"].forEach((nome) => {
    el(`aba-${nome}`).style.display = nome === aba ? "block" : "none";
  });
  document.querySelectorAll(".aba").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === aba));
}

// ======================= Dados =======================
async function tentar(caminho) {
  try {
    return await apiFetch(caminho);
  } catch (e) {
    falhas.push(`${caminho} (${e.message})`);
    return [];
  }
}

async function carregarTudo() {
  falhas = [];
  [medicamentos, exames, atendimentos, consultas, pacientes, prescricoes, itensPrescricao, pedidos, itensPedido] =
    await Promise.all([
      tentar("/medicamentos"),
      tentar("/exames"),
      tentar("/atendimentos"),
      tentar("/consultas"),
      tentar("/pacientes"),
      tentar("/prescricoes"),
      tentar("/prescricao-medicamentos"),
      tentar("/pedidos-exames"),
      tentar("/pedidos-exames-itens"),
    ]);

  if (falhas.length) {
    mostrarAviso("Algumas listas não carregaram: " + falhas.join("; "), "erro");
  }
  renderPrescricoes();
  renderPedidos();
  renderMedicamentos();
  renderExames();
}

function nomeMedicamento(id) {
  const m = medicamentos.find((x) => x.id_medicamento === id);
  return m ? m.nome : `Medicamento #${id}`;
}

function nomeExame(id) {
  const e = exames.find((x) => x.id_exame === id);
  return e ? e.nome : `Exame #${id}`;
}

function rotuloAtendimento(idAtendimento) {
  const at = atendimentos.find((a) => a.id_atendimento === idAtendimento);
  if (!at) return `Atendimento #${idAtendimento}`;
  const consulta = consultas.find((c) => c.id_consulta === at.id_consulta);
  const paciente = consulta ? pacientes.find((p) => p.id_paciente === consulta.id_paciente) : null;
  const quando = consulta ? formatarData(consulta.data_consulta) : "";
  return `${paciente ? paciente.nome : "Paciente"} · ${quando} (atend. #${idAtendimento})`;
}

function opcoesAtendimento() {
  if (atendimentos.length === 0) return `<option value="">Nenhum atendimento registrado</option>`;
  return (
    `<option value="">Selecione...</option>` +
    atendimentos.map((a) => `<option value="${a.id_atendimento}">${escapeHtml(rotuloAtendimento(a.id_atendimento))}</option>`).join("")
  );
}

function pillStatus(status) {
  return `<span class="pill ${CLASSE_STATUS[status] || "pill-info"}">${escapeHtml(String(status || "—").replace("_", " "))}</span>`;
}

// ======================= Prescrições =======================
function renderPrescricoes() {
  const corpo = el("tabela-prescricoes");
  if (prescricoes.length === 0) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhuma prescrição encontrada.</td></tr>`;
    return;
  }
  corpo.innerHTML = prescricoes
    .map((p) => {
      const qtd = itensPrescricao.filter((i) => i.id_prescricao === p.id_prescricao).length;
      return `<tr>
        <td>${formatarDataHora(p.data_prescricao)}</td>
        <td><strong>${escapeHtml(rotuloAtendimento(p.id_atendimento))}</strong></td>
        <td>${pillStatus(p.status)}</td>
        <td>${qtd}</td>
        <td><div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="detalhes" data-id="${p.id_prescricao}">Detalhes</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${p.id_prescricao}">Excluir</button>
        </div></td>
      </tr>`;
    })
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const prescricao = prescricoes.find((p) => p.id_prescricao === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "detalhes") abrirDetalhePrescricao(prescricao.id_prescricao);
      if (botao.dataset.acao === "excluir") excluirPrescricao(prescricao);
    });
  });
}

async function recarregarPrescricoes() {
  falhas = [];
  prescricoes = await tentar("/prescricoes");
  itensPrescricao = await tentar("/prescricao-medicamentos");
  renderPrescricoes();
}

function abrirFormPrescricao() {
  const html = `
    <div class="form-grupo"><label>Atendimento *</label><select id="np-atendimento">${opcoesAtendimento()}</select></div>
    <div class="form-grupo"><label>Observação</label><textarea id="np-obs"></textarea></div>`;

  abrirModal("Nova prescrição", html, {
    textoSalvar: "Criar e adicionar medicamentos",
    aoSalvar: async (corpo) => {
      const idAtendimento = corpo.querySelector("#np-atendimento").value;
      if (!idAtendimento) throw new Error("Selecione o atendimento. Se a lista estiver vazia, registre um atendimento na Agenda.");
      const nova = await apiFetch("/prescricoes", {
        method: "POST",
        body: JSON.stringify({
          id_atendimento: Number(idAtendimento),
          observacao: corpo.querySelector("#np-obs").value.trim() || null,
          status: "ativa",
        }),
      });
      await recarregarPrescricoes();
      // abre os detalhes depois que este modal fechar
      setTimeout(() => abrirDetalhePrescricao(nova.id_prescricao), 50);
    },
  });
}

function htmlDetalhePrescricao(p) {
  const itens = itensPrescricao.filter((i) => i.id_prescricao === p.id_prescricao);
  const linhas = itens.length
    ? itens
        .map(
          (i) => `<div class="lista-item" style="align-items:flex-start;">
            <span><strong>${escapeHtml(nomeMedicamento(i.id_medicamento))}</strong><br>
              <small style="color:#6c757d;">${escapeHtml(i.dosagem)} · ${escapeHtml(i.frequencia)} · ${escapeHtml(i.duracao)} · qtd ${escapeHtml(i.quantidade)}${i.instrucoes ? " · " + escapeHtml(i.instrucoes) : ""}</small></span>
            <button type="button" class="botao botao-perigo botao-sm" data-remover="${i.id_prescricao_medicamento}">Remover</button>
          </div>`
        )
        .join("")
    : `<p class="placeholder-aviso">Nenhum medicamento nesta prescrição ainda.</p>`;

  const opcoesMed =
    `<option value="">Selecione o medicamento...</option>` +
    medicamentos.map((m) => `<option value="${m.id_medicamento}">${escapeHtml(m.nome)}</option>`).join("");

  return `
    <div class="bloco-detalhe">
      <h3>Prescrição</h3>
      <div class="dados-grid">
        <div><span class="rot">Paciente / atendimento</span>${escapeHtml(rotuloAtendimento(p.id_atendimento))}</div>
        <div><span class="rot">Data</span>${formatarDataHora(p.data_prescricao)}</div>
      </div>
      <div class="form-linha" style="margin-top:0.8rem;">
        <div class="form-grupo" style="flex:0 0 160px;">
          <label>Status</label>
          <select id="dp-status">
            ${["ativa", "concluida", "cancelada"].map((s) => `<option value="${s}" ${p.status === s ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </div>
        <div class="form-grupo"><label>Observação</label><input type="text" id="dp-obs" value="${escapeHtml(p.observacao)}" /></div>
      </div>
      <button type="button" class="botao botao-secundario botao-sm" id="dp-salvar">Salvar status e observação</button>
    </div>

    <div class="bloco-detalhe">
      <h3>Medicamentos</h3>
      ${linhas}
    </div>

    <div class="bloco-detalhe">
      <h3>Adicionar medicamento</h3>
      <div class="form-grupo"><select id="di-med">${opcoesMed}</select></div>
      <div class="form-linha">
        <div class="form-grupo"><label>Dosagem *</label><input type="text" id="di-dosagem" placeholder="ex: 500 mg" /></div>
        <div class="form-grupo"><label>Frequência *</label><input type="text" id="di-freq" placeholder="ex: 8 em 8 horas" /></div>
      </div>
      <div class="form-linha">
        <div class="form-grupo"><label>Duração *</label><input type="text" id="di-duracao" placeholder="ex: 7 dias" /></div>
        <div class="form-grupo"><label>Quantidade *</label><input type="text" id="di-qtd" placeholder="ex: 21" /></div>
      </div>
      <div class="form-grupo"><label>Instruções</label><input type="text" id="di-instr" placeholder="ex: tomar após as refeições" /></div>
      <button type="button" class="botao botao-primario botao-sm" id="di-adicionar">Adicionar à prescrição</button>
    </div>`;
}

async function abrirDetalhePrescricao(id) {
  const p = prescricoes.find((x) => x.id_prescricao === id);
  if (!p) return;
  const corpo = abrirModal(`Prescrição #${id}`, htmlDetalhePrescricao(p), { largura: "720px" });
  ligarDetalhePrescricao(corpo, p);
}

function ligarDetalhePrescricao(corpo, p) {
  const atualizar = async () => {
    await recarregarPrescricoes();
    const atual = prescricoes.find((x) => x.id_prescricao === p.id_prescricao);
    if (!atual) return fecharModal();
    corpo.innerHTML = htmlDetalhePrescricao(atual);
    ligarDetalhePrescricao(corpo, atual);
  };

  corpo.querySelector("#dp-salvar").addEventListener("click", async () => {
    try {
      await apiFetch(`/prescricoes/${p.id_prescricao}`, {
        method: "PUT",
        body: JSON.stringify({
          id_atendimento: p.id_atendimento,
          observacao: corpo.querySelector("#dp-obs").value.trim() || null,
          status: corpo.querySelector("#dp-status").value,
        }),
      });
      mostrarAviso("Prescrição atualizada.");
      await atualizar();
    } catch (e) {
      mostrarAviso(e.message, "erro");
    }
  });

  corpo.querySelector("#di-adicionar").addEventListener("click", async () => {
    const idMed = corpo.querySelector("#di-med").value;
    const dosagem = corpo.querySelector("#di-dosagem").value.trim();
    const frequencia = corpo.querySelector("#di-freq").value.trim();
    const duracao = corpo.querySelector("#di-duracao").value.trim();
    const quantidade = Number(corpo.querySelector("#di-qtd").value.trim());
    if (!idMed || !dosagem || !frequencia || !duracao) {
      return mostrarAviso("Preencha medicamento, dosagem, frequência e duração.", "erro");
    }
    if (!Number.isInteger(quantidade) || quantidade <= 0) {
      return mostrarAviso("A quantidade precisa ser um número inteiro maior que zero.", "erro");
    }
    try {
      await apiFetch("/prescricao-medicamentos", {
        method: "POST",
        body: JSON.stringify({
          id_prescricao: p.id_prescricao,
          id_medicamento: Number(idMed),
          dosagem,
          frequencia,
          duracao,
          quantidade,
          instrucoes: corpo.querySelector("#di-instr").value.trim() || null,
        }),
      });
      mostrarAviso("Medicamento adicionado.");
      await atualizar();
    } catch (e) {
      mostrarAviso(e.message, "erro");
    }
  });

  corpo.querySelectorAll("button[data-remover]").forEach((botao) => {
    botao.addEventListener("click", async () => {
      try {
        await apiFetch(`/prescricao-medicamentos/${botao.dataset.remover}`, { method: "DELETE" });
        await atualizar();
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  });
}

async function excluirPrescricao(p) {
  if (!confirm(`Excluir a prescrição #${p.id_prescricao} e os medicamentos dela?`)) return;
  try {
    // apaga os itens antes, senão o banco recusa a exclusão da prescrição
    for (const item of itensPrescricao.filter((i) => i.id_prescricao === p.id_prescricao)) {
      await apiFetch(`/prescricao-medicamentos/${item.id_prescricao_medicamento}`, { method: "DELETE" });
    }
    await apiFetch(`/prescricoes/${p.id_prescricao}`, { method: "DELETE" });
    await recarregarPrescricoes();
    mostrarAviso("Prescrição excluída.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
    await recarregarPrescricoes();
  }
}

// ======================= Pedidos de exame =======================
function renderPedidos() {
  const corpo = el("tabela-pedidos");
  if (pedidos.length === 0) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhum pedido de exame encontrado.</td></tr>`;
    return;
  }
  corpo.innerHTML = pedidos
    .map((p) => {
      const qtd = itensPedido.filter((i) => i.id_pedido_exame === p.id_pedido_exame).length;
      return `<tr>
        <td>${formatarDataHora(p.data_pedido)}</td>
        <td><strong>${escapeHtml(rotuloAtendimento(p.id_atendimento))}</strong></td>
        <td>${pillStatus(p.status)}</td>
        <td>${qtd}</td>
        <td><div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="detalhes" data-id="${p.id_pedido_exame}">Detalhes</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${p.id_pedido_exame}">Excluir</button>
        </div></td>
      </tr>`;
    })
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const pedido = pedidos.find((p) => p.id_pedido_exame === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "detalhes") abrirDetalhePedido(pedido.id_pedido_exame);
      if (botao.dataset.acao === "excluir") excluirPedido(pedido);
    });
  });
}

async function recarregarPedidos() {
  falhas = [];
  pedidos = await tentar("/pedidos-exames");
  itensPedido = await tentar("/pedidos-exames-itens");
  renderPedidos();
}

function abrirFormPedido() {
  const html = `
    <div class="form-grupo"><label>Atendimento *</label><select id="pe-atendimento">${opcoesAtendimento()}</select></div>
    <div class="form-grupo"><label>Observações</label><textarea id="pe-obs"></textarea></div>`;

  abrirModal("Novo pedido de exame", html, {
    textoSalvar: "Criar e adicionar exames",
    aoSalvar: async (corpo) => {
      const idAtendimento = corpo.querySelector("#pe-atendimento").value;
      if (!idAtendimento) throw new Error("Selecione o atendimento. Se a lista estiver vazia, registre um atendimento na Agenda.");
      const novo = await apiFetch("/pedidos-exames", {
        method: "POST",
        body: JSON.stringify({
          id_atendimento: Number(idAtendimento),
          status: "pendente",
          observacoes: corpo.querySelector("#pe-obs").value.trim() || null,
        }),
      });
      await recarregarPedidos();
      setTimeout(() => abrirDetalhePedido(novo.id_pedido_exame), 50);
    },
  });
}

function htmlDetalhePedido(p) {
  const itens = itensPedido.filter((i) => i.id_pedido_exame === p.id_pedido_exame);
  const linhas = itens.length
    ? itens
        .map(
          (i) => `<div class="lista-item" style="align-items:flex-start;">
            <span><strong>${escapeHtml(nomeExame(i.id_exame))}</strong>${i.observacoes ? `<br><small style="color:#6c757d;">${escapeHtml(i.observacoes)}</small>` : ""}
              <br><small>${i.resultado ? `Resultado (${formatarData(i.data_resultado)}): ${escapeHtml(i.resultado)}` : '<span style="color:#b4660a;">Sem resultado</span>'}</small></span>
            <span style="display:flex;gap:6px;flex-shrink:0;">
              <button type="button" class="botao botao-secundario botao-sm" data-resultado="${i.id_pedido_exame_item}">${i.resultado ? "Editar resultado" : "Registrar resultado"}</button>
              <button type="button" class="botao botao-perigo botao-sm" data-remover="${i.id_pedido_exame_item}">Remover</button>
            </span>
          </div>`
        )
        .join("")
    : `<p class="placeholder-aviso">Nenhum exame neste pedido ainda.</p>`;

  const opcoesEx =
    `<option value="">Selecione o exame...</option>` +
    exames.map((e) => `<option value="${e.id_exame}">${escapeHtml(e.nome)}</option>`).join("");

  return `
    <div class="bloco-detalhe">
      <h3>Pedido</h3>
      <div class="dados-grid">
        <div><span class="rot">Paciente / atendimento</span>${escapeHtml(rotuloAtendimento(p.id_atendimento))}</div>
        <div><span class="rot">Data</span>${formatarDataHora(p.data_pedido)}</div>
      </div>
      <div class="form-linha" style="margin-top:0.8rem;">
        <div class="form-grupo" style="flex:0 0 180px;">
          <label>Status</label>
          <select id="dpe-status">
            ${[["pendente", "pendente"], ["em_andamento", "em andamento"], ["concluido", "concluído"]]
              .map(([valor, rotulo]) => `<option value="${valor}" ${p.status === valor ? "selected" : ""}>${rotulo}</option>`).join("")}
          </select>
        </div>
        <div class="form-grupo"><label>Observações</label><input type="text" id="dpe-obs" value="${escapeHtml(p.observacoes)}" /></div>
      </div>
      <button type="button" class="botao botao-secundario botao-sm" id="dpe-salvar">Salvar status e observações</button>
    </div>

    <div class="bloco-detalhe">
      <h3>Exames solicitados</h3>
      ${linhas}
    </div>

    <div class="bloco-detalhe">
      <h3>Adicionar exame</h3>
      <div class="form-grupo"><select id="dei-exame">${opcoesEx}</select></div>
      <div class="form-grupo"><label>Observações</label><input type="text" id="dei-obs" /></div>
      <button type="button" class="botao botao-primario botao-sm" id="dei-adicionar">Adicionar ao pedido</button>
    </div>`;
}

async function abrirDetalhePedido(id) {
  const p = pedidos.find((x) => x.id_pedido_exame === id);
  if (!p) return;
  const corpo = abrirModal(`Pedido de exame #${id}`, htmlDetalhePedido(p), { largura: "680px" });
  ligarDetalhePedido(corpo, p);
}

function ligarDetalhePedido(corpo, p) {
  const atualizar = async () => {
    await recarregarPedidos();
    const atual = pedidos.find((x) => x.id_pedido_exame === p.id_pedido_exame);
    if (!atual) return fecharModal();
    corpo.innerHTML = htmlDetalhePedido(atual);
    ligarDetalhePedido(corpo, atual);
  };

  corpo.querySelector("#dpe-salvar").addEventListener("click", async () => {
    try {
      await apiFetch(`/pedidos-exames/${p.id_pedido_exame}`, {
        method: "PUT",
        body: JSON.stringify({
          id_atendimento: p.id_atendimento,
          status: corpo.querySelector("#dpe-status").value,
          observacoes: corpo.querySelector("#dpe-obs").value.trim() || null,
        }),
      });
      mostrarAviso("Pedido atualizado.");
      await atualizar();
    } catch (e) {
      mostrarAviso(e.message, "erro");
    }
  });

  corpo.querySelector("#dei-adicionar").addEventListener("click", async () => {
    const idExame = corpo.querySelector("#dei-exame").value;
    if (!idExame) return mostrarAviso("Selecione o exame.", "erro");
    try {
      await apiFetch("/pedidos-exames-itens", {
        method: "POST",
        body: JSON.stringify({
          id_pedido_exame: p.id_pedido_exame,
          id_exame: Number(idExame),
          observacoes: corpo.querySelector("#dei-obs").value.trim() || null,
        }),
      });
      mostrarAviso("Exame adicionado.");
      await atualizar();
    } catch (e) {
      mostrarAviso(e.message, "erro");
    }
  });

  corpo.querySelectorAll("button[data-resultado]").forEach((botao) => {
    botao.addEventListener("click", () => {
      const item = itensPedido.find((i) => i.id_pedido_exame_item === Number(botao.dataset.resultado));
      abrirFormResultado(item);
    });
  });

  corpo.querySelectorAll("button[data-remover]").forEach((botao) => {
    botao.addEventListener("click", async () => {
      try {
        await apiFetch(`/pedidos-exames-itens/${botao.dataset.remover}`, { method: "DELETE" });
        await atualizar();
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  });
}

function abrirFormResultado(item) {
  const html = `
    <p style="margin-top:0;"><strong>${escapeHtml(nomeExame(item.id_exame))}</strong></p>
    <div class="form-grupo"><label>Resultado *</label><textarea id="rs-texto">${escapeHtml(item.resultado)}</textarea></div>
    <div class="form-grupo"><label>Data do resultado</label><input type="date" id="rs-data" value="${escapeHtml(item.data_resultado || hojeISO())}" /></div>`;

  abrirModal("Resultado do exame", html, {
    aoSalvar: async (corpo) => {
      const resultado = corpo.querySelector("#rs-texto").value.trim();
      if (!resultado) throw new Error("Informe o resultado do exame.");
      await apiFetch(`/pedidos-exames-itens/${item.id_pedido_exame_item}`, {
        method: "PUT",
        body: JSON.stringify({
          id_pedido_exame: item.id_pedido_exame,
          id_exame: item.id_exame,
          observacoes: item.observacoes ?? null,
          resultado,
          data_resultado: corpo.querySelector("#rs-data").value || null,
        }),
      });
      await recarregarPedidos();
      mostrarAviso("Resultado registrado.");
      // reabre os detalhes do pedido depois que este modal fechar
      setTimeout(() => abrirDetalhePedido(item.id_pedido_exame), 50);
    },
  });
}

async function excluirPedido(p) {
  if (!confirm(`Excluir o pedido #${p.id_pedido_exame} e os exames dele?`)) return;
  try {
    for (const item of itensPedido.filter((i) => i.id_pedido_exame === p.id_pedido_exame)) {
      await apiFetch(`/pedidos-exames-itens/${item.id_pedido_exame_item}`, { method: "DELETE" });
    }
    await apiFetch(`/pedidos-exames/${p.id_pedido_exame}`, { method: "DELETE" });
    await recarregarPedidos();
    mostrarAviso("Pedido excluído.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
    await recarregarPedidos();
  }
}

// ======================= Medicamentos =======================
function renderMedicamentos() {
  const corpo = el("tabela-medicamentos");
  if (medicamentos.length === 0) {
    corpo.innerHTML = `<tr><td colspan="4" class="vazio">Nenhum medicamento cadastrado.</td></tr>`;
    return;
  }
  corpo.innerHTML = medicamentos
    .map(
      (m) => `<tr>
        <td><strong>${escapeHtml(m.nome)}</strong></td>
        <td>${escapeHtml(m.descricao || "—")}</td>
        <td>${escapeHtml(m.quantidade_estoque ?? 0)}</td>
        <td><div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${m.id_medicamento}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${m.id_medicamento}">Excluir</button>
        </div></td>
      </tr>`
    )
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const med = medicamentos.find((m) => m.id_medicamento === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormMedicamento(med);
      if (botao.dataset.acao === "excluir") excluirMedicamento(med);
    });
  });
}

function abrirFormMedicamento(med = null) {
  const editando = !!med;
  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="md-nome" value="${escapeHtml(med?.nome)}" /></div>
    <div class="form-grupo"><label>Descrição</label><textarea id="md-desc">${escapeHtml(med?.descricao)}</textarea></div>
    <div class="form-grupo"><label>Quantidade em estoque</label><input type="text" id="md-estoque" value="${escapeHtml(med?.quantidade_estoque ?? 0)}" /></div>`;

  abrirModal(editando ? "Editar medicamento" : "Novo medicamento", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#md-nome").value.trim();
      const estoque = Number(corpo.querySelector("#md-estoque").value.trim() || 0);
      if (!nome) throw new Error("Informe o nome do medicamento.");
      if (!Number.isInteger(estoque) || estoque < 0) throw new Error("O estoque precisa ser um número inteiro, zero ou maior.");
      const dados = { nome, descricao: corpo.querySelector("#md-desc").value.trim() || null, quantidade_estoque: estoque };
      if (editando) {
        await apiFetch(`/medicamentos/${med.id_medicamento}`, { method: "PUT", body: JSON.stringify(dados) });
      } else {
        await apiFetch("/medicamentos", { method: "POST", body: JSON.stringify(dados) });
      }
      medicamentos = await tentar("/medicamentos");
      renderMedicamentos();
      mostrarAviso(editando ? "Medicamento atualizado." : "Medicamento cadastrado.");
    },
  });
}

async function excluirMedicamento(med) {
  if (!confirm(`Excluir o medicamento "${med.nome}"?`)) return;
  try {
    await apiFetch(`/medicamentos/${med.id_medicamento}`, { method: "DELETE" });
    medicamentos = await tentar("/medicamentos");
    renderMedicamentos();
    mostrarAviso("Medicamento excluído.");
  } catch (e) {
    mostrarAviso("Não foi possível excluir. Ele pode estar em uma prescrição. " + e.message, "erro");
  }
}

// ======================= Exames =======================
function renderExames() {
  const corpo = el("tabela-exames");
  if (exames.length === 0) {
    corpo.innerHTML = `<tr><td colspan="3" class="vazio">Nenhum exame cadastrado.</td></tr>`;
    return;
  }
  corpo.innerHTML = exames
    .map(
      (e) => `<tr>
        <td><strong>${escapeHtml(e.nome)}</strong></td>
        <td>${escapeHtml(e.descricao || "—")}</td>
        <td><div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${e.id_exame}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${e.id_exame}">Excluir</button>
        </div></td>
      </tr>`
    )
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const exame = exames.find((x) => x.id_exame === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormExame(exame);
      if (botao.dataset.acao === "excluir") excluirExame(exame);
    });
  });
}

function abrirFormExame(exame = null) {
  const editando = !!exame;
  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="ex-nome" value="${escapeHtml(exame?.nome)}" /></div>
    <div class="form-grupo"><label>Descrição</label><textarea id="ex-desc">${escapeHtml(exame?.descricao)}</textarea></div>`;

  abrirModal(editando ? "Editar exame" : "Novo exame", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#ex-nome").value.trim();
      if (!nome) throw new Error("Informe o nome do exame.");
      const dados = { nome, descricao: corpo.querySelector("#ex-desc").value.trim() || null };
      if (editando) {
        await apiFetch(`/exames/${exame.id_exame}`, { method: "PUT", body: JSON.stringify(dados) });
      } else {
        await apiFetch("/exames", { method: "POST", body: JSON.stringify(dados) });
      }
      exames = await tentar("/exames");
      renderExames();
      mostrarAviso(editando ? "Exame atualizado." : "Exame cadastrado.");
    },
  });
}

async function excluirExame(exame) {
  if (!confirm(`Excluir o exame "${exame.nome}"?`)) return;
  try {
    await apiFetch(`/exames/${exame.id_exame}`, { method: "DELETE" });
    exames = await tentar("/exames");
    renderExames();
    mostrarAviso("Exame excluído.");
  } catch (e) {
    mostrarAviso("Não foi possível excluir. Ele pode estar em um pedido. " + e.message, "erro");
  }
}

iniciar();
