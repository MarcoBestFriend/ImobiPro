#!/bin/bash

################################################################################
# IMOBIPRO - SCRIPT DE INSTALAÇÃO AUTOMÁTICA
################################################################################
# Autor: Sistema ImobiPro
# Data: Janeiro 2026
# Descrição: Instala automaticamente todas as dependências e configura
#            o ambiente do ImobiPro no Ubuntu 24.04
################################################################################

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir cabeçalhos
print_header() {
    echo -e "\n${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}\n"
}

# Função para imprimir sucesso
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para imprimir erro
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Função para imprimir aviso
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Verificar se está rodando no Ubuntu
check_os() {
    if [ ! -f /etc/os-release ]; then
        print_error "Sistema operacional não identificado"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        print_warning "Este script foi feito para Ubuntu, mas pode funcionar em outras distribuições Debian-based"
        read -p "Deseja continuar? (s/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Sistema operacional: $PRETTY_NAME"
}

# Verificar Python 3
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não encontrado"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
    return 0
}

# Instalar dependências do sistema
install_system_deps() {
    print_header "INSTALANDO DEPENDÊNCIAS DO SISTEMA"
    
    print_warning "Este processo requer permissões de administrador (sudo)"
    
    echo "Atualizando lista de pacotes..."
    sudo apt update
    
    echo -e "\nInstalando Python 3, pip e venv..."
    sudo apt install -y python3 python3-pip python3-venv
    
    if [ $? -eq 0 ]; then
        print_success "Dependências do sistema instaladas"
    else
        print_error "Erro ao instalar dependências"
        exit 1
    fi
}

# Instalar VS Code (opcional)
install_vscode() {
    print_header "INSTALAÇÃO DO VS CODE"
    
    if command -v code &> /dev/null; then
        print_success "VS Code já está instalado"
        return 0
    fi
    
    echo "O VS Code é um editor de código recomendado para trabalhar com o ImobiPro."
    read -p "Deseja instalar o VS Code? (s/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Instalando VS Code via snap..."
        sudo snap install code --classic
        
        if [ $? -eq 0 ]; then
            print_success "VS Code instalado com sucesso"
        else
            print_error "Erro ao instalar VS Code"
        fi
    else
        print_warning "VS Code não foi instalado (pode instalar depois com: sudo snap install code --classic)"
    fi
}

# Criar estrutura de diretórios
create_structure() {
    print_header "CRIANDO ESTRUTURA DE DIRETÓRIOS"
    
    PROJECT_DIR="$HOME/ImobiPro"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Diretório $PROJECT_DIR já existe"
        read -p "Deseja sobrescrever? (s/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_error "Instalação cancelada"
            exit 1
        fi
    fi
    
    echo "Criando estrutura de pastas em $PROJECT_DIR..."
    mkdir -p "$PROJECT_DIR"/{database,core,utils,templates,static/{css,js,images,uploads},backups}
    
    if [ $? -eq 0 ]; then
        print_success "Estrutura de diretórios criada em $PROJECT_DIR"
    else
        print_error "Erro ao criar estrutura de diretórios"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
}

# Criar ambiente virtual
create_venv() {
    print_header "CONFIGURANDO AMBIENTE VIRTUAL PYTHON"
    
    echo "Criando ambiente virtual (venv)..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        print_success "Ambiente virtual criado"
    else
        print_error "Erro ao criar ambiente virtual"
        exit 1
    fi
    
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    
    if [ $? -eq 0 ]; then
        print_success "Ambiente virtual ativado"
    else
        print_error "Erro ao ativar ambiente virtual"
        exit 1
    fi
}

# Instalar dependências Python
install_python_deps() {
    print_header "INSTALANDO DEPENDÊNCIAS PYTHON"
    
    echo "Atualizando pip..."
    pip install --upgrade pip
    
    echo -e "\nInstalando bibliotecas do ImobiPro..."
    pip install flask flask-login werkzeug openpyxl pillow reportlab
    
    if [ $? -eq 0 ]; then
        print_success "Dependências Python instaladas"
        
        echo -e "\nPacotes instalados:"
        pip list | grep -E "flask|werkzeug|openpyxl|pillow|reportlab"
    else
        print_error "Erro ao instalar dependências Python"
        exit 1
    fi
}

# Criar arquivo requirements.txt
create_requirements() {
    print_header "CRIANDO ARQUIVO DE DEPENDÊNCIAS"
    
    cat > requirements.txt << 'EOF'
# ImobiPro - Dependências Python
# Instalação: pip install -r requirements.txt

# Framework Web
flask>=3.0.0
flask-login>=0.6.3

# Segurança e utilitários
werkzeug>=3.0.0

# Manipulação de Excel
openpyxl>=3.1.0

# Processamento de imagens
pillow>=10.0.0

# Geração de PDFs
reportlab>=4.0.0
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Arquivo requirements.txt criado"
    else
        print_error "Erro ao criar requirements.txt"
    fi
}

# Criar script de inicialização
create_init_script() {
    print_header "CRIANDO SCRIPT DE INICIALIZAÇÃO"
    
    cat > iniciar.sh << 'EOF'
#!/bin/bash

# Script de inicialização do ImobiPro

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}===========================================${NC}"
echo -e "${GREEN}    ImobiPro - Sistema de Gestão${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Ir para o diretório do projeto
cd "$(dirname "$0")"

# Ativar ambiente virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Ambiente virtual ativado${NC}\n"
else
    echo -e "${RED}✗ Ambiente virtual não encontrado${NC}"
    exit 1
fi

# Verificar se o banco existe
if [ ! -f "database/imobipro.db" ]; then
    echo -e "${YELLOW}⚠ Banco de dados não encontrado${NC}"
    echo -e "Execute primeiro: python3 migrar_planilha.py ImobiPro.xlsx\n"
fi

# Menu
echo "Opções disponíveis:"
echo "1. Executar migração da planilha"
echo "2. Fazer backup completo"
echo "3. Abrir shell Python com banco carregado"
echo "4. Sair"
echo

read -p "Escolha uma opção: " opcao

case $opcao in
    1)
        if [ -f "ImobiPro.xlsx" ]; then
            python3 migrar_planilha.py ImobiPro.xlsx
        else
            echo -e "\n${RED}✗ Arquivo ImobiPro.xlsx não encontrado${NC}"
        fi
        ;;
    2)
        python3 utils/backup.py
        ;;
    3)
        python3 -i -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); db.connect(); print('Database manager carregado como: db')"
        ;;
    4)
        echo "Saindo..."
        ;;
    *)
        echo "Opção inválida"
        ;;
esac
EOF
    
    chmod +x iniciar.sh
    
    if [ $? -eq 0 ]; then
        print_success "Script iniciar.sh criado"
    else
        print_error "Erro ao criar script de inicialização"
    fi
}

# Criar .gitignore
create_gitignore() {
    cat > .gitignore << 'EOF'
# Python
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Banco de dados
database/*.db
database/*.db-journal

# Backups
backups/

# Uploads
static/uploads/*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db

# Dados sensíveis
*.xlsx
!ImobiPro_exemplo.xlsx
EOF
    
    print_success "Arquivo .gitignore criado"
}

# Mensagem final
show_final_message() {
    print_header "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    
    echo -e "${GREEN}O ImobiPro está pronto para uso!${NC}\n"
    
    echo "📁 Diretório do projeto:"
    echo "   $PROJECT_DIR"
    echo
    
    echo "📋 Próximos passos:"
    echo
    echo "1. Copie sua planilha ImobiPro.xlsx para:"
    echo "   $PROJECT_DIR/"
    echo
    echo "2. Entre no diretório do projeto:"
    echo "   ${YELLOW}cd $PROJECT_DIR${NC}"
    echo
    echo "3. Ative o ambiente virtual:"
    echo "   ${YELLOW}source venv/bin/activate${NC}"
    echo
    echo "4. Execute a migração dos dados:"
    echo "   ${YELLOW}python3 migrar_planilha.py ImobiPro.xlsx${NC}"
    echo
    echo "5. Ou use o script de inicialização:"
    echo "   ${YELLOW}./iniciar.sh${NC}"
    echo
    
    echo "📚 Documentação completa:"
    echo "   Veja o arquivo README.md no diretório do projeto"
    echo
    
    echo "💾 Backup:"
    echo "   Execute regularmente: ${YELLOW}python3 utils/backup.py${NC}"
    echo
    
    print_success "Instalação finalizada!"
}

################################################################################
# EXECUÇÃO PRINCIPAL
################################################################################

main() {
    clear
    
    print_header "INSTALADOR DO IMOBIPRO - SISTEMA DE GESTÃO IMOBILIÁRIA"
    
    echo "Este script irá:"
    echo "  • Verificar dependências do sistema"
    echo "  • Instalar Python 3, pip e venv"
    echo "  • Criar estrutura de diretórios"
    echo "  • Configurar ambiente virtual Python"
    echo "  • Instalar bibliotecas necessárias"
    echo "  • Criar scripts auxiliares"
    echo
    
    read -p "Deseja continuar? (s/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_error "Instalação cancelada"
        exit 1
    fi
    
    # Executar etapas
    check_os
    
    if ! check_python; then
        install_system_deps
    fi
    
    install_vscode
    create_structure
    create_venv
    install_python_deps
    create_requirements
    create_init_script
    create_gitignore
    
    show_final_message
}

# Executar
main
