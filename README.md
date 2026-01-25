# 🏠 ImobiPro - Sistema de Gestão Imobiliária

Sistema completo para gestão de imóveis, contratos, despesas e receitas de aluguéis.

**Versão:** 1.0.0  
**Data:** Janeiro 2026  
**Desenvolvido para:** Ubuntu 24.04 (compatível com outras distribuições Linux)

---

## 📋 Índice

1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalação](#instalação)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Uso Básico](#uso-básico)
6. [Migração da Planilha](#migração-da-planilha)
7. [Sistema de Backup](#sistema-de-backup)
8. [Próximos Passos](#próximos-passos)

---

## ✨ Características

### Funcionalidades Atuais (Fase 1 - Concluída)

- ✅ **Banco de Dados SQLite**
  - Schema completo e otimizado
  - Relacionamentos entre tabelas
  - Validações e constraints
  - Views para consultas frequentes
  
- ✅ **Migração de Dados**
  - Importação automática da planilha Excel
  - Validação de dados durante migração
  - Log detalhado de erros
  - Verificação de integridade
  
- ✅ **Sistema de Backup**
  - Backup automático do banco SQLite
  - Exportação completa para Excel
  - Restauração de backups
  - Limpeza automática de backups antigos

### Funcionalidades Planejadas

- 🔄 Interface web local (Flask)
- 🔄 Lançamento automático de aluguéis
- 🔄 Lançamento de despesas recorrentes
- 🔄 Relatórios gerenciais em Excel
- 🔄 Dashboard com indicadores
- 🔄 Sistema de alertas de vencimento
- 🔄 Gestão de reajustes contratuais
- 🔄 Upload de fotos de vistorias
- 🔄 Geração de contratos em PDF

---

## 💻 Requisitos

### Sistema Operacional
- Ubuntu 24.04 (ou outras distribuições Linux)
- Python 3.10 ou superior

### Bibliotecas Python
- flask
- flask-login
- werkzeug
- openpyxl
- pillow
- reportlab

---

## 🚀 Instalação

### Passo 1: Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Passo 2: Instalar VS Code (Opcional mas Recomendado)

```bash
sudo snap install code --classic
```

### Passo 3: Criar Estrutura do Projeto

```bash
# Criar diretório principal
mkdir -p ~/ImobiPro
cd ~/ImobiPro

# Criar estrutura de pastas
mkdir -p database core utils templates static/{css,js,images,uploads} backups
```

### Passo 4: Configurar Ambiente Virtual Python

```bash
# Instalar pip e venv se necessário
sudo apt install python3-pip python3-venv -y

# Criar ambiente virtual (ISOLADO - não afeta o sistema)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

**⚠️ IMPORTANTE:** Sempre ative o ambiente virtual antes de trabalhar:
```bash
cd ~/ImobiPro
source venv/bin/activate
```

### Passo 5: Instalar Dependências

```bash
# Com o ambiente virtual ativado:
pip install flask flask-login werkzeug openpyxl pillow reportlab
```

### Passo 6: Copiar Arquivos do Sistema

Copie os seguintes arquivos para as respectivas pastas:

```
~/ImobiPro/
├── database/
│   ├── schema.sql          # Arquivo 1
│   └── db_manager.py       # Arquivo 2
├── utils/
│   └── backup.py           # Arquivo 4
├── migrar_planilha.py      # Arquivo 3
└── README.md               # Este arquivo
```

### Passo 7: Copiar sua Planilha Excel

```bash
# Copie sua planilha para o diretório do projeto
cp /caminho/para/ImobiPro.xlsx ~/ImobiPro/
```

---

## 📁 Estrutura do Projeto

```
ImobiPro/
├── venv/                          # Ambiente virtual Python (isolado)
├── database/
│   ├── schema.sql                 # Estrutura do banco de dados
│   ├── db_manager.py              # Gerenciador do banco
│   └── imobipro.db               # Banco de dados (criado após migração)
├── core/                          # Módulos principais (futuro)
│   ├── imoveis.py
│   ├── contratos.py
│   └── financeiro.py
├── utils/
│   └── backup.py                  # Sistema de backup
├── backups/                       # Backups automáticos
├── templates/                     # Templates HTML (futuro)
├── static/                        # Arquivos estáticos (futuro)
├── migrar_planilha.py            # Script de migração
├── ImobiPro.xlsx                 # Sua planilha original
└── README.md                     # Este arquivo
```

---

## 🎯 Uso Básico

### Ativar Ambiente Virtual

**SEMPRE execute antes de usar o sistema:**

```bash
cd ~/ImobiPro
source venv/bin/activate
```

Você verá `(venv)` no início da linha do terminal.

### Testar o Banco de Dados

```bash
# Testar criação do banco e inserção de dados de teste
python3 database/db_manager.py
```

Saída esperada:
```
Inicializando banco de dados...
✓ Banco de dados inicializado com sucesso!

Inserindo imóvel de teste...
✓ Imóvel inserido com ID: 1

Buscando todos os imóveis...
✓ Encontrados 1 imóveis

Estatísticas do sistema:
  total_imoveis: 1
  imoveis_disponiveis: 1
  ...
```

---

## 📊 Migração da Planilha

### Executar Migração

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar migração
python3 migrar_planilha.py ImobiPro.xlsx
```

### Saída Esperada

```
======================================================================
INICIANDO MIGRAÇÃO DA PLANILHA PARA SQLITE
======================================================================
Arquivo: ImobiPro.xlsx
Data: 13/01/2026 14:30:00

✓ Arquivo Excel validado: ImobiPro.xlsx

Inicializando banco de dados...
✓ Banco de dados inicializado com sucesso!

Carregando planilha Excel...

======================================================================
MIGRANDO IMÓVEIS
======================================================================
Campos encontrados: ['ID', 'Endereço', 'Cidade', ...]
  ✓ Linha 2: Rua ABC, 123 (ID: 1)
  ✓ Linha 3: Av. XYZ, 456 (ID: 2)
  ...

✓ Imóveis migrados: 40

======================================================================
MIGRANDO PESSOAS
======================================================================
...

======================================================================
MIGRAÇÃO CONCLUÍDA
======================================================================
✓ Registros migrados com sucesso: 150
✗ Erros encontrados: 0

Verificando integridade do banco de dados...
✓ Integridade do banco verificada com sucesso!

Estatísticas do banco de dados:
  Total de imóveis: 40
  Imóveis disponíveis: 12
  Imóveis ocupados: 28
  Contratos ativos: 28
  Taxa de ocupação: 70.0%
```

### Verificar Dados Migrados

Você pode usar um visualizador SQLite para verificar os dados:

```bash
# Instalar SQLite Browser (opcional)
sudo apt install sqlitebrowser

# Abrir o banco
sqlitebrowser database/imobipro.db
```

---

## 💾 Sistema de Backup

### Backup Completo

```bash
# Executar backup completo (SQLite + Excel)
python3 utils/backup.py
```

Escolha a opção **1** no menu.

### Backups Automáticos

Os backups são salvos em `~/ImobiPro/backups/` com nomes automáticos:

```
imobipro_backup_db_20260113_143000.db       # Backup SQLite
imobipro_backup_excel_20260113_143005.xlsx  # Backup Excel
```

### Listar Backups Disponíveis

```bash
python3 utils/backup.py
```

Escolha a opção **4** no menu.

### Restaurar Backup

```bash
python3 utils/backup.py
```

Escolha a opção **5** e selecione o backup desejado.

**⚠️ ATENÇÃO:** A restauração substitui o banco atual. Um backup de segurança é criado automaticamente antes da restauração.

---

## 🔧 Solução de Problemas

### Erro: "ModuleNotFoundError"

**Causa:** Ambiente virtual não está ativado ou dependências não instaladas.

**Solução:**
```bash
cd ~/ImobiPro
source venv/bin/activate
pip install flask flask-login werkzeug openpyxl pillow reportlab
```

### Erro: "Arquivo não encontrado"

**Causa:** Você está executando o script de fora do diretório do projeto.

**Solução:**
```bash
cd ~/ImobiPro
python3 migrar_planilha.py ImobiPro.xlsx
```

### Erro: "Permission denied"

**Causa:** Arquivo do banco sem permissão de escrita.

**Solução:**
```bash
chmod 644 database/imobipro.db
```

### Banco Corrompido

**Solução:**
```bash
# Restaurar do último backup
python3 utils/backup.py
# Escolher opção 5 e selecionar o backup mais recente
```

---

## 🎓 Comandos Úteis

### Ver Versão do Python

```bash
python3 --version
```

### Listar Pacotes Instalados

```bash
pip list
```

### Desativar Ambiente Virtual

```bash
deactivate
```

### Criar Backup Manual Rápido

```bash
# Backup do banco
cp database/imobipro.db backups/manual_$(date +%Y%m%d_%H%M%S).db

# Backup de tudo
tar -czf backups/imobipro_full_$(date +%Y%m%d_%H%M%S).tar.gz \
    database/ core/ utils/ migrar_planilha.py
```

---

## 📝 Próximos Passos

Agora que a **Fase 1** está concluída, vamos para a **Fase 2**:

### Semana 2 - Interface Web Local

1. Criar aplicação Flask
2. Templates HTML básicos
3. Dashboard com estatísticas
4. Visualização de todas as tabelas

### Semana 3 - Funcionalidades Core

1. Lançamento automático de aluguéis
2. Lançamento de despesas recorrentes
3. Alertas de vencimentos

### Semana 4 - Relatórios

1. Exportação de relatórios em Excel
2. Gráficos e indicadores
3. Filtros avançados

---

## 📞 Suporte

Se encontrar problemas durante a instalação ou uso:

1. Verifique se o ambiente virtual está ativado
2. Confira se todos os arquivos estão nos locais corretos
3. Leia as mensagens de erro com atenção
4. Consulte a seção "Solução de Problemas"

---

## 📜 Licença

Sistema desenvolvido para uso pessoal.

---

## 🙏 Créditos

Desenvolvido com auxílio de IA (Claude - Anthropic)

---

**Última atualização:** 13/01/2026
