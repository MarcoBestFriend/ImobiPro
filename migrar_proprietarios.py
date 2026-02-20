"""Script de migração: recria receitas com constraints corretas e finaliza migração."""
import sqlite3

conn = sqlite3.connect('database/imobipro.db')
cur = conn.cursor()

try:
    # Verificar estado atual
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas = [r[0] for r in cur.fetchall()]
    print("Tabelas existentes:", tabelas)

    # Passo 1: Mover dados de 'receitas' (vazia, schema errado) para temp
    cur.execute("ALTER TABLE receitas RENAME TO receitas_schema_errado")
    print("Tabela receitas (schema errado) renomeada.")

    # Passo 2: Criar nova tabela com constraints corretas
    cur.execute("""
        CREATE TABLE receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            id_contrato     INTEGER,
            id_imovel       INTEGER,
            id_proprietario INTEGER,
            tipo_receita    TEXT NOT NULL DEFAULT 'Aluguel',

            mes_referencia      DATE NOT NULL,
            aluguel_devido      REAL NOT NULL,
            condominio_devido   REAL DEFAULT 0,
            iptu_devido         REAL DEFAULT 0,
            desconto_multa      REAL DEFAULT 0,
            valor_total_devido  REAL NOT NULL,

            vencimento_previsto DATE NOT NULL,
            data_recebimento    DATE,
            valor_recebido      REAL,

            status      TEXT NOT NULL DEFAULT 'Pendente',
            observacoes TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (id_contrato)     REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (id_imovel)       REFERENCES imoveis(id),
            FOREIGN KEY (id_proprietario) REFERENCES proprietarios(id),

            CHECK(status       IN ('Pendente', 'Recebido', 'Atrasado', 'Cancelado')),
            CHECK(tipo_receita IN ('Aluguel', 'Empréstimo', 'Outros')),

            UNIQUE(id_contrato, mes_referencia)
        )
    """)
    print("Nova tabela receitas criada com constraints corretas.")

    # Passo 3: Copiar dados do backup original (receitas_bkp)
    cur.execute("""
        INSERT INTO receitas (
            id, id_contrato, id_imovel, id_proprietario, tipo_receita,
            mes_referencia, aluguel_devido, condominio_devido, iptu_devido,
            desconto_multa, valor_total_devido, vencimento_previsto,
            data_recebimento, valor_recebido, status, observacoes, data_cadastro
        )
        SELECT
            id, id_contrato, NULL, NULL, 'Aluguel',
            mes_referencia, aluguel_devido, condominio_devido, iptu_devido,
            desconto_multa, valor_total_devido, vencimento_previsto,
            data_recebimento, valor_recebido, status, observacoes, data_cadastro
        FROM receitas_bkp
    """)
    total = cur.execute("SELECT COUNT(*) FROM receitas").fetchone()[0]
    print(f"Dados copiados: {total} receitas migradas.")

    # Passo 4: Remover tabelas temporárias
    cur.execute("DROP TABLE receitas_bkp")
    cur.execute("DROP TABLE receitas_schema_errado")
    print("Tabelas temporárias removidas.")

    # Passo 5: Recriar triggers (AFTER, não BEFORE)
    cur.execute("DROP TRIGGER IF EXISTS calcular_total_receita_insert")
    cur.execute("DROP TRIGGER IF EXISTS calcular_total_receita_update")

    cur.execute("""
        CREATE TRIGGER calcular_total_receita_insert
        AFTER INSERT ON receitas
        BEGIN
            UPDATE receitas
            SET valor_total_devido =
                COALESCE(NEW.aluguel_devido, 0) +
                COALESCE(NEW.condominio_devido, 0) +
                COALESCE(NEW.iptu_devido, 0) +
                COALESCE(NEW.desconto_multa, 0)
            WHERE id = NEW.id;
        END
    """)
    cur.execute("""
        CREATE TRIGGER calcular_total_receita_update
        AFTER UPDATE ON receitas
        BEGIN
            UPDATE receitas
            SET valor_total_devido =
                COALESCE(NEW.aluguel_devido, 0) +
                COALESCE(NEW.condominio_devido, 0) +
                COALESCE(NEW.iptu_devido, 0) +
                COALESCE(NEW.desconto_multa, 0)
            WHERE id = NEW.id;
        END
    """)
    print("Triggers recriados (AFTER INSERT/UPDATE).")

    # Passo 6: Recriar view vw_receitas_pendentes
    cur.execute("DROP VIEW IF EXISTS vw_receitas_pendentes")
    cur.execute("""
        CREATE VIEW vw_receitas_pendentes AS
        SELECT
            r.id,
            r.id_contrato,
            r.tipo_receita,
            COALESCE(c.id_imovel, r.id_imovel)                          AS id_imovel,
            COALESCE(i_c.endereco_completo, i_r.endereco_completo, '-') AS imovel,
            COALESCE(p.nome_completo, pr.nome, '-')                     AS inquilino,
            r.mes_referencia,
            r.valor_total_devido,
            r.vencimento_previsto,
            r.status,
            CASE
                WHEN r.vencimento_previsto < DATE('now') AND r.status = 'Pendente' THEN 'Atrasado'
                WHEN r.vencimento_previsto = DATE('now') THEN 'Vence Hoje'
                ELSE 'A Receber'
            END AS situacao
        FROM receitas r
        LEFT JOIN contratos     c   ON r.id_contrato     = c.id
        LEFT JOIN imoveis       i_c ON c.id_imovel       = i_c.id
        LEFT JOIN imoveis       i_r ON r.id_imovel       = i_r.id
        LEFT JOIN pessoas       p   ON c.id_inquilino    = p.id
        LEFT JOIN proprietarios pr  ON r.id_proprietario = pr.id
        WHERE r.status IN ('Pendente', 'Atrasado')
        ORDER BY r.vencimento_previsto DESC
    """)
    print("View vw_receitas_pendentes reconstruída.")

    conn.commit()

    # Verificação final
    cur.execute("SELECT COUNT(*) FROM proprietarios")
    print(f"\nProprietários cadastrados: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM receitas")
    print(f"Receitas na nova tabela: {cur.fetchone()[0]}")
    cur.execute("PRAGMA table_info(receitas)")
    print("Colunas:", [c[1] for c in cur.fetchall()])

    print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO.")

except Exception as e:
    conn.rollback()
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
