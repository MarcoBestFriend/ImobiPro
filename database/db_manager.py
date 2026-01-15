"""
================================================================================
IMOBIPRO - GERENCIADOR DO BANCO DE DADOS
================================================================================
Autor: Sistema ImobiPro
Data: Janeiro 2026
Descrição: Classe responsável por todas as operações com o banco de dados SQLite.
           Fornece métodos seguros para conexão, consultas e manipulação de dados.
================================================================================
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    """
    Classe para gerenciar todas as operações com o banco de dados SQLite.
    
    Esta classe implementa o padrão Singleton para garantir uma única conexão
    com o banco de dados e fornece métodos seguros para todas as operações CRUD.
    """
    
    def __init__(self, db_path: str = 'database/imobipro.db'):
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        
        # Criar diretório do banco se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    def connect(self) -> sqlite3.Connection:
        """
        Estabelece conexão com o banco de dados (thread-safe).
        Cria uma nova conexão a cada chamada para evitar problemas com threads.
        
        Returns:
            sqlite3.Connection: Conexão ativa com o banco
        """
        # IMPORTANTE: Criar nova conexão com check_same_thread=False
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        # Retornar resultados como dicionários (mais fácil de trabalhar)
        connection.row_factory = sqlite3.Row
        # Ativar foreign keys (importante para integridade referencial)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    
    def close(self):
        """
        Fecha a conexão com o banco de dados.
        NOTA: Com a nova implementação thread-safe, as conexões são fechadas
        automaticamente após cada operação.
        """
        pass  # Não faz nada, pois cada operação gerencia sua própria conexão
    
    def initialize_database(self):
        """
        Inicializa o banco de dados executando o arquivo schema.sql.
        Este método deve ser executado apenas uma vez na primeira instalação.
        """
        schema_path = 'database/schema.sql'
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")
        
        # Ler o arquivo SQL
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Conectar e executar o schema
        conn = self.connect()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            print("✓ Banco de dados inicializado com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"✗ Erro ao inicializar banco de dados: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Executa uma consulta SELECT e retorna os resultados.
        
        Args:
            query (str): Consulta SQL
            params (tuple): Parâmetros para a consulta (proteção contra SQL injection)
        
        Returns:
            List[Dict]: Lista de dicionários com os resultados
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            # Converter Row objects para dicionários
            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            print(f"✗ Erro ao executar consulta: {e}")
            print(f"  Query: {query}")
            return []
        finally:
            conn.close()  # Fechar conexão após uso
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        Executa uma operação INSERT, UPDATE ou DELETE.
        
        Args:
            query (str): Comando SQL
            params (tuple): Parâmetros para o comando
        
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
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
            conn.close()  # Fechar conexão após uso
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insere um novo registro em uma tabela.
        
        Args:
            table (str): Nome da tabela
            data (Dict): Dicionário com os dados a inserir (coluna: valor)
        
        Returns:
            Optional[int]: ID do registro inserido, ou None se falhar
        """
        # Preparar colunas e valores
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
            return last_id  # Retorna o ID do registro inserido
        except sqlite3.Error as e:
            print(f"✗ Erro ao inserir em {table}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()  # Fechar conexão após uso
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = ()) -> bool:
        """
        Atualiza registros em uma tabela.
        
        Args:
            table (str): Nome da tabela
            data (Dict): Dicionário com os dados a atualizar (coluna: valor)
            where (str): Cláusula WHERE (ex: "id = ?")
            where_params (tuple): Parâmetros para a cláusula WHERE
        
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        # Preparar SET clause
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + where_params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        return self.execute_update(query, values)
    
    def delete(self, table: str, where: str, where_params: tuple = ()) -> bool:
        """
        Deleta registros de uma tabela.
        
        Args:
            table (str): Nome da tabela
            where (str): Cláusula WHERE (ex: "id = ?")
            where_params (tuple): Parâmetros para a cláusula WHERE
        
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute_update(query, where_params)
    
    def get_all(self, table: str, order_by: str = None) -> List[Dict]:
        """
        Retorna todos os registros de uma tabela.
        
        Args:
            table (str): Nome da tabela
            order_by (str): Cláusula ORDER BY (opcional)
        
        Returns:
            List[Dict]: Lista de registros
        """
        query = f"SELECT * FROM {table}"
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self.execute_query(query)
    
    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        """
        Retorna um registro específico pelo ID.
        
        Args:
            table (str): Nome da tabela
            record_id (int): ID do registro
        
        Returns:
            Optional[Dict]: Registro encontrado ou None
        """
        query = f"SELECT * FROM {table} WHERE id = ?"
        results = self.execute_query(query, (record_id,))
        return results[0] if results else None
    
    def get_where(self, table: str, where: str, params: tuple = (), order_by: str = None) -> List[Dict]:
        """
        Retorna registros que atendem uma condição.
        
        Args:
            table (str): Nome da tabela
            where (str): Cláusula WHERE
            params (tuple): Parâmetros para a cláusula WHERE
            order_by (str): Cláusula ORDER BY (opcional)
        
        Returns:
            List[Dict]: Lista de registros
        """
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
    
    def get_despesas_mes(self, mes: str, ano: str) -> List[Dict]:
        """
        Retorna despesas de um mês específico.
        
        Args:
            mes (str): Mês (01-12)
            ano (str): Ano (YYYY)
        
        Returns:
            List[Dict]: Lista de despesas
        """
        query = """
            SELECT d.*, i.endereco as imovel_endereco, i.cidade
            FROM despesas d
            JOIN imoveis i ON d.id_imovel = i.id
            WHERE strftime('%m', d.data_vencimento) = ?
            AND strftime('%Y', d.data_vencimento) = ?
            ORDER BY d.data_vencimento
        """
        return self.execute_query(query, (mes, ano))
    
    def get_receitas_mes(self, mes: str, ano: str) -> List[Dict]:
        """
        Retorna receitas de um mês específico.
        
        Args:
            mes (str): Mês (01-12)
            ano (str): Ano (YYYY)
        
        Returns:
            List[Dict]: Lista de receitas
        """
        mes_ref = f"{mes}/{ano}"
        query = """
            SELECT r.*, c.valor_aluguel, i.endereco as imovel_endereco, 
                   p.nome as inquilino_nome
            FROM receitas r
            JOIN contratos c ON r.id_contrato = c.id
            JOIN imoveis i ON c.id_imovel = i.id
            JOIN pessoas p ON c.id_inquilino = p.id
            WHERE r.mes_referencia = ?
            ORDER BY r.data_vencimento
        """
        return self.execute_query(query, (mes_ref,))
    
    def get_estatisticas_dashboard(self) -> Dict[str, Any]:
        """
        Retorna estatísticas para o dashboard.
        
        Returns:
            Dict: Dicionário com estatísticas gerais
        """
        stats = {}
        
        # Total de imóveis
        stats['total_imoveis'] = len(self.get_all('imoveis'))
        
        # Imóveis por status (ocupado)
        stats['imoveis_disponiveis'] = len(self.get_imoveis_disponiveis())
        stats['imoveis_ocupados'] = len(self.get_where('imoveis', "ocupado = ?", ('Sim',)))
        
        # Contratos ativos
        stats['contratos_ativos'] = len(self.get_contratos_ativos())
        
        # Despesas pendentes
        stats['despesas_pendentes'] = len(self.get_despesas_pendentes())
        
        # Receitas pendentes
        stats['receitas_pendentes'] = len(self.get_receitas_pendentes())
        
        # Total de pessoas cadastradas
        stats['total_pessoas'] = len(self.get_all('pessoas'))
        
        # Taxa de ocupação
        if stats['total_imoveis'] > 0:
            stats['taxa_ocupacao'] = (stats['imoveis_ocupados'] / stats['total_imoveis']) * 100
        else:
            stats['taxa_ocupacao'] = 0
        
        return stats
    
    def verificar_integridade(self) -> Tuple[bool, List[str]]:
        """
        Verifica a integridade do banco de dados.
        
        Returns:
            Tuple[bool, List[str]]: (sucesso, lista de erros)
        """
        erros = []
        
        try:
            # Verificar integridade do SQLite
            result = self.execute_query("PRAGMA integrity_check")
            if result and result[0].get('integrity_check') != 'ok':
                erros.append("Integridade do banco comprometida")
            
            # Verificar foreign keys
            result = self.execute_query("PRAGMA foreign_key_check")
            if result:
                erros.append(f"Problemas com chaves estrangeiras: {len(result)} registros")
            
            return (len(erros) == 0, erros)
            
        except Exception as e:
            erros.append(f"Erro ao verificar integridade: {str(e)}")
            return (False, erros)
    
    def __enter__(self):
        """Suporte para context manager (with statement)."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager."""
        self.close()

"""
INSTRUÇÕES: 
1. Abra o arquivo database/db_manager.py no VSCode
2. Procure pela classe DatabaseManager (deve ter uma linha que diz "class DatabaseManager:")
3. Role até o final da classe (antes da última linha que tem só "}")
4. Cole TODOS os métodos abaixo DENTRO da classe DatabaseManager
5. Salve o arquivo (Ctrl+S)
"""

# ============================================================================
# COLE ESTES MÉTODOS DENTRO DA CLASSE DatabaseManager
# ============================================================================

    def listar_imoveis(self):
        """Lista todos os imóveis cadastrados"""
        query = '''
            SELECT * FROM imoveis 
            ORDER BY cidade, bairro, endereco
        '''
        return self.executar_query(query)

    def listar_imoveis_disponiveis(self):
        """Lista apenas imóveis disponíveis para locação"""
        query = '''
            SELECT * FROM imoveis 
            WHERE status = 'disponivel' 
            ORDER BY cidade, bairro, endereco
        '''
        return self.executar_query(query)

    def buscar_imovel(self, imovel_id):
        """Busca um imóvel específico pelo ID"""
        query = 'SELECT * FROM imoveis WHERE id = ?'
        resultado = self.executar_query(query, (imovel_id,))
        return resultado[0] if resultado else None

    def inserir_imovel(self, **kwargs):
        """Insere um novo imóvel no banco de dados"""
        # Lista de campos da tabela imoveis
        campos = [
            'endereco', 'numero', 'complemento', 'bairro', 'cidade', 
            'estado', 'cep', 'tipo', 'quartos', 'banheiros', 'vagas',
            'area_total', 'valor_compra', 'valor_atual', 'iptu_anual',
            'matricula', 'inscricao_municipal', 'status', 'observacoes'
        ]
        
        # Filtra apenas os campos que foram passados
        campos_presentes = [c for c in campos if c in kwargs]
        valores = [kwargs[c] for c in campos_presentes]
        
        # Monta a query
        placeholders = ', '.join(['?' for _ in campos_presentes])
        campos_str = ', '.join(campos_presentes)
        
        query = f'INSERT INTO imoveis ({campos_str}) VALUES ({placeholders})'
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(valores))
        self.conn.commit()
        
        return cursor.lastrowid

    def atualizar_imovel(self, imovel_id, **kwargs):
        """Atualiza os dados de um imóvel"""
        if not kwargs:
            return
        
        # Monta a lista de campos a atualizar
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            campos.append(f'{campo} = ?')
            valores.append(valor)
        
        valores.append(imovel_id)
        
        query = f'UPDATE imoveis SET {", ".join(campos)} WHERE id = ?'
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(valores))
        self.conn.commit()

    def excluir_imovel(self, imovel_id):
        """Exclui um imóvel (apenas se não tiver contratos ativos)"""
        # Primeiro verifica se há contratos ativos
        query = '''
            SELECT COUNT(*) as total 
            FROM contratos 
            WHERE imovel_id = ? AND status = 'ativo'
        '''
        resultado = self.executar_query(query, (imovel_id,))
        
        if resultado[0]['total'] > 0:
            raise Exception('Não é possível excluir imóvel com contratos ativos')
        
        # Se não houver contratos ativos, pode excluir
        query = 'DELETE FROM imoveis WHERE id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (imovel_id,))
        self.conn.commit()

    def listar_contratos(self):
        """Lista todos os contratos com informações dos imóveis e pessoas"""
        query = '''
            SELECT 
                c.*,
                i.endereco || ', ' || i.numero as imovel_endereco,
                i.cidade as imovel_cidade,
                p_inq.nome as inquilino_nome,
                p_fia.nome as fiador_nome
            FROM contratos c
            JOIN imoveis i ON c.imovel_id = i.id
            JOIN pessoas p_inq ON c.inquilino_id = p_inq.id
            LEFT JOIN pessoas p_fia ON c.fiador_id = p_fia.id
            ORDER BY c.data_inicio DESC
        '''
        return self.executar_query(query)

    def buscar_contrato(self, contrato_id):
        """Busca um contrato específico pelo ID"""
        query = 'SELECT * FROM contratos WHERE id = ?'
        resultado = self.executar_query(query, (contrato_id,))
        return resultado[0] if resultado else None

    def inserir_contrato(self, **kwargs):
        """Insere um novo contrato no banco de dados"""
        # Lista de campos da tabela contratos
        campos = [
            'imovel_id', 'inquilino_id', 'fiador_id', 'data_inicio', 
            'data_fim', 'valor_aluguel', 'dia_vencimento', 
            'taxa_administracao', 'indice_reajuste', 
            'periodicidade_reajuste', 'status', 'observacoes'
        ]
        
        # Filtra apenas os campos que foram passados
        campos_presentes = [c for c in campos if c in kwargs and kwargs[c] is not None]
        valores = [kwargs[c] for c in campos_presentes]
        
        # Monta a query
        placeholders = ', '.join(['?' for _ in campos_presentes])
        campos_str = ', '.join(campos_presentes)
        
        query = f'INSERT INTO contratos ({campos_str}) VALUES ({placeholders})'
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(valores))
        self.conn.commit()
        
        return cursor.lastrowid

    def atualizar_contrato(self, contrato_id, **kwargs):
        """Atualiza os dados de um contrato"""
        if not kwargs:
            return
        
        # Monta a lista de campos a atualizar
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            campos.append(f'{campo} = ?')
            valores.append(valor)
        
        valores.append(contrato_id)
        
        query = f'UPDATE contratos SET {", ".join(campos)} WHERE id = ?'
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(valores))
        self.conn.commit()

    def listar_pessoas(self):
        """Lista todas as pessoas cadastradas"""
        query = '''
            SELECT * FROM pessoas 
            ORDER BY nome
        '''
        return self.executar_query(query)

# ============================================================================
# FIM DOS MÉTODOS - 
# ============================================================================
# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def formatar_moeda(valor: float) -> str:
    """
    Formata um valor numérico para formato de moeda brasileira.
    
    Args:
        valor (float): Valor a formatar
    
    Returns:
        str: Valor formatado (ex: "R$ 1.500,00")
    """
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


def formatar_data(data: str) -> str:
    """
    Formata uma data do formato ISO (YYYY-MM-DD) para formato brasileiro (DD/MM/YYYY).
    
    Args:
        data (str): Data no formato ISO
    
    Returns:
        str: Data formatada
    """
    if not data:
        return ""
    try:
        dt = datetime.strptime(data, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except:
        return data


def data_para_iso(data: str) -> str:
    """
    Converte data do formato brasileiro (DD/MM/YYYY) para ISO (YYYY-MM-DD).
    
    Args:
        data (str): Data no formato brasileiro
    
    Returns:
        str: Data no formato ISO
    """
    if not data:
        return ""
    try:
        dt = datetime.strptime(data, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return data


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Exemplo de uso do DatabaseManager.
    Este bloco só é executado quando o arquivo é rodado diretamente.
    """
    
    # Criar instância do gerenciador
    db = DatabaseManager()
    
    # Inicializar o banco de dados
    print("Inicializando banco de dados...")
    db.initialize_database()
    
    # Exemplo: Inserir um imóvel
    print("\nInserindo imóvel de teste...")
    imovel_id = db.insert('imoveis', {
        'endereco_completo': 'Rua Teste, 123 - Centro',
        'tipo_imovel': 'Casa',
        'valor_iptu_anual': 1200.00,
        'forma_pagamento_iptu': 'Anual',
        'aluguel_pretendido': 1500.00,
        'condominio_sugerido': 300.00,
        'ocupado': 'Não'
    })
    
    if imovel_id:
        print(f"✓ Imóvel inserido com ID: {imovel_id}")
    
    # Buscar todos os imóveis
    print("\nBuscando todos os imóveis...")
    imoveis = db.get_all('imoveis')
    print(f"✓ Encontrados {len(imoveis)} imóveis")
    
    # Exibir estatísticas
    print("\nEstatísticas do sistema:")
    stats = db.get_estatisticas_dashboard()
    for chave, valor in stats.items():
        print(f"  {chave}: {valor}")
    
    # Fechar conexão
    db.close()
    print("\n✓ Teste concluído com sucesso!")