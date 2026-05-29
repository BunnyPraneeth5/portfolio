// ═══════════════════════════════════════
// AOS INITIALIZATION (Bypassed dynamically for cinematic reveals)
// ═══════════════════════════════════════
try {
    AOS.init({
        duration: 1200,
        easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
        once: true,
        mirror: false
    });
} catch(e) {}

// ═══════════════════════════════════════
// MOBILE MENU TOGGLE
// ═══════════════════════════════════════
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        const icon = mobileMenuToggle.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    });
}

document.querySelectorAll('#mobileMenu a').forEach(link => {
    link.addEventListener('click', () => {
        if (!mobileMenuToggle || !mobileMenu) return;
        mobileMenu.classList.remove('active');
        const icon = mobileMenuToggle.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    });
});

// ── FORCE CINEMATIC DARK MODE ──
document.body.classList.add('dark-mode');
localStorage.setItem('darkMode', 'true');

// ═══════════════════════════════════════
// DOM CONTENT LOADED & PREMIUM INTERACTION
// ═══════════════════════════════════════
let convergenceBoost = 1.0; // Environmental speed boost factor

document.addEventListener('DOMContentLoaded', () => {

    // ── ACTIVE NAVIGATION STATE SYNC ──
    const activeChapter = document.body.dataset.chapter || 'home';
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && (href.includes(activeChapter) || (activeChapter === 'home' && (href.includes('index') || href === '/')))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // ── CURSOR GLOW CREATION ──
    let cursorGlow = document.getElementById('cursor-glow');
    if (!cursorGlow) {
        cursorGlow = document.createElement('div');
        cursorGlow.id = 'cursor-glow';
        document.body.appendChild(cursorGlow);
    }
    document.addEventListener('mousemove', (e) => {
        cursorGlow.style.left = (e.clientX - 150) + 'px';
        cursorGlow.style.top = (e.clientY - 150) + 'px';
    });

    // ── HIGH-TECH RETICLE MICRO-CURSOR SYSTEM ──
    if (window.matchMedia('(pointer: fine)').matches) {
        let dot = document.querySelector('.custom-cursor-dot');
        if (!dot) {
            dot = document.createElement('div');
            dot.className = 'custom-cursor-dot';
            document.body.appendChild(dot);
        }
        let ring = document.querySelector('.custom-cursor-ring');
        if (!ring) {
            ring = document.createElement('div');
            ring.className = 'custom-cursor-ring';
            document.body.appendChild(ring);
        }

        let mouseX = 0, mouseY = 0;
        let ringX = 0, ringY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            dot.style.left = mouseX + 'px';
            dot.style.top = mouseY + 'px';
        });

        function animateCustomCursor() {
            ringX += (mouseX - ringX) * 0.12;
            ringY += (mouseY - ringY) * 0.12;
            ring.style.left = ringX + 'px';
            ring.style.top = ringY + 'px';
            requestAnimationFrame(animateCustomCursor);
        }
        animateCustomCursor();

        // Snap cursors to interactive elements
        const interactives = 'a, button, input, textarea, .glass-card, .skill-card, .project-card';
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest(interactives)) {
                dot.classList.add('cursor-hover');
                ring.classList.add('cursor-hover');
            }
        });
        document.addEventListener('mouseout', (e) => {
            if (!e.target.closest(interactives)) {
                dot.classList.remove('cursor-hover');
                ring.classList.remove('cursor-hover');
            }
        });
    }

    // ── SPOTLIGHT TRACKER & INTERACTIVE CARD COORDINATES ──
    document.addEventListener('mousemove', (e) => {
        const card = e.target.closest('.glass-card, .skill-card, .project-card');
        if (card) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        }
    });

    // ── OVERRIDE AOS WITH TACTILE DEPTH EMERGENCE ──
    document.querySelectorAll('[data-aos]').forEach(el => {
        el.removeAttribute('data-aos');
        el.classList.add('reveal');
    });

    // ── REVEAL SYSTEM OBSERVER ──
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.05 });

    document.querySelectorAll('.reveal, .chapter-label').forEach(el => {
        revealObserver.observe(el);
    });

    // ── HERO MULTI-ROLE TYPING CAROUSEL (Safely scoped to Home template only) ──
    const textSpan = document.getElementById('typewriter');
    if (textSpan) {
        // Check if there is an inline typewriter script already configured/running
        const hasInlineTypewriter = Array.from(document.querySelectorAll('script')).some(script => 
            script.textContent && script.textContent.includes('typewriter_phrases')
        );
        if (!hasInlineTypewriter) {
            const roles = [
                'AI Engineer',
                'Machine Learning Explorer',
                'Full-Stack Developer',
                'Security Researcher'
            ];
            
            let roleIdx = 0;
            let charIdx = 0;
            let isDeleting = false;
            let speed = 80;

            function playTypewriter() {
                const current = roles[roleIdx];
                if (isDeleting) {
                    textSpan.textContent = current.substring(0, charIdx - 1);
                    charIdx--;
                    speed = 40;
                } else {
                    textSpan.textContent = current.substring(0, charIdx + 1);
                    charIdx++;
                    speed = 80;
                }

                if (!isDeleting && charIdx === current.length) {
                    isDeleting = true;
                    speed = 2000;
                } else if (isDeleting && charIdx === 0) {
                    isDeleting = false;
                    roleIdx = (roleIdx + 1) % roles.length;
                    speed = 500;
                }

                setTimeout(playTypewriter, speed);
            }
            
            setTimeout(playTypewriter, 1000);
        }
    }

    // ── AUDIO SYSTEM GESTURED INITIATOR ──
    const soundBtn = document.createElement('button');
    soundBtn.id = 'cinematicSoundToggle';
    soundBtn.className = 'cinematic-sound-toggle';
    
    // Set initial text based on localStorage preference
    const audioPref = localStorage.getItem('audioPreferred');
    if (audioPref === 'on') {
        soundBtn.textContent = '♪ AUDIO ON';
        soundBtn.classList.add('active');
    } else {
        soundBtn.textContent = '♪ AUDIO OFF';
        soundBtn.classList.remove('active');
    }
    
    document.body.appendChild(soundBtn);

    const triggerEvents = ['click', 'scroll', 'touchstart', 'keydown'];
    const handleGesture = () => {
        // Respect explicit user setting to stay off
        if (localStorage.getItem('audioPreferred') === 'off') {
            triggerEvents.forEach(evt => document.removeEventListener(evt, handleGesture));
            return;
        }
        if (!audioInitialized) {
            initAudio();
        } else if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
            soundBtn.textContent = '♪ AUDIO ON';
            soundBtn.classList.add('active');
            localStorage.setItem('audioPreferred', 'on');
        }
        triggerEvents.forEach(evt => document.removeEventListener(evt, handleGesture));
    };

    // Only register gesture listener if the user hasn't explicitly muted it
    if (audioPref !== 'off') {
        triggerEvents.forEach(evt => document.addEventListener(evt, handleGesture, { once: true, passive: true }));
    }

    soundBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!audioInitialized) {
            localStorage.setItem('audioPreferred', 'on');
            initAudio();
        } else if (audioCtx) {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
                soundBtn.textContent = '♪ AUDIO ON';
                soundBtn.classList.add('active');
                localStorage.setItem('audioPreferred', 'on');
            } else if (audioCtx.state === 'running') {
                audioCtx.suspend();
                soundBtn.textContent = '♪ AUDIO OFF';
                soundBtn.classList.remove('active');
                localStorage.setItem('audioPreferred', 'off');
            }
        }
    });

    // ── FOCUS ACKNOWLEDGEMENT (Convergence Response) ──
    document.querySelectorAll('form input, form textarea').forEach(el => {
        el.addEventListener('focus', () => {
            convergenceBoost = 2.5; // Boost particle stream on focus
        });
        el.addEventListener('blur', () => {
            convergenceBoost = 1.0;
        });
    });

    // ── ANCHOR SMOOTH SCROLL ──
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = this.getAttribute('href');
            if (!target || target === '#') return;
            const targetElement = document.querySelector(target);
            if (!targetElement) return;
            e.preventDefault();
            targetElement.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // ── CINEMATIC CAMERA CUTS (PAGE TRANSITIONS) ──
    const portal = document.createElement('div');
    portal.className = 'page-transition-portal';
    document.body.appendChild(portal);

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (event) => {
            const href = link.getAttribute('href');
            const target = link.getAttribute('target');
            if (!href || href.startsWith('#') || href.toLowerCase().startsWith('http')) return;
            if (target === '_blank' || link.hasAttribute('download')) return;
            if (/^(mailto:|tel:|javascript:)/i.test(href)) return;
            
            const destination = new URL(href, window.location.href);
            if (destination.origin !== window.location.origin || destination.href === window.location.href) return;
            
            event.preventDefault();
            document.body.classList.add('page-transition-out');
            setTimeout(() => { window.location.href = destination.href; }, 750);
        });
    });

    // ── START 3D SYSTEM ──
    init3DEngine();

}); // end DOMContentLoaded

// ═══════════════════════════════════════
// PROCEDURAL SPACETIME SOUNDSCAPE SYNTHESIZER
// ═══════════════════════════════════════
let audioCtx = null;
let masterGain = null;
let organicDrone1 = null;
let swellOsc1 = null, swellOsc2 = null, swellLfo = null;
let shimmerOsc = null, shimmerReverb = null;
let tremoloOsc = null;
let audioInitialized = false;

function generateReverb(audioCtx, duration = 8, decay = 4) {
    const sampleRate = audioCtx.sampleRate;
    const length = sampleRate * duration;
    const buffer = audioCtx.createBuffer(2, length, sampleRate);
    for (let channel = 0; channel < 2; channel++) {
        const data = buffer.getChannelData(channel);
        for (let i = 0; i < length; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
        }
    }
    return buffer;
}

function initAudio() {
    if (audioInitialized) return;
    audioInitialized = true;

    try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContextClass();
        
        masterGain = audioCtx.createGain();
        masterGain.gain.setValueAtTime(0, audioCtx.currentTime);
        masterGain.gain.linearRampToValueAtTime(0.18, audioCtx.currentTime + 4.0);
        
        // Deep Organ Drone C1 - 32.7 Hz
        const droneOsc = audioCtx.createOscillator();
        droneOsc.type = 'sine';
        droneOsc.frequency.setValueAtTime(32.7, audioCtx.currentTime);
        
        const droneGain = audioCtx.createGain();
        droneGain.gain.setValueAtTime(0.35, audioCtx.currentTime);
        
        const lowpass = audioCtx.createBiquadFilter();
        lowpass.type = 'lowpass';
        lowpass.frequency.setValueAtTime(100, audioCtx.currentTime);
        
        droneOsc.connect(droneGain);
        droneGain.connect(lowpass);
        lowpass.connect(masterGain);
        droneOsc.start();
        organicDrone1 = droneOsc;

        // Swelling harmonical perfect fifth C2 (65.4 Hz) & G2 (98 Hz)
        const swell1 = audioCtx.createOscillator();
        swell1.type = 'sine';
        swell1.frequency.setValueAtTime(65.4, audioCtx.currentTime);

        const swell2 = audioCtx.createOscillator();
        swell2.type = 'sine';
        swell2.frequency.setValueAtTime(98.0, audioCtx.currentTime);

        const swellGain1 = audioCtx.createGain();
        swellGain1.gain.setValueAtTime(0.12, audioCtx.currentTime);

        const swellGain2 = audioCtx.createGain();
        swellGain2.gain.setValueAtTime(0.12, audioCtx.currentTime);

        // Swelling Gain LFO (0.04 Hz, depth 0.05)
        const lfo = audioCtx.createOscillator();
        lfo.type = 'sine';
        lfo.frequency.setValueAtTime(0.04, audioCtx.currentTime);

        const lfoGain = audioCtx.createGain();
        lfoGain.gain.setValueAtTime(0.05, audioCtx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(swellGain1.gain);
        lfoGain.connect(swellGain2.gain);

        swell1.connect(swellGain1);
        swell2.connect(swellGain2);
        swellGain1.connect(masterGain);
        swellGain2.connect(masterGain);

        swell1.start();
        swell2.start();
        lfo.start();

        swellOsc1 = swell1;
        swellOsc2 = swell2;
        swellLfo = lfo;

        // High shimmer C4 - 261.6 Hz
        const shimmer = audioCtx.createOscillator();
        shimmer.type = 'sine';
        shimmer.frequency.setValueAtTime(261.6, audioCtx.currentTime);

        const shimmerGain = audioCtx.createGain();
        shimmerGain.gain.setValueAtTime(0.03, audioCtx.currentTime);

        const reverb = audioCtx.createConvolver();
        reverb.buffer = generateReverb(audioCtx, 8, 4);

        shimmer.connect(shimmerGain);
        shimmerGain.connect(reverb);
        reverb.connect(masterGain);
        shimmer.start();

        shimmerOsc = shimmer;
        shimmerReverb = reverb;

        // Heartbeat Tremolo (0.2 Hz, depth 0.015)
        const tremolo = audioCtx.createOscillator();
        tremolo.type = 'sine';
        tremolo.frequency.setValueAtTime(0.2, audioCtx.currentTime);

        const tremoloGain = audioCtx.createGain();
        tremoloGain.gain.setValueAtTime(0.015, audioCtx.currentTime);

        tremolo.connect(tremoloGain);
        tremoloGain.connect(masterGain.gain);
        tremolo.start();

        tremoloOsc = tremolo;

        masterGain.connect(audioCtx.destination);

        const soundToggleBtn = document.getElementById('cinematicSoundToggle');
        if (soundToggleBtn) {
            soundToggleBtn.textContent = '♪ AUDIO ON';
            soundToggleBtn.classList.add('active');
        }
    } catch (err) {
        console.warn('Web Audio API initialized with blocks:', err);
    }
}

// ═══════════════════════════════════════
// DYNAMIC COMPOSER SCRIPT LOADER CORE
// ═══════════════════════════════════════
const cdnScripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js'
];

function loadScriptsSequentially(urls, callback) {
    let index = 0;
    function loadNext() {
        if (index >= urls.length) {
            callback();
            return;
        }
        const url = urls[index];
        if (url.includes('three.min.js') && window.THREE) {
            index++;
            loadNext();
            return;
        }
        const script = document.createElement('script');
        script.src = url;
        script.onload = () => {
            index++;
            loadNext();
        };
        script.onerror = () => {
            console.warn('Failed to load CDN module: ' + url + ', continuing anyway.');
            index++;
            loadNext();
        };
        document.head.appendChild(script);
    }
    loadNext();
}

function loadThreeJS(callback) {
    loadScriptsSequentially(cdnScripts, callback);
}

// ═══════════════════════════════════════
// UNIFIED 3D ATMOSPHERIC BLOOM ENGINE
// ═══════════════════════════════════════
function init3DEngine() {
    const container = document.getElementById('particles-container');
    if (!container) return;

    container.innerHTML = '';
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    loadThreeJS(() => {
        if (!window.THREE) {
            console.warn('Three.js or dependencies failed to load. Falling back to 2D.');
            return;
        }
        try {
            const width = container.offsetWidth;
            const height = container.offsetHeight;

            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x020408, 0.08);

            const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
            camera.position.set(0, 0, 8.0);

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer.domElement);

            // Volumetric Light Shafts (Spotlights target cursor)
            const spotlight1 = new THREE.SpotLight(0x4dd0e1, 7.0, 30, Math.PI / 4, 0.9, 1.2);
            spotlight1.position.set(-6, 12, 4);
            scene.add(spotlight1);
            scene.add(spotlight1.target); // Essential for manual coordinate follow

            const spotlight2 = new THREE.SpotLight(0xc9a84c, 4.0, 30, Math.PI / 3, 0.7, 1.0);
            spotlight2.position.set(6, 12, -2);
            scene.add(spotlight2);
            scene.add(spotlight2.target);

            const ambLight = new THREE.AmbientLight(0x050a12, 1.2);
            scene.add(ambLight);

            // ── SECTION 1 (HOME) — Drifting lens bokeh / Volumetric Dust Haze ──
            function createSoftParticleTexture() {
                const canvas = document.createElement('canvas');
                canvas.width = 16;
                canvas.height = 16;
                const ctx = canvas.getContext('2d');
                const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
                grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
                grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 16, 16);
                return new THREE.CanvasTexture(canvas);
            }

            const dustCount = 350; // Drastically reduced from 1500 to avoid a galaxy/starfield dense look
            const dustGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(dustCount * 3);
            const dustData = [];
            for (let i = 0; i < dustCount; i++) {
                const x = (Math.random() - 0.5) * 18;
                const y = (Math.random() - 0.5) * 14;
                const z = (Math.random() - 0.5) * 16;
                positions[i*3] = x;
                positions[i*3+1] = y;
                positions[i*3+2] = z;

                dustData.push({
                    x, y, z,
                    speedY: 0.0015 + Math.random() * 0.002, // Slower lazy drift speed
                    speedX: (Math.random() - 0.5) * 0.0006,
                    amplitude: 0.1 + Math.random() * 0.15,
                    time: Math.random() * 100
                });
            }
            dustGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const dustMat = new THREE.PointsMaterial({
                color: 0x8ba0b8,
                size: 0.24, // Volumetric, defocused lens bokeh dots
                transparent: true,
                opacity: 0.15, // Extremely subtle
                blending: THREE.NormalBlending, // Normal blending to prevent glowing space starfield effect
                map: createSoftParticleTexture(),
                depthWrite: false
            });
            const dustPoints = new THREE.Points(dustGeo, dustMat);
            scene.add(dustPoints);

            // DISTANT COLOSSAL STRUCTURAL SHADOW (Home scale suggestion)
            const scaleStructure = new THREE.Mesh(
                new THREE.TorusGeometry(8.0, 0.15, 8, 32),
                new THREE.MeshStandardMaterial({
                    color: 0x03060c,
                    roughness: 0.95,
                    metalness: 0.1,
                    transparent: true,
                    opacity: 0.15
                })
            );
            scaleStructure.position.set(0, 0, -18);
            scene.add(scaleStructure);

            // ── SECTION 2 (ABOUT) — Monolithic Corridor ──
            const monolithicCorridor = new THREE.Group();
            const pillarGeo = new THREE.BoxGeometry(0.8, 12, 0.8);
            const pillarMat = new THREE.MeshStandardMaterial({
                color: 0x03060b,
                roughness: 0.9,
                metalness: 0.15,
                flatShading: true
            });

            for (let i = 0; i < 8; i++) {
                const zPos = -i * 4.0;
                const pLeft = new THREE.Mesh(pillarGeo, pillarMat);
                pLeft.position.set(-3.2, -2, zPos);
                monolithicCorridor.add(pLeft);

                const pRight = new THREE.Mesh(pillarGeo, pillarMat);
                pRight.position.set(3.2, -2, zPos);
                monolithicCorridor.add(pRight);

                const arch = new THREE.Mesh(new THREE.BoxGeometry(7.2, 0.5, 0.5), pillarMat);
                arch.position.set(0, 4, zPos);
                monolithicCorridor.add(arch);
            }
            scene.add(monolithicCorridor);
            monolithicCorridor.position.set(0, 0, -100);

            // ── SECTION 3 (SKILLS) — Floating Geometric frameworks ──
            const constructGroup = new THREE.Group();
            const gridMat = new THREE.MeshStandardMaterial({
                color: 0x4dd0e1,
                roughness: 0.2,
                metalness: 0.9,
                wireframe: true
            });
            
            const mainConstruct = new THREE.Mesh(new THREE.BoxGeometry(2.0, 2.0, 2.0), gridMat);
            constructGroup.add(mainConstruct);

            const plat1 = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.08, 1.6), new THREE.MeshStandardMaterial({
                color: 0x050a12,
                roughness: 0.3,
                metalness: 0.8
            }));
            plat1.position.y = 1.2;
            constructGroup.add(plat1);

            const plat2 = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.08, 1.6), new THREE.MeshStandardMaterial({
                color: 0x050a12,
                roughness: 0.3,
                metalness: 0.8
            }));
            plat2.position.y = -1.2;
            plat2.rotation.y = Math.PI / 2;
            constructGroup.add(plat2);

            scene.add(constructGroup);
            constructGroup.position.set(0, 0, -100);

            // ── SECTION 4 (PROJECTS) — Recursive Reflections Mirror World ──
            const projectsMirrorWorld = new THREE.Group();
            const mirrorMat = new THREE.MeshStandardMaterial({
                color: 0xc9a84c,
                roughness: 0.08,
                metalness: 0.98,
                flatShading: true
            });

            const corePrism = new THREE.Mesh(new THREE.OctahedronGeometry(1.5, 0), mirrorMat);
            projectsMirrorWorld.add(corePrism);

            const reflectiveRingMat = new THREE.MeshStandardMaterial({
                color: 0x4dd0e1,
                roughness: 0.1,
                metalness: 0.95,
                wireframe: true
            });

            for (let i = 0; i < 6; i++) {
                const ring = new THREE.Mesh(new THREE.TorusGeometry(2.2 + i * 0.6, 0.03, 8, 4), reflectiveRingMat);
                ring.rotation.z = i * Math.PI / 8;
                projectsMirrorWorld.add(ring);
            }

            scene.add(projectsMirrorWorld);
            projectsMirrorWorld.position.set(0, 0, -100);

            // ── SECTION 5 (BLOG) — Floating Memory Cells ──
            const archiveGroup = new THREE.Group();
            const prisms = [];
            const prismCount = 8;
            const prismGeo = new THREE.OctahedronGeometry(0.48, 0);
            const crystalMat = new THREE.MeshStandardMaterial({
                color: 0x8ba0b8,
                roughness: 0.05,
                metalness: 0.95,
                transparent: true,
                opacity: 0.8
            });

            for (let i = 0; i < prismCount; i++) {
                const angle = (i / prismCount) * Math.PI * 2;
                const radius = 3.4;
                const prism = new THREE.Mesh(prismGeo, crystalMat);
                const px = Math.cos(angle) * radius;
                const py = (Math.random() - 0.5) * 1.2;
                const pz = Math.sin(angle) * radius;
                prism.position.set(px, py, pz);
                archiveGroup.add(prism);
                prisms.push({ mesh: prism, angle, radius, py });
            }
            scene.add(archiveGroup);
            archiveGroup.position.set(0, 0, -100);

            // ── SIGNATURE MOTIF: THE GUIDING STREAM ──
            const streamParticleCount = 280;
            const streamGeo = new THREE.BufferGeometry();
            const streamPositions = new Float32Array(streamParticleCount * 3);
            const streamParticlesData = [];

            function getStreamPoint(t, chapter, index) {
                let p = new THREE.Vector3();
                if (chapter === 'home') {
                    p.set(
                        Math.sin(t * Math.PI * 2.0) * 0.12,
                        Math.cos(t * Math.PI * 2.0) * 0.12,
                        5.0 - t * 10.0
                    );
                } 
                else if (chapter === 'about') {
                    p.set(
                        Math.sin(t * Math.PI * 2.8) * 1.5,
                        Math.cos(t * Math.PI * 1.8) * 0.7,
                        3.5 - t * 11.0
                    );
                } 
                else if (chapter === 'skills') {
                    const branchId = index % 3;
                    const offsetAngle = branchId * (Math.PI * 2 / 3);
                    const splitStart = 0.28;
                    const spread = t > splitStart ? (t - splitStart) * 2.4 : 0;
                    p.set(
                        Math.cos(offsetAngle) * spread + Math.sin(t * Math.PI) * 0.3,
                        Math.sin(offsetAngle) * spread,
                        3.5 - t * 9.5
                    );
                } 
                else if (chapter === 'projects') {
                    const angle = t * Math.PI * 6.0;
                    p.set(
                        Math.sin(angle) * (1.6 + Math.cos(angle * 0.5)),
                        Math.cos(angle) * (1.6 + Math.cos(angle * 0.5)),
                        1.8 - t * 7.5
                    );
                } 
                else if (chapter === 'blog') {
                    const wave = Math.sin(t * Math.PI * 4.0 + index) * 0.75;
                    p.set(
                        wave,
                        Math.cos(t * Math.PI * 2.0 + index) * 0.75,
                        2.8 - t * 7.5
                    );
                } 
                else if (chapter === 'contact') {
                    const streamId = index % 6;
                    const startAngle = streamId * (Math.PI * 2 / 6);
                    const radius = 5.5 * (1.0 - t);
                    p.set(
                        Math.cos(startAngle) * radius,
                        Math.sin(startAngle) * radius + Math.sin(t * Math.PI) * 0.6,
                        -10.0 + t * 13.0
                    );
                }
                return p;
            }

            for (let i = 0; i < streamParticleCount; i++) {
                const t = Math.random();
                const p = getStreamPoint(t, 'home', i);
                streamPositions[i*3] = p.x;
                streamPositions[i*3+1] = p.y;
                streamPositions[i*3+2] = p.z;

                streamParticlesData.push({
                    t,
                    speed: 0.0035 + Math.random() * 0.002,
                    wiggleTime: Math.random() * 50
                });
            }

            streamGeo.setAttribute('position', new THREE.BufferAttribute(streamPositions, 3));
            const streamMat = new THREE.PointsMaterial({
                color: 0x4dd0e1,
                size: 0.048,
                transparent: true,
                opacity: 0.85,
                blending: THREE.AdditiveBlending
            });
            const streamPoints = new THREE.Points(streamGeo, streamMat);
            scene.add(streamPoints);

            // ── VOLUMETRIC POST-PROCESSING COMPOSER SETUP ──
            let composer;
            if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
                const renderPass = new THREE.RenderPass(scene, camera);
                const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(width, height), 1.5, 0.4, 0.85);
                bloomPass.threshold = 0.15;
                bloomPass.strength = 1.0;
                bloomPass.radius = 0.65;

                composer = new THREE.EffectComposer(renderer);
                composer.addPass(renderPass);
                composer.addPass(bloomPass);
            }

            // Mouse Parallax
            let mouseX = 0, mouseY = 0;
            document.addEventListener('mousemove', (e) => {
                mouseX = (e.clientX - width / 2) * 0.0002;
                mouseY = (e.clientY - height / 2) * 0.0002;
            });

            // Resize
            window.addEventListener('resize', () => {
                const w = container.offsetWidth;
                const h = container.offsetHeight;
                camera.aspect = w / h;
                camera.updateProjectionMatrix();
                renderer.setSize(w, h);
                if (composer) {
                    composer.setSize(w, h);
                }
            });

            // Register global hover listener on skill-cards for physical material response
            let activeSkillHover = 0;
            document.addEventListener('mouseover', (e) => {
                if (e.target.closest('.skill-card')) {
                    activeSkillHover = 1.0;
                }
            });
            document.addEventListener('mouseout', (e) => {
                if (e.target.closest('.skill-card')) {
                    activeSkillHover = 0;
                }
            });

            // ── AUDIO SYSTEM NAV INTEGRATION (Critical Issue 8) ──
            // Inject audio toggle directly inside the floating nav utility bar
            const navActions = document.querySelector('nav .flex.items-center.space-x-4');
            if (navActions) {
                navActions.insertBefore(soundBtn, navActions.firstChild);
            } else {
                document.body.appendChild(soundBtn);
            }

            // Animation Loop
            let lastDraw = 0;
            const clock = new THREE.Clock();

            function animate(timestamp) {
                requestAnimationFrame(animate);

                if (timestamp - lastDraw < 16) return; // Cap at ~60fps
                lastDraw = timestamp;

                const time = clock.getElapsedTime();
                const chapter = document.body.dataset.chapter || 'home';

                // ── UNIQUE PAGE IDENTITIES: ATMOSPHERIC INTERPOLATION (Critical Issue 6) ──
                let targetFogDensity = 0.08;
                let targetAmbLight = 0.8;
                let targetSpot1Intensity = 6.0;
                let targetSpot2Intensity = 3.0;
                let targetStreamSpeed = 0.0035;

                if (chapter === 'home') {
                    targetFogDensity = 0.045; // Minimal, open, spacious void
                    targetAmbLight = 1.0;
                    targetSpot1Intensity = 4.0;
                    targetSpot2Intensity = 2.0;
                    targetStreamSpeed = 0.0022; // Solitary stream beginning
                } else if (chapter === 'about') {
                    targetFogDensity = 0.095; // Intimate, dense revealing fog corridor
                    targetAmbLight = 0.45; // High contrast
                    targetSpot1Intensity = 8.0;
                    targetSpot2Intensity = 2.0;
                    targetStreamSpeed = 0.0032;
                } else if (chapter === 'skills') {
                    targetFogDensity = 0.07; // Interconnected structured frameworks
                    targetAmbLight = 0.7;
                    targetSpot1Intensity = 6.0;
                    targetSpot2Intensity = 4.0;
                    targetStreamSpeed = 0.0038;
                } else if (chapter === 'projects') {
                    targetFogDensity = 0.055; // Mirror world reflective clarity
                    targetAmbLight = 0.95; // Bright ambitious spotlighting
                    targetSpot1Intensity = 9.0;
                    targetSpot2Intensity = 5.0;
                    targetStreamSpeed = 0.0048;
                } else if (chapter === 'blog') {
                    targetFogDensity = 0.085; // Calmer reflection
                    targetAmbLight = 0.55; // Thoughtful dimness
                    targetSpot1Intensity = 3.0;
                    targetSpot2Intensity = 1.5;
                    targetStreamSpeed = 0.0018; // Meditative, preserved ideas
                } else if (chapter === 'contact') {
                    targetFogDensity = 0.115; // Dense focal convergence resolution
                    targetAmbLight = 0.5;
                    targetSpot1Intensity = 7.0;
                    targetSpot2Intensity = 3.0;
                    targetStreamSpeed = 0.006;
                }

                // Smooth linear interpolation (lerp) toward target parameters (Environment as silent character)
                scene.fog.density += (targetFogDensity - scene.fog.density) * 0.05;
                ambLight.intensity += (targetAmbLight - ambLight.intensity) * 0.05;
                spotlight1.intensity += (targetSpot1Intensity - spotlight1.intensity) * 0.05;
                spotlight2.intensity += (targetSpot2Intensity - spotlight2.intensity) * 0.05;

                // Parallax camera easing
                camera.position.x += (mouseX - camera.position.x) * 0.05;
                camera.position.y += (-mouseY - camera.position.y) * 0.05;
                camera.lookAt(scene.position);

                // VOLUMETRIC LIGHT FOLLOW CURSOR (Interactive Spotlights)
                spotlight1.target.position.set(mouseX * 12, -mouseY * 8, 0);
                spotlight1.target.updateMatrixWorld();

                // 1. DUST SYSTEM ANIMATION (Soft drifting lens bokeh particles)
                const posArr = dustPoints.geometry.attributes.position.array;
                const speedFactor = targetStreamSpeed / 0.0035; // Drifts slower/faster depending on chapter mood
                for (let i = 0; i < dustCount; i++) {
                    const data = dustData[i];
                    data.time += 0.03 * speedFactor;
                    data.y += data.speedY * speedFactor;
                    data.x += Math.sin(data.time) * data.speedX * data.amplitude * speedFactor;

                    if (data.y > 7) data.y = -7;
                    posArr[i*3] = data.x;
                    posArr[i*3+1] = data.y;
                }
                dustPoints.geometry.attributes.position.needsUpdate = true;

                // 2. THE GUIDING STREAM MORPHING ENGINE (Physical 3D curve interpolation - Critical Issue 7)
                const streamPosArr = streamPoints.geometry.attributes.position.array;
                for (let i = 0; i < streamParticleCount; i++) {
                    const data = streamParticlesData[i];
                    
                    // Respect section dynamic stream speed targets
                    const sectionSpeed = targetStreamSpeed * (1.0 + Math.random() * 0.2);
                    data.t += sectionSpeed * convergenceBoost;
                    data.wiggleTime += 0.08;

                    if (data.t > 1.0) data.t = 0;

                    const targetPos = getStreamPoint(data.t, chapter, i);
                    
                    const wiggleX = Math.sin(data.wiggleTime) * 0.08;
                    const wiggleY = Math.cos(data.wiggleTime) * 0.08;

                    const px = streamPosArr[i*3];
                    const py = streamPosArr[i*3+1];
                    const pz = streamPosArr[i*3+2];

                    streamPosArr[i*3] += (targetPos.x + wiggleX - px) * 0.08;
                    streamPosArr[i*3+1] += (targetPos.y + wiggleY - py) * 0.08;
                    streamPosArr[i*3+2] += (targetPos.z - pz) * 0.08;
                }
                streamPoints.geometry.attributes.position.needsUpdate = true;

                // Shift Guiding Stream color dynamically based on active page narrative
                if (chapter === 'home') {
                    streamMat.color.setHex(0x4dd0e1); // Cyan beginning
                } else if (chapter === 'about') {
                    streamMat.color.setHex(0xc9a84c); // Warm copper-gold connection
                } else if (chapter === 'skills') {
                    streamMat.color.setHex(0x4dd0e1); // Cyan branching paths
                } else if (chapter === 'projects') {
                    streamMat.color.setHex(0xc9a84c); // Complex copper loops
                } else if (chapter === 'blog') {
                    streamMat.color.setHex(0x8ba0b8); // Silver reflective trails
                } else if (chapter === 'contact') {
                    streamMat.color.setHex(0x4dd0e1); // Intense converging cyan
                }

                // 3. BACKGROUND ARCHITECTURAL ROUTING (80% Storytelling / 20% Architecture balance)
                const transitionSpeed = 0.06;
                
                if (chapter === 'home') {
                    monolithicCorridor.position.z += (-100 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (-100 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (-100 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (-100 - archiveGroup.position.z) * transitionSpeed;
                } 
                else if (chapter === 'about') {
                    monolithicCorridor.position.z += (-6.0 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (-100 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (-100 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (-100 - archiveGroup.position.z) * transitionSpeed;

                    // Discovery Scroll Travel: Slide monolithic columns slowly past the lens
                    const scrollProgress = window.pageYOffset / (document.documentElement.scrollHeight - window.innerHeight || 1);
                    monolithicCorridor.position.z = -6.0 + scrollProgress * 15.0;
                } 
                else if (chapter === 'skills') {
                    monolithicCorridor.position.z += (-100 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (2.2 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (-100 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (-100 - archiveGroup.position.z) * transitionSpeed;

                    // Capabilities become structure: float rotation
                    constructGroup.rotation.x = Math.sin(time * 0.25) * 0.15;
                    plat1.rotation.y = -time * 0.15;
                    plat2.rotation.y = time * 0.15;

                    // MEMORABLE SKILL MOMENT: Tilt structured grid group smoothly on skill hover event
                    const targetTiltY = activeSkillHover * 0.35;
                    constructGroup.rotation.y += (targetTiltY + time * 0.1 - constructGroup.rotation.y) * 0.06;
                } 
                else if (chapter === 'projects') {
                    monolithicCorridor.position.z += (-100 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (-100 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (2.0 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (-100 - archiveGroup.position.z) * transitionSpeed;

                    // Ambitious mirror loop orbits
                    projectsMirrorWorld.rotation.y = time * 0.06;
                    projectsMirrorWorld.rotation.x = Math.sin(time * 0.12) * 0.1;
                    corePrism.rotation.z = -time * 0.12;
                } 
                else if (chapter === 'blog') {
                    monolithicCorridor.position.z += (-100 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (-100 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (-100 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (1.8 - archiveGroup.position.z) * transitionSpeed;

                    // MEMORABLE REFLECTION MOMENT: Crystalline prisms (memory cells) breathe, rotate, and pulse
                    archiveGroup.rotation.y = time * 0.03;
                    prisms.forEach((p, idx) => {
                        p.mesh.rotation.x += 0.006;
                        p.mesh.rotation.y += 0.009;
                        p.mesh.position.y = p.py + Math.sin(time * 1.2 + idx) * 0.06;

                        // Soft pulser representing breathing stored memory nodes (Lanterns in haze)
                        const pulseScale = 0.5 + Math.sin(time * 1.5 + idx) * 0.5;
                        p.mesh.material.opacity = 0.3 + pulseScale * 0.5;
                    });
                } 
                else if (chapter === 'contact') {
                    monolithicCorridor.position.z += (-100 - monolithicCorridor.position.z) * transitionSpeed;
                    constructGroup.position.z += (-100 - constructGroup.position.z) * transitionSpeed;
                    projectsMirrorWorld.position.z += (-100 - projectsMirrorWorld.position.z) * transitionSpeed;
                    archiveGroup.position.z += (-100 - archiveGroup.position.z) * transitionSpeed;
                }

                if (composer) {
                    composer.render();
                } else {
                    renderer.render(scene, camera);
                }
            }

            animate(0);
        } catch (e) {
            console.error('3D Atmospheric engine failed to initialize:', e);
        }
    });
}
// ═══════════════════════════════════════
// END OF CINEMATIC BLOOM ENGINE
// ═══════════════════════════════════════
