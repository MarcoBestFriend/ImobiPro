"""
================================================================================
IMOBIPRO - EXPORTAR E IMPORTAR TABELAS
================================================================================
Autor: Sistema ImobiPro
Data: Janeiro 2026
Descricao: Sistema para exportar todas as tabelas do banco de dados para CSV
           e reimportar os dados a partir dos arquivos CSV.
================================================================================
"""

import os
import csv
import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple

# Adicionar o diretorio raiz ao path para importar o db_manager
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


class ExportadorImportador:
    """
    Classe para exportar e importar dados do banco de dados ImobiPro.
    """

    # Ordem das tabelas (importante para respeitar foreign keys na importacao)
    ORDEM_TABELAS = ['imoveis', 'pessoas', 'contratos', 'despesas', 'receitas']

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Inicializa o exportador/importador.

        Args:
            db_manager: Instancia do DatabaseManager (opcional)
        """
        self.db = db_manager or DatabaseManager()
        self.dir_exportacao = 'exportacoes'

        # Criar diretorio de exportacoes se nao existir
        os.makedirs(self.dir_exportacao, exist_ok=True)

    def _obter_colunas_tabela(self, tabela: str) -> List[str]:
        """
        Obtem a lista de colunas de uma tabela.

        Args:
            tabela: Nome da tabela

        Returns:
            Lista com nomes das colunas
        """
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = [row[1] for row in cursor.fetchall()]
        conn.close()
        return colunas

    def exportar_tabela_csv(self, tabela: str, diretorio: str = None) -> Tuple[bool, str]:
        """
        Exporta uma tabela para arquivo CSV.

        Args:
            tabela: Nome da tabela
            diretorio: Diretorio de destino (opcional)

        Returns:
            Tupla (sucesso, caminho_arquivo ou mensagem_erro)
        """
        diretorio = diretorio or self.dir_exportacao

        try:
            # Buscar todos os dados da tabela
            dados = self.db.get_all(tabela)

            if not dados:
                return True, f"Tabela {tabela} esta vazia (nenhum arquivo gerado)"

            # Nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{tabela}_{timestamp}.csv"
            caminho = os.path.join(diretorio, nome_arquivo)

            # Obter cabecalhos (nomes das colunas)
            cabecalhos = list(dados[0].keys())

            # Escrever CSV
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(dados)

            return True, caminho

        except Exception as e:
            return False, f"Erro ao exportar {tabela}: {str(e)}"

    def exportar_todas_tabelas(self) -> Dict:
        """
        Exporta todas as tabelas para arquivos CSV em um diretorio com timestamp.

        Returns:
            Dicionario com resultado da exportacao
        """
        print("\n" + "="*70)
        print("EXPORTANDO TODAS AS TABELAS PARA CSV")
        print("="*70)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        # Criar subdiretorio com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_export = os.path.join(self.dir_exportacao, f"export_{timestamp}")
        os.makedirs(dir_export, exist_ok=True)

        resultado = {
            'sucesso': True,
            'diretorio': dir_export,
            'arquivos': [],
            'erros': []
        }

        for tabela in self.ORDEM_TABELAS:
            print(f"\nExportando tabela: {tabela.upper()}...")

            sucesso, msg = self.exportar_tabela_csv(tabela, dir_export)

            if sucesso:
                if "vazia" in msg:
                    print(f"  ! {msg}")
                else:
                    print(f"  OK: {os.path.basename(msg)}")
                    resultado['arquivos'].append(msg)
            else:
                print(f"  ERRO: {msg}")
                resultado['erros'].append(msg)
                resultado['sucesso'] = False

        # Resumo
        print("\n" + "-"*70)
        print(f"Exportacao concluida!")
        print(f"Diretorio: {dir_export}")
        print(f"Arquivos gerados: {len(resultado['arquivos'])}")
        if resultado['erros']:
            print(f"Erros: {len(resultado['erros'])}")

        return resultado

    def importar_tabela_csv(self, tabela: str, caminho_csv: str,
                           limpar_tabela: bool = True) -> Tuple[bool, str]:
        """
        Importa dados de um arquivo CSV para uma tabela.

        Args:
            tabela: Nome da tabela destino
            caminho_csv: Caminho do arquivo CSV
            limpar_tabela: Se True, limpa a tabela antes de importar

        Returns:
            Tupla (sucesso, mensagem)
        """
        if not os.path.exists(caminho_csv):
            return False, f"Arquivo nao encontrado: {caminho_csv}"

        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Ler CSV
            with open(caminho_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                dados = list(reader)

            if not dados:
                return True, f"Arquivo CSV vazio para {tabela}"

            # Desabilitar triggers temporariamente para evitar problemas
            cursor.execute("PRAGMA foreign_keys = OFF")

            # Limpar tabela se solicitado
            if limpar_tabela:
                cursor.execute(f"DELETE FROM {tabela}")

            # Obter colunas da tabela
            colunas_tabela = self._obter_colunas_tabela(tabela)

            # Filtrar apenas colunas que existem na tabela
            colunas_csv = list(dados[0].keys())
            colunas_validas = [c for c in colunas_csv if c in colunas_tabela]

            # Preparar INSERT
            placeholders = ', '.join(['?' for _ in colunas_validas])
            colunas_str = ', '.join(colunas_validas)
            query = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"

            # Inserir dados
            contador = 0
            for registro in dados:
                valores = []
                for coluna in colunas_validas:
                    valor = registro.get(coluna, '')
                    # Converter valores vazios para None
                    if valor == '' or valor == 'None':
                        valor = None
                    valores.append(valor)

                try:
                    cursor.execute(query, valores)
                    contador += 1
                except sqlite3.IntegrityError as e:
                    print(f"    Aviso: Registro ignorado (duplicado ou FK invalida): {e}")

            # Reabilitar triggers
            cursor.execute("PRAGMA foreign_keys = ON")

            conn.commit()
            conn.close()

            return True, f"{contador} registros importados para {tabela}"

        except Exception as e:
            return False, f"Erro ao importar {tabela}: {str(e)}"

    def importar_de_diretorio(self, diretorio: str,
                              limpar_tabelas: bool = True) -> Dict:
        """
        Importa todas as tabelas a partir de arquivos CSV em um diretorio.

        Os arquivos devem ter o nome no formato: tabela_*.csv
        Exemplo: imoveis_20260120_123456.csv

        Args:
            diretorio: Diretorio com os arquivos CSV
            limpar_tabelas: Se True, limpa as tabelas antes de importar

        Returns:
            Dicionario com resultado da importacao
        """
        print("\n" + "="*70)
        print("IMPORTANDO TABELAS DE ARQUIVOS CSV")
        print("="*70)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Diretorio: {diretorio}")

        if not os.path.exists(diretorio):
            return {'sucesso': False, 'erros': [f"Diretorio nao encontrado: {diretorio}"]}

        resultado = {
            'sucesso': True,
            'importados': [],
            'erros': []
        }

        # Listar arquivos CSV no diretorio
        arquivos_csv = [f for f in os.listdir(diretorio) if f.endswith('.csv')]

        if not arquivos_csv:
            return {'sucesso': False, 'erros': ['Nenhum arquivo CSV encontrado']}

        # Mapear arquivos para tabelas
        mapa_arquivos = {}
        for arquivo in arquivos_csv:
            # Extrair nome da tabela do nome do arquivo
            for tabela in self.ORDEM_TABELAS:
                if arquivo.startswith(tabela + '_'):
                    if tabela not in mapa_arquivos:
                        mapa_arquivos[tabela] = []
                    mapa_arquivos[tabela].append(arquivo)

        # Ordenar arquivos por data (mais recente por tabela)
        for tabela in mapa_arquivos:
            mapa_arquivos[tabela].sort(reverse=True)

        # Importar na ordem correta (respeitar foreign keys)
        for tabela in self.ORDEM_TABELAS:
            if tabela not in mapa_arquivos:
                print(f"\n! Tabela {tabela}: Nenhum arquivo CSV encontrado")
                continue

            # Usar o arquivo mais recente
            arquivo = mapa_arquivos[tabela][0]
            caminho = os.path.join(diretorio, arquivo)

            print(f"\nImportando {tabela.upper()} de {arquivo}...")

            sucesso, msg = self.importar_tabela_csv(tabela, caminho, limpar_tabelas)

            if sucesso:
                print(f"  OK: {msg}")
                resultado['importados'].append({'tabela': tabela, 'arquivo': arquivo, 'msg': msg})
            else:
                print(f"  ERRO: {msg}")
                resultado['erros'].append(msg)
                resultado['sucesso'] = False

        # Resumo
        print("\n" + "-"*70)
        print(f"Importacao concluida!")
        print(f"Tabelas importadas: {len(resultado['importados'])}")
        if resultado['erros']:
            print(f"Erros: {len(resultado['erros'])}")

        return resultado

    def listar_exportacoes(self) -> List[Dict]:
        """
        Lista todas as exportacoes disponiveis.

        Returns:
            Lista de dicionarios com informacoes das exportacoes
        """
        exportacoes = []

        try:
            # Listar subdiretorios de exportacao
            for item in os.listdir(self.dir_exportacao):
                caminho = os.path.join(self.dir_exportacao, item)
                if os.path.isdir(caminho) and item.startswith('export_'):
                    # Contar arquivos CSV
                    arquivos = [f for f in os.listdir(caminho) if f.endswith('.csv')]

                    # Extrair data do nome
                    try:
                        data_str = item.replace('export_', '')
                        data = datetime.strptime(data_str, '%Y%m%d_%H%M%S')
                    except:
                        data = datetime.fromtimestamp(os.path.getmtime(caminho))

                    exportacoes.append({
                        'nome': item,
                        'caminho': caminho,
                        'data': data,
                        'arquivos': len(arquivos)
                    })

            # Ordenar por data (mais recente primeiro)
            exportacoes.sort(key=lambda x: x['data'], reverse=True)

        except Exception as e:
            print(f"Erro ao listar exportacoes: {e}")

        return exportacoes


# ============================================================================
# EXECUCAO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    """
    Interface de linha de comando para exportar/importar dados.
    """

    exp_imp = ExportadorImportador()

    print("\n" + "="*70)
    print("IMOBIPRO - EXPORTAR E IMPORTAR DADOS")
    print("="*70)
    print("\nOpcoes:")
    print("1. Exportar todas as tabelas para CSV")
    print("2. Importar tabelas de um diretorio")
    print("3. Listar exportacoes disponiveis")
    print("0. Sair")

    try:
        opcao = input("\nEscolha uma opcao: ").strip()

        if opcao == '1':
            resultado = exp_imp.exportar_todas_tabelas()
            if resultado['sucesso']:
                print(f"\nExportacao concluida com sucesso!")
                print(f"Arquivos salvos em: {resultado['diretorio']}")
            else:
                print("\nExportacao concluida com erros.")

        elif opcao == '2':
            # Listar exportacoes disponiveis
            exportacoes = exp_imp.listar_exportacoes()

            if not exportacoes:
                print("\nNenhuma exportacao disponivel.")
                diretorio = input("Digite o caminho do diretorio com os CSVs: ").strip()
            else:
                print("\nExportacoes disponiveis:\n")
                for i, exp in enumerate(exportacoes, 1):
                    print(f"{i}. {exp['nome']}")
                    print(f"   Data: {exp['data'].strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"   Arquivos: {exp['arquivos']} CSVs")
                    print()

                escolha = input("Escolha uma exportacao (numero) ou digite um caminho: ").strip()

                try:
                    idx = int(escolha) - 1
                    if 0 <= idx < len(exportacoes):
                        diretorio = exportacoes[idx]['caminho']
                    else:
                        diretorio = escolha
                except ValueError:
                    diretorio = escolha

            if diretorio:
                confirma = input(f"\nATENCAO: Isso ira substituir os dados atuais!\nDeseja continuar? (sim/nao): ")
                if confirma.lower() == 'sim':
                    resultado = exp_imp.importar_de_diretorio(diretorio)
                    if resultado['sucesso']:
                        print("\nImportacao concluida com sucesso!")
                    else:
                        print("\nImportacao concluida com erros.")
                else:
                    print("\nOperacao cancelada.")

        elif opcao == '3':
            exportacoes = exp_imp.listar_exportacoes()

            if exportacoes:
                print(f"\n{len(exportacoes)} exportacao(oes) disponivel(is):\n")
                for exp in exportacoes:
                    print(f"- {exp['nome']}")
                    print(f"  Data: {exp['data'].strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"  Arquivos: {exp['arquivos']} CSVs")
                    print(f"  Caminho: {exp['caminho']}")
                    print()
            else:
                print("\nNenhuma exportacao encontrada.")

        elif opcao == '0':
            print("\nSaindo...")
        else:
            print("\nOpcao invalida.")

    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
