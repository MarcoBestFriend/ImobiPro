# 🔧 Guia de Correção - ImobiPro

## Problemas Identificados

1. ❌ `templates/imoveis/form.html` não existe
2. ❌ Rotas de imóveis e contratos com problemas
3. ❌ Métodos auxiliares faltando no DatabaseManager
4. ❌ Erro 404 ao tentar acessar formulários

## Solução Passo a Passo

### 📁 Passo 1: Criar Estrutura de Pastas

```bash
cd ~/ImobiPro
mkdir -p templates/imoveis
mkdir -p templates/contratos
mkdir -p templates/pessoas
mkdir -p templates/despesas
mkdir -p templates/receitas
```

### 📄 Passo 2: Copiar Arquivo de Formulário de Imóveis

O arquivo `imoveis_form.html` que criei precisa ser colocado em `templates/imoveis/form.html`:

```bash
# No VSCode, crie o arquivo:
# templates/imoveis/form.html

# Cole o conteúdo do arquivo imoveis_form.html que forneci
```

### 🐍 Passo 3: Adicionar Métodos ao DatabaseManager

Abra o arquivo `database/db_manager.py` no VSCode e adicione os seguintes métodos na classe `DatabaseManager`:

```python
def listar_imoveis_disponiveis(self):
    """Retorna lista de imóveis disponíveis para locação"""
    query = '''
        SELECT * FROM imoveis 
        WHERE status = 'disponivel' 
        ORDER BY cidade, bairro, endereco
    '''
    return self.executar_query(query)

def buscar_imovel(self, imovel_id):
    """Retorna os dados de um imóvel específico"""
    query = 'SELECT * FROM imoveis WHERE id = ?'
    resultado = self.executar_query(query, (imovel_id,))
    return resultado[0] if resultado else None

def atualizar_imovel(self, imovel_id, **kwargs):
    """Atualiza os dados de um imóvel"""
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
    """Exclui um imóvel (se não tiver contratos ativos)"""
    # Verifica se há contratos ativos
    query = 'SELECT COUNT(*) as total FROM contratos WHERE imovel_id = ? AND status = "ativo"'
    resultado = self.executar_query(query, (imovel_id,))
    
    if resultado[0]['total'] > 0:
        raise Exception('Não é possível excluir imóvel com contratos ativos')
    
    query = 'DELETE FROM imoveis WHERE id = ?'
    self.executar_query(query, (imovel_id,), commit=True)

def listar_contratos(self):
    """Retorna lista de todos os contratos com informações relacionadas"""
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
    """Retorna os dados de um contrato específico"""
    query = 'SELECT * FROM contratos WHERE id = ?'
    resultado = self.executar_query(query, (contrato_id,))
    return resultado[0] if resultado else None

def atualizar_contrato(self, contrato_id, **kwargs):
    """Atualiza os dados de um contrato"""
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
    """Retorna lista de todas as pessoas"""
    query = 'SELECT * FROM pessoas ORDER BY nome'
    return self.executar_query(query)
```

### 🌐 Passo 4: Adicionar/Corrigir Rotas no app.py

Abra o arquivo `app.py` no VSCode e verifique/adicione as seguintes rotas:

```python
from flask import Flask, render_template, request, redirect, url_for, flash
from database.db_manager import DatabaseManager
import os

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
            
            imovel_id = db.inserir_imovel(**dados_imovel)
            flash(f'Imóvel cadastrado com sucesso! ID: {imovel_id}', 'success')
            return redirect(url_for('imoveis'))
            
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
            
            db.atualizar_imovel(id, **dados_imovel)
            flash('Imóvel atualizado com sucesso!', 'success')
            return redirect(url_for('imoveis'))
            
        except Exception as e:
            flash(f'Erro ao atualizar imóvel: {str(e)}', 'danger')
    
    try:
        imovel = db.buscar_imovel(id)
        if not imovel:
            flash('Imóvel não encontrado!', 'warning')
            return redirect(url_for('imoveis'))
        return render_template('imoveis/form.html', imovel=imovel)
    except Exception as e:
        flash(f'Erro ao carregar imóvel: {str(e)}', 'danger')
        return redirect(url_for('imoveis'))

# ============================================================================
# ROTAS DE CONTRATOS
# ============================================================================

@app.route('/contratos/novo', methods=['GET', 'POST'])
def contratos_novo():
    """Cadastra um novo contrato"""
    if request.method == 'POST':
        try:
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
            
            contrato_id = db.inserir_contrato(**dados_contrato)
            db.atualizar_imovel(dados_contrato['imovel_id'], status='ocupado')
            
            flash(f'Contrato cadastrado com sucesso! ID: {contrato_id}', 'success')
            return redirect(url_for('contratos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar contrato: {str(e)}', 'danger')
    
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
```

### ✅ Passo 5: Verificar o Arquivo base.html

Certifique-se de que `templates/base.html` existe e tem suporte para mensagens flash:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ImobiPro{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-building"></i> ImobiPro
            </a>
            <!-- Menu items -->
        </div>
    </nav>

    <!-- Mensagens Flash -->
    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Conteúdo Principal -->
    {% block content %}{% endblock %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 🧪 Passo 6: Testar as Correções

```bash
# Ativar o ambiente virtual
cd ~/ImobiPro
source venv/bin/activate

# Executar a aplicação
python3 app.py
```

Acesse no navegador:
- `http://localhost:5000/imoveis/novo` - Deve abrir o formulário
- `http://localhost:5000/contratos/novo` - Deve abrir o formulário

### 🔍 Verificação de Problemas Comuns

#### Se ainda aparecer erro 404:

1. **Verifique a estrutura de pastas:**
```bash
tree templates/
```

Deve mostrar:
```
templates/
├── base.html
├── imoveis/
│   ├── form.html
│   └── lista.html
└── contratos/
    ├── form.html
    └── lista.html
```

2. **Verifique se o app.py está importando corretamente:**
```python
from flask import Flask, render_template  # Certifique-se de importar render_template
```

3. **Verifique os logs no terminal** quando acessar a URL

#### Se aparecer erro de "NoneType":

Isso geralmente indica que algum campo obrigatório está vindo como `None`. Verifique:
- Se todos os campos do formulário têm o atributo `name` correto
- Se o método do formulário é `POST`
- Se a action do form aponta para a URL correta

### 📋 Checklist Final

- [ ] Pasta `templates/imoveis` criada
- [ ] Arquivo `templates/imoveis/form.html` criado
- [ ] Métodos adicionados ao `DatabaseManager`
- [ ] Rotas adicionadas/corrigidas no `app.py`
- [ ] Arquivo `base.html` com suporte a mensagens flash
- [ ] Aplicação testada e funcionando

### 🆘 Próximos Passos se Ainda Houver Erros

Se após seguir todos os passos ainda houver erros:

1. **Copie o erro exato** do terminal
2. **Verifique qual arquivo** está causando o problema
3. **Compartilhe** a mensagem de erro completa

### 💡 Dica de Debug

Para ver melhor os erros, adicione no início do `app.py`:

```python
app.config['DEBUG'] = True
```

Isso mostrará erros detalhados no navegador.

---

## 📞 Precisa de Ajuda?

Se encontrar algum problema específico:
1. Anote a mensagem de erro completa
2. Verifique em qual passo ocorreu
3. Me avise para eu ajudar com a solução específica

Boa sorte! 🚀
