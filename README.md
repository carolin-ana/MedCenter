# MedCenter

Sistema de gestão hospitalar/clínica desenvolvido como trabalho da disciplina Programação Orientada a Objetos e Gerenciamento de Banco de dados — UNASP - SP, 4º semestre de ADS.

Cobre cadastro de pacientes (com convênio), corpo clínico, agenda de consultas, prescrições, exames, internação/enfermagem e faturamento.

> 🚧 Projeto em desenvolvimento. Este README será atualizado conforme os módulos forem ficando prontos.

---

## Equipe

| Integrante | Módulo |
|---|---|
| Larissa Pimenta | Pacientes & Prontuário |
| Dennys de Oliveira | Corpo Clínico & Agenda |
| Matheus Cardoso | Farmácia & Exames |
| Matheus Silva | Internação & Enfermagem |
| Ana Carolina | Financeiro, Auth & Infraestrutura |

---

## Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** MySQL
- **ORM:** SQLAlchemy
- **Validação:** Pydantic
- **Autenticação:** JWT
- **Frontend:** HTML + CSS + JavaScript (puro, com Bootstrap via CDN)

---

## Diagrama do banco de dados

Veja [`docs/diagrama-er.png`](docs/diagrama-er.png) para o modelo completo (19 tabelas).

---

## Como rodar o projeto localmente

### Pré-requisitos
- [Python 3.x](https://www.python.org/downloads/) instalado
- [MySQL](https://dev.mysql.com/downloads/installer/) instalado e rodando (MySQL Installer ou XAMPP)
- Editor de código (recomendado: [VS Code](https://code.visualstudio.com/))

> ⚠️ Recomendamos manter o projeto fora de pastas sincronizadas pelo OneDrive/Google Drive — isso costuma causar erros de permissão e travamentos ao criar o ambiente virtual.

### 1. Clonar o repositório
```
git clone <url-do-repositorio>
cd MedCenter
```

### 2. Configurar o backend

Entre na pasta do backend:
```
cd backend
```

Crie e ative o ambiente virtual:
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

Instale as dependências:
```
pip install -r requirements.txt
```

Crie o arquivo `.env` na raiz de `backend` (copie de `.env.example`) e preencha com os dados do seu MySQL local:
```
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medcenter
SECRET_KEY=troque-essa-chave
```

Crie o banco de dados no MySQL (via MySQL Workbench ou phpMyAdmin):
```sql
CREATE DATABASE medcenter;
```

Suba o servidor:
```
uvicorn app.main:app --reload
```

A API deve subir em `http://127.0.0.1:8000` e a documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

### 3. Rodar o frontend

Abra a pasta `frontend` com a extensão **Live Server** do VS Code, ou abra o `index.html` direto no navegador.

> Certifique-se de que o backend (passo 2) esteja rodando antes de usar o frontend.

---

## Estrutura de pastas

```
backend/
  .env
  requirements.txt
  app/
    core/          -> configuração, conexão com banco, autenticação
    modules/        -> um módulo por área do sistema (pacientes, agenda, etc.)
    main.py
frontend/
  pacientes/
  agenda/
  farmacia-exames/
  internacao/
  financeiro/
  services/        -> funções que chamam a API
  index.html
docs/
  diagrama-er.png
  README.md
```

---

## Status dos módulos

| Módulo | Backend | Frontend |
|---|---|---|
| Pacientes & Prontuário | ⬜ | ⬜ |
| Corpo Clínico & Agenda | ⬜ | ⬜ |
| Farmácia & Exames | ⬜ | ⬜ |
| Internação & Enfermagem | ⬜ | ⬜ |
| Financeiro | ⬜ | ⬜ |
| Autenticação | ⬜ | ⬜ |

---

## Licença

Projeto acadêmico — uso educacional.
