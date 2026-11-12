/*
 * Tela de Pacientes: lista, busca, cadastro, edição, exclusão,
 * detalhes (contatos, prontuário, histórico de consultas) e convênios.
 */

let convenios = [];
const TIPOS_SANGUE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];
let mapaConvenios = {};

const el = (id) => document.getElementById(id);

function nomeConvenio(id) {
  return id ? mapaConvenios[id] || `Convênio #${id}` : "Particular";
}

// ======================= Início =======================
async function iniciar() {
  if (!montarLayout({ ativo: "pacientes", titulo: "Pacientes" })) return;

  document.querySelectorAll(".aba").forEach((botao) => {
    botao.addEventListener("click", () => { location.hash = botao.dataset.aba === "convenios" ? "#convenios" : "#pacientes"; });
  });
  window.addEventListener("hashchange", aplicarAba);

  el("btn-buscar").addEventListener("click", buscarPacientes);
  el("btn-limpar").addEventListener("click", () => { el("busca").value = ""; carregarPacientes(); });
  el("busca").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarPacientes(); });
  el("btn-novo-paciente").addEventListener("click", () => abrirFormPaciente());
  el("btn-novo-convenio").addEventListener("click", () => abrirFormConvenio());

  await carregarConvenios();
  await carregarPacientes();
  aplicarAba();
}

function aplicarAba() {
  const aba = location.hash === "#convenios" ? "convenios" : "pacientes";
  el("aba-pacientes").style.display = aba === "pacientes" ? "block" : "none";
  el("aba-convenios").style.display = aba === "convenios" ? "block" : "none";
  document.querySelectorAll(".aba").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === aba));
  marcarMenuAtivo(aba === "convenios" ? "convenios" : "pacientes");
}

// ======================= Convênios =======================
async function carregarConvenios() {
  try {
    convenios = await apiFetch("/convenios");
  } catch (e) {
    convenios = [];
    mostrarAviso("Não foi possível carregar os convênios: " + e.message, "erro");
  }
  mapaConvenios = {};
  convenios.forEach((c) => (mapaConvenios[c.id_convenio] = c.nome));

  const corpo = el("tabela-convenios");
  if (convenios.length === 0) {
    corpo.innerHTML = `<tr><td colspan="4" class="vazio">Nenhum convênio cadastrado.</td></tr>`;
    return;
  }
  corpo.innerHTML = convenios
    .map(
      (c) => `<tr>
        <td><strong>${escapeHtml(c.nome)}</strong></td>
        <td>${escapeHtml(c.registro_ans || "—")}</td>
        <td>${escapeHtml(c.telefone || "—")}</td>
        <td><div class="acoes">
          <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${c.id_convenio}">Editar</button>
          <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${c.id_convenio}">Excluir</button>
        </div></td>
      </tr>`
    )
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const convenio = convenios.find((c) => c.id_convenio === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "editar") abrirFormConvenio(convenio);
      if (botao.dataset.acao === "excluir") excluirConvenio(convenio);
    });
  });
}

function abrirFormConvenio(convenio = null) {
  const editando = !!convenio;
  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="c-nome" value="${escapeHtml(convenio?.nome)}" /></div>
    <div class="form-linha">
      <div class="form-grupo"><label>Registro ANS</label><input type="text" id="c-ans" value="${escapeHtml(convenio?.registro_ans)}" /></div>
      <div class="form-grupo"><label>Telefone</label><input type="text" id="c-tel" value="${escapeHtml(convenio?.telefone)}" /></div>
    </div>`;

  abrirModal(editando ? "Editar convênio" : "Novo convênio", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#c-nome").value.trim();
      if (!nome) throw new Error("Informe o nome do convênio.");
      const dados = {
        nome,
        registro_ans: corpo.querySelector("#c-ans").value.trim() || null,
        telefone: corpo.querySelector("#c-tel").value.trim() || null,
      };
      if (editando) {
        await apiFetch(`/convenios/${convenio.id_convenio}`, { method: "PUT", body: JSON.stringify(dados) });
      } else {
        await apiFetch("/convenios", { method: "POST", body: JSON.stringify(dados) });
      }
      await carregarConvenios();
      await carregarPacientes(); // a lista de pacientes mostra o nome do convênio
      mostrarAviso(editando ? "Convênio atualizado." : "Convênio cadastrado.");
    },
  });
}

async function excluirConvenio(convenio) {
  if (!confirm(`Excluir o convênio "${convenio.nome}"?`)) return;
  try {
    await apiFetch(`/convenios/${convenio.id_convenio}`, { method: "DELETE" });
    await carregarConvenios();
    await carregarPacientes();
    mostrarAviso("Convênio excluído.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
  }
}

// ======================= Lista de pacientes =======================
function buscarPacientes() {
  const termo = el("busca").value.trim();
  if (!termo) return carregarPacientes();

  const apenasNumeros = termo.replace(/\D/g, "");
  const pareceCpf = /^[\d.\-\s]+$/.test(termo) && apenasNumeros.length >= 11;
  const filtro = pareceCpf ? `?cpf=${apenasNumeros}` : `?nome=${encodeURIComponent(termo)}`;
  carregarPacientes(filtro);
}

async function carregarPacientes(filtro = "") {
  const corpo = el("tabela-pacientes");
  let lista = [];
  try {
    lista = await apiFetch("/pacientes" + filtro);
  } catch (e) {
    corpo.innerHTML = `<tr><td colspan="6" class="vazio">Erro ao carregar: ${escapeHtml(e.message)}</td></tr>`;
    return;
  }

  if (lista.length === 0) {
    corpo.innerHTML = `<tr><td colspan="6" class="vazio">Nenhum paciente encontrado.</td></tr>`;
    return;
  }

  corpo.innerHTML = lista
    .map(
      (p) => `<tr>
        <td><strong>${escapeHtml(p.nome)}</strong></td>
        <td>${escapeHtml(formatarCpf(p.cpf))}</td>
        <td>${formatarData(p.data_nascimento)}</td>
        <td>${escapeHtml(p.sexo || "—")}</td>
        <td><span class="pill ${p.id_convenio ? "pill-info" : "pill-alerta"}">${escapeHtml(nomeConvenio(p.id_convenio))}</span></td>
        <td>
          <div class="acoes">
            <button class="botao botao-secundario botao-sm" data-acao="detalhes" data-id="${p.id_paciente}">Detalhes</button>
            <button class="botao botao-secundario botao-sm" data-acao="editar" data-id="${p.id_paciente}">Editar</button>
            <button class="botao botao-perigo botao-sm" data-acao="excluir" data-id="${p.id_paciente}">Excluir</button>
          </div>
        </td>
      </tr>`
    )
    .join("");

  corpo.querySelectorAll("button[data-acao]").forEach((botao) => {
    const paciente = lista.find((p) => p.id_paciente === Number(botao.dataset.id));
    botao.addEventListener("click", () => {
      if (botao.dataset.acao === "detalhes") abrirDetalhes(paciente);
      if (botao.dataset.acao === "editar") abrirFormPaciente(paciente);
      if (botao.dataset.acao === "excluir") excluirPaciente(paciente);
    });
  });
}

// ======================= Cadastro / edição =======================
function abrirFormPaciente(paciente = null) {
  const editando = !!paciente;
  const opcoesConvenio =
    `<option value="">Particular (sem convênio)</option>` +
    convenios
      .map((c) => `<option value="${c.id_convenio}" ${paciente && paciente.id_convenio === c.id_convenio ? "selected" : ""}>${escapeHtml(c.nome)}</option>`)
      .join("");

  const html = `
    <div class="form-grupo"><label>Nome *</label><input type="text" id="f-nome" value="${escapeHtml(paciente?.nome)}" /></div>
    <div class="form-linha">
      <div class="form-grupo"><label>Data de nascimento</label><input type="date" id="f-nasc" value="${escapeHtml(paciente?.data_nascimento)}" /></div>
      <div class="form-grupo">
        <label>Sexo</label>
        <select id="f-sexo">
          <option value="">—</option>
          <option value="F" ${paciente?.sexo === "F" ? "selected" : ""}>Feminino</option>
          <option value="M" ${paciente?.sexo === "M" ? "selected" : ""}>Masculino</option>
        </select>
      </div>
    </div>
    <div class="form-grupo"><label>CPF (11 números)</label><input type="text" id="f-cpf" maxlength="14" value="${escapeHtml(paciente?.cpf)}" /></div>
    <div class="form-linha">
      <div class="form-grupo"><label>Convênio</label><select id="f-convenio">${opcoesConvenio}</select></div>
      <div class="form-grupo"><label>Nº da carteirinha</label><input type="text" id="f-carteirinha" value="${escapeHtml(paciente?.numero_carteirinha)}" /></div>
    </div>`;

  abrirModal(editando ? "Editar paciente" : "Novo paciente", html, {
    aoSalvar: async (corpo) => {
      const nome = corpo.querySelector("#f-nome").value.trim();
      const cpfBruto = corpo.querySelector("#f-cpf").value.trim();
      const cpf = cpfBruto.replace(/\D/g, "");
      const convenio = corpo.querySelector("#f-convenio").value;

      if (!nome) throw new Error("Informe o nome do paciente.");
      if (cpfBruto && cpf.length !== 11) throw new Error("O CPF precisa ter 11 números.");

      if (cpf) {
        const existentes = await apiFetch(`/pacientes?cpf=${cpf}`);
        const duplicado = existentes.some((p) => !editando || p.id_paciente !== paciente.id_paciente);
        if (duplicado) throw new Error("Já existe um paciente com esse CPF.");
      }

      const dados = {
        nome,
        data_nascimento: corpo.querySelector("#f-nasc").value || null,
        cpf: cpf || null,
        sexo: corpo.querySelector("#f-sexo").value || null,
        id_convenio: convenio ? Number(convenio) : null,
        numero_carteirinha: corpo.querySelector("#f-carteirinha").value.trim() || null,
      };

      if (editando) {
        await apiFetch(`/pacientes/${paciente.id_paciente}`, { method: "PUT", body: JSON.stringify(dados) });
      } else {
        await apiFetch("/pacientes", { method: "POST", body: JSON.stringify(dados) });
      }
      await carregarPacientes();
      mostrarAviso(editando ? "Paciente atualizado." : "Paciente cadastrado.");
    },
  });
}

async function excluirPaciente(paciente) {
  if (!confirm(`Excluir o paciente "${paciente.nome}"? Essa ação não pode ser desfeita.`)) return;
  try {
    await apiFetch(`/pacientes/${paciente.id_paciente}`, { method: "DELETE" });
    await carregarPacientes();
    mostrarAviso("Paciente excluído.");
  } catch (e) {
    mostrarAviso(e.message, "erro");
  }
}

// ======================= Detalhes =======================
async function abrirDetalhes(paciente) {
  const corpo = abrirModal(`Paciente: ${paciente.nome}`, `<p class="placeholder-aviso">Carregando...</p>`, { largura: "760px" });
  await renderDetalhes(corpo, paciente);
}

async function renderDetalhes(corpo, paciente) {
  const id = paciente.id_paciente;
  let contatos = [];
  let prontuario = null;
  let consultas = [];
  const mapaMedicos = {};
  const atendimentos = {};

  try { contatos = await apiFetch(`/pacientes/${id}/contatos`); } catch (e) { contatos = []; }
  try { prontuario = await apiFetch(`/pacientes/${id}/prontuario`); } catch (e) { prontuario = null; }

  // Histórico de consultas (vem do módulo de agenda)
  try {
    consultas = await apiFetch(`/consultas?id_paciente=${id}`);
    const medicos = await apiFetch("/medicos");
    medicos.forEach((m) => (mapaMedicos[m.id_medico] = m.nome));
    await Promise.all(
      consultas
        .filter((c) => c.status === "realizada")
        .map(async (c) => {
          try { atendimentos[c.id_consulta] = await apiFetch(`/consultas/${c.id_consulta}/atendimento`); } catch (e) { /* sem atendimento */ }
        })
    );
  } catch (e) {
    consultas = [];
  }

  const listaContatos = contatos.length
    ? contatos
        .map((c) => `<div class="lista-item"><span>${escapeHtml(c.tipo_contato)}: <strong>${escapeHtml(c.valor_contato)}</strong></span>
          <span style="display:flex;gap:6px;align-items:center;">
            ${c.eh_preferencial ? '<span class="pill pill-sucesso">Preferencial</span>' : `<button type="button" class="botao botao-secundario botao-sm" data-preferir="${c.id_contato}">Tornar preferencial</button>`}
            <button type="button" class="botao botao-perigo botao-sm" data-remover-contato="${c.id_contato}">Remover</button>
          </span></div>`)
        .join("")
    : `<p class="placeholder-aviso">Nenhum contato cadastrado.</p>`;

  const blocoProntuario = prontuario
    ? `<p style="margin:0 0 0.6rem;font-size:0.8rem;color:#6c757d;">Aberto em ${formatarData(prontuario.data_abertura)}</p>
       <div class="form-grupo" style="max-width:220px;">
         <label>Tipo sanguíneo</label>
         <select id="pe-sangue">
           <option value="">—</option>
           ${TIPOS_SANGUE.map((tipo) => `<option value="${tipo}" ${prontuario.tipo_sangue === tipo ? "selected" : ""}>${tipo}</option>`).join("")}
         </select>
       </div>
       <div class="form-grupo"><label>Observações</label><textarea id="pe-obs">${escapeHtml(prontuario.observacoes)}</textarea></div>
       <button type="button" class="botao botao-secundario botao-sm" id="btn-salvar-prontuario">Salvar prontuário</button>`
    : `<p class="placeholder-aviso">Esse paciente ainda não tem prontuário.</p>
       <div class="form-inline">
         <select id="p-sangue">
           <option value="">Tipo sanguíneo</option>
           ${TIPOS_SANGUE.map((t) => `<option value="${t}">${t}</option>`).join("")}
         </select>
         <input type="text" id="p-obs" placeholder="Observações" />
         <button type="button" class="botao botao-primario botao-sm" id="btn-abrir-prontuario">Abrir prontuário</button>
       </div>`;

  const historico = consultas.length
    ? consultas
        .map((c) => {
          const at = atendimentos[c.id_consulta];
          const classe = c.status === "realizada" ? "pill-sucesso" : c.status === "cancelada" ? "pill-alerta" : "pill-info";
          return `<div class="lista-item" style="align-items:flex-start;">
            <span>${formatarDataHora(c.data_consulta)} · ${escapeHtml(mapaMedicos[c.id_medico] || "Médico #" + c.id_medico)}
              ${at && at.diagnostico ? `<br><small style="color:#6c757d;">Diagnóstico: ${escapeHtml(at.diagnostico)}</small>` : ""}</span>
            <span class="pill ${classe}">${escapeHtml(c.status)}</span>
          </div>`;
        })
        .join("")
    : `<p class="placeholder-aviso">Nenhuma consulta registrada.</p>`;

  corpo.innerHTML = `
    <div class="bloco-detalhe">
      <h3>Dados</h3>
      <div class="dados-grid">
        <div><span class="rot">CPF</span>${escapeHtml(formatarCpf(paciente.cpf))}</div>
        <div><span class="rot">Nascimento</span>${formatarData(paciente.data_nascimento)}</div>
        <div><span class="rot">Convênio</span>${escapeHtml(nomeConvenio(paciente.id_convenio))}</div>
        <div><span class="rot">Carteirinha</span>${escapeHtml(paciente.numero_carteirinha || "—")}</div>
      </div>
    </div>

    <div class="bloco-detalhe">
      <h3>Contatos</h3>
      ${listaContatos}
      <div class="form-inline">
        <select id="ct-tipo">
          <option value="telefone">Telefone</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="email">E-mail</option>
        </select>
        <input type="text" id="ct-valor" placeholder="Número ou e-mail" />
        <label class="check" style="margin:0;"><input type="checkbox" id="ct-pref" /> Preferencial</label>
        <button type="button" class="botao botao-primario botao-sm" id="btn-add-contato">Adicionar</button>
      </div>
    </div>

    <div class="bloco-detalhe">
      <h3>Prontuário</h3>
      ${blocoProntuario}
    </div>

    <div class="bloco-detalhe">
      <h3>Histórico de consultas</h3>
      ${historico}
    </div>`;

  corpo.querySelector("#btn-add-contato").addEventListener("click", async () => {
    const valor = corpo.querySelector("#ct-valor").value.trim();
    if (!valor) return mostrarAviso("Informe o contato.", "erro");
    try {
      await apiFetch("/contatos", {
        method: "POST",
        body: JSON.stringify({
          id_paciente: id,
          tipo_contato: corpo.querySelector("#ct-tipo").value,
          valor_contato: valor,
          eh_preferencial: corpo.querySelector("#ct-pref").checked,
        }),
      });
      await renderDetalhes(corpo, paciente);
    } catch (e) {
      mostrarAviso(e.message, "erro");
    }
  });

  corpo.querySelectorAll("button[data-remover-contato]").forEach((botao) => {
    botao.addEventListener("click", async () => {
      try {
        await apiFetch(`/contatos/${botao.dataset.removerContato}`, { method: "DELETE" });
        await renderDetalhes(corpo, paciente);
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  });

  corpo.querySelectorAll("button[data-preferir]").forEach((botao) => {
    botao.addEventListener("click", async () => {
      try {
        await apiFetch(`/contatos/${botao.dataset.preferir}`, { method: "PUT", body: JSON.stringify({ eh_preferencial: true }) });
        await renderDetalhes(corpo, paciente);
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  });

  const botaoSalvarProntuario = corpo.querySelector("#btn-salvar-prontuario");
  if (botaoSalvarProntuario) {
    botaoSalvarProntuario.addEventListener("click", async () => {
      try {
        await apiFetch(`/prontuarios/${prontuario.id_prontuario}`, {
          method: "PUT",
          body: JSON.stringify({
            tipo_sangue: corpo.querySelector("#pe-sangue").value || null,
            observacoes: corpo.querySelector("#pe-obs").value.trim() || null,
          }),
        });
        mostrarAviso("Prontuário atualizado.");
        await renderDetalhes(corpo, paciente);
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  }

  const botaoProntuario = corpo.querySelector("#btn-abrir-prontuario");
  if (botaoProntuario) {
    botaoProntuario.addEventListener("click", async () => {
      try {
        await apiFetch("/prontuarios", {
          method: "POST",
          body: JSON.stringify({
            id_paciente: id,
            data_abertura: hojeISO(),
            tipo_sangue: corpo.querySelector("#p-sangue").value || null,
            observacoes: corpo.querySelector("#p-obs").value.trim() || null,
          }),
        });
        await renderDetalhes(corpo, paciente);
      } catch (e) {
        mostrarAviso(e.message, "erro");
      }
    });
  }
}

iniciar();
