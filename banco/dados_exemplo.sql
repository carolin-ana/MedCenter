-- =====================================================================
-- MedCenter - dados de exemplo (TODOS FICTÍCIOS) para a demonstração
-- Rode UMA vez, no MySQL Workbench, com o banco medcenter vazio de
-- dados de teste. Não mexe na tabela usuarios (o login continua o seu).
-- =====================================================================
USE medcenter;

-- Garante que estas colunas aceitam "ainda sem saída" / "sem texto"
ALTER TABLE internacao MODIFY data_saida DATETIME NULL;
ALTER TABLE internacao MODIFY motivo_internacao TEXT NULL;
ALTER TABLE internacao_quarto MODIFY data_saida DATETIME NULL;

-- ---------------------------------------------------------------------
-- 1. CONVÊNIOS
-- ---------------------------------------------------------------------
INSERT INTO convenio (nome, registro_ans, telefone) VALUES
('Unimed Exemplo',   '300001', '(11) 4000-1000'),
('Bradesco Saúde Exemplo', '300002', '(11) 4000-2000'),
('SulAmérica Exemplo',     '300003', '(11) 4000-3000');
SET @conv_unimed   = (SELECT id_convenio FROM convenio WHERE registro_ans = '300001' LIMIT 1);
SET @conv_bradesco = (SELECT id_convenio FROM convenio WHERE registro_ans = '300002' LIMIT 1);
SET @conv_sul      = (SELECT id_convenio FROM convenio WHERE registro_ans = '300003' LIMIT 1);

-- ---------------------------------------------------------------------
-- 2. ESPECIALIDADES E MÉDICOS
-- ---------------------------------------------------------------------
INSERT INTO especialidade (nome, descricao, area) VALUES
('Clínica Geral', 'Atendimento geral de adultos', 'Clínica'),
('Cardiologia',   'Doenças do coração e circulação', 'Clínica'),
('Pediatria',     'Saúde de crianças e adolescentes', 'Clínica'),
('Ortopedia',     'Ossos, músculos e articulações', 'Cirúrgica');
SET @esp_geral = (SELECT id_especialidade FROM especialidade WHERE nome = 'Clínica Geral' ORDER BY id_especialidade DESC LIMIT 1);
SET @esp_card  = (SELECT id_especialidade FROM especialidade WHERE nome = 'Cardiologia'   ORDER BY id_especialidade DESC LIMIT 1);
SET @esp_ped   = (SELECT id_especialidade FROM especialidade WHERE nome = 'Pediatria'     ORDER BY id_especialidade DESC LIMIT 1);
SET @esp_orto  = (SELECT id_especialidade FROM especialidade WHERE nome = 'Ortopedia'     ORDER BY id_especialidade DESC LIMIT 1);

INSERT INTO medicos (nome, crm, telefone) VALUES
('Dr. Rafael Almeida', 'CRM-SP 900001', '(11) 90000-0001'),
('Dra. Helena Duarte', 'CRM-SP 900002', '(11) 90000-0002'),
('Dr. Bruno Teixeira', 'CRM-SP 900003', '(11) 90000-0003'),
('Dra. Marina Lopes',  'CRM-SP 900004', '(11) 90000-0004');
SET @med1 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900001');
SET @med2 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900002');
SET @med3 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900003');
SET @med4 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900004');

-- Vínculo médico x especialidade (um médico pode ter mais de uma)
INSERT INTO medico_especialidade (id_medico, id_especialidade, data_inicio) VALUES
(@med1, @esp_geral, '2018-03-01'),
(@med2, @esp_card,  '2016-08-15'),
(@med2, @esp_geral, '2019-02-01'),
(@med3, @esp_orto,  '2020-01-10'),
(@med4, @esp_ped,   '2017-05-20');

-- ---------------------------------------------------------------------
-- 3. PACIENTES, CONTATOS E PRONTUÁRIOS
-- ---------------------------------------------------------------------
INSERT INTO pacientes (nome, data_nascimento, cpf, sexo, id_convenio, numero_carteirinha) VALUES
('Maria Fernanda Souza', '1985-04-12', '111.111.111-11', 'F', @conv_unimed,   'UNI-000123'),
('João Pedro Lima',      '1990-09-30', '222.222.222-22', 'M', @conv_bradesco, 'BRA-000456'),
('Ana Beatriz Costa',    '2016-01-25', '333.333.333-33', 'F', @conv_unimed,   'UNI-000789'),
('Carlos Eduardo Rocha', '1972-11-05', '444.444.444-44', 'M', NULL, NULL),
('Luciana Martins',      '1968-06-18', '555.555.555-55', 'F', @conv_sul,      'SUL-000321'),
('Pedro Henrique Alves', '2001-02-14', '666.666.666-66', 'M', NULL, NULL);
SET @p1 = (SELECT id_paciente FROM pacientes WHERE cpf = '111.111.111-11');
SET @p2 = (SELECT id_paciente FROM pacientes WHERE cpf = '222.222.222-22');
SET @p3 = (SELECT id_paciente FROM pacientes WHERE cpf = '333.333.333-33');
SET @p4 = (SELECT id_paciente FROM pacientes WHERE cpf = '444.444.444-44');
SET @p5 = (SELECT id_paciente FROM pacientes WHERE cpf = '555.555.555-55');
SET @p6 = (SELECT id_paciente FROM pacientes WHERE cpf = '666.666.666-66');

INSERT INTO contato_paciente (id_paciente, tipo_contato, valor_contato, eh_preferencial) VALUES
(@p1, 'telefone', '(11) 98888-1111', 1),
(@p1, 'email',    'maria.souza@exemplo.com', 0),
(@p2, 'telefone', '(11) 98888-2222', 1),
(@p3, 'telefone', '(11) 98888-3333', 1),
(@p4, 'telefone', '(11) 98888-4444', 1),
(@p4, 'email',    'carlos.rocha@exemplo.com', 0),
(@p5, 'telefone', '(11) 98888-5555', 1),
(@p6, 'email',    'pedro.alves@exemplo.com', 1);

INSERT INTO prontuario (id_paciente, data_abertura, tipo_sangue, observacoes) VALUES
(@p1, '2026-01-10', 'O+',  'Hipertensão leve controlada.'),
(@p2, '2026-02-03', 'A+',  'Sem alergias conhecidas.'),
(@p3, '2026-02-20', 'B+',  'Acompanhamento pediátrico de rotina.'),
(@p4, '2026-03-15', 'AB-', 'Fumante. Queixa de dor no joelho.'),
(@p5, '2026-04-02', 'O-',  'Diabetes tipo 2.'),
(@p6, '2026-05-08', 'A-',  'Sem observações.');

-- ---------------------------------------------------------------------
-- 4. CONSULTAS E ATENDIMENTOS
-- (as de "hoje" usam CURDATE(), então aparecem no dashboard)
-- ---------------------------------------------------------------------
INSERT INTO consulta (id_paciente, id_medico, data_consulta, status) VALUES
(@p1, @med2, TIMESTAMP(CURDATE(), '09:00:00'), 'agendada'),
(@p3, @med4, TIMESTAMP(CURDATE(), '10:30:00'), 'agendada'),
(@p6, @med1, TIMESTAMP(CURDATE(), '14:00:00'), 'agendada'),
(@p4, @med3, TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '11:00:00'), 'realizada'),
(@p2, @med1, TIMESTAMP(CURDATE() - INTERVAL 9 DAY, '15:30:00'), 'realizada'),
(@p5, @med2, TIMESTAMP(CURDATE() - INTERVAL 2 DAY, '08:30:00'), 'realizada'),
(@p1, @med1, TIMESTAMP(CURDATE() + INTERVAL 3 DAY, '16:00:00'), 'agendada'),
(@p6, @med4, TIMESTAMP(CURDATE() - INTERVAL 1 DAY, '13:00:00'), 'cancelada');

SET @c_carlos = (SELECT id_consulta FROM consulta WHERE id_paciente = @p4 AND status = 'realizada' LIMIT 1);
SET @c_joao   = (SELECT id_consulta FROM consulta WHERE id_paciente = @p2 AND status = 'realizada' LIMIT 1);
SET @c_luciana= (SELECT id_consulta FROM consulta WHERE id_paciente = @p5 AND status = 'realizada' LIMIT 1);

INSERT INTO atendimentos (id_consulta, descricao, diagnostico, observacoes) VALUES
(@c_carlos,  'Dor no joelho direito há duas semanas.', 'Tendinite patelar', 'Repouso e fisioterapia.'),
(@c_joao,    'Febre e dor de garganta.', 'Amigdalite', 'Retorno em 7 dias se persistir.'),
(@c_luciana, 'Controle de rotina do coração.', 'Hipertensão controlada', 'Manter medicação e dieta.');
SET @at_carlos  = (SELECT id_atendimento FROM atendimentos WHERE id_consulta = @c_carlos);
SET @at_joao    = (SELECT id_atendimento FROM atendimentos WHERE id_consulta = @c_joao);
SET @at_luciana = (SELECT id_atendimento FROM atendimentos WHERE id_consulta = @c_luciana);

-- ---------------------------------------------------------------------
-- 5. FARMÁCIA: MEDICAMENTOS, PRESCRIÇÕES
-- ---------------------------------------------------------------------
INSERT INTO medicamento (nome, descricao, quantidade_estoque) VALUES
('Dipirona 500mg',     'Analgésico e antitérmico',     200),
('Ibuprofeno 600mg',   'Anti-inflamatório',            150),
('Amoxicilina 500mg',  'Antibiótico',                   80),
('Losartana 50mg',     'Anti-hipertensivo',            120),
('Metformina 850mg',   'Controle de diabetes',         100),
('Omeprazol 20mg',     'Protetor gástrico',             60);
SET @m_dip  = (SELECT id_medicamento FROM medicamento WHERE nome = 'Dipirona 500mg'    ORDER BY id_medicamento DESC LIMIT 1);
SET @m_ibu  = (SELECT id_medicamento FROM medicamento WHERE nome = 'Ibuprofeno 600mg'  ORDER BY id_medicamento DESC LIMIT 1);
SET @m_amo  = (SELECT id_medicamento FROM medicamento WHERE nome = 'Amoxicilina 500mg' ORDER BY id_medicamento DESC LIMIT 1);
SET @m_los  = (SELECT id_medicamento FROM medicamento WHERE nome = 'Losartana 50mg'    ORDER BY id_medicamento DESC LIMIT 1);
SET @m_met  = (SELECT id_medicamento FROM medicamento WHERE nome = 'Metformina 850mg'  ORDER BY id_medicamento DESC LIMIT 1);

INSERT INTO prescricoes (id_atendimento, observacao, status) VALUES (@at_carlos,  'Tomar após as refeições.', 'ativa');
SET @pr_carlos = LAST_INSERT_ID();
INSERT INTO prescricoes (id_atendimento, observacao, status) VALUES (@at_joao,    'Completar todo o antibiótico.', 'ativa');
SET @pr_joao = LAST_INSERT_ID();
INSERT INTO prescricoes (id_atendimento, observacao, status) VALUES (@at_luciana, 'Uso contínuo.', 'ativa');
SET @pr_luciana = LAST_INSERT_ID();

INSERT INTO prescricao_medicamento (id_prescricao, id_medicamento, dosagem, frequencia, duracao, quantidade, instrucoes) VALUES
(@pr_carlos,  @m_ibu, '600mg', '8 em 8 horas',  '5 dias',  15, 'Tomar com alimento.'),
(@pr_joao,    @m_amo, '500mg', '8 em 8 horas',  '7 dias',  21, 'Não interromper o tratamento.'),
(@pr_joao,    @m_dip, '500mg', '6 em 6 horas',  '3 dias',  12, 'Se houver febre.'),
(@pr_luciana, @m_los, '50mg',  '1 vez ao dia',  '30 dias', 30, 'Pela manhã.'),
(@pr_luciana, @m_met, '850mg', '2 vezes ao dia','30 dias', 60, 'Junto das refeições.');

-- ---------------------------------------------------------------------
-- 6. EXAMES E PEDIDOS (um com resultado, outro pendente)
-- ---------------------------------------------------------------------
INSERT INTO exame (nome, descricao) VALUES
('Hemograma completo',   'Análise das células do sangue'),
('Glicemia em jejum',    'Dosagem de glicose no sangue'),
('Raio-X de joelho',     'Imagem do joelho'),
('Eletrocardiograma',    'Atividade elétrica do coração');
SET @e_hemo = (SELECT id_exame FROM exame WHERE nome = 'Hemograma completo' ORDER BY id_exame DESC LIMIT 1);
SET @e_gli  = (SELECT id_exame FROM exame WHERE nome = 'Glicemia em jejum'  ORDER BY id_exame DESC LIMIT 1);
SET @e_rx   = (SELECT id_exame FROM exame WHERE nome = 'Raio-X de joelho'   ORDER BY id_exame DESC LIMIT 1);
SET @e_ecg  = (SELECT id_exame FROM exame WHERE nome = 'Eletrocardiograma'  ORDER BY id_exame DESC LIMIT 1);

INSERT INTO pedido_exame (id_atendimento, status, observacoes) VALUES (@at_carlos, 'concluido', 'Investigar lesão no joelho.');
SET @pe_carlos = LAST_INSERT_ID();
INSERT INTO pedido_exame (id_atendimento, status, observacoes) VALUES (@at_luciana, 'pendente', 'Controle semestral.');
SET @pe_luciana = LAST_INSERT_ID();
INSERT INTO pedido_exame (id_atendimento, status, observacoes) VALUES (@at_joao, 'pendente', 'Confirmar infecção.');
SET @pe_joao = LAST_INSERT_ID();

INSERT INTO pedido_exame_item (id_pedido_exame, id_exame, observacoes, resultado, data_resultado) VALUES
(@pe_carlos,  @e_rx,   'Joelho direito', 'Sem fraturas. Leve inflamação do tendão patelar.', CURDATE() - INTERVAL 3 DAY),
(@pe_luciana, @e_gli,  'Jejum de 8 horas', NULL, NULL),
(@pe_luciana, @e_ecg,  NULL, NULL, NULL),
(@pe_joao,    @e_hemo, NULL, NULL, NULL);

-- ---------------------------------------------------------------------
-- 7. QUARTOS E ENFERMEIROS
-- ---------------------------------------------------------------------
INSERT INTO quartos (numero_quarto, tipo, capacidade, status) VALUES
('101', 'Individual',  1, 'disponivel'),
('102', 'Individual',  1, 'disponivel'),
('201', 'Enfermaria',  3, 'disponivel'),
('202', 'Enfermaria',  3, 'disponivel'),
('UTI1','UTI',         1, 'disponivel');
SET @q101 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '101' ORDER BY id_quarto DESC LIMIT 1);
SET @q102 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '102' ORDER BY id_quarto DESC LIMIT 1);
SET @q201 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '201' ORDER BY id_quarto DESC LIMIT 1);

INSERT INTO enfermeiros (nome_enfermeiro, coren, turno, telefone) VALUES
('Juliana Ramos',  'COREN-SP 700001', 'Manhã',    '(11) 97777-0001'),
('Ricardo Nunes',  'COREN-SP 700002', 'Tarde',    '(11) 97777-0002'),
('Patrícia Gomes', 'COREN-SP 700003', 'Noite',    '(11) 97777-0003');
SET @en1 = (SELECT id_enfermeiro FROM enfermeiros WHERE coren = 'COREN-SP 700001');
SET @en2 = (SELECT id_enfermeiro FROM enfermeiros WHERE coren = 'COREN-SP 700002');
SET @en3 = (SELECT id_enfermeiro FROM enfermeiros WHERE coren = 'COREN-SP 700003');

-- ---------------------------------------------------------------------
-- 8. INTERNAÇÕES (duas ativas e uma que já teve alta)
-- ---------------------------------------------------------------------
-- Ativa 1: Luciana, quarto 101
INSERT INTO internacao (id_paciente, id_medico_responsavel, data_entrada, data_saida, motivo_internacao)
VALUES (@p5, @med2, NOW() - INTERVAL 2 DAY, NULL, 'Descompensação da diabetes e pressão alta.');
SET @i_luciana = LAST_INSERT_ID();
INSERT INTO internacao_quarto (id_internacao, id_quarto, data_entrada, data_saida)
VALUES (@i_luciana, @q101, NOW() - INTERVAL 2 DAY, NULL);

-- Ativa 2: Carlos, quarto 201 (enfermaria compartilhável)
INSERT INTO internacao (id_paciente, id_medico_responsavel, data_entrada, data_saida, motivo_internacao)
VALUES (@p4, @med3, NOW() - INTERVAL 1 DAY, NULL, 'Cirurgia de joelho programada.');
SET @i_carlos = LAST_INSERT_ID();
INSERT INTO internacao_quarto (id_internacao, id_quarto, data_entrada, data_saida)
VALUES (@i_carlos, @q201, NOW() - INTERVAL 1 DAY, NULL);

-- Com alta: João, esteve no quarto 102
INSERT INTO internacao (id_paciente, id_medico_responsavel, data_entrada, data_saida, motivo_internacao)
VALUES (@p2, @med1, NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 7 DAY, 'Pneumonia leve, observação.');
SET @i_joao = LAST_INSERT_ID();
INSERT INTO internacao_quarto (id_internacao, id_quarto, data_entrada, data_saida)
VALUES (@i_joao, @q102, NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 7 DAY);

-- Quartos com paciente ficam "ocupado"
UPDATE quartos SET status = 'ocupado' WHERE id_quarto = @q101;
UPDATE quartos SET status = 'ocupado' WHERE id_quarto = @q201;

INSERT INTO atendimento_enfermeiro (id_internacao, id_enfermeiro, data_enfermeiro, observacoes) VALUES
(@i_luciana, @en1, NOW() - INTERVAL 1 DAY,  'Pressão 150/95. Medicação administrada.'),
(@i_luciana, @en3, NOW() - INTERVAL 12 HOUR,'Glicemia 210. Insulina aplicada.'),
(@i_carlos,  @en2, NOW() - INTERVAL 6 HOUR, 'Pré-operatório. Sinais vitais estáveis.'),
(@i_joao,    @en1, NOW() - INTERVAL 9 DAY,  'Temperatura 38°C. Paciente hidratado.');

-- ---------------------------------------------------------------------
-- 9. FATURAMENTO (convênio = o do paciente; particular = sem convênio)
-- ---------------------------------------------------------------------
INSERT INTO faturamento (id_paciente, id_consulta, id_internacao, id_convenio, valor_total, data_faturamento, status) VALUES
(@p4, @c_carlos,   NULL,        NULL,          250.00,  CURDATE() - INTERVAL 5 DAY, 'pago'),
(@p2, @c_joao,     NULL,        @conv_bradesco,180.00,  CURDATE() - INTERVAL 9 DAY, 'pago'),
(@p5, @c_luciana,  NULL,        @conv_sul,     220.00,  CURDATE() - INTERVAL 2 DAY, 'pendente'),
(@p2, NULL,        @i_joao,     @conv_bradesco,4800.00, CURDATE() - INTERVAL 7 DAY, 'pendente'),
(@p5, NULL,        @i_luciana,  @conv_sul,     3500.00, CURDATE(),                  'pendente'),
(@p4, NULL,        @i_carlos,   NULL,          7200.00, CURDATE(),                  'pendente');

-- ---------------------------------------------------------------------
-- Conferência rápida (opcional): quantos registros ficaram em cada tabela
-- ---------------------------------------------------------------------
SELECT 'convenio' t, COUNT(*) n FROM convenio UNION ALL
SELECT 'pacientes', COUNT(*) FROM pacientes UNION ALL
SELECT 'medicos', COUNT(*) FROM medicos UNION ALL
SELECT 'consulta', COUNT(*) FROM consulta UNION ALL
SELECT 'atendimentos', COUNT(*) FROM atendimentos UNION ALL
SELECT 'prescricoes', COUNT(*) FROM prescricoes UNION ALL
SELECT 'pedido_exame_item', COUNT(*) FROM pedido_exame_item UNION ALL
SELECT 'quartos', COUNT(*) FROM quartos UNION ALL
SELECT 'internacao', COUNT(*) FROM internacao UNION ALL
SELECT 'faturamento', COUNT(*) FROM faturamento;
