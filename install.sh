#!/bin/bash

# --- Colores ---
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
echo -e "${BLUE}[*] SP3CTER Installer - Multi-Operator & Cross-Platform Mode${NC}"

# 1. Actualizar repositorios del sistema
echo -e "${GREEN}[+] Actualizando repositorios del sistema...${NC}"
sudo apt-get update -y

# 2. Instalar el compilador de C# (Para generar los implantes de Windows)
echo -e "${GREEN}[+] Instalando Mono Compiler Framework (mcs)...${NC}"
sudo apt-get install mono-mcs -y

# 3. Instalar el entorno de Go (Para generar los implantes nativos de Linux y macOS)
echo -e "${GREEN}[+] Instalando Go Compiler Framework (Golang)...${NC}"
sudo apt-get install golang -y

# 4. Instalar dependencias de Python vía APT (Evita bloqueos de entornos virtuales de PIP en Kali)
echo -e "${GREEN}[+] Instalando dependencias del Servidor vía APT...${NC}"
sudo apt-get install -y \
    python3-flask \
    python3-flask-session \
    python3-pefile \
    python3-flask-cors \
    python3-requests \
    sqlite3 \
    python3-pip

# 5. Configurar permisos de ejecución y entorno seguro
echo -e "${GREEN}[+] Configurando permisos de infraestructura...${NC}"
chmod +x app.py

# Si la base de datos ya existe, aseguramos que tenga permisos de lectura/escritura para el operador
if [ -f "zentryx_c2.db" ]; then
    chmod 664 zentryx_c2.db
fi

echo -e "------------------------------------------------------"
echo -e "${GREEN}[✔] ENTORNO MULTI-OPERADOR CONFIGURADO CON ÉXITO.${NC}"
echo -e "${BLUE}[!] Puedes iniciar el servidor de control con:${NC}"
echo -e "${CYAN}    python3 app.py <tu_password>${NC}"
echo -e "------------------------------------------------------"
