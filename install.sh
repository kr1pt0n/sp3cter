#!/bin/bash

GREEN='\033[1;32m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "    _____ ____  _____   ______ ______ ______ ____  "
echo "   / ___// __ \|__  /  / ____//_  __// ____// __ \ "
echo "   \__ \/ /_/ / /_ <  / /      / /  / __/  / /_/ / "
echo "  ___/ / ____/___/ / / /___   / /  / /___ / _, _/  "
echo " /____/_/    /____/  \____/  /_/  /_____//_/ |_|   "
echo "                                                   "
echo -e "${NC}"
echo -e "${BLUE}[*] SP3CTER Installer - Kali/Parrot OS Mode${NC}"

echo -e "${GREEN}[+] Actualizando repositorios...${NC}"
sudo apt-get update -y

echo -e "${GREEN}[+] Instalar Mono Compiler (mcs)...${NC}"
sudo apt-get install mono-mcs -y

echo -e "${GREEN}[+] Instalando dependencias de Python vía APT...${NC}"
sudo apt-get install -y \
    python3-flask \
    python3-flask-session \
    python3-pefile \
    python3-requests

echo -e "${GREEN}[+] Configurando permisos para app.py...${NC}"
chmod +x app.py

echo -e "------------------------------------------------------"
echo -e "${GREEN}[✔] SP3CTER LISTO PARA OPERAR.${NC}"
echo -e "${BLUE}[!] Ejecuta el C2 con:${NC}"
echo -e "${CYAN}    python3 app.py <tu_password>${NC}"
echo -e "------------------------------------------------------"
