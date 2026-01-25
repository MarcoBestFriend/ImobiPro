#!/usr/bin/env python3
"""
Script de Diagnóstico do ImobiPro
Verifica a estrutura do projeto e identifica problemas
"""

import os
import sys
from pathlib import Path

class Colors:
    """Cores para output no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime um cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def verificar_estrutura_pastas():
    """Verifica se a estrutura de pastas está correta"""
    print_header("VERIFICANDO ESTRUTURA DE PASTAS")
    
    pastas_necessarias = [
        'database',
        'templates',
        'templates/imoveis',
        'templates/contratos',
        'templates/pessoas',
        'templates/despesas',
        'templates/receitas',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'utils',
        'backups'
    ]
    
    problemas = []
    
    for pasta in pastas_necessarias:
        if os.path.exists(pasta):
            print_success(f"Pasta existe: {pasta}")
        else:
            print_error(f"Pasta NÃO existe: {pasta}")
            problemas.append(f"Criar pasta: {pasta}")
    
    return problemas

def verificar_arquivos_necessarios():
    """Verifica se os arquivos necessários existem"""
    print_header("VERIFICANDO ARQUIVOS NECESSÁRIOS")
    
    arquivos_necessarios = {
        'app.py': 'Arquivo principal da aplicação',
        'database/schema.sql': 'Schema do banco de dados',
        'database/db_manager.py': 'Gerenciador do banco de dados',
        'templates/base.html': 'Template base',
        'templates/imoveis/lista.html': 'Lista de imóveis',
        'templates/imoveis/form.html': 'Formulário de imóveis',
        'templates/contratos/lista.html': 'Lista de contratos',
        'templates/contratos/form.html': 'Formulário de contratos',
        'requirements.txt': 'Dependências do projeto'
    }
    
    problemas = []
    
    for arquivo, descricao in arquivos_necessarios.items():
        if os.path.exists(arquivo):
            print_success(f"{arquivo} - {descricao}")
        else:
            print_error(f"{arquivo} NÃO encontrado - {descricao}")
            problemas.append(f"Criar arquivo: {arquivo}")
    
    return problemas

def verificar_app_py():
    """Verifica se o app.py tem as rotas necessárias"""
    print_header("VERIFICANDO ROTAS NO APP.PY")
    
    if not os.path.exists('app.py'):
        print_error("Arquivo app.py não encontrado!")
        return ["Arquivo app.py não existe"]
    
    with open('app.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    rotas_necessarias = {
        '/imoveis': 'Lista de imóveis',
        '/imoveis/novo': 'Cadastro de imóveis',
        '/imoveis/editar': 'Edição de imóveis',
        '/contratos': 'Lista de contratos',
        '/contratos/novo': 'Cadastro de contratos',
        '/contratos/editar': 'Edição de contratos'
    }
    
    problemas = []
    
    for rota, descricao in rotas_necessarias.items():
        if f"'{rota}'" in conteudo or f'"{rota}"' in conteudo:
            print_success(f"Rota encontrada: {rota} - {descricao}")
        else:
            print_error(f"Rota NÃO encontrada: {rota} - {descricao}")
            problemas.append(f"Adicionar rota: {rota}")
    
    # Verifica imports importantes
    imports_necessarios = [
        'Flask',
        'render_template',
        'request',
        'redirect',
        'url_for',
        'flash'
    ]
    
    print("\n" + Colors.BOLD + "Verificando imports:" + Colors.END)
    for imp in imports_necessarios:
        if imp in conteudo:
            print_success(f"Import encontrado: {imp}")
        else:
            print_warning(f"Import possivelmente faltando: {imp}")
            problemas.append(f"Verificar import: {imp}")
    
    return problemas

def verificar_db_manager():
    """Verifica se o db_manager.py tem os métodos necessários"""
    print_header("VERIFICANDO DATABASE MANAGER")
    
    if not os.path.exists('database/db_manager.py'):
        print_error("Arquivo database/db_manager.py não encontrado!")
        return ["Arquivo db_manager.py não existe"]
    
    with open('database/db_manager.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    metodos_necessarios = {
        'listar_imoveis': 'Listar todos os imóveis',
        'listar_imoveis_disponiveis': 'Listar imóveis disponíveis',
        'buscar_imovel': 'Buscar imóvel por ID',
        'inserir_imovel': 'Inserir novo imóvel',
        'atualizar_imovel': 'Atualizar imóvel',
        'excluir_imovel': 'Excluir imóvel',
        'listar_contratos': 'Listar todos os contratos',
        'buscar_contrato': 'Buscar contrato por ID',
        'inserir_contrato': 'Inserir novo contrato',
        'atualizar_contrato': 'Atualizar contrato',
        'listar_pessoas': 'Listar todas as pessoas'
    }
    
    problemas = []
    
    for metodo, descricao in metodos_necessarios.items():
        if f"def {metodo}" in conteudo:
            print_success(f"Método encontrado: {metodo}() - {descricao}")
        else:
            print_error(f"Método NÃO encontrado: {metodo}() - {descricao}")
            problemas.append(f"Adicionar método: {metodo}()")
    
    return problemas

def verificar_templates():
    """Verifica se os templates têm a estrutura correta"""
    print_header("VERIFICANDO TEMPLATES")
    
    problemas = []
    
    # Verifica base.html
    if os.path.exists('templates/base.html'):
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        checks = {
            'get_flashed_messages': 'Suporte a mensagens flash',
            'block content': 'Block de conteúdo',
            'block title': 'Block de título',
            'bootstrap': 'Bootstrap CSS'
        }
        
        print("\nVerificando base.html:")
        for check, descricao in checks.items():
            if check in conteudo.lower():
                print_success(f"{descricao}")
            else:
                print_warning(f"{descricao} - pode estar faltando")
                problemas.append(f"Verificar em base.html: {descricao}")
    else:
        print_error("templates/base.html não encontrado!")
        problemas.append("Criar templates/base.html")
    
    # Verifica form de imóveis
    if os.path.exists('templates/imoveis/form.html'):
        print_success("templates/imoveis/form.html existe")
    else:
        print_error("templates/imoveis/form.html NÃO existe - PROBLEMA PRINCIPAL!")
        problemas.append("URGENTE: Criar templates/imoveis/form.html")
    
    # Verifica form de contratos
    if os.path.exists('templates/contratos/form.html'):
        print_success("templates/contratos/form.html existe")
        
        # Verifica se o form tem method e action
        with open('templates/contratos/form.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'method=' in conteudo.lower():
            print_success("Formulário tem atributo method")
        else:
            print_warning("Formulário pode não ter atributo method")
            problemas.append("Verificar method no form de contratos")
        
        if 'action=' in conteudo.lower() or 'url_for' in conteudo:
            print_success("Formulário tem atributo action/url_for")
        else:
            print_warning("Formulário pode não ter atributo action")
            problemas.append("Verificar action no form de contratos")
    else:
        print_error("templates/contratos/form.html não encontrado!")
        problemas.append("Verificar templates/contratos/form.html")
    
    return problemas

def verificar_ambiente_virtual():
    """Verifica se o ambiente virtual está ativo"""
    print_header("VERIFICANDO AMBIENTE VIRTUAL")
    
    problemas = []
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Ambiente virtual ESTÁ ATIVO")
    else:
        print_warning("Ambiente virtual NÃO está ativo")
        print_info("Execute: source venv/bin/activate")
        problemas.append("Ativar ambiente virtual: source venv/bin/activate")
    
    # Verifica se a pasta venv existe
    if os.path.exists('venv'):
        print_success("Pasta venv existe")
    else:
        print_error("Pasta venv NÃO existe")
        problemas.append("Criar ambiente virtual: python3 -m venv venv")
    
    return problemas

def verificar_banco_dados():
    """Verifica se o banco de dados existe"""
    print_header("VERIFICANDO BANCO DE DADOS")
    
    problemas = []
    
    if os.path.exists('database/imobipro.db'):
        print_success("Banco de dados existe: database/imobipro.db")
        
        # Verifica tamanho do banco
        tamanho = os.path.getsize('database/imobipro.db')
        print_info(f"Tamanho do banco: {tamanho / 1024:.2f} KB")
        
        if tamanho < 1024:  # Menos de 1KB
            print_warning("Banco muito pequeno - pode estar vazio")
            problemas.append("Verificar se dados foram migrados")
    else:
        print_warning("Banco de dados NÃO existe")
        print_info("Execute: python3 migrar_planilha.py ImobiPro.xlsx")
        problemas.append("Criar banco: python3 migrar_planilha.py ImobiPro.xlsx")
    
    return problemas

def gerar_relatorio_final(todos_problemas):
    """Gera relatório final com todos os problemas encontrados"""
    print_header("RELATÓRIO FINAL")
    
    if not todos_problemas:
        print_success("PARABÉNS! Nenhum problema encontrado!")
        print_info("O sistema parece estar configurado corretamente.")
        return
    
    print_error(f"Foram encontrados {len(todos_problemas)} problemas:\n")
    
    # Agrupa problemas por categoria
    urgentes = [p for p in todos_problemas if 'URGENTE' in p]
    importantes = [p for p in todos_problemas if 'Criar' in p or 'Adicionar' in p]
    verificar = [p for p in todos_problemas if 'Verificar' in p]
    outros = [p for p in todos_problemas if p not in urgentes + importantes + verificar]
    
    if urgentes:
        print(f"\n{Colors.RED}{Colors.BOLD}🔴 URGENTES:{Colors.END}")
        for i, p in enumerate(urgentes, 1):
            print(f"  {i}. {p}")
    
    if importantes:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}🟡 IMPORTANTES:{Colors.END}")
        for i, p in enumerate(importantes, 1):
            print(f"  {i}. {p}")
    
    if verificar:
        print(f"\n{Colors.BLUE}{Colors.BOLD}🔵 VERIFICAR:{Colors.END}")
        for i, p in enumerate(verificar, 1):
            print(f"  {i}. {p}")
    
    if outros:
        print(f"\n{Colors.BOLD}OUTROS:{Colors.END}")
        for i, p in enumerate(outros, 1):
            print(f"  {i}. {p}")
    
    print(f"\n{Colors.BOLD}RECOMENDAÇÃO:{Colors.END}")
    print("1. Resolva primeiro os problemas URGENTES")
    print("2. Depois os IMPORTANTES")
    print("3. Por fim, verifique os outros itens")
    print(f"\n{Colors.BLUE}Consulte o arquivo GUIA_CORRECOES.md para instruções detalhadas{Colors.END}")

def main():
    """Função principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║              🏠 DIAGNÓSTICO DO IMOBIPRO 🏠                        ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    # Verifica se estamos no diretório correto
    if not os.path.exists('app.py') and not os.path.exists('database'):
        print_error("ERRO: Este script deve ser executado no diretório raiz do ImobiPro!")
        print_info("Navegue até ~/ImobiPro e execute novamente")
        sys.exit(1)
    
    todos_problemas = []
    
    # Executa todas as verificações
    todos_problemas.extend(verificar_ambiente_virtual())
    todos_problemas.extend(verificar_estrutura_pastas())
    todos_problemas.extend(verificar_arquivos_necessarios())
    todos_problemas.extend(verificar_banco_dados())
    todos_problemas.extend(verificar_db_manager())
    todos_problemas.extend(verificar_app_py())
    todos_problemas.extend(verificar_templates())
    
    # Gera relatório final
    gerar_relatorio_final(todos_problemas)
    
    print(f"\n{Colors.BOLD}Diagnóstico concluído!{Colors.END}\n")

if __name__ == '__main__':
    main()
