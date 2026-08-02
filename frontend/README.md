# Interface web hospitalar

Painel Next.js para operar a API FastAPI do projeto.

## Desenvolvimento local

Em um terminal, execute o backend:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --env-file .env
```

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:3000`. A URL padrão da API é
`http://127.0.0.1:8000` e pode ser alterada no cabeçalho da interface.

## Recursos

- dashboard e validação da base;
- pacientes, atendimentos e procedimentos;
- residentes, preceptores, unidades e catálogo;
- escalas com proteção concorrente;
- internações e altas;
- stored procedures;
- views e consultas analíticas;
- auditoria de atendimentos.

## Build

```powershell
npm run build
npm run build:cloudflare
```

Para uma implantação remota funcional, configure uma URL HTTPS pública do
backend em `NEXT_PUBLIC_API_BASE_URL` ou pela própria interface.
