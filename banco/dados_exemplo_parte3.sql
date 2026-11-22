-- =====================================================================
-- MedCenter - parte 3: continua a partir dos QUARTOS.
-- Use SOMENTE depois de a parte 2 ter chegado até os exames.
-- =====================================================================
USE medcenter;

SET @conv_bradesco = (SELECT id_convenio FROM convenio WHERE registro_ans = '300002' LIMIT 1);
SET @conv_sul      = (SELECT id_convenio FROM convenio WHERE registro_ans = '300003' LIMIT 1);
SET @med1 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900001');
SET @med2 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900002');
SET @med3 = (SELECT id_medico FROM medicos WHERE crm = 'CRM-SP 900003');
SET @p2 = (SELECT id_paciente FROM pacientes WHERE cpf = '22222222222');
SET @p4 = (SELECT id_paciente FROM pacientes WHERE cpf = '44444444444');
SET @p5 = (SELECT id_paciente FROM pacientes WHERE cpf = '55555555555');
SET @c_carlos  = (SELECT id_consulta FROM consulta WHERE id_paciente = @p4 AND status = 'realizada' LIMIT 1);
SET @c_joao    = (SELECT id_consulta FROM consulta WHERE id_paciente = @p2 AND status = 'realizada' LIMIT 1);
SET @c_luciana = (SELECT id_consulta FROM consulta WHERE id_paciente = @p5 AND status = 'realizada' LIMIT 1);

-- ---------------------------------------------------------------------
-- 7. QUARTOS E ENFERMEIROS
-- ---------------------------------------------------------------------
INSERT IGNORE INTO quartos (numero_quarto, tipo, capacidade, status) VALUES
('111', 'Individual',  1, 'disponivel'),
('112', 'Individual',  1, 'disponivel'),
('211', 'Enfermaria',  3, 'disponivel'),
('212', 'Enfermaria',  3, 'disponivel'),
('UTI9','UTI',         1, 'disponivel');
SET @q101 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '111' ORDER BY id_quarto DESC LIMIT 1);
SET @q102 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '112' ORDER BY id_quarto DESC LIMIT 1);
SET @q201 = (SELECT id_quarto FROM quartos WHERE numero_quarto = '211' ORDER BY id_quarto DESC LIMIT 1);

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
