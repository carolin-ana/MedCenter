/*
 * Tela de Agenda: consultas (com filtros, atendimento, remarcar, cancelar),
 * médicos (com várias especialidades) e especialidades.
 */

let medicos = [];
let especialidades = [];
let pacientes = [];
let mapaPacientes = {};
let mapaMedicos = {};

const el = (id) => document.getElementById(id);
const CLASSE_STATUS = { agendada: "pill-info", realizada: "pill-sucesso", cancelada: "pill-alerta" };

// ======================= Início =======================
async function iniciar() {
  if (!montarLayout({ ativo: "agenda", titulo: "Agenda e corpo clínico" })) return;

  document.querySelectorAll(".aba").forEach((botao) => {
    botao.addEventListener("click", () => {
      location.hash = botao.dataset.aba === "agenda" ? "#agenda" : "#" + botao.dataset.aba;
    });
  });
  window.addEventListener("hashchange", aplicarAba);

  el("btn-filtrar").addEventListener("click", carregarConsultas);
  el("btn-limpar-filtros").addEventListener("click", () => {
    el("filtro-medico").value = "";
    el("filtro-data").value = "";
    el("filtro-status").value = "";
    carregarConsultas();
  });
  el("btn-nova-consulta").addEventListener("click", abrirFormConsulta);
  el("btn-novo-medico").addEventListener("click", () => abrirFormMedico());
  el("btn-nova-especialidade").addEventListener("click", () => abrirFormEspecialidade());

  await carregarBase();
  el("filtro-data").value = hojeISO();
  await carregarConsultas();
  aplicarAba();
}

function aplicarAba() {
  const hash = location.hash.replace("#", "");
  const aba = ["medicos", "especialidades"].includes(hash) ? hash : "agenda";
  ["agenda", "medicos", "especialidades"].forEach((nome) => {
    el(`aba-${nome}`).style.display = nome === aba ? "block" : "none";
  });
  document.querySelectorAll(".aba").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === aba));
  marcarMenuAtivo(aba === "medicos" ? "medicos" : "agenda");
}

// ======================= Dados base =======================
async function carregarBase() {
  try {
    [medicos, especialidades, pacientes] = await Promise.all([
      apiFetch("/medicos"),
      apiFetch("/especialidades"),
      apiFetch("/pacientes"),
    ]);
  } catch (e) {
    mostrarAviso("Erro ao carregar dados: " + e.message, "erro");
  }
  atualizarMapas();
  preencherFiltroMedicos();
  await renderMedicos();
  renderEspecialidades();
}

function atualizarMapas() {
  mapaPacientes = {};
  mapaMedicos = {};
  pacientes.forEach((p) => (mapaPacientes[p.id_paciente] = p.nome));
  medicos.forEach((m) => (mapaMedicos[m.id_medico] = m.nome));
}

function preencherFiltroMedicos() {
  const selecionado = el("filtro-medico").value;
  el("filtro-medico").innerHTML =
    `<option value="">Todos os médicos</option>` +
    medicos.map((m) => `<option value="${m.id_medico}">${escapeHtml(m.nome)}</option>`).join("");
  el("filtro-medico").value = selecionado;
}

// ======================= Consultas =======================
async function carregarConsultas() {
  const params = new URLSearchParams();
  if (el("filtro-medico").value) params.append("id_medico", el("filtro-medico").value);
  if (el("filtro-data").value) params.append("data", el("filtro-data").value);
  if (el("filtro-status").value) params.append("status", el("filtro-status").value);

  const corpo = el("tabela-consultas");
  let lista = [];
  try {
    lista = await apiFetch("/consultas?" + params.toString());
  } catch (e) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Erro ao carregar: ${escapeHtml(e.message)}</td></tr>`;
    return;
  }

  if (lista.length === 0) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhuma consulta encontrada com esses filtros.</td></tr>`;
    return;
  }

  corpo.innerHTML = lista
    .map((c) => {
      let acoes = "";
      if (c.status === "agendada") {
        acoes = `
          <button class="botao botao-primario botao-sm" data-acao="atender" data-id="${c.id_consulta}">Atender</button>
          <button class="botao botao-secundario botao-sm" data-acao="remarcar" data-id="${c.id_consulta}">Remarcar</button>
          <button class="botao botao-perigo botao-sm" data-acao="cancelar" data-id="${c.id_consulta}">Cancelar</button>`;
      } else if (c.status === "realizada") {
        acoes = `<button class="botao botao-secundario botao-sm" data-acao="ver" data-id="${c.id_consulta}">Ver atendimento</button>`;
      }
      return `<tr>
        <td><strong>${formatarDataHora(c.data_consulta)}</strong></td>
        <td>${escapeHtml(mapaPacientes[c.id_paciente] || "Paciente #" + c.id_paciente)}</td>
        <td>${escapeHtml(mapaMedicos[c.id_medico] || "Médico #" + c.id_medico)}</td>
        <td><span class="pill ${CLASSE_STATUS[c.status] || "pill-info"}">${escapeHtml(c.status)}</span></td>
        <td><div class="acoes">${acoes}</div></td>
      </tr>`;
    })
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const consulta = lista.find((c) => c.id_consulta === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      const acao = botao.dataset.acao;
      if (acao === "atender") abrirFormAtendimento(consulta);
      if (acao === "ver") abrirAtendimento(consulta);
      if (acao === "remarcar") abrirRemarcar(consulta);
      if (acao === "cancelar") cancelarConsulta(consulta);
    });
  });
}

function abrirFormConsulta() {
  if (pacientes.length === 0 || medicos.length === 0) {
    return mostrarAviso("Cadastre pelo menos um paciente e um médico antes de agendar.", "erro");
  }
  const html = `
    <div class="form-grupo">
      <label>Paciente *</label>
      <select id="n-paciente">
        <option value="">Selecione...</option>
        ${pacientes.map((p) => `<option value="${p.id_paciente}">${escapeHtml(p.nome)}</option>`).join("")}
      </select>
    </div>
    <div class="form-grupo">
      <label>Médico *</label>
      <select id="n-medico">
        <option value="">Selecione...</option>
        ${medicos.map((m) => `<option value="${m.id_medico}">${escapeHtml(m.nome)}</option>`).join("")}
      </select>
    </div>
    <div class="form-grupo"><label>Data e hora *</label><input type="datetime-local" id="n-data" value="${hojeISO()}T09:00" /></div>`;

  abrirModal("Nova consulta", html, {
    textoSalvar: "Agendar",
    aoSalvar: async (corpo) => {
      const idPaciente = corpo.querySelector("#n-paciente").value;
      const idMedico = corpo.querySelector("#n-medico").value;
      const dataHora = corpo.querySelector("#n-data").value;
      if (!idPaciente || !idMedico || !dataHora) throw new Error("Preencha paciente, médico e data/hora.");

      await apiFetch("/consultas", {
        method: "POST",
        body: JSON.stringify({
          id_paciente: Number(idPaciente),
          id_medico: Number(idMedico),
          data_consulta: dataHora + ":00",
        }),
      });

      // Mostra a consulta recém-criada: ajusta os filtros para o dia e o médico dela
      el("filtro-data").value = dataHora.split("T")[0];
      el("filtro-medico").value = idMedico;
      el("filtro-status").value = "";
      await carregarConsultas();
      mostrarAviso("Consulta agendada.");
    },
  });
}

function abrirRemarcar(consulta) {
  const html = `<div class="form-grupo"><label>Nova data e hora</label><input type="datetime-local" id="r-data" value="${escapeHtml(String(consulta.data_consulta).slice(0, 16))}" /></div>`;
  abrirModal("Remarcar consulta", html, {
    aoSalvar: async (corpo) => {
      const dataHora = corpo.querySelector("#r-data").value;
      if (!dataHora) throw new Error("Informe a nova data e hora.");
      await apiFetch(`/consultas/${consulta.id_consulta}`, {
        method: "PUT",
        body: JSON.stringify({ data_consulta: dataHora + ":00" }),
      });
      el("filtro-data").value = dataHora.split("T")[0];
      await carregarConsultas();
      mostrarAviso("Consulta remarcada.");
    },
  });
}

async function cancelarConsulta(consulta) {
  if (!confirm("Cancelar essa consulta?")) return;
  try {
    await apiFetch(`/consultas/${consulta.id_consulta}`, { method: "PUT", body: JSON.stringify({ status: "cancelada" }) });
    await carregarConsultas();
    mostrarAviso("Consulta cancelada.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
  }
}

// ======================= Atendimento =======================
function camposAtendimento(atendimento = {}) {
  return `
    <div class="form-grupo"><label>Descrição</label><textarea id="a-desc">${escapeHtml(atendimento.descricao)}</textarea></div>
    <div class="form-grupo"><label>Diagnóstico</label><textarea id="a-diag">${escapeHtml(atendimento.diagnostico)}</textarea></div>
    <div class="form-grupo"><label>Observações</label><textarea id="a-obs">${escapeHtml(atendimento.observacoes)}</textarea></div>`;
}

function lerCamposAtendimento(corpo) {
  return {
    descricao: corpo.querySelector("#a-desc").value.trim() || null,
    diagnostico: corpo.querySelector("#a-diag").value.trim() || null,
    observacoes: corpo.querySelector("#a-obs").value.trim() || null,
  };
}

function abrirFormAtendimento(consulta) {
  const titulo = `Atendimento: ${mapaPacientes[consulta.id_paciente] || "paciente"}`;
  abrirModal(titulo, camposAtendimento(), {
    textoSalvar: "Registrar atendimento",
    aoSalvar: async (corpo) => {
      await apiFetch("/atendimentos", {
        method: "POST",
        body: JSON.stringify({ id_consulta: consulta.id_consulta, ...lerCamposAtendimento(corpo) }),
      });
      await carregarConsultas();
      mostrarAviso("Atendimento registrado. A consulta passou para realizada.");
    },
  });
}

async function abrirAtendimento(consulta) {
  let atendimento;
  try {
    atendimento = await apiFetch(`/consultas/${consulta.id_consulta}/atendimento`);
  } catch (e) {
    return mostrarAviso(e.message, "erro");
  }
  abrirModal("Atendimento realizado", camposAtendimento(atendimento), {
    aoSalvar: async (corpo) => {
      await apiFetch(`/atendimentos/${atendimento.id_atendimento}`, {
        method: "PUT",
        body: JSON.stringify(lerCamposAtendimento(corpo)),
      });
      mostrarAviso("Atendimento atualizado.");
    },
  });
}

// ======================= Médicos =======================
async function renderMedicos() {
  const corpo = el("tabela-medicos");
  try {
    medicos = await apiFetch("/medicos");
  } catch (e) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Erro ao carregar: ${escapeHtml(e.message)}</td></tr>`;
    return;
  }
  atualizarMapas();

  if (medicos.length === 0) {
    corpo.innerHTML = `<tr><td colspan="5" class="vazio">Nenhum médico cadastrado.</td></tr>`;
    return;
  }

  const especialidadesDoMedico = {};
  await Promise.all(
    medicos.map(async (m) => {
      try { especialidadesDoMedico[m.id_medico] = await apiFetch(`/medicos/${m.id_medico}/especialidades`); }
      catch (e) { especialidadesDoMedico[m.id_medico] = []; }
    })
  );

  corpo.innerHTML = medicos
    .map((m) => {
      const chips = (especialidadesDoMedico[m.id_medico] || []).map((e) => `<span class="chip">${escapeHtml(e.nome)}</span>`).join("");
      return `<tr>
        <td><strong>${escapeHtml(m.nome)}</strong></td>
        <td>${escapeHtml(m.crm || "—")}</td>
        <td>${escapeHtml(m.telefone || "—")}</td>
        <td>${chips || '<span class="placeholder-aviso">nenhuma</span>'}</td>
        <td>
          <div class="acoes">
            <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${m.id_medico}">Editar</button>
            <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${m.id_medico}">Excluir</button>
          </div>
        </td>
      </tr>`;
    })
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const medico = medicos.find((m) => m.id_medico === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormMedico(medico, (especialidadesDoMedico[medico.id_medico] || []).map((e) => e.id_especialidade));
      if (botao.dataset.acao === "excluir") excluirMedico(medico);
    });
  });
}

function abrirFormMedico(medico = null, idsAtuais = []) {
  const editando = !!medico;
  const checkboxes = especialidades.length
    ? especialidades
        .map((e) => `<label class="check"><input type="checkbox" name="esp" value="${e.id_especialidade}" ${idsAtuais.includes(e.id_especialidade) ? "checked" : ""} /> ${escapeHtml(e.nome)}</label>`)
        .join("")
    : `<p class="placeholder-aviso">Cadastre especialidades na aba "Especialidades" para poder vinculá-las.</p>`;

  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="m-nome" value="${escapeHtml(medico?.nome)}" /></div>
    <div class="form-linha">
      <div class="form-grupo"><label>CRM</label><input type="text" id="m-crm" value="${escapeHtml(medico?.crm)}" /></div>
      <div class="form-grupo"><label>Telefone</label><input type="text" id="m-tel" value="${escapeHtml(medico?.telefone)}" /></div>
    </div>
    <div class="form-grupo"><label>Especialidades</label>${checkboxes}</div>`;

  abrirModal(editando ? "Editar médico" : "Novo médico", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#m-nome").value.trim();
      if (!nome) throw new Error("Informe o nome do médico.");
      const dados = {
        nome,
        crm: corpo.querySelector("#m-crm").value.trim() || null,
        telefone: corpo.querySelector("#m-tel").value.trim() || null,
      };
      const selecionadas = [...corpo.querySelectorAll('input[name="esp"]:checked')].map((c) => Number(c.value));

      if (!editando) {
        await apiFetch("/medicos", { method: "POST", body: JSON.stringify({ ...dados, ids_especialidades: selecionadas }) });
      } else {
        await apiFetch(`/medicos/${medico.id_medico}`, { method: "PUT", body: JSON.stringify(dados) });
        // Sincroniza as especialidades: adiciona as novas e remove as desmarcadas
        for (const idEsp of selecionadas.filter((i) => !idsAtuais.includes(i))) {
          await apiFetch(`/medicos/${medico.id_medico}/especialidades`, { method: "POST", body: JSON.stringify({ id_especialidade: idEsp }) });
        }
        for (const idEsp of idsAtuais.filter((i) => !selecionadas.includes(i))) {
          await apiFetch(`/medicos/${medico.id_medico}/especialidades/${idEsp}`, { method: "DELETE" });
        }
      }
      await renderMedicos();
      preencherFiltroMedicos();
      mostrarAviso(editando ? "Médico atualizado." : "Médico cadastrado.");
    },
  });
}

async function excluirMedico(medico) {
  if (!confirm(`Excluir o médico "${medico.nome}"?`)) return;
  try {
    // Remove os vínculos de especialidade antes, senão o banco recusa a exclusão
    const vinculos = await apiFetch(`/medicos/${medico.id_medico}/especialidades`);
    for (const e of vinculos) {
      await apiFetch(`/medicos/${medico.id_medico}/especialidades/${e.id_especialidade}`, { method: "DELETE" });
    }
    await apiFetch(`/medicos/${medico.id_medico}`, { method: "DELETE" });
    await renderMedicos();
    preencherFiltroMedicos();
    mostrarAviso("Médico excluído.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
    await renderMedicos();
  }
}

// ======================= Especialidades =======================
function renderEspecialidades() {
  const corpo = el("tabela-especialidades");
  if (especialidades.length === 0) {
    corpo.innerHTML = `<tr><td colspan="4" class="vazio">Nenhuma especialidade cadastrada.</td></tr>`;
    return;
  }
  corpo.innerHTML = especialidades
    .map(
      (e) => `<tr>
        <td><strong>${escapeHtml(e.nome)}</strong></td>
        <td>${escapeHtml(e.area || "—")}</td>
        <td>${escapeHtml(e.descricao || "—")}</td>
        <td>
          <div class="acoes">
            <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${e.id_especialidade}">Editar</button>
            <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${e.id_especialidade}">Excluir</button>
          </div>
        </td>
      </tr>`
    )
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const esp = especialidades.find((e) => e.id_especialidade === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormEspecialidade(esp);
      if (botao.dataset.acao === "excluir") excluirEspecialidade(esp);
    });
  });
}

function abrirFormEspecialidade(esp = null) {
  const editando = !!esp;
  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="e-nome" value="${escapeHtml(esp?.nome)}" /></div>
    <div class="form-grupo"><label>Área</label><input type="text" id="e-area" value="${escapeHtml(esp?.area)}" /></div>
    <div class="form-grupo"><label>Descrição</label><textarea id="e-desc">${escapeHtml(esp?.descricao)}</textarea></div>`;

  abrirModal(editando ? "Editar especialidade" : "Nova especialidade", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#e-nome").value.trim();
      if (!nome) throw new Error("Informe o nome da especialidade.");
      const dados = {
        nome,
        area: corpo.querySelector("#e-area").value.trim() || null,
        descricao: corpo.querySelector("#e-desc").value.trim() || null,
      };
      if (editando) {
        await apiFetch(`/especialidades/${esp.id_especialidade}`, { method: "PUT", body: JSON.stringify(dados) });
      } else {
        await apiFetch("/especialidades", { method: "POST", body: JSON.stringify(dados) });
      }
      especialidades = await apiFetch("/especialidades");
      renderEspecialidades();
      await renderMedicos();
      mostrarAviso(editando ? "Especialidade atualizada." : "Especialidade cadastrada.");
    },
  });
}

async function excluirEspecialidade(esp) {
  if (!confirm(`Excluir a especialidade "${esp.nome}"?`)) return;
  try {
    await apiFetch(`/especialidades/${esp.id_especialidade}`, { method: "DELETE" });
    especialidades = await apiFetch("/especialidades");
    renderEspecialidades();
    mostrarAviso("Especialidade excluída.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
  }
}

iniciar();
