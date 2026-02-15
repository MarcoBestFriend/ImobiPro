#!/usr/bin/env python3
"""
Script de migração para separar condomínio em dois campos:
- condominio_inquilino: valor pago pelo inquilino (despesas ordinárias)
- condominio_total: valor total do condomínio (ordinárias + extraordinárias)

Execução: python3 migrar_condominio.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'imobipro.db')

def fazer_backup():
    """Cria um backup do banco antes da migração."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    backup_path = os.path.join(backup_dir, f'imobipro_pre_migracao_{timestamp}.db')
    shutil.copy2(DB_PATH, backup_path)
    print(f"✓ Backup criado: {backup_path}")
    return backup_path

def verificar_coluna_existe(conn, tabela, coluna):
    """Verifica se uma coluna já existe na tabela."""
    cursor = conn.execute(f"PRAGMA table_info({tabela})")
    colunas = [row[1] for row in cursor.fetchall()]
    return coluna in colunas

def executar_migracao():
    """Executa a migração do banco de dados."""
    print("\n" + "="*60)
    print("MIGRAÇÃO: Separação de campos de condomínio")
    print("="*60)

    # Verificar se o banco existe
    if not os.path.exists(DB_PATH):
        print(f"✗ Banco de dados não encontrado: {DB_PATH}")
        return False

    # Fazer backup
    backup_path = fazer_backup()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar se a migração já foi feita
        if verificar_coluna_existe(conn, 'imoveis', 'condominio_inquilino'):
            print("✓ Migração já foi executada anteriormente (campo condominio_inquilino existe).")

            # Verificar se o campo antigo ainda existe e precisa ser removido
            if verificar_coluna_existe(conn, 'imoveis', 'condominio_sugerido'):
                print("  Nota: O campo antigo 'condominio_sugerido' ainda existe.")

            conn.close()
            return True

        print("\nExecutando alterações no banco de dados...")

        # SQLite não suporta RENAME COLUMN em versões antigas, então vamos:
        # 1. Adicionar as novas colunas
        # 2. Copiar os dados
        # 3. (Não vamos remover a coluna antiga para manter compatibilidade)

        # Passo 1: Adicionar nova coluna condominio_inquilino
        print("  → Adicionando coluna 'condominio_inquilino'...")
        cursor.execute("""
            ALTER TABLE imoveis
            ADD COLUMN condominio_inquilino REAL
        """)

        # Passo 2: Adicionar nova coluna condominio_total
        print("  → Adicionando coluna 'condominio_total'...")
        cursor.execute("""
            ALTER TABLE imoveis
            ADD COLUMN condominio_total REAL
        """)

        # Passo 3: Copiar valores do campo antigo para os novos
        print("  → Copiando valores de 'condominio_sugerido' para os novos campos...")
        cursor.execute("""
            UPDATE imoveis
            SET condominio_inquilino = condominio_sugerido,
                condominio_total = condominio_sugerido
            WHERE condominio_sugerido IS NOT NULL
        """)

        # Commit das alterações
        conn.commit()

        # Verificar quantos registros foram atualizados
        cursor.execute("SELECT COUNT(*) FROM imoveis WHERE condominio_inquilino IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"  → {count} imóveis atualizados com os novos campos.")

        print("\n" + "="*60)
        print("✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\nPróximos passos:")
        print("1. Reinicie a aplicação (python3 app.py)")
        print("2. Acesse o CRUD de imóveis e atualize os valores de")
        print("   'Condomínio Total' para aqueles que têm despesas extraordinárias.")
        print("\nNota: O campo antigo 'condominio_sugerido' foi mantido para")
        print("      compatibilidade. Ele pode ser removido manualmente depois.")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ ERRO na migração: {e}")
        print(f"\nO backup foi criado em: {backup_path}")
        print("Você pode restaurá-lo se necessário.")
        return False

if __name__ == '__main__':
    executar_migracao()
