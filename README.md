# MedCenter

Sistema de gestão hospitalar desenvolvido como trabalho da disciplina de Programação Orientada a Objetos e Gerenciamento de Banco de Dados (UNASP-SP, 4º semestre de ADS).

Cobre cadastro de pacientes (com convênio), corpo clínico, agenda de consultas, prescrições, exames, internação/enfermagem e faturamento.

> Projeto em desenvolvimento. Entrega prevista para **23/11/2026**.

---

## Equipe

| Integrante | Módulo |
|---|---|
| Larissa Pimenta | Pacientes & Prontuário |
| Dennys | Corpo Clínico & Agenda |
| Matheus Cardoso | Farmácia & Exames |
| Matheus Silva | Internação & Enfermagem |
| Ana Carolina | Financeiro, Autenticação & Infraestrutura |

---

## Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** MySQL
- **ORM:** SQLAlchemy (driver PyMySQL)
- **Validação:** Pydantic
- **Autenticação:** JWT
- **Frontend:** HTML + CSS + JavaScript puro (sem build), com Bootstrap Icons via CDN

---

## Programação Orientada a Objetos no projeto

O backend usa uma **camada de serviço** entre as rotas e o banco:

- `app/core/base_service.py` define a classe genérica `BaseService`, com o CRUD padrão (`listar`, `obter`, `criar`, `atualizar`, `excluir`).
- Cada módulo tem uma classe de serviço que **herda** de `BaseService` (ex.: `FaturamentoService`, `ConsultaService`).
- Os serviços **sobrescrevem** métodos (polimorfismo) para aplicar regras de negócio e depois chamam `super()` para reaproveitar o comportamento padrão. Exemplo: `FaturamentoService.criar()` puxa o convênio do paciente automaticamente, e `ConsultaService.criar()` impede dois atendimentos do mesmo médico no mesmo horário.
- A conexão com o banco fica **encapsulada** dentro das classes de serviço (`_db`). As rotas só chamam os métodos públicos.

Padrão de cada módulo: `models.py` → `schemas.py` → `service.py` → `routes.py`.

---

## Diagrama do banco de dados

Veja [`docs/diagrama-er.png`](docs/diagrama-er.png): modelo completo, com 22 tabelas.

---

## Como rodar o projeto localmente

### Pré-requisitos
- [Python 3](https://www.python.org/downloads/) instalado
- [MySQL](https://dev.mysql.com/downloads/installer/) instalado e rodando
- [VS Code](https://code.visualstudio.com/) (com a extensão Live Server para o frontend)

> Mantenha o projeto **fora de pastas sincronizadas** (OneDrive, Google Drive). Isso causa erros de permissão e trava a criação do ambiente virtual.

### 1. Clonar o repositório
```
git clone https://github.com/carolin-ana/MedCenter.git
cd MedCenter
```

### 2. Criar o banco no MySQL
No MySQL Workbench, rode:
```sql
CREATE DATABASE medcenter;
```
O SQLAlchemy cria as tabelas, mas **não** cria o banco em si.

### 3. Configurar o backend
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Em Mac/Linux, ative o ambiente com `source venv/bin/activate`.

Se o PowerShell bloquear a ativação do venv, rode uma vez:
```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 4. Criar o arquivo `.env`
Crie `backend/.env` (na raiz de `backend`, **não** dentro de `app/core`):
```
DB_USER=root
DB_PASSWORD=sua_senha_do_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medcenter
SECRET_KEY=uma-chave-longa-e-aleatoria
```
Para gerar uma chave: `python -c "import secrets; print(secrets.token_hex(32))"`

O `.env` está no `.gitignore` e **nunca** deve ser enviado ao GitHub.

### 5. Subir o servidor
```
uvicorn app.main:app --reload
```
Ao subir, o SQLAlchemy cria no MySQL as tabelas que ainda não existirem. A API fica em `http://127.0.0.1:8000` e a documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

### 6. Criar o primeiro usuário
Cada pessoa tem o próprio MySQL local, então o banco começa sem usuários. No Swagger, use `POST /auth/registrar`:
```json
{
  "nome": "Admin",
  "email": "admin@teste.com",
  "senha": "123456",
  "perfil": "admin"
}
```
Depois clique em **Authorize** (cadeado) e entre com o email e a senha. As rotas protegidas exigem esse login.

### 7. Rodar o frontend
Com o backend rodando, abra `frontend/index.html` com o **Live Server** do VS Code (botão direito no arquivo → *Open with Live Server*) e faça login.

---

## Estrutura de pastas

```
backend/
  .env                  (local, não vai pro GitHub)
  requirements.txt
  app/
    main.py             ponto de entrada da API
    core/               config, banco, segurança (JWT), BaseService
    modules/
      auth/
      pacientes/
      agenda/
      farmacia_exames/
      internacao/
      financeiro/
frontend/
  index.html            dashboard
  style.css
  services/api.js       funções que chamam a API
  financeiro/
docs/
  diagrama-er.png
```

---

## Status dos módulos

| Módulo | Responsável | Backend | Frontend |
|---|---|---|---|
| Autenticação | Ana Carolina | ✅ | ✅ (login no dashboard) |
| Financeiro | Ana Carolina | ✅ | ✅ |
| Pacientes & Prontuário | Larissa | ✅ | ⬜ |
| Corpo Clínico & Agenda | Dennys | ✅ | ⬜ |
| Farmácia & Exames | Matheus Cardoso | 🔶 em andamento | ⬜ |
| Internação & Enfermagem | Matheus Silva | ⬜ (só models) | ⬜ |

Legenda: ✅ pronto · 🔶 em andamento · ⬜ não iniciado

---

## Problemas comuns

| Erro | Causa e solução |
|---|---|
| `Unknown database 'medcenter'` | O banco não foi criado. Rode o `CREATE DATABASE` do passo 2. |
| `Access denied for user 'root'` | A senha do `.env` não bate com a do MySQL. |
| `uvicorn` não é reconhecido | O venv não está ativo. Rode `venv\Scripts\activate`. |
| Erro de `bcrypt` ao registrar usuário | Incompatibilidade entre `passlib` e `bcrypt`. O `requirements.txt` já fixa uma versão compatível. |
| `401 Not authenticated` | Faltou o **Authorize** no Swagger, ou o token expirou. |
| `Fatal error in launcher` ao usar `pip` | O venv foi criado em outra pasta. Apague a pasta `venv` e crie de novo. |

---

## Licença

Projeto acadêmico, para uso educacional.
