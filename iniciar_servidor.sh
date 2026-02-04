#!/bin/bash
# =====================================================
#   INICIADOR DO SERVIDOR - REFORMA/EAGLE (Linux/Mac)
# =====================================================
#   Execute este arquivo para iniciar o servidor
#   Django com túnel ngrok
# =====================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}========================================"
echo "  EAGLE - Sistema de Gestão Fiscal"
echo "  Iniciando servidor..."
echo -e "========================================${NC}"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO] Python3 não encontrado!${NC}"
    echo "Instale Python 3.10+ primeiro."
    exit 1
fi

# Diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ativa ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}[INFO] Ativando ambiente virtual (venv)...${NC}"
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo -e "${GREEN}[INFO] Ativando ambiente virtual (.venv)...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}[AVISO] Ambiente virtual não encontrado.${NC}"
    echo -e "${YELLOW}[DICA] Crie um com: python3 -m venv venv${NC}"
fi

# Verifica/instala dependências
echo ""
echo -e "${CYAN}[INFO] Verificando dependências...${NC}"
if ! python3 -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}[INFO] Instalando dependências...${NC}"
    pip install -r requirements.txt
fi

# Inicia o servidor
echo ""
echo -e "${CYAN}[INFO] Iniciando servidor com ngrok...${NC}"
echo ""
python3 iniciar_servidor.py

# Cleanup ao sair
trap "echo -e '\n${GREEN}Servidor encerrado.${NC}'" EXIT
