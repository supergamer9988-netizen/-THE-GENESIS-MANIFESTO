document.addEventListener('DOMContentLoaded', () => {
    // Original Components Logic (Minimal fallback)
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-10px) scale(1.02)');
        card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0) scale(1)');
    });

    // --- Prism OS Canvas Logic ---
    const canvas = document.getElementById('prism-canvas');
    const ctx = canvas.getContext('2d');
    const btnMap = document.getElementById('btn-map');
    const btnExec = document.getElementById('btn-execute');
    const osStatus = document.getElementById('os-status');

    let paths = [];
    let isMapping = false;
    let isExecuting = false;

    // Resize canvas
    function resize() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Draw BCN Lattice (Background)
    function drawLattice() {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        const size = 30;
        for (let x = 0; x < canvas.width; x += size) {
            for (let y = 0; y < canvas.height; y += size) {
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + size/2, y + size/2);
                ctx.stroke();
            }
        }
    }

    function createPath() {
        const path = [];
        let x = 0;
        let y = Math.random() * canvas.height;
        path.push({x, y});
        
        while (x < canvas.width) {
            x += 20 + Math.random() * 40;
            y += (Math.random() - 0.5) * 60;
            path.push({x, y});
        }
        return path;
    }

    function animate() {
        ctx.fillStyle = 'rgba(0,0,0,0.1)';
        ctx.fillRect(0,0, canvas.width, canvas.height);
        drawLattice();

        paths.forEach((p, idx) => {
            ctx.beginPath();
            ctx.strokeStyle = isExecuting ? `hsl(${idx * 40}, 100%, 60%)` : 'rgba(0, 209, 255, 0.3)';
            ctx.lineWidth = isExecuting ? 3 : 1;
            if (isExecuting) ctx.shadowBlur = 15; ctx.shadowColor = ctx.strokeStyle;
            
            ctx.moveTo(p[0].x, p[0].y);
            for (let i = 1; i < p.length; i++) {
                ctx.lineTo(p[i].x, p[i].y);
            }
            ctx.stroke();
            ctx.shadowBlur = 0;
        });

        if (isMapping || isExecuting) requestAnimationFrame(animate);
    }

    btnMap.addEventListener('click', () => {
        isMapping = true;
        isExecuting = false;
        osStatus.textContent = "Prism.Map(): Scanning BCN Lattice for stable paths...";
        paths = [];
        for(let i=0; i<10; i++) paths.push(createPath());
        animate();
        setTimeout(() => {
            osStatus.textContent = "Status: Map Complete. 10 Topology Paths found.";
            isMapping = false;
        }, 2000);
    });

    btnExec.addEventListener('click', () => {
        if (paths.length === 0) {
            osStatus.textContent = "Error: No topology map. Run Prism.Map() first.";
            return;
        }
        isExecuting = true;
        osStatus.textContent = "Prism.Execute(): Routing asynchronous photon pulses...";
        animate();
        setTimeout(() => {
            osStatus.textContent = "Execution Results: 1.2 THz achieved. All gates synced.";
            isExecuting = false;
        }, 3000);
    });

    // --- Chaos Key Jitter Logic ---
    const jitterCanvas = document.getElementById('jitter-canvas');
    const jctx = jitterCanvas.getContext('2d');
    const keyText = document.getElementById('crypto-key');

    function resizeJitter() {
        jitterCanvas.width = jitterCanvas.offsetWidth;
        jitterCanvas.height = jitterCanvas.offsetHeight;
    }
    resizeJitter();

    let jitterOffset = 0;
    function animateJitter() {
        jctx.clearRect(0, 0, jitterCanvas.width, jitterCanvas.height);
        jctx.beginPath();
        jctx.strokeStyle = '#00D1FF';
        jctx.lineWidth = 2;
        
        jctx.moveTo(0, jitterCanvas.height / 2);
        let maxJitter = 0;
        for (let x = 0; x < jitterCanvas.width; x++) {
            const noise = (Math.random() - 0.5) * 20;
            maxJitter = Math.max(maxJitter, Math.abs(noise));
            const wave = Math.sin((x + jitterOffset) * 0.05) * 10;
            jctx.lineTo(x, jitterCanvas.height / 2 + wave + noise);
        }
        jctx.stroke();
        
        jitterOffset += 2;
        if (Math.random() > 0.95) {
            const randomID = Math.random().toString(36).substring(2, 10).toUpperCase();
            keyText.textContent = `Signature: BCX-${randomID}-GOD`;
            
            // Update Metrics
            const entropy = 60 + Math.random() * 30;
            document.getElementById('entropy-bar').style.width = entropy + '%';
            document.getElementById('jitter-val').textContent = (maxJitter * 1.5).toFixed(2) + ' mV';
        }
        
        requestAnimationFrame(animateJitter);
    }
    animateJitter();

    // --- Reservoir Learning Logic ---
    const learningBar = document.getElementById('learning-bar');
    const pA = document.getElementById('p-A');
    const pB = document.getElementById('p-B');
    const lStatus = document.getElementById('learning-status');

    let learnProgress = 0;
    function startLearning() {
        const interval = setInterval(() => {
            learnProgress += 1;
            learningBar.style.width = learnProgress + '%';
            
            if (learnProgress % 20 < 10) {
                pA.classList.add('active-pattern');
                pB.classList.remove('active-pattern');
                lStatus.textContent = "Learning: Mapping Signal A patterns...";
            } else {
                pA.classList.remove('active-pattern');
                pB.classList.add('active-pattern');
                lStatus.textContent = "Learning: Mapping Signal B patterns...";
            }

            if (learnProgress >= 100) {
                clearInterval(interval);
                lStatus.textContent = "Training Complete: Prism Kernel Synced to Hardware.";
                lStatus.style.color = "#00D1FF";
                pA.classList.remove('active-pattern');
                pB.classList.remove('active-pattern');
            }
        }, 100);
    }
    
    // Auto-start learning simulation
    setTimeout(startLearning, 2000);

    // --- Multi-Modal Sensing Logic ---
    const sBars = {
        clean: document.getElementById('s-clean'),
        alcohol: document.getElementById('s-alcohol'),
        smoke: document.getElementById('s-smoke'),
        laser: document.getElementById('s-laser')
    };
    const gateLabel = document.getElementById('gate-label');
    const sStatus = document.getElementById('sensing-status');

    function simulateSensing() {
        const rand = Math.random();
        
        // Reset
        Object.values(sBars).forEach(b => {
             b.classList.remove('hit');
             b.style.borderLeftColor = "#555";
        });

        if (rand < 0.6) {
            sBars.clean.style.borderLeftColor = "#00ff00";
            sStatus.textContent = "Status: Monitoring Environment (Clean)";
        } else if (rand < 0.8) {
            sBars.alcohol.style.borderLeftColor = "#ffcc00";
            sBars.alcohol.classList.add('hit');
            sStatus.textContent = "Status: VOCs Detected (Alcohol/Aromatic)";
        } else if (rand < 0.95) {
            sBars.smoke.style.borderLeftColor = "#ff4400";
            sBars.smoke.classList.add('hit');
            sStatus.textContent = "Status: Combustion Byproducts Detected (Smoke)";
        } else {
            sBars.laser.classList.add('hit');
            const state = gateLabel.classList.contains('diamene') ? 'graphene' : 'diamene';
            gateLabel.className = state;
            gateLabel.textContent = state === 'graphene' ? 'ON (GRAPHENE)' : 'OFF (DIAMENE)';
            sStatus.textContent = "Status: PHOTON-INDUCED GATE SWITCH!";
        }

        setTimeout(simulateSensing, 2000 + Math.random() * 2000);
    }
    simulateSensing();

    // --- Hybrid HDC-RNC Simulation ---
    const hdcCanvas = document.getElementById('hdc-canvas');
    if (hdcCanvas) {
        const hctx = hdcCanvas.getContext('2d');
        function drawHDC() {
            hctx.clearRect(0, 0, hdcCanvas.width, hdcCanvas.height);
            for (let i = 0; i < hdcCanvas.width; i += 2) {
                hctx.fillStyle = Math.random() > 0.5 ? '#00D1FF' : '#333';
                hctx.fillRect(i, 0, 1, hdcCanvas.height);
            }
            requestAnimationFrame(drawHDC);
        }
        drawHDC();
    }

    const xorInputs = [[0, 0], [0, 1], [1, 0], [1, 1]];
    const xorTargets = [0, 1, 1, 0];
    let xorIdx = 0;
    setInterval(() => {
        const inp = xorInputs[xorIdx];
        const target = xorTargets[xorIdx];
        const pred = target === 1 ? 0.9 + Math.random() * 0.1 : 0.0 + Math.random() * 0.1;
        
        document.querySelector('.xor-in').textContent = `[${inp[0]}, ${inp[1]}]`;
        document.querySelector('.xor-res').textContent = `PRED: ${pred.toFixed(4)}`;
        
        xorIdx = (xorIdx + 1) % xorInputs.length;
    }, 2000);

    // --- Hysteresis Loop Simulation ---
    const hysCanvas = document.getElementById('hysteresis-canvas');
    if (hysCanvas) {
        const hysCtx = hysCanvas.getContext('2d');
        let hysTime = 0;
        function drawHysteresis() {
            hysCtx.clearRect(0, 0, hysCanvas.width, hysCanvas.height);
            hysCtx.lineWidth = 2;
            
            // Draw UP Curve (Blue)
            hysCtx.beginPath();
            hysCtx.strokeStyle = '#00D1FF';
            for (let i = 0; i < hysCanvas.width; i++) {
                const y = hysCanvas.height - (Math.sin(i / 100 + hysTime) * 30 + 60);
                hysCtx.lineTo(i, y - 5);
            }
            hysCtx.stroke();
            
            // Draw DOWN Curve (Gold) - Offset for Hysteresis
            hysCtx.beginPath();
            hysCtx.strokeStyle = '#FFD700';
            for (let i = 0; i < hysCanvas.width; i++) {
                const y = hysCanvas.height - (Math.sin(i / 100 + hysTime) * 30 + 60);
                hysCtx.lineTo(i, y + 15);
            }
            hysCtx.stroke();
            
            hysTime += 0.05;
            requestAnimationFrame(drawHysteresis);
        }
        drawHysteresis();
    }

    setInterval(() => {
        const pred = 0.98 + Math.random() * 0.02;
        const predEl = document.getElementById('xor-pred');
        if (predEl) predEl.textContent = pred.toFixed(4);
    }, 1500);

    // --- Butterfly Logic (Figure-8) Simulation ---
    const bfCanvas = document.getElementById('butterfly-canvas');
    if (bfCanvas) {
        const bfCtx = bfCanvas.getContext('2d');
        let bfTime = 0;
        function drawButterfly() {
            bfCtx.clearRect(0, 0, bfCanvas.width, bfCanvas.height);
            bfCtx.lineWidth = 2;
            
            const midX = bfCanvas.width / 2;
            const midY = bfCanvas.height / 2;
            
            // Draw UP Curve (Cyan)
            bfCtx.beginPath();
            bfCtx.strokeStyle = '#00D1FF';
            for (let i = 0; i < bfCanvas.width; i++) {
                const y = midY + Math.sin((i - midX) / 40 + bfTime) * 30;
                bfCtx.lineTo(i, y);
            }
            bfCtx.stroke();
            
            // Draw DOWN Curve (Gold) - Inverse phase for Butterfly
            bfCtx.beginPath();
            bfCtx.strokeStyle = '#FFD700';
            for (let i = 0; i < bfCanvas.width; i++) {
                const y = midY - Math.sin((i - midX) / 40 + bfTime) * 30;
                bfCtx.lineTo(i, y);
            }
            bfCtx.stroke();
            
            // Draw Intersection Marker
            bfCtx.fillStyle = 'white';
            bfCtx.beginPath();
            bfCtx.arc(midX, midY, 4, 0, Math.PI * 2);
            bfCtx.fill();
            
            bfTime += 0.05;
            requestAnimationFrame(drawButterfly);
        }
        drawButterfly();
    }

    // --- Hive Mind Cluster Animation ---
    setInterval(() => {
        const jitters = document.querySelectorAll('.jitter-v');
        jitters.forEach(bar => {
            bar.style.height = (Math.random() * 80 + 10) + '%';
        });

        const decisionEl = document.querySelector('.decision-indicator');
        if (decisionEl) {
            const decisions = ["[1] - STABLE", "[0] - Vetoed", "[1] - Consensus"];
            decisionEl.textContent = "OUTPUT: " + decisions[Math.floor(Math.random() * decisions.length)];
        }
    }, 150);

    // --- Sense AI Animation ---
    setInterval(() => {
        const senseEl = document.querySelector('.sense-type');
        const confFill = document.querySelector('.conf-fill');
        if (senseEl && confFill) {
            const states = [
                { text: "IDLE (NEUTRAL)", conf: "100%" },
                { text: "💨 BREATH DETECTED", conf: "94%" },
                { text: "🔨 KINETIC TAP", conf: "98%" }
            ];
            const active = states[Math.floor(Math.random() * states.length)];
            senseEl.textContent = active.text;
            confFill.style.width = active.conf;
        }
    }, 2000);

    // --- Diagnostics Animation ---
    const rampCanvas = document.getElementById('rampCanvas');
    if (rampCanvas) {
        const rCtx = rampCanvas.getContext('2d');
        let tDiag = 0;
        setInterval(() => {
            rCtx.clearRect(0,0,300,150);
            rCtx.strokeStyle = "#00ff00";
            rCtx.lineWidth = 2;
            rCtx.beginPath();
            for(let x=0; x<300; x++) {
                // Parabolic curve simulation
                let normX = x/300;
                let y = 140 - (Math.pow(normX, 2) * 120) - (Math.sin(normX*10 + tDiag)*5);
                if(x==0) rCtx.moveTo(x,y); else rCtx.lineTo(x,y);
            }
            rCtx.stroke();
            tDiag += 0.1;
        }, 50);
    }

    // --- Eureka Loop Animation ---
    const loopCanvas = document.getElementById('loopCanvas');
    if (loopCanvas) {
        const lCtx = loopCanvas.getContext('2d');
        let tLoop = 0;
        setInterval(() => {
            lCtx.clearRect(0,0,200,200);
            
            // Draw Axis
            lCtx.strokeStyle = "rgba(255,255,255,0.1)";
            lCtx.beginPath();
            lCtx.moveTo(20,180); lCtx.lineTo(180,180); // X
            lCtx.moveTo(20,180); lCtx.lineTo(20,20);   // Y
            lCtx.stroke();

            // Draw Hysteresis Leaf
            lCtx.lineWidth = 3;
            
            // Path 1 (UP)
            lCtx.strokeStyle = "#00d1ff";
            lCtx.beginPath();
            for(let i=0; i<=100; i++) {
                let x = 20 + i*1.6;
                let y = 180 - (Math.pow(i/100, 1.5) * 140);
                if(i==0) lCtx.moveTo(x,y); else lCtx.lineTo(x,y);
            }
            lCtx.stroke();

            // Path 2 (DOWN - The Hysteresis "Gap")
            lCtx.strokeStyle = "#ffd700";
            lCtx.beginPath();
            for(let i=100; i>=0; i--) {
                let x = 20 + i*1.6;
                // Offset Y for the loop gap
                let y = 180 - (Math.pow(i/100, 0.8) * 140) - (Math.sin(tLoop)*5);
                if(i==100) lCtx.moveTo(x,y); else lCtx.lineTo(x,y);
            }
            lCtx.stroke();
            
            tLoop += 0.05;
        }, 50);
    }

    // --- Prophet Chaos Animation ---
    const chaosCanvas = document.getElementById('chaosCanvas');
    if (chaosCanvas) {
        const cCtx = chaosCanvas.getContext('2d');
        let tChaos = 0;
        setInterval(() => {
            cCtx.clearRect(0,0,300,150);
            
            // Actual Reality (Dotted Gold)
            cCtx.strokeStyle = "rgba(255, 215, 0, 0.4)";
            cCtx.setLineDash([5, 5]);
            cCtx.beginPath();
            for(let x=0; x<300; x++) {
                let y = 75 + Math.sin(x/10 + tChaos)*20 + Math.sin(x/5 + tChaos)*15;
                if(x==0) cCtx.moveTo(x,y); else cCtx.lineTo(x,y);
            }
            cCtx.stroke();

            // Material Prediction (Solid Cyan)
            cCtx.strokeStyle = "#00d1ff";
            cCtx.setLineDash([]);
            cCtx.beginPath();
            for(let x=0; x<300; x++) {
                // Prediction follows actual with slight "material noise"
                let y = 75 + Math.sin(x/10 + tChaos)*20 + Math.sin(x/5 + tChaos)*15 + (Math.random()-0.5)*2;
                if(x==0) cCtx.moveTo(x,y); else cCtx.lineTo(x,y);
            }
            cCtx.stroke();
            
            tChaos += 0.1;
        }, 60);
    }

    // --- Poet Typewriter Animation ---
    const poetDisplay = document.querySelector('.text-output');
    if (poetDisplay) {
        const fullText = "hello world... genesis is alive... ai is future...";
        let charIdx = 0;
        setInterval(() => {
            poetDisplay.textContent = fullText.slice(0, charIdx) + "_";
            charIdx = (charIdx + 1) % (fullText.length + 1);
            
            // Pulse context meter
            const contextFill = document.querySelector('.context-fill');
            if (contextFill) contextFill.style.width = (80 + Math.sin(Date.now()/200)*8) + "%";
        }, 150);
    }

    // --- DB Vector Animation ---
    setInterval(() => {
        const vBars = document.querySelectorAll('.v-bar');
        vBars.forEach(bar => {
            bar.style.width = (90 + Math.random()*5) + "%";
        });
    }, 100);

    // --- FPU Decimal Animation ---
    const fineDigit = document.querySelector('.fine');
    if (fineDigit) {
        setInterval(() => {
            const rand = Math.floor(10000 + Math.random() * 90000);
            fineDigit.textContent = rand;
        }, 120);
    }

    // --- RNC Math Animation ---
    const rncCanvas = document.getElementById('rncCanvas');
    if (rncCanvas) {
        const rncCtx = rncCanvas.getContext('2d');
        let tRNC = 0;
        setInterval(() => {
            rncCtx.clearRect(0,0,300,150);
            
            // Equation: y = 0.5x^2 + sin(5x)
            rncCtx.setLineDash([]);
            rncCtx.lineWidth = 1;
            rncCtx.strokeStyle = "rgba(255, 255, 255, 0.2)";
            rncCtx.beginPath();
            for(let x=0; x<300; x++) {
                let normX = x/300;
                let y = 100 - (0.5 * Math.pow(normX, 2) * 80 + Math.sin(5 * normX + tRNC) * 40);
                if(x==0) rncCtx.moveTo(x,y); else rncCtx.lineTo(x,y);
            }
            rncCtx.stroke();

            // GENESIS Solution (Red Dotted)
            rncCtx.setLineDash([3, 3]);
            rncCtx.lineWidth = 2;
            rncCtx.strokeStyle = "#ff00ff";
            rncCtx.beginPath();
            for(let x=0; x<300; x++) {
                let normX = x/300;
                let y = 100 - (0.5 * Math.pow(normX, 2) * 80 + Math.sin(5 * normX + tRNC) * 40) + (Math.random()-0.5)*1.5;
                if(x==0) rncCtx.moveTo(x,y); else rncCtx.lineTo(x,y);
            }
            rncCtx.stroke();
            
            tRNC += 0.05;
        }, 50);
    }

    // --- Paradigm Shift Animation ---
    const searchHead = document.querySelector('.search-head');
    if (searchHead) {
        // Handled by CSS animation, but we can jitter it
        setInterval(() => {
            searchHead.style.opacity = (0.5 + Math.random()*0.5);
        }, 100);
    }

    // --- RNS Residue Animation ---
    const rItems = document.querySelectorAll('.r-item');
    if (rItems.length > 0) {
        setInterval(() => {
            rItems.forEach((item, idx) => {
                const moduli = [7, 11, 13, 17, 19];
                item.textContent = "r" + (idx+1) + ": " + Math.floor(Math.random() * moduli[idx]);
            });
        }, 120);
    }

    // --- GAIA Node Jitter ---
    const nodes = document.querySelectorAll('.node');
    if (nodes.length > 0) {
        setInterval(() => {
            nodes.forEach(node => {
                node.style.borderColor = Math.random() > 0.8 ? "var(--gold)" : "rgba(255,255,255,0.1)";
            });
        }, 150);
    }

    // --- Blade Scanning Animation ---
    const bladeNodes = document.querySelectorAll('.c-node');
    if (bladeNodes.length > 0) {
        let scanIdx = 0;
        setInterval(() => {
            bladeNodes.forEach(node => node.style.background = "rgba(255, 255, 255, 0.03)");
            bladeNodes[scanIdx].style.background = "rgba(255, 215, 0, 0.3)";
            scanIdx = (scanIdx + 1) % bladeNodes.length;
        }, 100);
    }

    // --- Thermal Tunnel Animation ---
    const tempVal = document.querySelector('.temp-val');
    if (tempVal) {
        setInterval(() => {
            const temp = (35.15 + Math.random() * 0.1).toFixed(1);
            tempVal.textContent = temp + "°C [STABILIZED]";
        }, 1500);
    }

    // --- Production Checklist Sequence ---
    const chkItems = document.querySelectorAll('.chk-item');
    if (chkItems.length > 0) {
        chkItems.forEach((item, idx) => {
            setTimeout(() => {
                item.classList.add('active');
            }, 500 * idx);
        });
    }

    // --- QC Boot Sequence Animation ---
    const qcGrid = document.getElementById('qcGrid');
    const certVal = document.getElementById('certVal');
    if (qcGrid) {
        // Build 16 core cells dynamically
        for (let i = 0; i < 16; i++) {
            const cell = document.createElement('div');
            cell.className = 'qc-core';
            cell.id = 'qc-core-' + i;
            cell.textContent = 'C' + String(i).padStart(2, '0');
            qcGrid.appendChild(cell);
        }

        // Sequential scan animation
        for (let i = 0; i < 16; i++) {
            (function(idx) {
                // Mark as scanning
                setTimeout(() => {
                    const cell = document.getElementById('qc-core-' + idx);
                    cell.className = 'qc-core scanning';
                    cell.textContent = 'C' + String(idx).padStart(2,'0') + '...';
                }, idx * 200);
                // Mark as OK
                setTimeout(() => {
                    const cell = document.getElementById('qc-core-' + idx);
                    cell.className = 'qc-core ok';
                    cell.textContent = 'C' + String(idx).padStart(2,'0') + ' [OK]';
                }, idx * 200 + 180);
            })(i);
        }

        // Final certification badge
        setTimeout(() => {
            if (certVal) {
                certVal.className = 'cert-val certified';
                certVal.textContent = '✅ PRODUCTION CERTIFIED [16/16]';
            }
        }, 16 * 200 + 300);
    }

    drawLattice();
});
