"""
Correções para o arquivo app.py do ImobiPro
Este arquivo contém as rotas que devem ser adicionadas ou corrigidas no app.py
"""

# ============================================================================
# ROTAS DE IMÓVEIS - Adicionar/Corrigir no app.py
# ============================================================================

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database.db_manager import DatabaseManager
import os

# Inicialização (deve estar no início do app.py)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Instância do gerenciador de banco
db = DatabaseManager()

# ============================================================================
# ROTAS DE IMÓVEIS
# ============================================================================

@app.route('/imoveis')
def imoveis():
    """Lista todos os imóveis"""
    try:
        imoveis = db.listar_imoveis()
        return render_template('imoveis/lista.html', imoveis=imoveis)
    except Exception as e:
        flash(f'Erro ao carregar imóveis: {str(e)}', 'danger')
        return render_template('imoveis/lista.html', imoveis=[])

@app.route('/imoveis/novo', methods=['GET', 'POST'])
def imoveis_novo():
    """Cadastra um novo imóvel"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            dados_imovel = {
                'endereco': request.form.get('endereco'),
                'numero': request.form.get('numero'),
                'complemento': request.form.get('complemento'),
                'bairro': request.form.get('bairro'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado'),
                'cep': request.form.get('cep'),
                'tipo': request.form.get('tipo'),
                'quartos': int(request.form.get('quartos', 0)),
                'banheiros': int(request.form.get('banheiros', 0)),
                'vagas': int(request.form.get('vagas', 0)),
                'area_total': float(request.form.get('area_total', 0)) if request.form.get('area_total') else None,
                'valor_compra': float(request.form.get('valor_compra', 0)) if request.form.get('valor_compra') else None,
                'valor_atual': float(request.form.get('valor_atual', 0)) if request.form.get('valor_atual') else None,
                'iptu_anual': float(request.form.get('iptu_anual', 0)) if request.form.get('iptu_anual') else None,
                'matricula': request.form.get('matricula'),
                'inscricao_municipal': request.form.get('inscricao_municipal'),
                'status': request.form.get('status', 'disponivel'),
                'observacoes': request.form.get('observacoes')
            }
            
            # Insere no banco
            imovel_id = db.inserir_imovel(**dados_imovel)
            
            flash(f'Imóvel cadastrado com sucesso! ID: {imovel_id}', 'success')
            return redirect(url_for('imoveis'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar imóvel: {str(e)}', 'danger')
            return render_template('imoveis/form.html', imovel=None)
    
    # GET - Exibe formulário vazio
    return render_template('imoveis/form.html', imovel=None)

@app.route('/imoveis/editar/<int:id>', methods=['GET', 'POST'])
def imoveis_editar(id):
    """Edita um imóvel existente"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            dados_imovel = {
                'endereco': request.form.get('endereco'),
                'numero': request.form.get('numero'),
                'complemento': request.form.get('complemento'),
                'bairro': request.form.get('bairro'),
                'cidade': request.form.get('cidade'),
                'estado': request.form.get('estado'),
                'cep': request.form.get('cep'),
                'tipo': request.form.get('tipo'),
                'quartos': int(request.form.get('quartos', 0)),
                'banheiros': int(request.form.get('banheiros', 0)),
                'vagas': int(request.form.get('vagas', 0)),
                'area_total': float(request.form.get('area_total', 0)) if request.form.get('area_total') else None,
                'valor_compra': float(request.form.get('valor_compra', 0)) if request.form.get('valor_compra') else None,
                'valor_atual': float(request.form.get('valor_atual', 0)) if request.form.get('valor_atual') else None,
                'iptu_anual': float(request.form.get('iptu_anual', 0)) if request.form.get('iptu_anual') else None,
                'matricula': request.form.get('matricula'),
                'inscricao_municipal': request.form.get('inscricao_municipal'),
                'status': request.form.get('status'),
                'observacoes': request.form.get('observacoes')
            }
            
            # Atualiza no banco
            db.atualizar_imovel(id, **dados_imovel)
            
            flash('Imóvel atualizado com sucesso!', 'success')
            return redirect(url_for('imoveis'))
            
        except Exception as e:
            flash(f'Erro ao atualizar imóvel: {str(e)}', 'danger')
    
    # GET - Busca dados do imóvel
    try:
        imovel = db.buscar_imovel(id)
        if not imovel:
            flash('Imóvel não encontrado!', 'warning')
            return redirect(url_for('imoveis'))
        return render_template('imoveis/form.html', imovel=imovel)
    except Exception as e:
        flash(f'Erro ao carregar imóvel: {str(e)}', 'danger')
        return redirect(url_for('imoveis'))

@app.route('/imoveis/excluir/<int:id>', methods=['POST'])
def imoveis_excluir(id):
    """Exclui um imóvel"""
    try:
        db.excluir_imovel(id)
        flash('Imóvel excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir imóvel: {str(e)}', 'danger')
    return redirect(url_for('imoveis'))

# ============================================================================
# ROTAS DE CONTRATOS
# ============================================================================

@app.route('/contratos')
def contratos():
    """Lista todos os contratos"""
    try:
        contratos = db.listar_contratos()
        return render_template('contratos/lista.html', contratos=contratos)
    except Exception as e:
        flash(f'Erro ao carregar contratos: {str(e)}', 'danger')
        return render_template('contratos/lista.html', contratos=[])

@app.route('/contratos/novo', methods=['GET', 'POST'])
def contratos_novo():
    """Cadastra um novo contrato"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            dados_contrato = {
                'imovel_id': int(request.form.get('imovel_id')),
                'inquilino_id': int(request.form.get('inquilino_id')),
                'fiador_id': int(request.form.get('fiador_id')) if request.form.get('fiador_id') else None,
                'data_inicio': request.form.get('data_inicio'),
                'data_fim': request.form.get('data_fim'),
                'valor_aluguel': float(request.form.get('valor_aluguel')),
                'dia_vencimento': int(request.form.get('dia_vencimento')),
                'taxa_administracao': float(request.form.get('taxa_administracao', 0)) if request.form.get('taxa_administracao') else None,
                'indice_reajuste': request.form.get('indice_reajuste'),
                'periodicidade_reajuste': int(request.form.get('periodicidade_reajuste', 12)),
                'observacoes': request.form.get('observacoes')
            }
            
            # Insere no banco
            contrato_id = db.inserir_contrato(**dados_contrato)
            
            # Atualiza status do imóvel para ocupado
            db.atualizar_imovel(dados_contrato['imovel_id'], status='ocupado')
            
            flash(f'Contrato cadastrado com sucesso! ID: {contrato_id}', 'success')
            return redirect(url_for('contratos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar contrato: {str(e)}', 'danger')
            return render_template('contratos/form.html', 
                                 contrato=None, 
                                 imoveis=db.listar_imoveis_disponiveis(),
                                 pessoas=db.listar_pessoas())
    
    # GET - Exibe formulário vazio com dados auxiliares
    try:
        imoveis = db.listar_imoveis_disponiveis()
        pessoas = db.listar_pessoas()
        return render_template('contratos/form.html', 
                             contrato=None, 
                             imoveis=imoveis,
                             pessoas=pessoas)
    except Exception as e:
        flash(f'Erro ao carregar dados: {str(e)}', 'danger')
        return redirect(url_for('contratos'))

@app.route('/contratos/editar/<int:id>', methods=['GET', 'POST'])
def contratos_editar(id):
    """Edita um contrato existente"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            dados_contrato = {
                'imovel_id': int(request.form.get('imovel_id')),
                'inquilino_id': int(request.form.get('inquilino_id')),
                'fiador_id': int(request.form.get('fiador_id')) if request.form.get('fiador_id') else None,
                'data_inicio': request.form.get('data_inicio'),
                'data_fim': request.form.get('data_fim'),
                'valor_aluguel': float(request.form.get('valor_aluguel')),
                'dia_vencimento': int(request.form.get('dia_vencimento')),
                'taxa_administracao': float(request.form.get('taxa_administracao', 0)) if request.form.get('taxa_administracao') else None,
                'indice_reajuste': request.form.get('indice_reajuste'),
                'periodicidade_reajuste': int(request.form.get('periodicidade_reajuste', 12)),
                'status': request.form.get('status'),
                'observacoes': request.form.get('observacoes')
            }
            
            # Atualiza no banco
            db.atualizar_contrato(id, **dados_contrato)
            
            flash('Contrato atualizado com sucesso!', 'success')
            return redirect(url_for('contratos'))
            
        except Exception as e:
            flash(f'Erro ao atualizar contrato: {str(e)}', 'danger')
    
    # GET - Busca dados do contrato
    try:
        contrato = db.buscar_contrato(id)
        if not contrato:
            flash('Contrato não encontrado!', 'warning')
            return redirect(url_for('contratos'))
        
        imoveis = db.listar_imoveis()
        pessoas = db.listar_pessoas()
        return render_template('contratos/form.html', 
                             contrato=contrato,
                             imoveis=imoveis,
                             pessoas=pessoas)
    except Exception as e:
        flash(f'Erro ao carregar contrato: {str(e)}', 'danger')
        return redirect(url_for('contratos'))

@app.route('/contratos/encerrar/<int:id>', methods=['POST'])
def contratos_encerrar(id):
    """Encerra um contrato e libera o imóvel"""
    try:
        contrato = db.buscar_contrato(id)
        if not contrato:
            flash('Contrato não encontrado!', 'warning')
            return redirect(url_for('contratos'))
        
        # Encerra o contrato
        db.atualizar_contrato(id, status='encerrado')
        
        # Atualiza status do imóvel para disponível
        db.atualizar_imovel(contrato['imovel_id'], status='disponivel')
        
        flash('Contrato encerrado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao encerrar contrato: {str(e)}', 'danger')
    
    return redirect(url_for('contratos'))

# ============================================================================
# MÉTODOS AUXILIARES PARA O DatabaseManager
# ============================================================================

"""
Adicione estes métodos na classe DatabaseManager em database/db_manager.py:

def listar_imoveis_disponiveis(self):
    '''Retorna lista de imóveis disponíveis para locação'''
    query = '''
        SELECT * FROM imoveis 
        WHERE status = 'disponivel' 
        ORDER BY cidade, bairro, endereco
    '''
    return self.executar_query(query)

def buscar_imovel(self, imovel_id):
    '''Retorna os dados de um imóvel específico'''
    query = 'SELECT * FROM imoveis WHERE id = ?'
    resultado = self.executar_query(query, (imovel_id,))
    return resultado[0] if resultado else None

def atualizar_imovel(self, imovel_id, **kwargs):
    '''Atualiza os dados de um imóvel'''
    campos = []
    valores = []
    
    for campo, valor in kwargs.items():
        if valor is not None:
            campos.append(f'{campo} = ?')
            valores.append(valor)
    
    if not campos:
        return
    
    valores.append(imovel_id)
    query = f'UPDATE imoveis SET {", ".join(campos)} WHERE id = ?'
    
    self.executar_query(query, tuple(valores), commit=True)

def excluir_imovel(self, imovel_id):
    '''Exclui um imóvel (se não tiver contratos ativos)'''
    # Verifica se há contratos ativos
    query = 'SELECT COUNT(*) as total FROM contratos WHERE imovel_id = ? AND status = "ativo"'
    resultado = self.executar_query(query, (imovel_id,))
    
    if resultado[0]['total'] > 0:
        raise Exception('Não é possível excluir imóvel com contratos ativos')
    
    query = 'DELETE FROM imoveis WHERE id = ?'
    self.executar_query(query, (imovel_id,), commit=True)

def listar_contratos(self):
    '''Retorna lista de todos os contratos com informações relacionadas'''
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
    '''Retorna os dados de um contrato específico'''
    query = 'SELECT * FROM contratos WHERE id = ?'
    resultado = self.executar_query(query, (contrato_id,))
    return resultado[0] if resultado else None

def atualizar_contrato(self, contrato_id, **kwargs):
    '''Atualiza os dados de um contrato'''
    campos = []
    valores = []
    
    for campo, valor in kwargs.items():
        if valor is not None:
            campos.append(f'{campo} = ?')
            valores.append(valor)
    
    if not campos:
        return
    
    valores.append(contrato_id)
    query = f'UPDATE contratos SET {", ".join(campos)} WHERE id = ?'
    
    self.executar_query(query, tuple(valores), commit=True)

def listar_pessoas(self):
    '''Retorna lista de todas as pessoas'''
    query = 'SELECT * FROM pessoas ORDER BY nome'
    return self.executar_query(query)
"""

# ============================================================================
# NOTAS IMPORTANTES
# ============================================================================

"""
1. Certifique-se de que o SECRET_KEY está configurado corretamente
2. Verifique se as pastas templates/imoveis e templates/contratos existem
3. As rotas usam flash() para mensagens - certifique-se de ter isso no base.html
4. Adicione os métodos auxiliares ao DatabaseManager conforme indicado
5. Teste cada rota individualmente após implementar
"""
