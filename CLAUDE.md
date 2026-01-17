# ImobiPro - Sistema de Gestão Imobiliária

## 📋 Informações Rápidas do Projeto

- **Nome**: ImobiPro
- **Versão**: 1.0.0 (versão funcional - branch "inicio")
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
├── app.py                          # Aplicação Flask (543 linhas)
├── config.py                       # Configurações
├── requirements.txt                # Dependências
├── database/
│   ├── schema.sql                  # Schema SQLite completo
│   ├── db_manager.py               # Gerenciador (496 linhas)
│   └── imobipro.db                 # Banco de dados
├── templates/
│   ├── base.html                   # Base (tema dark)
│   ├── dashboard.html              # Dashboard principal
│   ├── imoveis/listar.html
│   ├── imoveis/form.html
│   ├── imoveis/ver.html
│   ├── pessoas/listar.html
│   ├── pessoas/form.html
│   ├── contratos/listar.html
│   ├── contratos/form.html
│   ├── despesas/listar.html
│   ├── receitas/listar.html
│   └── relatorios/index.html
├── utils/backup.py                 # Backup/restore
└── migrar_planilha.py             # Migração Excel→SQLite
```

## 🗄️ Dicionário de Dados - Schema Completo

### Tabela: imoveis

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária (auto) | Sim |
| endereco_completo | TEXT | Endereço completo | Sim |
| inscricao_imobiliaria | TEXT | Inscrição municipal | Não |
| tipo_imovel | TEXT | Casa/Apartamento/etc | Sim |
| ocupado | TEXT | "Sim" ou "Não" (auto) | Sim |
| valor_iptu_anual | REAL | Valor anual IPTU | Não |
| forma_pagamento_iptu | TEXT | "Anual" ou "Mensal" | Sim |
| aluguel_pretendido | REAL | Valor sugerido | Não |
| condominio_sugerido | REAL | Valor condomínio | Não |
| dia_venc_condominio | INTEGER | Dia 1-31 | Não |
| cidade | TEXT | Cidade (padrão: "Campo Grande") | Não |
| estado | TEXT | UF (padrão: "MS") | Não |
| cep | TEXT | CEP | Não |
| observacoes | TEXT | Observações | Não |
| data_cadastro | TIMESTAMP | Data criação (auto) | Sim |
| data_atualizacao | TIMESTAMP | Última atualização (auto) | Sim |

**Regras**:
- `ocupado` é atualizado por trigger (quando contrato ativo/encerrado)
- Valores aceitos: `forma_pagamento_iptu` = "Anual" ou "Mensal"
- Valores aceitos: `ocupado` = "Sim" ou "Não"

---

### Tabela: pessoas

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id | INTEGER | Chave primária | Sim |
| situacao | TEXT | "Inquilino"/"Fiador"/"Ambos" | Sim |
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

### Dashboard
```
GET  /               → Redireciona /dashboard
GET  /dashboard      → Dashboard com stats
```

### Imóveis
```
GET  /imoveis                   → Lista
GET  /imoveis/novo              → Form cadastro
POST /imoveis/novo              → Processar
GET  /imoveis/<id>              → Detalhes
GET  /imoveis/<id>/editar       → Form editar
POST /imoveis/<id>/editar       → Processar
```

### Pessoas
```
GET  /pessoas                   → Lista
GET  /pessoas/novo              → Form cadastro
POST /pessoas/novo              → Processar
GET  /pessoas/<id>/editar       → Form editar
POST /pessoas/<id>/editar       → Processar
```

### Contratos
```
GET  /contratos                 → Lista
GET  /contratos/novo            → Form cadastro
POST /contratos/novo            → Processar
GET  /contratos/<id>/editar     → Form editar
POST /contratos/<id>/editar     → Processar
```

### Despesas e Receitas
```
GET  /despesas                  → Lista (filtros)
GET  /receitas                  → Lista (filtros)
```

### Relatórios
```
GET  /relatorios                → Página (parcial)
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

## ✅ Estado Atual (16/01/2026)

### Dados Migrados
- 25 imóveis
- 13 disponíveis
- 12 ocupados
- 12 contratos ativos

### Implementado
- ✅ Dashboard
- ✅ CRUD imóveis
- ✅ CRUD pessoas
- ✅ CRUD contratos
- ✅ Lista despesas/receitas
- ✅ Migração Excel
- ✅ Backup

### Planejado (NÃO FAZER SEM PERMISSÃO)
- ⏳ Lançamento automático aluguéis
- ⏳ Despesas recorrentes
- ⏳ Alertas vencimento
- ⏳ Reajustes automáticos
- ⏳ Exportar Excel
- ⏳ Gerar PDFs

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
