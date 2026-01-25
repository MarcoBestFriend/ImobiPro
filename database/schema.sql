-- ============================================================================
-- IMOBIPRO - SISTEMA DE GESTÃO IMOBILIÁRIA
-- Schema do Banco de Dados SQLite - VERSÃO CORRIGIDA
-- ============================================================================
-- Baseado na análise completa da planilha ImobiPro.xlsx
-- Inclui todos os campos reais e regras de negócio identificadas
-- ============================================================================

-- ============================================================================
-- TABELA: imoveis
-- Campos baseados na análise da aba "imoveis"
-- ============================================================================
CREATE TABLE IF NOT EXISTS imoveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Dados básicos (da planilha)
    endereco_completo TEXT NOT NULL,           -- EnderecoCompleto
    inscricao_imobiliaria TEXT,                -- InscricaoImobiliaria
    matricula TEXT,                            -- Matrícula do imóvel no cartório
    tipo_imovel TEXT NOT NULL,                  -- Descrição do imóvel (aposentos, conservação)

    -- Proprietário
    id_proprietario INTEGER,                   -- FK → pessoas.id

    -- Status (calculado dinamicamente)
    ocupado TEXT DEFAULT 'Não',                -- Ocupado (Sim/Não)

    -- Dados financeiros
    valor_iptu_anual REAL,                     -- ValorIPTUAnual
    forma_pagamento_iptu TEXT DEFAULT 'Anual', -- FormaPagamentoIPTU (Anual/Mensal)
    aluguel_pretendido REAL,                   -- AluguelPretendido
    condominio_sugerido REAL,                  -- CondominioSugerido
    dia_venc_condominio INTEGER,               -- DiaVencCondominio
    valor_mercado REAL,                        -- Valor de mercado do imóvel
    data_aquisicao DATE,                       -- Data de aquisição

    -- Medidores
    numero_hidrometro TEXT,                    -- Número do hidrômetro
    numero_relogio_energia TEXT,               -- Número do relógio de energia

    -- Localização
    cidade TEXT DEFAULT 'Campo Grande',
    estado TEXT DEFAULT 'MS',
    cep TEXT,

    -- Controle
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Chaves estrangeiras
    FOREIGN KEY (id_proprietario) REFERENCES pessoas(id) ON DELETE SET NULL,

    -- Validações
    CHECK(forma_pagamento_iptu IN ('Anual', 'Mensal')),
    CHECK(ocupado IN ('Sim', 'Não'))
);

-- ============================================================================
-- TABELA: pessoas
-- Campos baseados na análise da aba "pessoas"
-- ============================================================================
CREATE TABLE IF NOT EXISTS pessoas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Dados básicos
    situacao TEXT NOT NULL,                    -- Situação (Inquilino/Fiador)
    nome_completo TEXT NOT NULL,               -- NomeCompleto
    cpf_cnpj TEXT UNIQUE,                      -- CPFNJP (com máscara)
    telefone TEXT,                             -- Telefone
    email TEXT,                                -- Email
    
    -- Endereço
    endereco_completo TEXT,                    -- EnderecoCompleto
    cidade TEXT,                               -- Cidade
    
    -- Dados patrimoniais e familiares
    patrimonio REAL,                           -- Patrimonio
    estado_civil TEXT,                         -- EstadoCivil
    nome_conjuge TEXT,                         -- NomeConjuge
    cpf_conjuge TEXT,                          -- CPFConjuge
    
    -- Controle
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Validações
    CHECK(situacao IN ('Inquilino', 'Fiador', 'Proprietário', 'Ambos')),
    CHECK(estado_civil IN ('Solteiro', 'Casado', 'Divorciado', 'Viúvo', NULL))
);

-- ============================================================================
-- TABELA: contratos
-- Campos baseados na análise da aba "contratos"
-- ============================================================================
CREATE TABLE IF NOT EXISTS contratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Relacionamentos
    id_imovel INTEGER NOT NULL,                -- ID_Propriedade (FK)
    id_inquilino INTEGER NOT NULL,             -- ID_Inquilino (FK)
    id_fiador INTEGER,                         -- ID_Fiador (FK) - opcional
    
    -- Tipo de garantia
    garantia TEXT NOT NULL DEFAULT 'nenhuma',  -- Garantia: antecipado, nenhuma, fiança, caução
    
    -- Datas
    inicio_contrato DATE NOT NULL,             -- InicioContrato
    fim_contrato DATE,                         -- FimContrato (calculado ou manual)
    
    -- Valores
    valor_aluguel REAL NOT NULL,               -- ValorAluguel
    dia_vencimento INTEGER NOT NULL,           -- DiaVenc
    
    -- Status e controle
    status_contrato TEXT NOT NULL DEFAULT 'Ativo',  -- StatusContrato
    observacoes TEXT,                          -- Obs
    
    -- Campos para reajuste (futuro)
    indice_reajuste TEXT DEFAULT 'IGPM',
    data_base_reajuste DATE,
    ultimo_reajuste DATE,
    percentual_ultimo_reajuste REAL,
    
    -- Controle
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves estrangeiras
    FOREIGN KEY (id_imovel) REFERENCES imoveis(id) ON DELETE CASCADE,
    FOREIGN KEY (id_inquilino) REFERENCES pessoas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_fiador) REFERENCES pessoas(id) ON DELETE SET NULL,
    
    -- Validações
    CHECK(garantia IN ('antecipado', 'nenhuma', 'fiança', 'caução')),
    CHECK(status_contrato IN ('Ativo', 'Prorrogado', 'Encerrado', 'Rescindido')),
    CHECK(dia_vencimento >= 1 AND dia_vencimento <= 31),
    CHECK(valor_aluguel > 0)
);

-- ============================================================================
-- TABELA: fiadores_contrato
-- Relacionamento N:N entre contratos e fiadores (múltiplos fiadores)
-- ============================================================================
CREATE TABLE IF NOT EXISTS fiadores_contrato (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_contrato INTEGER NOT NULL,
    id_pessoa_fiador INTEGER NOT NULL,
    ordem INTEGER DEFAULT 1,                   -- Fiador1, Fiador2, Fiador3
    
    FOREIGN KEY (id_contrato) REFERENCES contratos(id) ON DELETE CASCADE,
    FOREIGN KEY (id_pessoa_fiador) REFERENCES pessoas(id) ON DELETE CASCADE,
    
    UNIQUE(id_contrato, id_pessoa_fiador)
);

-- ============================================================================
-- TABELA: despesas
-- Campos baseados na análise da aba "despesas"
-- ============================================================================
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Relacionamento
    id_imovel INTEGER NOT NULL,
    
    -- Referência temporal
    mes_referencia DATE,                       -- MesReferencia
    
    -- Tipo e detalhes
    tipo_despesa TEXT NOT NULL,                -- TipoDespesa: Manutenção, Condomínio, Reforma, IPTU
    motivo_despesa TEXT,                       -- MotivoDespesa
    
    -- Valores
    valor_previsto REAL NOT NULL,              -- ValorPrevisto
    valor_pago REAL,                           -- ValorPago
    
    -- Datas
    vencimento_previsto DATE,                  -- VencimentoPrevisto
    data_pagamento DATE,                       -- DataPagamento
    
    -- Controle
    observacoes TEXT,                          -- Observacoes
    recorrente INTEGER DEFAULT 0,              -- 0=Não, 1=Sim (para despesas mensais)
    
    -- Controle automático
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves estrangeiras
    FOREIGN KEY (id_imovel) REFERENCES imoveis(id) ON DELETE CASCADE,
    
    -- Validações
    CHECK(tipo_despesa IN ('Manutenção', 'Condomínio', 'Reforma', 'IPTU', 'Outros')),
    CHECK(valor_previsto >= 0)
);

-- ============================================================================
-- TABELA: receitas
-- Campos baseados na análise da aba "receitas"
-- ============================================================================
CREATE TABLE IF NOT EXISTS receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Relacionamento
    id_contrato INTEGER NOT NULL,
    
    -- Referência temporal
    mes_referencia DATE NOT NULL,              -- MesReferencia
    
    -- Valores devidos (componentes)
    aluguel_devido REAL NOT NULL,              -- AluguelDevido
    condominio_devido REAL DEFAULT 0,          -- CondominioDevido
    iptu_devido REAL DEFAULT 0,                -- IPTUDevido
    desconto_multa REAL DEFAULT 0,             -- Desconto(-) Multa(+)
    valor_total_devido REAL NOT NULL,          -- ValorTotalDevido (calculado)
    
    -- Datas
    vencimento_previsto DATE NOT NULL,         -- VencimentoPrevisto
    data_recebimento DATE,                     -- DataRecebimento
    
    -- Valores recebidos
    valor_recebido REAL,                       -- ValorRecebido
    
    -- Status
    status TEXT NOT NULL DEFAULT 'Pendente',   -- Status: Pendente, Recebido, Atrasado
    observacoes TEXT,                          -- Observacoes
    
    -- Controle
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves estrangeiras
    FOREIGN KEY (id_contrato) REFERENCES contratos(id) ON DELETE CASCADE,
    
    -- Validações
    CHECK(status IN ('Pendente', 'Recebido', 'Atrasado', 'Cancelado')),
    
    -- Garantir unicidade por contrato/mês
    UNIQUE(id_contrato, mes_referencia)
);

-- ============================================================================
-- TABELA: configuracoes (mantida do schema original)
-- ============================================================================
CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT,
    descricao TEXT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_imoveis_ocupado ON imoveis(ocupado);
CREATE INDEX IF NOT EXISTS idx_pessoas_situacao ON pessoas(situacao);
CREATE INDEX IF NOT EXISTS idx_pessoas_cpf ON pessoas(cpf_cnpj);
CREATE INDEX IF NOT EXISTS idx_contratos_status ON contratos(status_contrato);
CREATE INDEX IF NOT EXISTS idx_contratos_imovel ON contratos(id_imovel);
CREATE INDEX IF NOT EXISTS idx_contratos_inquilino ON contratos(id_inquilino);
CREATE INDEX IF NOT EXISTS idx_despesas_imovel ON despesas(id_imovel);
CREATE INDEX IF NOT EXISTS idx_despesas_tipo ON despesas(tipo_despesa);
CREATE INDEX IF NOT EXISTS idx_receitas_contrato ON receitas(id_contrato);
CREATE INDEX IF NOT EXISTS idx_receitas_status ON receitas(status);

-- ============================================================================
-- TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- ============================================================================

-- Trigger: Atualizar campo "ocupado" quando contrato é inserido/atualizado
CREATE TRIGGER IF NOT EXISTS atualizar_imovel_ocupado_insert
AFTER INSERT ON contratos
BEGIN
    UPDATE imoveis
    SET ocupado = 'Sim'
    WHERE id = NEW.id_imovel
    AND NEW.status_contrato IN ('Ativo', 'Prorrogado');
END;

CREATE TRIGGER IF NOT EXISTS atualizar_imovel_ocupado_update
AFTER UPDATE ON contratos
BEGIN
    -- Marcar como ocupado se status for Ativo ou Prorrogado
    UPDATE imoveis
    SET ocupado = 'Sim'
    WHERE id = NEW.id_imovel
    AND NEW.status_contrato IN ('Ativo', 'Prorrogado');

    -- Marcar como disponível se não houver contratos ativos/prorrogados
    UPDATE imoveis
    SET ocupado = 'Não'
    WHERE id = NEW.id_imovel
    AND NEW.status_contrato IN ('Encerrado', 'Rescindido')
    AND NOT EXISTS (
        SELECT 1 FROM contratos
        WHERE id_imovel = NEW.id_imovel
        AND status_contrato IN ('Ativo', 'Prorrogado')
    );
END;

-- Trigger: Calcular valor_total_devido em receitas
CREATE TRIGGER IF NOT EXISTS calcular_total_receita_insert
BEFORE INSERT ON receitas
BEGIN
    UPDATE receitas
    SET valor_total_devido = NEW.aluguel_devido + NEW.condominio_devido + NEW.iptu_devido + NEW.desconto_multa
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS calcular_total_receita_update
BEFORE UPDATE ON receitas
BEGIN
    UPDATE receitas
    SET valor_total_devido = NEW.aluguel_devido + NEW.condominio_devido + NEW.iptu_devido + NEW.desconto_multa
    WHERE id = NEW.id;
END;

-- Trigger: Atualizar timestamps
CREATE TRIGGER IF NOT EXISTS update_imoveis_timestamp 
AFTER UPDATE ON imoveis
BEGIN
    UPDATE imoveis SET data_atualizacao = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_pessoas_timestamp 
AFTER UPDATE ON pessoas
BEGIN
    UPDATE pessoas SET data_atualizacao = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contratos_timestamp 
AFTER UPDATE ON contratos
BEGIN
    UPDATE contratos SET data_atualizacao = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Contratos ativos com todas as informações
CREATE VIEW IF NOT EXISTS vw_contratos_completos AS
SELECT 
    c.id,
    c.id_imovel,
    i.endereco_completo as imovel_endereco,
    i.tipo_imovel,
    p_inq.nome_completo as inquilino_nome,
    p_inq.telefone as inquilino_telefone,
    p_inq.cpf_cnpj as inquilino_cpf,
    p_fiad.nome_completo as fiador_nome,
    c.garantia,
    c.valor_aluguel,
    c.dia_vencimento,
    c.inicio_contrato,
    c.fim_contrato,
    c.status_contrato,
    c.observacoes
FROM contratos c
JOIN imoveis i ON c.id_imovel = i.id
JOIN pessoas p_inq ON c.id_inquilino = p_inq.id
LEFT JOIN pessoas p_fiad ON c.id_fiador = p_fiad.id;

-- View: Despesas pendentes com detalhes
CREATE VIEW IF NOT EXISTS vw_despesas_pendentes AS
SELECT 
    d.id,
    d.id_imovel,
    i.endereco_completo as imovel,
    d.tipo_despesa,
    d.motivo_despesa,
    d.valor_previsto,
    d.vencimento_previsto,
    CASE 
        WHEN d.vencimento_previsto < DATE('now') THEN 'Atrasado'
        WHEN d.vencimento_previsto = DATE('now') THEN 'Vence Hoje'
        ELSE 'A Vencer'
    END as situacao
FROM despesas d
JOIN imoveis i ON d.id_imovel = i.id
WHERE d.data_pagamento IS NULL
ORDER BY d.vencimento_previsto;

-- View: Receitas pendentes com detalhes
CREATE VIEW IF NOT EXISTS vw_receitas_pendentes AS
SELECT 
    r.id,
    r.id_contrato,
    c.id_imovel,
    i.endereco_completo as imovel,
    p.nome_completo as inquilino,
    r.mes_referencia,
    r.valor_total_devido,
    r.vencimento_previsto,
    r.status,
    CASE 
        WHEN r.vencimento_previsto < DATE('now') AND r.status = 'Pendente' THEN 'Atrasado'
        WHEN r.vencimento_previsto = DATE('now') THEN 'Vence Hoje'
        ELSE 'A Receber'
    END as situacao
FROM receitas r
JOIN contratos c ON r.id_contrato = c.id
JOIN imoveis i ON c.id_imovel = i.id
JOIN pessoas p ON c.id_inquilino = p.id
WHERE r.status IN ('Pendente', 'Atrasado')
ORDER BY r.vencimento_previsto;

-- ============================================================================
-- DADOS INICIAIS
-- ============================================================================
INSERT OR IGNORE INTO configuracoes (chave, valor, descricao) VALUES
('sistema_nome', 'ImobiPro', 'Nome do sistema'),
('sistema_versao', '1.0.0', 'Versão do sistema'),
('backup_automatico', '1', 'Ativar backup automático (0=Não, 1=Sim)'),
('dias_alerta_vencimento', '7', 'Dias de antecedência para alertas de vencimento'),
('indice_reajuste_padrao', 'IGPM', 'Índice padrão para reajuste de contratos');

-- ============================================================================
-- FIM DO SCHEMA CORRIGIDO
-- ============================================================================