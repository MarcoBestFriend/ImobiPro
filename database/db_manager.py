"""
================================================================================
IMOBIPRO - GERENCIADOR DO BANCO DE DADOS
================================================================================
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    """Classe para gerenciar todas as operações com o banco de dados SQLite."""
    
    def __init__(self, db_path: str = 'database/imobipro.db'):
        """Inicializa o gerenciador do banco de dados."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    def connect(self) -> sqlite3.Connection:
        """Estabelece conexão com o banco de dados (thread-safe)."""
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        pass
    
    def initialize_database(self):
        """Inicializa o banco de dados executando o arquivo schema.sql."""
        schema_path = 'database/schema.sql'
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = self.connect()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            print("✓ Banco de dados inicializado com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"✗ Erro ao inicializar banco de dados: {e}")
            return False
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Executa uma consulta SELECT e retorna os resultados."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            print(f"✗ Erro ao executar consulta: {e}")
            print(f"  Query: {query}")
            return []
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Executa uma operação INSERT, UPDATE ou DELETE."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Erro ao executar atualização: {e}")
            print(f"  Query: {query}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insere um novo registro em uma tabela."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, values)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id
        except sqlite3.Error as e:
            print(f"✗ Erro ao inserir em {table}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = ()) -> bool:
        """Atualiza registros em uma tabela."""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + where_params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        return self.execute_update(query, values)
    
    def delete(self, table: str, where: str, where_params: tuple = ()) -> bool:
        """Deleta registros de uma tabela."""
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute_update(query, where_params)
    
    def get_all(self, table: str, order_by: str = None) -> List[Dict]:
        """Retorna todos os registros de uma tabela."""
        query = f"SELECT * FROM {table}"
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self.execute_query(query)
    
    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        """Retorna um registro específico pelo ID."""
        query = f"SELECT * FROM {table} WHERE id = ?"
        results = self.execute_query(query, (record_id,))
        return results[0] if results else None
    
    def get_where(self, table: str, where: str, params: tuple = (), order_by: str = None) -> List[Dict]:
        """Retorna registros que atendem uma condição."""
        query = f"SELECT * FROM {table} WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self.execute_query(query, params)
    
    # =========================================================================
    # MÉTODOS ESPECÍFICOS PARA CADA ENTIDADE
    # =========================================================================
    
    def get_imoveis_disponiveis(self) -> List[Dict]:
        """Retorna todos os imóveis disponíveis (não ocupados)."""
        return self.get_where('imoveis', "ocupado = ?", ('Não',), 'endereco_completo')
    
    def get_contratos_ativos(self) -> List[Dict]:
        """Retorna todos os contratos ativos usando a view."""
        return self.execute_query("SELECT * FROM vw_contratos_completos WHERE status_contrato = 'Ativo' ORDER BY imovel_endereco")
    
    def get_despesas_pendentes(self) -> List[Dict]:
        """Retorna todas as despesas pendentes usando a view."""
        return self.execute_query("SELECT * FROM vw_despesas_pendentes")
    
    def get_receitas_pendentes(self) -> List[Dict]:
        """Retorna todas as receitas pendentes usando a view."""
        return self.execute_query("SELECT * FROM vw_receitas_pendentes")
    
    def get_estatisticas_dashboard(self) -> Dict[str, Any]:
        """Retorna estatísticas para o dashboard."""
        stats = {}
        
        stats['total_imoveis'] = len(self.get_all('imoveis'))
        stats['imoveis_disponiveis'] = len(self.get_imoveis_disponiveis())
        stats['imoveis_ocupados'] = len(self.get_where('imoveis', "ocupado = ?", ('Sim',)))
        stats['contratos_ativos'] = len(self.get_contratos_ativos())
        stats['despesas_pendentes'] = len(self.get_despesas_pendentes())
        stats['receitas_pendentes'] = len(self.get_receitas_pendentes())
        stats['total_pessoas'] = len(self.get_all('pessoas'))
        
        if stats['total_imoveis'] > 0:
            stats['taxa_ocupacao'] = (stats['imoveis_ocupados'] / stats['total_imoveis']) * 100
        else:
            stats['taxa_ocupacao'] = 0
        
        return stats
    
    def verificar_integridade(self) -> Tuple[bool, List[str]]:
        """Verifica a integridade do banco de dados."""
        erros = []
        
        try:
            result = self.execute_query("PRAGMA integrity_check")
            if result and result[0].get('integrity_check') != 'ok':
                erros.append("Integridade do banco comprometida")
            
            result = self.execute_query("PRAGMA foreign_key_check")
            if result:
                erros.append(f"Problemas com chaves estrangeiras: {len(result)} registros")
            
            return (len(erros) == 0, erros)
            
        except Exception as e:
            erros.append(f"Erro ao verificar integridade: {str(e)}")
            return (False, erros)
    
    def __enter__(self):
        """Suporte para context manager (with statement)."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager."""
        self.close()