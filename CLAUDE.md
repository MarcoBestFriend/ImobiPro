# ImobiPro - Sistema de Gestão Imobiliária

## 📋 Informações Rápidas do Projeto

- **Nome**: ImobiPro
- **Versão**: 1.6.0 (Consulta detalhada de pessoas, contratos e receitas)
- **Objetivo**: Sistema completo para gestão de imóveis, contratos, despesas e receitas de aluguéis
- **Stack**: Python 3.10+, Flask, SQLite, Jinja2
- **Ambiente**: Ubuntu 24.04, VSCode
- **Repositório**: https://github.com/MarcoBestFriend/ImobiPro
- **Branch Funcional**: inicio

## 🎯 Contexto do Desenvolvedor

O desenvolvedor tem **pouco conhecimento de programação**, mas está aprendendo. Por isso:
- ✅ Sempre explique o que cada código faz
- ✅ Use linguagem clara e didática
- ✅ Evite jargões técnicos desnecessários
- ✅ Forneça exemplos práticos
- ✅ **Faça perguntas antes de implementar mudanças significativas**
- ❌ Nunca altere código sem permissão explícita
- ❌ **Nunca mude o visual/design sem autorização**

## 🚀 Comandos Importantes

### Ativar Ambiente Virtual
```bash
cd ~/ImobiPro
source venv/bin/activate
```

### Executar Aplicação
```bash
python3 app.py
# Acesso: http://localhost:5000
```

### Executar Migração de Dados
```bash
python3 migrar_planilha.py ImobiPro.xlsx
```

### Executar Backup
```bash
python3 utils/backup.py
```

## 📂 Estrutura de Arquivos

```
ImobiPro/
├── app.py                          # Aplicação Flask (~2500 linhas)
├── config.py                       # Configurações
├── requirements.txt                # Dependências
├── database/
│   ├── schema.sql                  # Schema SQLite completo
│   ├── db_manager.py               # Gerenciador (~500 linhas)
│   └── imobipro.db                 # Banco de dados
├── backups/                        # Backups automáticos (SQLite + Excel)
├── templates/
│   ├── base.html                   # Base (tema dark)
│   ├── login.html                  # Página de login
│   ├── dashboard.html              # Dashboard principal
│   ├── admin/
│   │   ├── usuarios.html           # Lista de usuários
│   │   └── usuario_form.html       # Cadastro/edição de usuário
│   ├── imoveis/listar.html
│   ├── imoveis/form.html           # Cadastro/edição de imóveis
│   ├── imoveis/ver.html
│   ├── imoveis/atualizar_condominios.html  # Atualização em lote
│   ├── pessoas/listar.html
│   ├── pessoas/form.html
│   ├── pessoas/ver.html            # Consulta detalhada de pessoa
│   ├── contratos/listar.html
│   ├── contratos/form.html         # Cadastro/edição de contratos
│   ├── contratos/ver.html          # Consulta detalhada de contrato
│   ├── despesas/listar.html        # Lista + botões lançamento automático
│   ├── despesas/form.html          # Cadastro/edição de despesas
│   ├── receitas/listar.html
│   ├── receitas/form.html          # Cadastro/edição de receitas
│   ├── receitas/ver.html           # Consulta detalhada de receita
│   ├── relatorios/
│   │   ├── index.html              # Menu de relatórios
│   │   └── despesas_pendentes.html # Relatório despesas pendentes
│   └── dados/index.html            # Página de backup/importação
├── utils/backup.py                 # Backup/restore
├── migrar_planilha.py             # Migração Excel→SQLite
└── migrar_condominio.py           # Migração condomínio_sugerido → inquilino/total
```

## 🗄️ Dicionário de Dados - Schema Completo

### Tabela: imoveis

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária (auto) | Sim |
| endereco_completo | TEXT | Endereço completo | Sim |
| inscricao_imobiliaria | TEXT | Inscrição municipal | Não |
| matricula | TEXT | Matrícula do imóvel no cartório | Não |
| tipo_imovel | TEXT | Descrição do imóvel (aposentos, conservação) | Sim |
| id_proprietario | INTEGER | FK → pessoas.id (legado) | Não |
| proprietario | TEXT | Nome do proprietário (opções fixas) | Não |
| ocupado | TEXT | "Sim" ou "Não" (auto) | Sim |
| valor_iptu_anual | REAL | Valor anual IPTU | Não |
| forma_pagamento_iptu | TEXT | "Anual" ou "Mensal" | Sim |
| aluguel_pretendido | REAL | Valor sugerido para locação | Não |
| condominio_inquilino | REAL | Condomínio pago pelo inquilino (despesas ordinárias) | Não |
| condominio_total | REAL | Condomínio total (ordinárias + extraordinárias) | Não |
| dia_venc_condominio | INTEGER | Dia vencimento condomínio (1-31) | Não |
| valor_mercado | REAL | Valor de mercado do imóvel | Não |
| data_aquisicao | DATE | Data de aquisição | Não |
| numero_hidrometro | TEXT | Número do hidrômetro | Não |
| numero_relogio_energia | TEXT | Número do relógio de energia | Não |
| cidade | TEXT | Cidade (padrão: "Campo Grande") | Não |
| estado | TEXT | UF (padrão: "MS") | Não |
| cep | TEXT | CEP | Não |
| observacoes | TEXT | Observações gerais | Não |
| data_cadastro | TIMESTAMP | Data criação (auto) | Sim |
| data_atualizacao | TIMESTAMP | Última atualização (auto) | Sim |

**Regras**:
- `ocupado` é atualizado por trigger (quando contrato ativo/encerrado)
- Valores aceitos: `forma_pagamento_iptu` = "Anual" ou "Mensal"
- Valores aceitos: `ocupado` = "Sim" ou "Não"
- Valores aceitos: `proprietario` = "Marco", "Beatriz", "Gilma", "Antonio", "Marco e Bia" (ou NULL)
- `id_proprietario` referencia a tabela pessoas (campo legado, não utilizado)

---

### Tabela: pessoas

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| situacao | TEXT | "Inquilino"/"Fiador"/"Proprietário"/"Ambos" | Sim |
| nome_completo | TEXT | Nome completo | Sim |
| cpf_cnpj | TEXT | CPF/CNPJ (único) | Não |
| telefone | TEXT | Telefone | Não |
| email | TEXT | E-mail | Não |
| endereco_completo | TEXT | Endereço | Não |
| cidade | TEXT | Cidade | Não |
| patrimonio | REAL | Patrimônio | Não |
| estado_civil | TEXT | Estado civil | Não |
| nome_conjuge | TEXT | Nome cônjuge | Não |
| cpf_conjuge | TEXT | CPF cônjuge | Não |
| observacoes | TEXT | Observações | Não |
| data_cadastro | TIMESTAMP | Auto | Sim |
| data_atualizacao | TIMESTAMP | Auto | Sim |

**Regras**:
- Valores aceitos: `situacao` = "Inquilino", "Fiador" ou "Ambos"
- `cpf_cnpj` deve ser único

---

### Tabela: contratos

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| id_imovel | INTEGER | FK → imoveis.id | Sim |
| id_inquilino | INTEGER | FK → pessoas.id | Sim |
| id_fiador | INTEGER | FK → pessoas.id | Não |
| garantia | TEXT | Tipo garantia | Sim |
| inicio_contrato | DATE | Data início | Sim |
| fim_contrato | DATE | Data fim | Não |
| valor_aluguel | REAL | Aluguel mensal (>0) | Sim |
| dia_vencimento | INTEGER | Dia 1-31 | Sim |
| status_contrato | TEXT | Status | Sim |
| indice_reajuste | TEXT | IGPM/IPCA/etc | Não |
| data_base_reajuste | DATE | Data base reajuste | Não |
| ultimo_reajuste | DATE | Último reajuste | Não |
| percentual_ultimo_reajuste | REAL | % aplicado | Não |
| observacoes | TEXT | Observações | Não |
| data_cadastro | TIMESTAMP | Auto | Sim |
| data_atualizacao | TIMESTAMP | Auto | Sim |

**Regras**:
- Valores `garantia`: "antecipado", "nenhuma", "fiança", "caução"
- Valores `status_contrato`: "Ativo", "Prorrogado", "Encerrado", "Rescindido"
- Se `garantia`="fiança", então `id_fiador` é obrigatório
- `valor_aluguel` > 0
- `dia_vencimento` entre 1-31
- **Renovação automática** (alertar dashboard)

---

### Tabela: despesas

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| id_imovel | INTEGER | FK → imoveis.id | Sim |
| mes_referencia | DATE | Mês referência | Não |
| tipo_despesa | TEXT | Tipo | Sim |
| motivo_despesa | TEXT | Descrição | Não |
| valor_previsto | REAL | Valor previsto (>=0) | Sim |
| valor_pago | REAL | Valor pago | Não |
| vencimento_previsto | DATE | Vencimento | Não |
| data_pagamento | DATE | Data pagamento | Não |
| observacoes | TEXT | Observações | Não |
| recorrente | INTEGER | 0=Não, 1=Sim | Não |
| data_cadastro | TIMESTAMP | Auto | Sim |

**Regras**:
- Valores `tipo_despesa`: "Manutenção", "Condomínio", "Reforma", "IPTU", "Outros"
- `recorrente`=1 indica despesa mensal

---

### Tabela: receitas

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| id_contrato | INTEGER | FK → contratos.id | Sim |
| mes_referencia | DATE | Mês competência | Sim |
| aluguel_devido | REAL | Valor aluguel | Sim |
| condominio_devido | REAL | Valor condomínio | Não |
| iptu_devido | REAL | Valor IPTU | Não |
| desconto_multa | REAL | Desconto(-)/Multa(+) | Não |
| valor_total_devido | REAL | Total (calculado) | Sim |
| vencimento_previsto | DATE | Vencimento | Sim |
| data_recebimento | DATE | Recebimento | Não |
| valor_recebido | REAL | Valor recebido | Não |
| status | TEXT | Status pagamento | Sim |
| observacoes | TEXT | Observações | Não |
| data_cadastro | TIMESTAMP | Auto | Sim |

**Regras**:
- Valores `status`: "Pendente", "Recebido", "Atrasado", "Cancelado"
- `valor_total_devido` = aluguel + condomínio + iptu + desconto_multa (trigger)
- UNIQUE(id_contrato, mes_referencia)

---

### Tabela: usuarios

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| username | TEXT | Nome de usuário (único) | Sim |
| senha_hash | TEXT | Senha criptografada (werkzeug) | Sim |
| nome_completo | TEXT | Nome para exibição | Sim |
| email | TEXT | Email (opcional) | Não |
| ativo | INTEGER | 0=Inativo, 1=Ativo | Sim |
| admin | INTEGER | 0=Usuário, 1=Administrador | Sim |
| ultimo_acesso | TIMESTAMP | Último login | Não |
| data_cadastro | TIMESTAMP | Auto | Sim |
| data_atualizacao | TIMESTAMP | Auto | Sim |

**Regras**:
- `username` deve ser único e em minúsculas
- Senhas são armazenadas com hash (werkzeug.security)
- Usuários inativos não podem fazer login
- Apenas administradores podem gerenciar usuários

**Usuário padrão:**
- **Username:** `admin`
- **Senha:** `imobipro2026`

---

### Views SQL (Consultas Prontas)

**vw_contratos_completos**: Contratos + imóveis + pessoas
**vw_despesas_pendentes**: Despesas não pagas + situação
**vw_receitas_pendentes**: Receitas não recebidas + situação

---

## 🔧 Métodos do DatabaseManager

### CRUD Básico
```python
db.execute_query(query, params)            # SELECT
db.execute_update(query, params)           # INSERT/UPDATE/DELETE
db.insert(table, data_dict)                # Inserir
db.update(table, data, where, params)      # Atualizar
db.delete(table, where, params)            # Deletar
db.get_all(table, order_by)                # Buscar todos
db.get_by_id(table, id)                    # Buscar por ID
db.get_where(table, where, params, order)  # Buscar condição
```

### Específicos do Sistema
```python
db.get_imoveis_disponiveis()               # ocupado='Não'
db.get_contratos_ativos()                  # vw_contratos_completos
db.get_despesas_pendentes()                # vw_despesas_pendentes
db.get_receitas_pendentes()                # vw_receitas_pendentes
db.get_estatisticas_dashboard()            # Stats completas
```

**get_estatisticas_dashboard() retorna:**
```python
{
    'total_imoveis': int,
    'imoveis_disponiveis': int,
    'imoveis_ocupados': int,
    'contratos_ativos': int,
    'despesas_pendentes': int,
    'receitas_pendentes': int,
    'total_pessoas': int,
    'taxa_ocupacao': float  # %
}
```

---

## 🌐 Rotas Flask

### Autenticação
```
GET  /login                         → Página de login
POST /login                         → Processar login
GET  /logout                        → Fazer logout
```

### Administração de Usuários (somente admin)
```
GET  /admin/usuarios                → Lista de usuários
GET  /admin/usuarios/novo           → Form novo usuário
POST /admin/usuarios/novo           → Criar usuário
GET  /admin/usuarios/<id>/editar    → Form editar
POST /admin/usuarios/<id>/editar    → Processar edição
POST /admin/usuarios/<id>/excluir   → Excluir usuário
POST /admin/usuarios/<id>/toggle-ativo → Ativar/desativar
```

### Dashboard
```
GET  /               → Redireciona /dashboard
GET  /dashboard      → Dashboard com stats (imóveis disponíveis, despesas vencidas,
                        próxima despesa, próximo vencimento de contrato,
                        receitas pendentes, taxa de ocupação)
```

### Imóveis
```
GET  /imoveis                       → Lista
GET  /imoveis/novo                  → Form cadastro
POST /imoveis/novo                  → Processar
GET  /imoveis/<id>                  → Detalhes
GET  /imoveis/<id>/editar           → Form editar
POST /imoveis/<id>/editar           → Processar
POST /imoveis/<id>/excluir          → Excluir (com confirmação)
GET  /imoveis/atualizar-condominios → Form atualização em lote
POST /imoveis/atualizar-condominios → Processar atualização
```

### Pessoas
```
GET  /pessoas                   → Lista
GET  /pessoas/novo              → Form cadastro
POST /pessoas/novo              → Processar
GET  /pessoas/<id>              → Consulta detalhada (dados, contratos como inquilino/fiador)
GET  /pessoas/<id>/editar       → Form editar
POST /pessoas/<id>/editar       → Processar
POST /pessoas/<id>/excluir      → Excluir (com confirmação)
```

### Contratos
```
GET  /contratos                 → Lista
GET  /contratos/novo            → Form cadastro
POST /contratos/novo            → Processar
GET  /contratos/<id>            → Consulta detalhada (imóvel, inquilino, fiador, receitas)
GET  /contratos/<id>/editar     → Form editar
POST /contratos/<id>/editar     → Processar
POST /contratos/<id>/excluir    → Excluir (com confirmação)
```

### Despesas
```
GET  /despesas                      → Lista (filtros + estatísticas)
GET  /despesas/nova                 → Form cadastro
POST /despesas/nova                 → Processar
GET  /despesas/<id>/editar          → Form editar
POST /despesas/<id>/editar          → Processar
POST /despesas/<id>/excluir         → Excluir
POST /despesas/<id>/pagar           → Marcar como paga (atalho)
POST /despesas/gerar-iptu-anual     → Gera IPTU para todos imóveis
POST /despesas/gerar-condominio-mensal → Gera condomínio do mês
```

### Receitas
```
GET  /receitas                      → Lista (filtros + estatísticas)
GET  /receitas/nova                 → Form cadastro
POST /receitas/nova                 → Processar
GET  /receitas/<id>                 → Consulta detalhada (composição valor, imóvel, inquilino, recebimento)
GET  /receitas/<id>/editar          → Form editar
POST /receitas/<id>/editar          → Processar
POST /receitas/<id>/excluir         → Excluir
POST /receitas/<id>/receber         → Marcar como recebida (atalho)
```

### Dados (Importar/Exportar/Backup)
```
GET  /dados                         → Página de backup/restore
GET  /dados/exportar                → Download ZIP com CSVs de todas as tabelas
POST /dados/importar                → Upload ZIP para restaurar dados
GET  /dados/backup                  → Download do arquivo SQLite
POST /dados/executar-backup         → Criar backup na pasta backups/
```

### Relatórios
```
GET  /relatorios                              → Página de relatórios
GET  /relatorios/despesas-pendentes           → Relatório de despesas pendentes (HTML)
GET  /relatorios/despesas-pendentes/excel     → Exportar despesas para Excel
GET  /relatorios/imoveis-desocupados          → Relatório de imóveis desocupados (HTML)
GET  /relatorios/imoveis-desocupados/excel    → Exportar imóveis desocupados para Excel
GET  /relatorios/cobrancas-mes/excel          → Relatório de cobranças do mês (Excel)
GET  /relatorios/contratos/excel              → Relatório de contratos (Excel)
GET  /relatorios/fluxo-caixa/excel            → Fluxo de caixa por proprietário (Excel)
```

---

## 🎨 Filtros Jinja2

```python
{{ valor|formatar_moeda }}      # 1500.50 → "R$ 1.500,50"
{{ data|formatar_data }}        # "2026-01-15" → "15/01/2026"
{{ status|status_badge }}       # Retorna classe CSS
```

**Classes badge:**
- "Ativo" → badge-success
- "Pendente" → badge-warning
- "Atrasado" → badge-danger

---

## 🎨 Design System

### Visual
- **Tema**: Dark minimalista
- **Fundo**: `#1a1d29` (primário), `#252936` (secundário)
- **Texto**: `#e4e6eb` (primário), `#b0b3b8` (secundário)
- **Accent**: `#4a9eff`
- **Layout**: Sidebar 260px + conteúdo responsivo

### Princípios
- ✅ Minimalista, sem enfeites
- ✅ Fundo escuro, bom contraste
- ✅ Mobile-first (futuro)
- ❌ **NUNCA altere visual sem permissão**

---

## ✅ Estado Atual (10/02/2026)

### Dados Reais Importados
- 29 imóveis (dados reais do arquivo imoveis2026.xlsx)
- Pessoas cadastradas conforme necessidade
- Contratos cadastrados conforme necessidade

### Implementado
- ✅ Dashboard (imóveis disponíveis, despesas vencidas, próxima despesa, próx. venc. contrato)
- ✅ CRUD imóveis (listar, novo, editar, excluir, visualizar)
- ✅ CRUD pessoas (listar, novo, editar, excluir, **visualizar**) - consulta com contratos relacionados
- ✅ CRUD contratos (listar, novo, editar, excluir, **visualizar**) - consulta com receitas, imóvel, inquilino, fiador
- ✅ CRUD despesas (listar, novo, editar, excluir, pagar) - **status "Atrasada" automático**
- ✅ CRUD receitas (listar, novo, editar, excluir, receber, **visualizar**) - consulta com composição de valor
- ✅ **Lançamento automático IPTU anual** (data de vencimento customizada via modal)
- ✅ **Lançamento automático Condomínio mensal** (usa condominio_total)
- ✅ **Atualização em lote de condomínios** (inquilino e total separados)
- ✅ **Separação de condomínio**: inquilino (ordinárias) vs total (ordinárias + extraordinárias)
- ✅ Importação/Exportação de dados (ZIP com CSVs)
- ✅ Migração Excel
- ✅ Backup manual e download do banco
- ✅ **Backup automático diário** (02:00, mantém últimos 7)
- ✅ **Sistema de login** com usuários no banco de dados
- ✅ **Administração de usuários** (criar, editar, excluir, ativar/desativar)
- ✅ **Relatório de Despesas Pendentes** com exportação Excel
- ✅ **Relatório de Imóveis Desocupados** com exportação Excel
- ✅ **Relatório de Cobranças do Mês** (usa condominio_inquilino)
- ✅ **Relatório de Contratos** (Excel direto)
- ✅ **Relatório de Fluxo de Caixa** por proprietário (receitas/despesas pagas)
- ✅ **Botões de cadastro rápido** de inquilino/fiador no formulário de contratos

### Planejado (NÃO FAZER SEM PERMISSÃO)
- ⏳ Lançamento automático de receitas/aluguéis do mês
- ⏳ Alertas de vencimento
- ⏳ Reajustes automáticos de contratos
- ⏳ Gerar PDFs (contratos, recibos)

---

## 🔐 Segurança

### Sistema de Login
- Todas as rotas exigem autenticação (exceto /login)
- Senhas armazenadas com hash (werkzeug.security)
- Sessão com "remember me" ativado
- Último acesso registrado no banco

### Níveis de Acesso
- **Usuário comum:** Acesso a todas as funcionalidades do sistema
- **Administrador:** Acesso adicional à área de gerenciamento de usuários

### Credenciais Padrão
- **Usuário:** `admin`
- **Senha:** `imobipro2026`
- Para alterar, acesse: Menu > Usuários > Editar

### Backup Automático
- Executa diariamente às 02:00
- Mantém os últimos 7 backups na pasta `backups/`
- Usa APScheduler (configurado em app.py)

---

## ⚙️ Lançamentos Automáticos

### Gerar IPTU Anual
- **Rota**: `POST /despesas/gerar-iptu-anual`
- **Parâmetro**: `data_vencimento` (informada via modal antes de gerar)
- **O que faz**: Cria despesas de IPTU para todos os imóveis com `valor_iptu_anual > 0`
- **Vencimento**: Data informada pelo usuário no modal
- **Proteção**: Não cria duplicatas (verifica se já existe IPTU para o ano)
- **Tipo despesa**: "IPTU"
- **Descrição**: "IPTU Anual {ano}"

### Gerar Condomínio Mensal
- **Rota**: `POST /despesas/gerar-condominio-mensal`
- **O que faz**: Cria despesas de condomínio para todos os imóveis com `condominio_total > 0`
- **Valor usado**: `condominio_total` (inclui despesas ordinárias + extraordinárias)
- **Vencimento**: Usa `dia_venc_condominio` do imóvel (ou dia 10 se não definido)
- **Proteção**: Não cria duplicatas (verifica se já existe condomínio para o mês)
- **Tipo despesa**: "Condomínio"
- **Descrição**: "Condomínio {mês}/{ano}"

### Atualizar Condomínios em Lote
- **Rota**: `GET/POST /imoveis/atualizar-condominios`
- **O que faz**: Exibe todos os imóveis com condomínio cadastrado e permite atualizar os valores
- **Campos**: Condomínio Inquilino (despesas ordinárias) e Condomínio Total (ordinárias + extraordinárias)
- **Campos em branco**: Não são alterados
- **Aceita**: Valores com vírgula ou ponto decimal

---

## 📊 Relatórios Excel

### Relatório de Cobranças do Mês
- **Rota**: `GET /relatorios/cobrancas-mes/excel`
- **Colunas**: Endereço, Inquilino, Telefone, Aluguel, IPTU, Condomínio, Vencimento, Proprietário
- **Filtro**: Contratos Ativos ou Prorrogados
- **Condomínio**: Usa `condominio_inquilino` (valor cobrado do inquilino)
- **IPTU**: Calculado automaticamente (anual ÷ 12) quando forma de pagamento = "Mensal"

### Relatório de Contratos
- **Rota**: `GET /relatorios/contratos/excel`
- **Colunas**: Endereço, Proprietário, Inquilino, Garantia, Início, Término, Aluguel, Dia Venc., Data Base Reajuste, Observações
- **Filtro opcional**: `?status=Ativo` (ou Prorrogado, Encerrado, Rescindido)
- **Ordenação**: Por status e endereço

### Relatório de Despesas Pendentes
- **Rota**: `GET /relatorios/despesas-pendentes/excel`
- **Colunas**: ID, Imóvel, Tipo, Descrição, Vencimento, Valor, Situação
- **Filtros**: Tipo, Vencimento até, Situação (vencidas/a vencer)

### Relatório de Imóveis Desocupados
- **Rota**: `GET /relatorios/imoveis-desocupados/excel`
- **Colunas**: ID, Endereço, Proprietário, Tipo/Descrição, Aluguel Pretendido, Valor de Mercado
- **Filtro opcional**: Proprietário

### Relatório de Fluxo de Caixa
- **Rota**: `GET /relatorios/fluxo-caixa/excel`
- **Parâmetros**: `data_inicio` e `data_fim` (obrigatórios)
- **Colunas**: Proprietário/Endereço, Receita, IPTU, Condomínio, Saldo
- **Agrupamento**: Por proprietário com subtotais
- **Receita**: Somente valores **recebidos** no período
- **Despesas**: Somente valores **pagos** no período (IPTU e Condomínio)
- **Inclui**: Imóveis desocupados (podem ter despesas)
- **Saldo**: Receita - IPTU - Condomínio

---

## 🚨 REGRAS CRÍTICAS

### ❌ NUNCA FAZER

1. **NUNCA altere visual sem permissão**
2. **NUNCA use campos inexistentes**
   - ❌ `endereco`, `numero`, `bairro`
   - ✅ `endereco_completo`
   - ❌ `nome`, `cpf`
   - ✅ `nome_completo`, `cpf_cnpj`
3. **NUNCA implemente features não pedidas**
4. **NUNCA modifique sem entender impacto**

### ✅ SEMPRE FAZER

1. **SEMPRE use nomes corretos de campos**
2. **SEMPRE faça perguntas antes**
3. **SEMPRE explique didaticamente**
4. **SEMPRE teste antes de confirmar**
5. **SEMPRE respeite estrutura existente**

---

## 📝 Padrões de Código

### Python
```python
# Type hints
def buscar_imovel(self, id: int) -> Optional[Dict]:

# Docstrings
"""Retorna estatísticas do dashboard."""

# Trate exceções
try:
    ...
except Exception as e:
    print(f"Erro: {e}")
```

### SQL
- Use prepared statements (params)
- Prefira views quando disponível
- Use métodos DatabaseManager

### Templates
- Sempre `{% extends "base.html" %}`
- Use filtros: `|formatar_moeda`
- Lógica no Python, não template

---

## 📞 FAQ

**Q: Campo para endereço do imóvel?**  
A: `endereco_completo` (TEXT)

**Q: Como saber se imóvel está ocupado?**  
A: Campo `ocupado` = "Sim" ou "Não" (automático)

**Q: Posso criar novos campos?**  
A: Não sem permissão explícita

**Q: Formatar moeda nos templates?**  
A: `{{ valor|formatar_moeda }}`

**Q: Formatar datas?**  
A: `{{ data|formatar_data }}`

---

## 🎯 Resumo para Claude Code

**Sistema**: ImobiPro (gestão imobiliária)  
**Stack**: Python/Flask/SQLite  

**Prioridades:**
1. Respeite estrutura existente
2. Pergunte antes de implementar
3. Use linguagem clara
4. Consulte dicionário de dados
5. Nunca altere visual sem permissão

**Quando em dúvida:**
- Consulte schema neste arquivo
- Verifique métodos DatabaseManager
- Pergunte ao desenvolvedor

**Lembre-se:**
- Desenvolvedor está aprendendo
- Sistema já funciona - não quebre
- Planejamento é fundamental
