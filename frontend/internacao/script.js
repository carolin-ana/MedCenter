
/*
 * Módulo de Internação e Enfermagem
 * Cadastro, listagem, edição e exclusão.
 */

let internacoes = [];
let enfermeiros = [];
let quartos = [];
let atendimentos = [];
let pacientes = [];
let medicos = [];

const el = (id) => document.getElementById(id);

function valorSeguro(valor) {
  return valor === null || valor === undefined || valor === ""
    ? "—"
    : escapeHtml(String(valor));
}

function dataHoraInput(valor) {
  if (!valor) return "";
  return String(valor).slice(0, 16);
}

function dataAtualInput() {
  const agora = new Date();
  const ajuste = agora.getTimezoneOffset() * 60000;
  return new Date(agora.getTime() - ajuste).toISOString().slice(0, 16);
}

function nomePaciente(id) {
  const paciente = pacientes.find((p) => p.id_paciente === Number(id));
  return paciente ? paciente.nome : `Paciente #${id}`;
}

function nomeMedico(id) {
  const medico = medicos.find((m) => m.id_medico === Number(id));
  return medico ? medico.nome : (id ? `Médico #${id}` : "Não informado");
}

function nomeEnfermeiro(id) {
  const enfermeiro = enfermeiros.find((e) => e.id_enfermeiro === Number(id));
  return enfermeiro ? enfermeiro.nome_enfermeiro : `Enfermeiro #${id}`;
}

// ======================= Inicialização =======================

async function iniciar() {
  if (!montarLayout({
    ativo: "internacao",
    titulo: "Internação e Enfermagem"
  })) return;

  document.querySelectorAll(".aba").forEach((botao) => {
    botao.addEventListener("click", () => {
      location.hash = botao.dataset.aba;
    });
  });

  window.addEventListener("hashchange", aplicarAba);

  el("btn-nova-internacao").addEventListener("click", () => abrirFormInternacao());
  el("btn-novo-enfermeiro").addEventListener("click", () => abrirFormEnfermeiro());
  el("btn-novo-quarto").addEventListener("click", () => abrirFormQuarto());
  el("btn-novo-atendimento").addEventListener("click", () => abrirFormAtendimento());

  await carregarDados();
  aplicarAba();
}

function aplicarAba() {
  const nomes = ["internacoes", "enfermeiros", "quartos", "atendimentos"];
  const aba = nomes.includes(location.hash.replace("#", ""))
    ? location.hash.replace("#", "")
    : "internacoes";

  nomes.forEach((nome) => {
    el(`aba-${nome}`).style.display = nome === aba ? "block" : "none";
  });

  document.querySelectorAll(".aba").forEach((botao) => {
    botao.classList.toggle("ativa", botao.dataset.aba === aba);
  });

  marcarMenuAtivo("internacao");
}

// ======================= Carregamento =======================

async function carregarDados() {
  const resultados = await Promise.allSettled([
    apiFetch("/internacao/internacoes"),
    apiFetch("/internacao/enfermeiros"),
    apiFetch("/internacao/quartos"),
    apiFetch("/internacao/atendimentos"),
    apiFetch("/pacientes"),
    apiFetch("/medicos")
  ]);

  internacoes = resultados[0].status === "fulfilled" ? resultados[0].value : [];
  enfermeiros = resultados[1].status === "fulfilled" ? resultados[1].value : [];
  quartos = resultados[2].status === "fulfilled" ? resultados[2].value : [];
  atendimentos = resultados[3].status === "fulfilled" ? resultados[3].value : [];
  pacientes = resultados[4].status === "fulfilled" ? resultados[4].value : [];
  medicos = resultados[5].status === "fulfilled" ? resultados[5].value : [];

  renderInternacoes();
  renderEnfermeiros();
  renderQuartos();
  renderAtendimentos();

  const falhas = resultados.filter((r) => r.status === "rejected");
  if (falhas.length) {
    mostrarAviso(
      "Algumas informações não puderam ser carregadas. Confira se os módulos relacionados estão disponíveis.",
      "erro"
    );
  }
}

// ======================= Internações =======================

function renderInternacoes() {
  const corpo = el("tabela-internacoes");

  if (!internacoes.length) {
    corpo.innerHTML = `<tr><td colspan="6" class="vazio">Nenhuma internação cadastrada.</td></tr>`;
    return;
  }

  corpo.innerHTML = internacoes.map((i) => `
    <tr>
      <td>${i.id_internacao}</td>
      <td><strong>${valorSeguro(nomePaciente(i.id_paciente))}</strong></td>
      <td>${valorSeguro(nomeMedico(i.id_medico_responsavel))}</td>
      <td>${i.data_entrada ? formatarDataHora(i.data_entrada) : "—"}</td>
      <td>${i.data_saida ? formatarDataHora(i.data_saida) : "Em andamento"}</td>
      <td>
        <div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${i.id_internacao}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${i.id_internacao}">Excluir</button>
        </div>
      </td>
    </tr>
  `).join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const item = internacoes.find((i) => i.id_internacao === Number(botao.dataset.id));

    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormInternacao(item);
      if (botao.dataset.acao === "excluir") excluirRegistro(
        "/internacao/internacoes",
        item.id_internacao,
        "internação"
      );
    });
  });
}

function abrirFormInternacao(item = null) {
  const editando = !!item;

  const opcoesPacientes = pacientes.map((p) => `
    <option value="${p.id_paciente}" ${item?.id_paciente === p.id_paciente ? "selected" : ""}>
      ${escapeHtml(p.nome)}
    </option>
  `).join("");

  const opcoesMedicos = `
    <option value="">Não informado</option>
    ${medicos.map((m) => `
      <option value="${m.id_medico}" ${item?.id_medico_responsavel === m.id_medico ? "selected" : ""}>
        ${escapeHtml(m.nome)}
      </option>
    `).join("")}
  `;

  const html = `
    <div class="form-grupo">
      <label>Paciente *</label>
      <select id="i-paciente">
        <option value="">Selecione um paciente</option>
        ${opcoesPacientes}
      </select>
    </div>

    <div class="form-grupo">
      <label>Médico responsável</label>
      <select id="i-medico">${opcoesMedicos}</select>
    </div>

    <div class="form-linha">
      <div class="form-grupo">
        <label>Data e hora de entrada</label>
        <input type="datetime-local" id="i-entrada"
          value="${dataHoraInput(item?.data_entrada) || dataAtualInput()}" />
      </div>
      <div class="form-grupo">
        <label>Data e hora de saída</label>
        <input type="datetime-local" id="i-saida"
          value="${dataHoraInput(item?.data_saida)}" />
      </div>
    </div>

    <div class="form-grupo">
      <label>Motivo da internação</label>
      <textarea id="i-motivo">${escapeHtml(item?.motivo_internacao || "")}</textarea>
    </div>
  `;

  abrirModal(editando ? "Editar internação" : "Nova internação", html, {
    aoSalvar: async (corpo) => {
      const idPaciente = corpo.querySelector("#i-paciente").value;

      if (!idPaciente) throw new Error("Selecione um paciente.");

      const dados = {
        id_paciente: Number(idPaciente),
        id_medico_responsavel: corpo.querySelector("#i-medico").value
          ? Number(corpo.querySelector("#i-medico").value)
          : null,
        data_entrada: corpo.querySelector("#i-entrada").value || null,
        data_saida: corpo.querySelector("#i-saida").value || null,
        motivo_internacao: corpo.querySelector("#i-motivo").value.trim() || null
      };

      if (editando) {
        await apiFetch(`/internacao/internacoes/${item.id_internacao}`, {
          method: "PUT",
          body: JSON.stringify(dados)
        });
      } else {
        await apiFetch("/internacao/internacoes", {
          method: "POST",
          body: JSON.stringify(dados)
        });
      }

      await carregarDados();
      mostrarAviso(editando ? "Internação atualizada." : "Internação cadastrada.");
    }
  });
}

// ======================= Enfermeiros =======================

function renderEnfermeiros() {
  const corpo = el("tabela-enfermeiros");

  if (!enfermeiros.length) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhum enfermeiro cadastrado.</td></tr>`;
    return;
  }

  corpo.innerHTML = enfermeiros.map((e) => `
    <tr>
      <td><strong>${valorSeguro(e.nome_enfermeiro)}</strong></td>
      <td>${valorSeguro(e.coren)}</td>
      <td>${valorSeguro(e.turno)}</td>
      <td>${valorSeguro(e.telefone)}</td>
      <td>
        <div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${e.id_enfermeiro}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${e.id_enfermeiro}">Excluir</button>
        </div>
      </td>
    </tr>
  `).join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const item = enfermeiros.find((e) => e.id_enfermeiro === Number(botao.dataset.id));

    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormEnfermeiro(item);
      if (botao.dataset.acao === "excluir") excluirRegistro(
        "/internacao/enfermeiros",
        item.id_enfermeiro,
        "enfermeiro"
      );
    });
  });
}

function abrirFormEnfermeiro(item = null) {
  const editando = !!item;

  const html = `
    <div class="form-grupo">
      <label>Nome *</label>
      <input type="text" id="e-nome" value="${escapeHtml(item?.nome_enfermeiro || "")}" />
    </div>
    <div class="form-linha">
      <div class="form-grupo">
        <label>COREN</label>
        <input type="text" id="e-coren" value="${escapeHtml(item?.coren || "")}" />
      </div>
      <div class="form-grupo">
        <label>Turno</label>
        <select id="e-turno">
          <option value="">Selecione</option>
          ${["Manhã", "Tarde", "Noite", "Integral"].map((t) =>
            `<option value="${t}" ${item?.turno === t ? "selected" : ""}>${t}</option>`
          ).join("")}
        </select>
      </div>
    </div>
    <div class="form-grupo">
      <label>Telefone</label>
      <input type="text" id="e-telefone" value="${escapeHtml(item?.telefone || "")}" />
    </div>
  `;

  abrirModal(editando ? "Editar enfermeiro" : "Novo enfermeiro", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#e-nome").value.trim();
      if (!nome) throw new Error("Informe o nome do enfermeiro.");

      const dados = {
        nome_enfermeiro: nome,
        coren: corpo.querySelector("#e-coren").value.trim() || null,
        turno: corpo.querySelector("#e-turno").value || null,
        telefone: corpo.querySelector("#e-telefone").value.trim() || null
      };

      if (editando) {
        await apiFetch(`/internacao/enfermeiros/${item.id_enfermeiro}`, {
          method: "PUT",
          body: JSON.stringify(dados)
        });
      } else {
        await apiFetch("/internacao/enfermeiros", {
          method: "POST",
          body: JSON.stringify(dados)
        });
      }

      await carregarDados();
      mostrarAviso(editando ? "Enfermeiro atualizado." : "Enfermeiro cadastrado.");
    }
  });
}

// ======================= Quartos =======================

function renderQuartos() {
  const corpo = el("tabela-quartos");

  if (!quartos.length) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhum quarto cadastrado.</td></tr>`;
    return;
  }

  corpo.innerHTML = quartos.map((q) => `
    <tr>
      <td><strong>${valorSeguro(q.numero_quarto)}</strong></td>
      <td>${valorSeguro(q.tipo)}</td>
      <td>${valorSeguro(q.capacidade)}</td>
      <td>${valorSeguro(q.status)}</td>
      <td>
        <div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${q.id_quarto}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${q.id_quarto}">Excluir</button>
        </div>
      </td>
    </tr>
  `).join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const item = quartos.find((q) => q.id_quarto === Number(botao.dataset.id));

    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormQuarto(item);
      if (botao.dataset.acao === "excluir") excluirRegistro(
        "/internacao/quartos",
        item.id_quarto,
        "quarto"
      );
    });
  });
}

function abrirFormQuarto(item = null) {
  const editando = !!item;

  const html = `
    <div class="form-linha">
      <div class="form-grupo">
        <label>Número do quarto</label>
        <input type="text" id="q-numero" value="${escapeHtml(item?.numero_quarto || "")}" />
      </div>
      <div class="form-grupo">
        <label>Tipo</label>
        <input type="text" id="q-tipo" placeholder="Ex.: Individual, enfermaria"
          value="${escapeHtml(item?.tipo || "")}" />
      </div>
    </div>
    <div class="form-linha">
      <div class="form-grupo">
        <label>Capacidade</label>
        <input type="number" min="1" id="q-capacidade"
          value="${item?.capacidade ?? ""}" />
      </div>
      <div class="form-grupo">
        <label>Status</label>
        <select id="q-status">
          <option value="disponivel" ${!item || item.status === "disponivel" ? "selected" : ""}>Disponível</option>
          <option value="ocupado" ${item?.status === "ocupado" ? "selected" : ""}>Ocupado</option>
        </select>
      </div>
    </div>
  `;

  abrirModal(editando ? "Editar quarto" : "Novo quarto", html, {
    aoSalvar: async (corpo) => {
      const capacidade = corpo.querySelector("#q-capacidade").value;

      const dados = {
        numero_quarto: corpo.querySelector("#q-numero").value.trim() || null,
        tipo: corpo.querySelector("#q-tipo").value.trim() || null,
        capacidade: capacidade ? Number(capacidade) : null,
        status: corpo.querySelector("#q-status").value
      };

      if (dados.capacidade !== null && dados.capacidade < 1) {
        throw new Error("A capacidade deve ser maior que zero.");
      }

      if (editando) {
        await apiFetch(`/internacao/quartos/${item.id_quarto}`, {
          method: "PUT",
          body: JSON.stringify(dados)
        });
      } else {
        await apiFetch("/internacao/quartos", {
          method: "POST",
          body: JSON.stringify(dados)
        });
      }

      await carregarDados();
      mostrarAviso(editando ? "Quarto atualizado." : "Quarto cadastrado.");
    }
  });
}

// ======================= Atendimentos de enfermagem =======================

function renderAtendimentos() {
  const corpo = el("tabela-atendimentos");

  if (!atendimentos.length) {
    corpo.innerHTML = `<tr><td colspan="6" class="vazio">Nenhum atendimento cadastrado.</td></tr>`;
    return;
  }

  corpo.innerHTML = atendimentos.map((a) => `
    <tr>
      <td>${a.id_atendimento_enfermeiro}</td>
      <td>#${a.id_internacao}</td>
      <td>${valorSeguro(nomeEnfermeiro(a.id_enfermeiro))}</td>
      <td>${a.data_enfermeiro ? formatarDataHora(a.data_enfermeiro) : "—"}</td>
      <td>${valorSeguro(a.observacoes)}</td>
      <td>
        <div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${a.id_atendimento_enfermeiro}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${a.id_atendimento_enfermeiro}">Excluir</button>
        </div>
      </td>
    </tr>
  `).join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const item = atendimentos.find(
      (a) => a.id_atendimento_enfermeiro === Number(botao.dataset.id)
    );

    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormAtendimento(item);
      if (botao.dataset.acao === "excluir") excluirRegistro(
        "/internacao/atendimentos",
        item.id_atendimento_enfermeiro,
        "atendimento"
      );
    });
  });
}

function abrirFormAtendimento(item = null) {
  const editando = !!item;

  const opcoesInternacoes = internacoes.map((i) => `
    <option value="${i.id_internacao}" ${item?.id_internacao === i.id_internacao ? "selected" : ""}>
      Internação #${i.id_internacao} - ${escapeHtml(nomePaciente(i.id_paciente))}
    </option>
  `).join("");

  const opcoesEnfermeiros = enfermeiros.map((e) => `
    <option value="${e.id_enfermeiro}" ${item?.id_enfermeiro === e.id_enfermeiro ? "selected" : ""}>
      ${escapeHtml(e.nome_enfermeiro)}
    </option>
  `).join("");

  const html = `
    <div class="form-grupo">
      <label>Internação *</label>
      <select id="a-internacao">
        <option value="">Selecione uma internação</option>
        ${opcoesInternacoes}
      </select>
    </div>
    <div class="form-grupo">
      <label>Enfermeiro *</label>
      <select id="a-enfermeiro">
        <option value="">Selecione um enfermeiro</option>
        ${opcoesEnfermeiros}
      </select>
    </div>
    <div class="form-grupo">
      <label>Data e hora do atendimento</label>
      <input type="datetime-local" id="a-data"
        value="${dataHoraInput(item?.data_enfermeiro) || dataAtualInput()}" />
    </div>
    <div class="form-grupo">
      <label>Observações</label>
      <textarea id="a-observacoes">${escapeHtml(item?.observacoes || "")}</textarea>
    </div>
  `;

  abrirModal(editando ? "Editar atendimento" : "Novo atendimento", html, {
    aoSalvar: async (corpo) => {
      const idInternacao = corpo.querySelector("#a-internacao").value;
      const idEnfermeiro = corpo.querySelector("#a-enfermeiro").value;

      if (!idInternacao) throw new Error("Selecione uma internação.");
      if (!idEnfermeiro) throw new Error("Selecione um enfermeiro.");

      const dados = {
        id_internacao: Number(idInternacao),
        id_enfermeiro: Number(idEnfermeiro),
        data_enfermeiro: corpo.querySelector("#a-data").value || null,
        observacoes: corpo.querySelector("#a-observacoes").value.trim() || null
      };

      if (editando) {
        await apiFetch(`/internacao/atendimentos/${item.id_atendimento_enfermeiro}`, {
          method: "PUT",
          body: JSON.stringify(dados)
        });
      } else {
        await apiFetch("/internacao/atendimentos", {
          method: "POST",
          body: JSON.stringify(dados)
        });
      }

      await carregarDados();
      mostrarAviso(editando ? "Atendimento atualizado." : "Atendimento cadastrado.");
    }
  });
}

// ======================= Exclusão genérica =======================

async function excluirRegistro(endpoint, id, nome) {
  if (!confirm(`Deseja realmente excluir este ${nome}?`)) return;

  try {
    await apiFetch(`${endpoint}/${id}`, { method: "DELETE" });
    await carregarDados();
    mostrarAviso(`${nome.charAt(0).toUpperCase() + nome.slice(1)} excluído.`);
  } catch (e) {
    mostrarAviso(e.message, "erro");
  }
}

iniciar();
