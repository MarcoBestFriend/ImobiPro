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
