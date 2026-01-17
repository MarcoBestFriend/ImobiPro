"""
================================================================================
IMOBIPRO - APLICAÇÃO WEB PRINCIPAL
================================================================================
Autor: Sistema ImobiPro
Data: Janeiro 2026
Descrição: Aplicação Flask principal com todas as rotas e funcionalidades
================================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import os

from config import get_config
from database.db_manager import DatabaseManager

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(get_config('development'))

# Inicializar gerenciador de banco de dados
db = DatabaseManager()


# ============================================================================
# FILTROS PERSONALIZADOS PARA TEMPLATES
# ============================================================================

@app.template_filter('formatar_moeda')
def formatar_moeda(valor):
    """Formata valor como moeda brasileira."""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {float(valor):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


@app.template_filter('formatar_data')
def formatar_data(data):
    """Formata data para formato brasileiro."""
    if not data:
        return ""
    if isinstance(data, str):
        try:
            dt = datetime.strptime(data, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except:
            return data
    if isinstance(data, (date, datetime)):
        return data.strftime('%d/%m/%Y')
    return data


@app.template_filter('status_badge')
def status_badge(status):
    """Retorna classe CSS para badge de status."""
    badges = {
        'Ativo': 'badge-success',
        'Prorrogado': 'badge-info',
        'Encerrado': 'badge-secondary',
        'Rescindido': 'badge-danger',
        'Pendente': 'badge-warning',
        'Recebido': 'badge-success',
        'Atrasado': 'badge-danger',
        'Sim': 'badge-success',
        'Não': 'badge-secondary',
    }
    return badges.get(status, 'badge-primary')


# ============================================================================
# ROTAS - PÁGINA INICIAL E DASHBOARD
# ============================================================================

@app.route('/')
def index():
    """Página inicial - redireciona para dashboard."""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Dashboard principal com estatísticas e resumos."""
    # Buscar estatísticas
    stats = db.get_estatisticas_dashboard()
    
    # Buscar contratos ativos
    contratos_ativos = db.get_contratos_ativos()
    
    # Buscar despesas pendentes (próximas a vencer)
    despesas_pendentes = db.get_despesas_pendentes()
    
    # Buscar receitas pendentes (próximas a vencer)
    receitas_pendentes = db.get_receitas_pendentes()
    
    # Imóveis disponíveis
    imoveis_disponiveis = db.get_imoveis_disponiveis()
    
    return render_template('dashboard.html',
                         stats=stats,
                         contratos_ativos=contratos_ativos[:5],  # Últimos 5
                         despesas_pendentes=despesas_pendentes[:5],
                         receitas_pendentes=receitas_pendentes[:5],
                         imoveis_disponiveis=imoveis_disponiveis[:5])


# ============================================================================
# ROTAS - IMÓVEIS
# ============================================================================

@app.route('/imoveis')
def listar_imoveis():
    """Lista todos os imóveis."""
    # Buscar parâmetros de filtro
    filtro_ocupado = request.args.get('ocupado', '')
    busca = request.args.get('busca', '')
    
    # Buscar imóveis
    if filtro_ocupado:
        imoveis = db.get_where('imoveis', 'ocupado = ?', (filtro_ocupado,), 'endereco_completo')
    elif busca:
        imoveis = db.get_where('imoveis', 'endereco_completo LIKE ?', (f'%{busca}%',), 'endereco_completo')
    else:
        imoveis = db.get_all('imoveis', 'endereco_completo')
    
    return render_template('imoveis/listar.html', imoveis=imoveis, filtro_ocupado=filtro_ocupado, busca=busca)


@app.route('/imoveis/novo', methods=['GET', 'POST'])
def novo_imovel():
    """Cadastra novo imóvel."""
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            dados = {
                'endereco_completo': request.form.get('endereco_completo'),
                'inscricao_imobiliaria': request.form.get('inscricao_imobiliaria'),
                'tipo_imovel': request.form.get('tipo_imovel'),
                'valor_iptu_anual': request.form.get('valor_iptu_anual') or None,
                'forma_pagamento_iptu': request.form.get('forma_pagamento_iptu', 'Anual'),
                'aluguel_pretendido': request.form.get('aluguel_pretendido') or None,
                'condominio_sugerido': request.form.get('condominio_sugerido') or None,
                'dia_venc_condominio': request.form.get('dia_venc_condominio') or None,
                'cidade': request.form.get('cidade') or 'Campo Grande',
                'estado': request.form.get('estado') or 'MS',
                'cep': request.form.get('cep'),
                'observacoes': request.form.get('observacoes'),
            }
            
            # Validar campo obrigatório
            if not dados['endereco_completo']:
                flash('Endereço completo é obrigatório!', 'danger')
                return render_template('imoveis/form.html', imovel=dados, config=app.config)
            
            # Inserir no banco
            imovel_id = db.insert('imoveis', dados)
            
            if imovel_id:
                flash(f'Imóvel cadastrado com sucesso! ID: {imovel_id}', 'success')
                return redirect(url_for('listar_imoveis'))
            else:
                flash('Erro ao cadastrar imóvel.', 'danger')
                
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('imoveis/form.html', imovel=None, config=app.config)


@app.route('/imoveis/<int:id>')
def ver_imovel(id):
    """Visualiza detalhes de um imóvel."""
    imovel = db.get_by_id('imoveis', id)
    
    if not imovel:
        flash('Imóvel não encontrado.', 'danger')
        return redirect(url_for('listar_imoveis'))
    
    # Buscar contratos do imóvel
    contratos = db.get_where('contratos', 'id_imovel = ?', (id,), 'inicio_contrato DESC')
    
    # Buscar despesas do imóvel
    despesas = db.get_where('despesas', 'id_imovel = ?', (id,), 'vencimento_previsto DESC')
    
    return render_template('imoveis/ver.html', imovel=imovel, contratos=contratos, despesas=despesas)


@app.route('/imoveis/<int:id>/editar', methods=['GET', 'POST'])
def editar_imovel(id):
    """Edita um imóvel existente."""
    imovel = db.get_by_id('imoveis', id)
    
    if not imovel:
        flash('Imóvel não encontrado.', 'danger')
        return redirect(url_for('listar_imoveis'))
    
    if request.method == 'POST':
        try:
            dados = {
                'endereco_completo': request.form.get('endereco_completo'),
                'inscricao_imobiliaria': request.form.get('inscricao_imobiliaria'),
                'tipo_imovel': request.form.get('tipo_imovel'),
                'valor_iptu_anual': request.form.get('valor_iptu_anual') or None,
                'forma_pagamento_iptu': request.form.get('forma_pagamento_iptu'),
                'aluguel_pretendido': request.form.get('aluguel_pretendido') or None,
                'condominio_sugerido': request.form.get('condominio_sugerido') or None,
                'dia_venc_condominio': request.form.get('dia_venc_condominio') or None,
                'cidade': request.form.get('cidade') or 'Campo Grande',
                'estado': request.form.get('estado') or 'MS',
                'cep': request.form.get('cep'),
                'observacoes': request.form.get('observacoes'),
            }

            if not dados['endereco_completo']:
                flash('Endereço completo é obrigatório!', 'danger')
                return render_template('imoveis/form.html', imovel=dados, config=app.config)

            if db.update('imoveis', dados, 'id = ?', (id,)):
                flash('Imóvel atualizado com sucesso!', 'success')
                return redirect(url_for('ver_imovel', id=id))
            else:
                flash('Erro ao atualizar imóvel.', 'danger')
                
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('imoveis/form.html', imovel=imovel, config=app.config)


@app.route('/imoveis/<int:id>/excluir', methods=['POST'])
def excluir_imovel(id):
    """Exclui um imóvel."""
    try:
        if db.delete('imoveis', 'id = ?', (id,)):
            flash('Imóvel excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir imóvel.', 'danger')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')
    
    return redirect(url_for('listar_imoveis'))


# ============================================================================
# ROTAS - PESSOAS
# ============================================================================

@app.route('/pessoas')
def listar_pessoas():
    """Lista todas as pessoas."""
    situacao = request.args.get('situacao', '')
    busca = request.args.get('busca', '')
    
    if situacao:
        pessoas = db.get_where('pessoas', 'situacao = ?', (situacao,), 'nome_completo')
    elif busca:
        pessoas = db.get_where('pessoas', 'nome_completo LIKE ?', (f'%{busca}%',), 'nome_completo')
    else:
        pessoas = db.get_all('pessoas', 'nome_completo')
    
    return render_template('pessoas/listar.html', pessoas=pessoas, situacao=situacao, busca=busca)


@app.route('/pessoas/novo', methods=['GET', 'POST'])
def nova_pessoa():
    """Cadastra nova pessoa."""
    if request.method == 'POST':
        try:
            dados = {
                'situacao': request.form.get('situacao'),
                'nome_completo': request.form.get('nome_completo'),
                'cpf_cnpj': request.form.get('cpf_cnpj'),
                'telefone': request.form.get('telefone'),
                'email': request.form.get('email'),
                'endereco_completo': request.form.get('endereco_completo'),
                'cidade': request.form.get('cidade'),
                'patrimonio': request.form.get('patrimonio') or None,
                'estado_civil': request.form.get('estado_civil'),
                'nome_conjuge': request.form.get('nome_conjuge'),
                'cpf_conjuge': request.form.get('cpf_conjuge'),
                'observacoes': request.form.get('observacoes'),
            }
            
            if not dados['nome_completo']:
                flash('Nome completo é obrigatório!', 'danger')
                return render_template('pessoas/form.html', pessoa=dados, config=app.config)
            
            pessoa_id = db.insert('pessoas', dados)
            
            if pessoa_id:
                flash(f'Pessoa cadastrada com sucesso! ID: {pessoa_id}', 'success')
                return redirect(url_for('listar_pessoas'))
            else:
                flash('Erro ao cadastrar pessoa.', 'danger')
                
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('pessoas/form.html', pessoa=None, config=app.config)


# ============================================================================
# ROTAS - CONTRATOS
# ============================================================================

@app.route('/contratos')
def listar_contratos():
    """Lista todos os contratos."""
    status = request.args.get('status', '')
    
    if status:
        contratos = db.get_where('contratos', 'status_contrato = ?', (status,), 'inicio_contrato DESC')
    else:
        contratos = db.get_all('contratos', 'inicio_contrato DESC')
    
    # Enriquecer com dados relacionados
    for contrato in contratos:
        contrato['imovel'] = db.get_by_id('imoveis', contrato['id_imovel'])
        contrato['inquilino'] = db.get_by_id('pessoas', contrato['id_inquilino'])
        if contrato['id_fiador']:
            contrato['fiador'] = db.get_by_id('pessoas', contrato['id_fiador'])
    
    return render_template('contratos/listar.html', contratos=contratos, status=status, config=app.config)


@app.route('/contratos/novo', methods=['GET', 'POST'])
def novo_contrato():
    """Cadastra novo contrato."""
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            dados = {
                'id_imovel': request.form.get('id_imovel'),
                'id_inquilino': request.form.get('id_inquilino'),
                'id_fiador': request.form.get('id_fiador') or None,
                'garantia': request.form.get('garantia'),
                'inicio_contrato': request.form.get('inicio_contrato'),
                'fim_contrato': request.form.get('fim_contrato') or None,
                'valor_aluguel': request.form.get('valor_aluguel'),
                'dia_vencimento': request.form.get('dia_vencimento'),
                'indice_reajuste': request.form.get('indice_reajuste', 'IGPM'),
                'data_base_reajuste': request.form.get('data_base_reajuste') or None,
                'status_contrato': request.form.get('status_contrato', 'Ativo'),
                'observacoes': request.form.get('observacoes'),
            }
            
            # Validações
            if not dados['id_imovel'] or not dados['id_inquilino']:
                flash('Imóvel e Inquilino são obrigatórios!', 'danger')
                return redirect(url_for('novo_contrato'))
            
            # Se garantia é fiança, fiador é obrigatório
            if dados['garantia'] == 'fiança' and not dados['id_fiador']:
                flash('Fiador é obrigatório quando a garantia é "fiança"!', 'danger')
                return redirect(url_for('novo_contrato'))
            
            # Inserir contrato
            contrato_id = db.insert('contratos', dados)
            
            if contrato_id:
                flash(f'Contrato cadastrado com sucesso! ID: {contrato_id}', 'success')
                return redirect(url_for('listar_contratos'))
            else:
                flash('Erro ao cadastrar contrato.', 'danger')
                
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    # Buscar dados para os selects
    imoveis_disponiveis = db.get_imoveis_disponiveis()
    inquilinos = db.get_where('pessoas', "situacao IN ('Inquilino', 'Ambos')", (), 'nome_completo')
    fiadores = db.get_where('pessoas', "situacao IN ('Fiador', 'Ambos')", (), 'nome_completo')
    
    return render_template('contratos/form.html', 
                         contrato=None, 
                         imoveis_disponiveis=imoveis_disponiveis,
                         inquilinos=inquilinos,
                         fiadores=fiadores,
                         config=app.config)


@app.route('/contratos/<int:id>/editar', methods=['GET', 'POST'])
def editar_contrato(id):
    """Edita um contrato existente."""
    contrato = db.get_by_id('contratos', id)
    
    if not contrato:
        flash('Contrato não encontrado.', 'danger')
        return redirect(url_for('listar_contratos'))
    
    if request.method == 'POST':
        try:
            dados = {
                'id_imovel': request.form.get('id_imovel'),
                'id_inquilino': request.form.get('id_inquilino'),
                'id_fiador': request.form.get('id_fiador') or None,
                'garantia': request.form.get('garantia'),
                'inicio_contrato': request.form.get('inicio_contrato'),
                'fim_contrato': request.form.get('fim_contrato') or None,
                'valor_aluguel': request.form.get('valor_aluguel'),
                'dia_vencimento': request.form.get('dia_vencimento'),
                'indice_reajuste': request.form.get('indice_reajuste'),
                'data_base_reajuste': request.form.get('data_base_reajuste') or None,
                'status_contrato': request.form.get('status_contrato'),
                'observacoes': request.form.get('observacoes'),
            }
            
            # Validação de fiador
            if dados['garantia'] == 'fiança' and not dados['id_fiador']:
                flash('Fiador é obrigatório quando a garantia é "fiança"!', 'danger')
                return redirect(url_for('editar_contrato', id=id))
            
            if db.update('contratos', dados, 'id = ?', (id,)):
                flash('Contrato atualizado com sucesso!', 'success')
                return redirect(url_for('listar_contratos'))
            else:
                flash('Erro ao atualizar contrato.', 'danger')
                
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    # Buscar dados para os selects (incluindo imóvel atual)
    imoveis_disponiveis = db.get_imoveis_disponiveis()
    # Adicionar o imóvel atual se não estiver na lista
    imovel_atual = db.get_by_id('imoveis', contrato['id_imovel'])
    if imovel_atual and imovel_atual not in imoveis_disponiveis:
        imoveis_disponiveis.insert(0, imovel_atual)
    
    inquilinos = db.get_where('pessoas', "situacao IN ('Inquilino', 'Ambos')", (), 'nome_completo')
    fiadores = db.get_where('pessoas', "situacao IN ('Fiador', 'Ambos')", (), 'nome_completo')
    
    return render_template('contratos/form.html',
                         contrato=contrato,
                         imoveis_disponiveis=imoveis_disponiveis,
                         inquilinos=inquilinos,
                         fiadores=fiadores,
                         config=app.config)


# ============================================================================
# ROTAS - DESPESAS
# ============================================================================

@app.route('/despesas')
def listar_despesas():
    """Lista todas as despesas."""
    tipo = request.args.get('tipo', '')
    status = request.args.get('status', '')
    
    if tipo:
        despesas = db.get_where('despesas', 'tipo_despesa = ?', (tipo,), 'vencimento_previsto DESC')
    elif status == 'pendente':
        despesas = db.get_despesas_pendentes()
    else:
        despesas = db.execute_query("""
            SELECT d.*, i.endereco_completo as imovel_endereco
            FROM despesas d
            JOIN imoveis i ON d.id_imovel = i.id
            ORDER BY d.vencimento_previsto DESC
            LIMIT 100
        """)
    
    return render_template('despesas/listar.html', despesas=despesas, tipo=tipo, status=status, config=app.config)


@app.route('/despesas/nova', methods=['GET', 'POST'])
def nova_despesa():
    """Cadastra nova despesa."""
    if request.method == 'POST':
        try:
            dados = {
                'id_imovel': request.form.get('id_imovel'),
                'tipo_despesa': request.form.get('tipo_despesa'),
                'motivo_despesa': request.form.get('motivo_despesa'),
                'mes_referencia': request.form.get('mes_referencia') or None,
                'valor_previsto': request.form.get('valor_previsto') or None,
                'valor_pago': request.form.get('valor_pago'),
                'vencimento_previsto': request.form.get('vencimento_previsto') or None,
                'data_pagamento': request.form.get('data_pagamento') or None,
                'observacoes': request.form.get('observacoes'),
            }

            # Validações
            if not dados['id_imovel'] or not dados['tipo_despesa'] or not dados['valor_pago']:
                flash('Imóvel, Tipo de Despesa e Valor Pago são obrigatórios!', 'danger')
                return redirect(url_for('nova_despesa'))

            despesa_id = db.insert('despesas', dados)

            if despesa_id:
                flash(f'Despesa cadastrada com sucesso! ID: {despesa_id}', 'success')
                return redirect(url_for('listar_despesas'))
            else:
                flash('Erro ao cadastrar despesa.', 'danger')

        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')

    # Buscar imóveis para o select
    imoveis = db.get_all('imoveis', 'endereco_completo')

    return render_template('despesas/form.html', despesa=None, imoveis=imoveis, config=app.config)


@app.route('/despesas/<int:id>/editar', methods=['GET', 'POST'])
def editar_despesa(id):
    """Edita uma despesa existente."""
    despesa = db.get_by_id('despesas', id)

    if not despesa:
        flash('Despesa não encontrada.', 'danger')
        return redirect(url_for('listar_despesas'))

    if request.method == 'POST':
        try:
            dados = {
                'id_imovel': request.form.get('id_imovel'),
                'tipo_despesa': request.form.get('tipo_despesa'),
                'motivo_despesa': request.form.get('motivo_despesa'),
                'mes_referencia': request.form.get('mes_referencia') or None,
                'valor_previsto': request.form.get('valor_previsto') or None,
                'valor_pago': request.form.get('valor_pago'),
                'vencimento_previsto': request.form.get('vencimento_previsto') or None,
                'data_pagamento': request.form.get('data_pagamento') or None,
                'observacoes': request.form.get('observacoes'),
            }

            if db.update('despesas', dados, 'id = ?', (id,)):
                flash('Despesa atualizada com sucesso!', 'success')
                return redirect(url_for('listar_despesas'))
            else:
                flash('Erro ao atualizar despesa.', 'danger')

        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')

    # Buscar imóveis para o select
    imoveis = db.get_all('imoveis', 'endereco_completo')

    return render_template('despesas/form.html', despesa=despesa, imoveis=imoveis, config=app.config)


@app.route('/despesas/<int:id>/excluir', methods=['POST'])
def excluir_despesa(id):
    """Exclui uma despesa."""
    try:
        if db.delete('despesas', 'id = ?', (id,)):
            flash('Despesa excluída com sucesso!', 'success')
        else:
            flash('Erro ao excluir despesa.', 'danger')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')

    return redirect(url_for('listar_despesas'))


@app.route('/despesas/<int:id>/pagar', methods=['POST'])
def pagar_despesa(id):
    """Marca uma despesa como paga."""
    try:
        despesa = db.get_by_id('despesas', id)
        if not despesa:
            flash('Despesa não encontrada.', 'danger')
            return redirect(url_for('listar_despesas'))

        dados = {
            'valor_pago': despesa['valor_previsto'],
            'data_pagamento': date.today().strftime('%Y-%m-%d')
        }

        if db.update('despesas', dados, 'id = ?', (id,)):
            flash('Despesa marcada como paga!', 'success')
        else:
            flash('Erro ao atualizar despesa.', 'danger')

    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')

    return redirect(url_for('listar_despesas'))


# ============================================================================
# ROTAS - RECEITAS
# ============================================================================

@app.route('/receitas')
def listar_receitas():
    """Lista todas as receitas."""
    status = request.args.get('status', '')
    
    if status == 'pendente':
        receitas = db.get_receitas_pendentes()
    else:
        receitas = db.execute_query("""
            SELECT r.*, c.valor_aluguel, i.endereco_completo as imovel_endereco,
                   p.nome_completo as inquilino_nome
            FROM receitas r
            JOIN contratos c ON r.id_contrato = c.id
            JOIN imoveis i ON c.id_imovel = i.id
            JOIN pessoas p ON c.id_inquilino = p.id
            ORDER BY r.vencimento_previsto DESC
            LIMIT 100
        """)
    
    return render_template('receitas/listar.html', receitas=receitas, status=status, config=app.config)


# ============================================================================
# ROTAS - RELATÓRIOS
# ============================================================================

@app.route('/relatorios')
def listar_relatorios():
    """Página de relatórios."""
    return render_template('relatorios/index.html')


# ============================================================================
# CONTEXTO GLOBAL PARA TEMPLATES
# ============================================================================

@app.context_processor
def inject_globals():
    """Injeta variáveis globais em todos os templates."""
    return {
        'ano_atual': datetime.now().year,
        'app_name': 'ImobiPro',
        'app_version': '1.0.0'
    }


# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Página não encontrada."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Erro interno do servidor."""
    return render_template('errors/500.html'), 500


# ============================================================================
# EXECUÇÃO DA APLICAÇÃO
# ============================================================================

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*70)
    print("🏠 IMOBIPRO - SISTEMA DE GESTÃO IMOBILIÁRIA")
    print("="*70)
    print(f"\n✓ Servidor iniciado!")
    print(f"✓ Acesse: http://localhost:5000")
    print(f"✓ Pressione Ctrl+C para encerrar\n")
    
    # Executar aplicação
    app.run(host='0.0.0.0', port=5000, debug=True)