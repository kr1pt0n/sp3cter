<div align="center">
  <br />
      <img src="https://raw.githubusercontent.com/kr1pt0n/sp3cter/refs/heads/main/assets/banner.png" alt="Project Banner">
    </a>
  <br />

 <div>
    <img src="https://img.shields.io/badge/-Python-black?style=for-the-badge&logoColor=white&logo=python&color=3776AB" alt="python" />
    <img src="https://img.shields.io/badge/-Flask-black?style=for-the-badge&logoColor=white&logo=flask&color=000000" alt="flask" />
    <img src="https://img.shields.io/badge/-C%23-black?style=for-the-badge&logoColor=white&logo=c-sharp&color=239120" alt="csharp" />
    <img src="https://img.shields.io/badge/-Windows-black?style=for-the-badge&logoColor=white&logo=windows&color=0078D6" alt="windows" />
  </div>

  <h3 align="center">SP3CTER</h3>

   <div align="center">
     SP3CTER es un Framework C2 ligero y potente diseñado para operaciones de Red Team, cuenta con un sistema de generación de beacons con técnicas de evasión y clonado de firmas.
    </div>
</div>

## Características

- **Servidor C2 Core**
  - Basado en Flask con autenticación dinámica por contraseña (operación en memoria).

- **Generador de Beacons**
  - Compilación dinámica de agentes en C# (.NET).

- **PE Signature Hijacking**
  - Capacidad de clonar certificados digitales de ejecutables legítimos para evadir motores de detección.
    
- **Técnica de Bloating**
  - Inyección de datos basura (junk data) para inflar el tamaño del binario y saltar escaneos rápidos de antivirus.

- **Panel de Control Aqua**
  - Interfaz web interactiva para la gestión de múltiples agentes, ejecución de comandos remotos y recepción de resultados.
    
- **Exfiltración de Datos**
  - Soporte nativo para descarga de archivos desde el host objetivo directamente al panel de control.

---

## Instalación (Kali Linux / Parrot OS)

Este proyecto está optimizado para distribuciones de seguridad. El instalador automático configurará el compilador Mono y todas las dependencias necesarias de Python:

### Setup

```bash
git clone https://github.com/kr1pt0n/sp3cter.git
cd sp3cter
chmod +x install.sh
sudo ./install.sh
[*] SP3CTER Installer - Kali/Parrot OS Mode
[+] Actualizando repositorios...
[+] Instalar Mono Compiler (mcs)...
[+] Instalando dependencias de Python vía APT...
[+] Configurando permisos para app.py...
------------------------------------------------------
[✔] SP3CTER LISTO PARA OPERAR.
[!] Ejecuta el C2 con:
    python3 app.py <tu_password>

```

---

## Ejecución

```bash
python3 app.py mi_password_secreta!$
   _____ ____  _____   ______ ______ ______ ____ 
  / ___// __ \|__  /  / ____//_  __// ____// __ \
  \__ \/ /_/ / /_ <  / /      / /  / __/  / /_/ /
 ___/ / ____/___/ / / /___   / /  / /___ / _, _/ 
/____/_/    /____/  \____/  /_/  /_____//_/ |_|  
                                                  
      >> Shadow Command & Control System <<

[*] Sp3cter C2 Core: ONLINE
[*] Password Set: *********************
[*] Listen: http://0.0.0.0:5000

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.X:5000
Press CTRL+C to quit
```

Abrir en navegador:

```text
http://localhost:5000
```

---

## Estructura

```text
sp3cter/
│
├── app.py
├── install.sh
├── signatures/
│   ├── chr.exe
│   └── fox.exe
├── assets/
│   ├── login.png
│   ├── dashboard.png
│   └── banner.png
├── templates/
│   ├── index.html
│   └── login.html
└── README.md
```

---

## Capturas

Totalmente personalizable - Estilo Dark Aqua :

<img src="https://raw.githubusercontent.com/kr1pt0n/sp3cter/refs/heads/main/assets/login.png" alt="Project Banner">
<img src="https://raw.githubusercontent.com/kr1pt0n/sp3cter/refs/heads/main/assets/dashboard.png" alt="Project Banner">
---

Aviso Legal

Este software ha sido creado con fines exclusivamente educativos y para pruebas de penetración autorizadas. El uso de SP3CTER contra objetivos sin consentimiento previo es ilegal y está penado por la ley. El desarrollador no se hace responsable del mal uso de esta herramienta.

---

## Developed by ALLPA-SEC Team 
