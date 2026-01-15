"""
ImobiPro - Sistema de Gestão Imobiliária
Arquivo principal da aplicação Flask
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database.db_manager import DatabaseManager
import os
from datetime import datetime

# Inicializa a aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-imobipro-2026')
app.config['DEBUG'] = True  # Ativa modo debug para ver erros detalhados

# Cria instância do gerenciador de banco de dados
db = DatabaseManager()

# Filtros personalizados para templates
@app.template_filter('formatar_moeda')
def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

@app.template_filter('formatar_data')
def formatar_data(data):
    """Formata data para padrão brasileiro"""
    if not data:
        return ""
    try:
        dt = datetime.strptime(str(data), '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except:
        return str(data)

# ============================================================================
# ROTA PRINCIPAL
# ============================================================================

@app.route('/')
def dashboard():
    """Página inicial com dashboard"""
    try:
        # Busca estatísticas gerais
        stats = db.get_estatisticas_dashboard()
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', stats={})

# ============================================================================
# ROTAS DE IMÓVEIS
# ============================================================================

@app.route('/imoveis')
def listar_imoveis():
    """Lista todos os imóveis"""
    try:
        imoveis = db.get_all('imoveis', order_by='endereco_completo')
        return render_template('imoveis/listar.html', imoveis=imoveis)
    except Exception as e:
        flash(f'Erro ao carregar imóveis: {str(e)}', 'danger')
        return render_template('imoveis/listar.html', imoveis=[])

@app.route('/imoveis/ver/<int:id>')
def imoveis_ver(id):
    """Visualiza detalhes de um imóvel"""
    try:
        imovel = db.get_by_id('imoveis', id)
        if not imovel:
            flash('Imóvel não encontrado!', 'warning')
            return redirect(url_for('listar_imoveis'))
        return render_template('imoveis/ver.html', imovel=imovel)
    except Exception as e:
        flash(f'Erro ao carregar imóvel: {str(e)}', 'danger')
        return redirect(url_for('listar_imoveis'))

@app.route('/imoveis/novo', methods=['GET', 'POST'])
def imoveis_novo():
    """Cadastra um novo imóvel"""
    if request.method == 'POST':
        try:
            dados_imovel = {
                'endereco_completo': request.form.get('endereco_completo'),
                'inscricao_imobiliaria': request.form.get('inscricao_imobiliaria'),
                'tipo_imovel': request.form.get('tipo_imovel'),
                'valor_iptu_anual': float(request.form.get('valor_iptu_anual')) if request.form.get('valor_iptu_anual') else None,
                'forma_pagamento_iptu': request.form.get('forma_pagamento_iptu', 'Anual'),
                'aluguel_pretendido': float(request.form.get('aluguel_pretendido')) if request.form.get('aluguel_pretendido') else None,
                'condominio_sugerido': float(request.form.get('condominio_sugerido')) if request.form.get('condominio_sugerido') else None,
                'dia_venc_condominio': int(request.form.get('dia_venc_condominio')) if request.form.get('dia_venc_condominio') else None,
                'cidade': request.form.get('cidade', 'Campo Grande'),
                'estado': request.form.get('estado', 'MS'),
                'cep': request.form.get('cep'),
                'observacoes': request.form.get('observacoes')
            }
            
            # Remove valores None
            dados_imovel = {k: v for k, v in dados_imovel.items() if v is not None and v != ''}
            
            # Insere no banco
            imovel_id = db.insert('imoveis', dados_imovel)
            
            flash(f'Imóvel cadastrado com sucesso! ID: {imovel_id}', 'success')
            return redirect(url_for('listar_imoveis'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar imóvel: {str(e)}', 'danger')
            return render_template('imoveis/form.html', imovel=None)
    
    return render_template('imoveis/form.html', imovel=None)

@app.route('/imoveis/editar/<int:id>', methods=['GET', 'POST'])
def imoveis_editar(id):
    """Edita um imóvel existente"""
    if request.method == 'POST':
        try:
            dados_imovel = {
                'endereco_completo': request.form.get('endereco_completo'),
                'inscricao_imobiliaria': request.form.get('inscricao_imobiliaria'),
                'tipo_imovel': request.form.get('tipo_imovel'),
                'valor_iptu_anual': float(request.form.get('valor_iptu_anual')) if request.form.get('valor_iptu_anual') else None,
                'forma_pagamento_iptu': request.form.get('forma_pagamento_iptu'),
                'aluguel_pretendido': float(request.form.get('aluguel_pretendido')) if request.form.get('aluguel_pretendido') else None,
                'condominio_sugerido': float(request.form.get('condominio_sugerido')) if request.form.get('condominio_sugerido') else None,
                'dia_venc_condominio': int(request.form.get('dia_venc_condominio')) if request.form.get('dia_venc_condominio') else None,
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado'),
                'cep': request.form.get('cep'),
                'observacoes': request.form.get('observacoes')
            }
            
            dados_imovel = {k: v for k, v in dados_imovel.items() if v != ''}
            
            db.update('imoveis', dados_imovel, 'id = ?', (id,))
            
            flash('Imóvel atualizado com sucesso!', 'success')
            return redirect(url_for('listar_imoveis'))
            
        except Exception as e:
            flash(f'Erro ao atualizar imóvel: {str(e)}', 'danger')
    
    try:
        imovel = db.get_by_id('imoveis', id)
        if not imovel:
            flash('Imóvel não encontrado!', 'warning')
            return redirect(url_for('listar_imoveis'))
        return render_template('imoveis/form.html', imovel=imovel)
    except Exception as e:
        flash(f'Erro ao carregar imóvel: {str(e)}', 'danger')
        return redirect(url_for('listar_imoveis'))

@app.route('/imoveis/excluir/<int:id>', methods=['POST'])
def imoveis_excluir(id):
    """Exclui um imóvel"""
    try:
        # Verifica se há contratos ativos
        contratos = db.get_where('contratos', 'id_imovel = ? AND status_contrato = ?', (id, 'Ativo'))
        if contratos:
            flash('Não é possível excluir imóvel com contratos ativos!', 'danger')
            return redirect(url_for('listar_imoveis'))
        
        db.delete('imoveis', 'id = ?', (id,))
        flash('Imóvel excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir imóvel: {str(e)}', 'danger')
    return redirect(url_for('listar_imoveis'))

# ============================================================================
# ROTAS DE PESSOAS
# ============================================================================

@app.route('/pessoas')
def listar_pessoas():
    """Lista todas as pessoas"""
    try:
        pessoas = db.get_all('pessoas', order_by='nome_completo')
        return render_template('pessoas/listar.html', pessoas=pessoas)
    except Exception as e:
        flash(f'Erro ao carregar pessoas: {str(e)}', 'danger')
        return render_template('pessoas/listar.html', pessoas=[])

@app.route('/pessoas/novo', methods=['GET', 'POST'])
def pessoas_novo():
    """Cadastra uma nova pessoa"""
    if request.method == 'POST':
        try:
            dados_pessoa = {
                'situacao': request.form.get('situacao'),
                'nome_completo': request.form.get('nome_completo'),
                'cpf_cnpj': request.form.get('cpf_cnpj'),
                'telefone': request.form.get('telefone'),
                'email': request.form.get('email'),
                'endereco_completo': request.form.get('endereco_completo'),
                'cidade': request.form.get('cidade'),
                'patrimonio': float(request.form.get('patrimonio')) if request.form.get('patrimonio') else None,
                'estado_civil': request.form.get('estado_civil'),
                'nome_conjuge': request.form.get('nome_conjuge'),
                'cpf_conjuge': request.form.get('cpf_conjuge'),
                'observacoes': request.form.get('observacoes')
            }
            
            dados_pessoa = {k: v for k, v in dados_pessoa.items() if v is not None and v != ''}
            
            pessoa_id = db.insert('pessoas', dados_pessoa)
            
            flash(f'Pessoa cadastrada com sucesso! ID: {pessoa_id}', 'success')
            return redirect(url_for('listar_pessoas'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar pessoa: {str(e)}', 'danger')
            return render_template('pessoas/form.html', pessoa=None)
    
    return render_template('pessoas/form.html', pessoa=None)

@app.route('/pessoas/editar/<int:id>', methods=['GET', 'POST'])
def pessoas_editar(id):
    """Edita uma pessoa existente"""
    if request.method == 'POST':
        try:
            dados_pessoa = {
                'situacao': request.form.get('situacao'),
                'nome_completo': request.form.get('nome_completo'),
                'cpf_cnpj': request.form.get('cpf_cnpj'),
                'telefone': request.form.get('telefone'),
                'email': request.form.get('email'),
                'endereco_completo': request.form.get('endereco_completo'),
                'cidade': request.form.get('cidade'),
                'patrimonio': float(request.form.get('patrimonio')) if request.form.get('patrimonio') else None,
                'estado_civil': request.form.get('estado_civil'),
                'nome_conjuge': request.form.get('nome_conjuge'),
                'cpf_conjuge': request.form.get('cpf_conjuge'),
                'observacoes': request.form.get('observacoes')
            }
            
            dados_pessoa = {k: v for k, v in dados_pessoa.items() if v != ''}
            
            db.update('pessoas', dados_pessoa, 'id = ?', (id,))
            
            flash('Pessoa atualizada com sucesso!', 'success')
            return redirect(url_for('listar_pessoas'))
            
        except Exception as e:
            flash(f'Erro ao atualizar pessoa: {str(e)}', 'danger')
    
    try:
        pessoa = db.get_by_id('pessoas', id)
        if not pessoa:
            flash('Pessoa não encontrada!', 'warning')
            return redirect(url_for('listar_pessoas'))
        return render_template('pessoas/form.html', pessoa=pessoa)
    except Exception as e:
        flash(f'Erro ao carregar pessoa: {str(e)}', 'danger')
        return redirect(url_for('listar_pessoas'))

# ============================================================================
# ROTAS DE CONTRATOS
# ============================================================================

@app.route('/contratos')
def listar_contratos():
    """Lista todos os contratos"""
    try:
        contratos = db.execute_query("SELECT * FROM vw_contratos_completos ORDER BY inicio_contrato DESC")
        return render_template('contratos/listar.html', contratos=contratos)
    except Exception as e:
        flash(f'Erro ao carregar contratos: {str(e)}', 'danger')
        return render_template('contratos/listar.html', contratos=[])

@app.route('/contratos/novo', methods=['GET', 'POST'])
def contratos_novo():
    """Cadastra um novo contrato"""
    if request.method == 'POST':
        try:
            dados_contrato = {
                'id_imovel': int(request.form.get('id_imovel')),
                'id_inquilino': int(request.form.get('id_inquilino')),
                'id_fiador': int(request.form.get('id_fiador')) if request.form.get('id_fiador') else None,
                'garantia': request.form.get('garantia', 'nenhuma'),
                'inicio_contrato': request.form.get('inicio_contrato'),
                'fim_contrato': request.form.get('fim_contrato'),
                'valor_aluguel': float(request.form.get('valor_aluguel')),
                'dia_vencimento': int(request.form.get('dia_vencimento')),
                'indice_reajuste': request.form.get('indice_reajuste', 'IGPM'),
                'status_contrato': 'Ativo',
                'observacoes': request.form.get('observacoes')
            }
            
            dados_contrato = {k: v for k, v in dados_contrato.items() if v is not None}
            
            contrato_id = db.insert('contratos', dados_contrato)
            
            flash(f'Contrato cadastrado com sucesso! ID: {contrato_id}', 'success')
            return redirect(url_for('listar_contratos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar contrato: {str(e)}', 'danger')
            imoveis = db.get_imoveis_disponiveis()
            pessoas = db.get_all('pessoas', order_by='nome_completo')
            return render_template('contratos/form.html', contrato=None, imoveis=imoveis, pessoas=pessoas)
    
    try:
        imoveis = db.get_imoveis_disponiveis()
        pessoas = db.get_all('pessoas', order_by='nome_completo')
        return render_template('contratos/form.html', contrato=None, imoveis=imoveis, pessoas=pessoas)
    except Exception as e:
        flash(f'Erro ao carregar dados: {str(e)}', 'danger')
        return redirect(url_for('listar_contratos'))

# ============================================================================
# ROTAS DE RECEITAS
# ============================================================================

@app.route('/receitas')
def listar_receitas():
    """Lista todas as receitas"""
    try:
        receitas = db.execute_query("SELECT * FROM vw_receitas_pendentes ORDER BY vencimento_previsto")
        return render_template('receitas/listar.html', receitas=receitas)
    except Exception as e:
        flash(f'Erro ao carregar receitas: {str(e)}', 'danger')
        return render_template('receitas/listar.html', receitas=[])

# ============================================================================
# ROTAS DE DESPESAS
# ============================================================================

@app.route('/despesas')
def listar_despesas():
    """Lista todas as despesas"""
    try:
        despesas = db.execute_query("SELECT * FROM vw_despesas_pendentes ORDER BY vencimento_previsto")
        return render_template('despesas/listar.html', despesas=despesas)
    except Exception as e:
        flash(f'Erro ao carregar despesas: {str(e)}', 'danger')
        return render_template('despesas/listar.html', despesas=[])

# ============================================================================
# ROTAS DE RELATÓRIOS
# ============================================================================

@app.route('/relatorios')
def listar_relatorios():
    """Página de relatórios"""
    try:
        return render_template('relatorios/index.html')
    except Exception as e:
        flash(f'Erro ao carregar relatórios: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ============================================================================
# EXECUÇÃO DA APLICAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏠 IMOBIPRO - Sistema de Gestão Imobiliária")
    print("="*70)
    print("\n✓ Servidor iniciado com sucesso!")
    print("✓ Acesse: http://localhost:5000")
    print("✓ Pressione Ctrl+C para parar o servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)