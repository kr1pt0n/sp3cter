<div align="center">
  <br />
      <img src="https://i.ibb.co/F4YdsHZX/Chat-GPT-Image-15-jun-2026-02-03-43-p-m.png" alt="Project Banner">
  <br />

 <div>
    <img src="https://img.shields.io/badge/-Python-black?style=for-the-badge&logoColor=white&logo=python&color=3776AB" alt="python" />
    <img src="https://img.shields.io/badge/-Flask-black?style=for-the-badge&logoColor=white&logo=flask&color=000000" alt="flask" />
    <img src="https://img.shields.io/badge/-C%23-black?style=for-the-badge&logoColor=white&logo=c-sharp&color=239120" alt="csharp" />
    <img src="https://img.shields.io/badge/-Mono-black?style=for-the-badge&logoColor=white&logo=mono&color=6E4AFF" alt="mono" />
    <img src="https://img.shields.io/badge/-Windows-black?style=for-the-badge&logoColor=white&logo=windows&color=0078D6" alt="windows" />
  </div>

  <h3 align="center">SP3CTER</h3>

   <div align="center">
     Lightweight Command & Control framework desarrollado para entornos de laboratorio, simulaciones de Red Team y ejercicios de seguridad autorizados. Incluye generación dinámica de agentes .NET, manipulación de metadatos PE, panel web interactivo y gestión centralizada de operaciones.
   </div>
</div>

---

## Características

### Servidor C2 Core

* Backend Flask ligero y rápido.
* Autenticación dinámica mediante contraseña definida al iniciar el servidor.
* Gestión de sesiones seguras.
* Base de datos SQLite integrada.

### Generador de Beacons

* Generación dinámica de agentes Windows en C#.
* Compilación automática mediante Mono Compiler.
* Compatible con Kali Linux, Parrot OS y Ubuntu 24.04.

### PE Metadata Cloning

* Clonado automático de metadatos PE.
* Uso de plantillas legítimas para replicar información descriptiva del binario.
* Soporte para múltiples firmas incluidas en la carpeta `signatures`.

### Bloating Engine

* Inserción automática de junk data.
* Modificación del tamaño final del ejecutable.
* Personalización del nivel de inflado del binario.

### Panel Aqua

* Dashboard moderno y responsivo.
* Gestión centralizada de agentes.
* Ejecución remota de tareas.
* Visualización de resultados en tiempo real.

### File Operations

* Descarga de archivos desde agentes conectados.
* Gestión de resultados desde la interfaz web.

### Multi-Platform Build Environment

* Kali Linux
* Parrot OS
* Ubuntu 24.04 LTS

---

## Instalación

### Kali Linux / Parrot OS

```bash
git clone https://github.com/kr1pt0n/sp3cter.git
cd sp3cter
chmod +x install.sh
sudo ./install.sh
```

### Ubuntu 24.04

```bash
git clone https://github.com/kr1pt0n/sp3cter.git
cd sp3cter
chmod +x install-ubuntu.sh
sudo ./install-ubuntu.sh
```

El instalador configurará automáticamente:

* Python 3
* Flask
* Requests
* SQLite
* Mono Complete
* Mono Compiler (mcs)
* Dependencias necesarias para la compilación de agentes

---

## Ejecución

```bash
python3 app.py mi_password_secreta!$
```

```text
   _____ ____  _____   ______ ______ ______ ____ 
  / ___// __ \|__  /  / ____//_  __// ____// __ \
  \__ \/ /_/ / /_ <  / /      / /  / __/  / /_/ /
 ___/ / ____/___/ / / /___   / /  / /___ / _, _/
/____/_/    /____/  \____/  /_/  /_____//_/ |_|

      >> Shadow Command & Control System <<

[*] Sp3cter C2 Core: ONLINE
[*] Password Set: *********************
[*] Listen: http://0.0.0.0:5000
```

Abrir:

```text
http://IP_DEL_SERVIDOR:5000
```

---

## Estructura

```text
sp3cter/
│
├── app.py
├── install.sh
├── install-ubuntu.sh
│
├── signatures/
│   ├── chr.exe
│   ├── fox.exe
│   └── ...
│
├── assets/
│   ├── login.png
│   ├── dashboard.png
│   └── banner.png
│
├── templates/
│   ├── login.html
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── zentryx_c2.db
└── README.md
```

---

## Capturas

Totalmente personalizable:

<img src="https://i.ibb.co/pvN9PrHk/dashboard.png" alt="Project Banner">
<img src="https://i.ibb.co/0j2nWkSK/login.png" alt="Project Banner">

---

## Aviso Legal

Este software ha sido desarrollado exclusivamente con fines educativos, investigación en ciberseguridad y ejercicios de seguridad autorizados.

El uso de esta herramienta contra sistemas, redes o dispositivos sin autorización expresa puede constituir una infracción legal. El desarrollador no asume responsabilidad alguna por el uso indebido de este software.

---

## Developed by ALLPA-SEC Team
