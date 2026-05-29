// ═══════════════════════════════════════
// AOS INITIALIZATION
// ═══════════════════════════════════════
AOS.init({
    duration: 900,
    easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
    once: true,
    mirror: false,
    offset: 80,
    anchorPlacement: 'top-bottom'
});

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

// ═══════════════════════════════════════
// DARK MODE MANAGEMENT
// ═══════════════════════════════════════
function updateDarkMode(isDark) {
    const icon = darkModeToggle.querySelector('i');
    const body = document.body;

    if (isDark) {
        body.classList.add('dark-mode');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        body.classList.remove('dark-mode');
        icon.classList.add('fa-moon');
        icon.classList.remove('fa-sun');
    }

    localStorage.setItem('darkMode', isDark);

    const ripple = document.createElement('span');
    ripple.style.cssText = `
        position: absolute; top: 50%; left: 50%;
        width: 40px; height: 40px;
        background: rgba(59, 130, 246, 0.3);
        border-radius: 50%; pointer-events: none;
        transform: translate(-50%, -50%) scale(0);
        animation: ripple 0.6s ease-out;
    `;
    darkModeToggle.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
}

if (!document.querySelector('#ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = '@keyframes ripple { to { transform: translate(-50%, -50%) scale(2); opacity: 0; } }';
    document.head.appendChild(style);
}

const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', (e) => {
        e.preventDefault();
        const isDark = !document.body.classList.contains('dark-mode');
        darkModeToggle.style.transform = 'scale(0.95) rotate(15deg)';
        setTimeout(() => {
            darkModeToggle.style.transform = 'scale(1) rotate(0deg)';
        }, 200);
        updateDarkMode(isDark);
    });
}

// ═══════════════════════════════════════
// SKILLS DATA
// ═══════════════════════════════════════
const skills = [
    {
        category: 'Agentic AI & MCP',
        items: [
            { name: 'MCP / Agentic AI', level: 85, icon: 'fas fa-robot' },
            { name: 'N8N Automation', level: 75, icon: 'fas fa-project-diagram' },
        ]
    },
    {
        category: 'ML & Data',
        items: [
            { name: 'Scikit-Learn', level: 90, icon: 'fas fa-chart-line' },
            { name: 'Pandas / NumPy', level: 90, icon: 'fas fa-table' },
            { name: 'TensorFlow', level: 80, icon: 'fas fa-brain' },
        ]
    },
    {
        category: 'Web & APIs',
        items: [
            { name: 'Django / DRF', level: 82, icon: 'fab fa-python' },
            { name: 'FastAPI', level: 82, icon: 'fas fa-bolt' },
            { name: 'HTML/CSS', level: 90, icon: 'fab fa-html5' }
        ]
    },
    {
        category: 'Languages',
        items: [
            { name: 'Python', level: 90, icon: 'fab fa-python' },
            { name: 'SQL', level: 85, icon: 'fas fa-database' }
        ]
    },
    {
        category: 'Security',
        items: [
            { name: 'SOC L1 / SIEM', level: 75, icon: 'fas fa-shield-alt' },
            { name: 'Threat Intelligence', level: 70, icon: 'fas fa-search' }
        ]
    },
    {
        category: 'Tools',
        items: [
            { name: 'Git & GitHub', level: 90, icon: 'fab fa-git-alt' },
            { name: 'PyQt6', level: 75, icon: 'fas fa-desktop' },
            { name: 'Jupyter', level: 88, icon: 'fas fa-book' }
        ]
    }
];

// ═══════════════════════════════════════
// PROJECTS DATA
// ═══════════════════════════════════════
const projects = [
    {
        title: 'College Gate Pass System',
        description: 'A secure, web-based system using QR code authentication to manage student passes.',
        link: 'https://github.com/BunnyPraneeth5/college-gate-pass',
        tags: ['Django', 'QR Code', 'Security'],
        image: 'path-to-image.jpg',
        features: ['QR Code Authentication', 'Real-time Tracking', 'Secure Database']
    },
    {
        title: 'Car Sales Price Prediction',
        description: 'Neural network built using TensorFlow that predicts car prices with 88% accuracy.',
        link: 'https://github.com/BunnyPraneeth5/car-price-prediction',
        liveDemo: 'https://car-price-predictor-demo.herokuapp.com',
        tags: ['TensorFlow', 'Machine Learning', 'Python'],
        image: 'path-to-image.jpg',
        features: ['Neural Network Model', 'Data Analysis', 'Price Prediction']
    },
    {
        title: 'AI-Generated Fitness Website',
        description: 'A futuristic fitness UI built using v0.dev and AI tools — backend API integration coming soon.',
        link: '#',
        tags: ['AI', 'Web Design', 'Fitness'],
        image: 'path-to-image.jpg',
        features: ['AI Integration', 'Modern UI', 'Fitness Tracking']
    }
];

// ═══════════════════════════════════════
// DOM CONTENT LOADED
// ═══════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {

    // ── FLOATING ORBS ──
    const orbClasses = ['orb orb-1', 'orb orb-2', 'orb orb-3'];
    orbClasses.forEach(cls => {
        const orb = document.createElement('div');
        orb.className = cls;
        document.body.prepend(orb);
    });

    // ── HERO AVATAR ROTATING RING ──
    const heroImg = document.querySelector('main img.rounded-full');
    if (heroImg) {
        heroImg.classList.add('hero-profile-img');
        const wrapper = document.createElement('div');
        wrapper.className = 'hero-avatar';
        heroImg.parentNode.insertBefore(wrapper, heroImg);
        wrapper.appendChild(heroImg);
    }

    // ── HERO TEXT ENTRANCE ──
    document.querySelectorAll('main .max-w-4xl > *').forEach(el => {
        el.classList.add('hero-entrance');
    });

    // Legacy hero profile image class
    const heroProfileImage = document.querySelector('main img');
    if (heroProfileImage) {
        heroProfileImage.classList.add('hero-profile-img');
    }

    // ── PAGE TRANSITION FOR INTERNAL LINKS (SCREEN WIPE) ──
    const pageWipe = document.createElement('div');
    pageWipe.className = 'page-transition-overlay';
    document.body.appendChild(pageWipe);

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
            setTimeout(() => { window.location.href = destination.href; }, 450);
        });
    });

    // ── DARK MODE INIT ──
    const savedDarkMode = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedDarkMode === 'true' || (savedDarkMode === null && prefersDark);
    document.body.style.transition = 'none';
    updateDarkMode(shouldBeDark);
    setTimeout(() => {
        document.body.style.transition = 'background 0.6s cubic-bezier(0.4, 0, 0.2, 1), color 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    }, 100);

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (localStorage.getItem('darkMode') === null) {
            updateDarkMode(e.matches);
        }
    });

    // ── AOS RE-INIT ──
    AOS.init({
        duration: 900,
        easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
        once: true,
        mirror: false,
        offset: 80,
        anchorPlacement: 'top-bottom'
    });

    // ── PARTICLES.JS ──
    if (document.querySelector('.particles-container') && window.particlesJS) {
        particlesJS('particles-container', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: document.body.classList.contains('dark-mode') ? '#60a5fa' : '#3b82f6' },
                shape: { type: 'circle' },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: document.body.classList.contains('dark-mode') ? '#60a5fa' : '#3b82f6',
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: true,
                    straight: false,
                    out_mode: 'out',
                    bounce: false
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: { enable: true, mode: 'grab' },
                    onclick: { enable: true, mode: 'push' },
                    resize: true
                }
            },
            retina_detect: true
        });
    }

    // ── SKILLS & PROJECTS ──
    const skillsContainer = document.querySelector('#skills .grid');
    const projectsContainer = document.querySelector('#projects .grid');

    if (skillsContainer) {
        renderSkills();
        const skillObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.querySelectorAll('.skill-progress').forEach((bar, i) => {
                        const level = bar.getAttribute('data-level');
                        setTimeout(() => {
                            bar.style.width = `${level}%`;
                        }, 200 + i * 150);
                    });
                }
            });
        }, { threshold: 0.2 });
        document.querySelectorAll('.skill-card').forEach(card => {
            skillObserver.observe(card);
        });
    }

    if (projectsContainer) {
        renderProjects();
    }

    // ── PAGE LOAD ANIMATION ──
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(1.02)';
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transform = 'scale(1)';
    }, 100);

    // ── NAV SHRINK ON SCROLL ──
    const navElement = document.querySelector('nav');
    if (navElement) {
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            if (currentScroll > 50) {
                navElement.classList.add('nav-scrolled');
            } else {
                navElement.classList.remove('nav-scrolled');
            }
            lastScroll = currentScroll;
        }, { passive: true });
    }

    // ── MICRO-CURSOR SYSTEM (DESKTOP ONLY) ──
    if (window.matchMedia('(pointer: fine)').matches) {
        const dot = document.createElement('div');
        dot.className = 'custom-cursor-dot';
        const ring = document.createElement('div');
        ring.className = 'custom-cursor-ring';
        document.body.appendChild(dot);
        document.body.appendChild(ring);

        let mouseX = 0, mouseY = 0;
        let ringX = 0, ringY = 0;
        let hideTimer = null;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            // Move the small dot instantly
            dot.style.left = mouseX + 'px';
            dot.style.top = mouseY + 'px';

            dot.style.opacity = '1';
            ring.style.opacity = '1';

            if (hideTimer) clearTimeout(hideTimer);
            hideTimer = setTimeout(() => {
                dot.style.opacity = '0';
                ring.style.opacity = '0';
            }, 3000);
        });

        // Lerping loop for smooth outer ring motion
        function animateCustomCursor() {
            const ease = 0.15;
            ringX += (mouseX - ringX) * ease;
            ringY += (mouseY - ringY) * ease;
            ring.style.left = ringX + 'px';
            ring.style.top = ringY + 'px';
            requestAnimationFrame(animateCustomCursor);
        }
        animateCustomCursor();

        document.addEventListener('mouseleave', () => {
            dot.style.opacity = '0';
            ring.style.opacity = '0';
        });

        // Hover expansions using dynamic delegation
        const interactives = 'a, button, .glass-card, .skill-card, .project-card, input, textarea, [role="button"]';
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

    // ── SPOTLIGHT TRACKER FOR PREMIUM CARDS ──
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

    // ── REVEAL-UP INTERSECTION OBSERVER ──
    const revealUpObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                revealUpObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -60px 0px'
    });

    document.querySelectorAll('.reveal-up').forEach(el => {
        revealUpObserver.observe(el);
    });

    // ── SECTION HEADING ANIMATED UNDERLINES ──
    const headingObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const line = entry.target.querySelector('.section-heading-line');
                if (line) line.classList.add('animate');
                headingObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('h2').forEach(h2 => {
        headingObserver.observe(h2.closest('[data-aos]') || h2);
    });

    // ── 3D TILT EFFECT ON GLASS CARDS (DESKTOP) ──
    if (window.matchMedia('(pointer: fine)').matches) {
        document.querySelectorAll('.glass-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = ((y - centerY) / centerY) * -5;
                const rotateY = ((x - centerX) / centerX) * 5;
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(${parseInt(getComputedStyle(document.documentElement).getPropertyValue('--card-hover-lift') || '-8')}px) scale(1.015)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
    }

    // ── ANIMATED STAT COUNTERS ──
    const statObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const text = el.textContent.trim();
                const match = text.match(/(\d+\.?\d*)/);
                if (match) {
                    const target = parseFloat(match[1]);
                    const suffix = text.replace(match[0], '');
                    const isDecimal = text.includes('.');
                    const duration = 1800;
                    const startTime = performance.now();

                    function updateCount(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const eased = 1 - Math.pow(1 - progress, 4); // Quartic ease out
                        const current = target * eased;
                        el.textContent = (isDecimal ? current.toFixed(1) : Math.floor(current)) + suffix;
                        if (progress < 1) requestAnimationFrame(updateCount);
                    }
                    requestAnimationFrame(updateCount);
                }
                statObserver.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.text-3xl.font-bold[class*="Orbitron"]').forEach(el => {
        statObserver.observe(el);
    });

    // ── SMOOTH PARALLAX ON HERO (DESKTOP) ──
    const heroSection = document.querySelector('main.min-h-screen');
    if (heroSection && window.matchMedia('(pointer: fine)').matches) {
        window.addEventListener('scroll', () => {
            const scroll = window.scrollY;
            if (scroll < window.innerHeight) {
                const opacity = 1 - (scroll / window.innerHeight) * 0.45;
                const translateY = scroll * 0.18;
                heroSection.style.opacity = opacity;
                heroSection.style.transform = `translateY(${translateY}px)`;
            }
        }, { passive: true });
    }

    // ── MAGNETIC BUTTONS & SOCIAL LINKS ──
    if (window.matchMedia('(pointer: fine)').matches) {
        const magnetics = document.querySelectorAll('.social-icon, a[class*="text-gray-400"], a[class*="rounded-full"], button[id="darkModeToggle"]');
        magnetics.forEach(el => {
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                el.style.transform = `translate(${x * 0.28}px, ${y * 0.28}px) scale(1.06)`;
                el.style.transition = 'transform 0.08s ease-out';
            });
            el.addEventListener('mouseleave', () => {
                el.style.transform = '';
                el.style.transition = 'transform 0.5s cubic-bezier(0.22, 1, 0.36, 1)';
            });
        });
    }

    // ── HERO MULTI-ROLE TYPING CAROUSEL ──
    const heroSub = document.querySelector('main p.text-xl');
    if (heroSub) {
        heroSub.innerHTML = '<span class="typewriter-text"></span><span class="typewriter-cursor">|</span>';
        const textSpan = heroSub.querySelector('.typewriter-text');
        
        const roles = [
            'Machine Learning Engineer & Full-Stack Developer',
            'Agentic AI & MCP Automation Developer',
            'Secure QR Authentication Engineer',
            'Data Science & Predictive Analytics Modeler'
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
                speed = 35; // faster deletion
            } else {
                textSpan.textContent = current.substring(0, charIdx + 1);
                charIdx++;
                speed = 70; // natural typing cadence
            }

            if (!isDeleting && charIdx === current.length) {
                isDeleting = true;
                speed = 2200; // lingering pause at full title
            } else if (isDeleting && charIdx === 0) {
                isDeleting = false;
                roleIdx = (roleIdx + 1) % roles.length;
                speed = 600; // brief pause before starting new title
            }

            setTimeout(playTypewriter, speed);
        }
        
        setTimeout(playTypewriter, 1200);
    }

}); // end DOMContentLoaded

// ═══════════════════════════════════════
// RENDER SKILLS
// ═══════════════════════════════════════
function renderSkills() {
    const skillsContainer = document.querySelector('#skills .grid');
    if (!skillsContainer) return;
    skillsContainer.innerHTML = '';
    skills.forEach((skill, index) => {
        const skillCard = document.createElement('div');
        skillCard.className = 'skill-card reveal';
        skillCard.setAttribute('data-aos', 'fade-up');
        skillCard.setAttribute('data-aos-delay', `${index * 100}`);
        skillCard.innerHTML = `
            <h3 class="text-xl font-['Orbitron'] mb-4">${skill.category}</h3>
            <div class="space-y-4">
                ${skill.items.map(item => `
                    <div class="skill-item">
                        <div class="flex items-center justify-between mb-1">
                            <div class="flex items-center space-x-2">
                                <i class="${item.icon} text-blue-400"></i>
                                <span class="text-gray-300">${item.name}</span>
                            </div>
                            <span class="text-blue-400">${item.level}%</span>
                        </div>
                        <div class="w-full bg-gray-700 rounded-full h-2.5">
                            <div class="skill-progress bg-gradient-to-r from-blue-500 to-purple-600 h-2.5 rounded-full"
                                 style="width: 0%"
                                 data-level="${item.level}">
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        skillsContainer.appendChild(skillCard);
    });
}

// ═══════════════════════════════════════
// RENDER PROJECTS
// ═══════════════════════════════════════
function renderProjects() {
    const projectsContainer = document.querySelector('#projects .grid');
    if (!projectsContainer) return;
    projectsContainer.innerHTML = '';
    projects.forEach((project, index) => {
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card reveal';
        projectCard.setAttribute('data-aos', 'fade-up');
        projectCard.setAttribute('data-aos-delay', `${index * 100}`);
        projectCard.innerHTML = `
            <div class="p-6">
                <h3 class="text-xl font-['Orbitron'] mb-2">${project.title}</h3>
                <p class="text-gray-300 mb-4">${project.description}</p>
                <div class="mb-4">
                    <h4 class="text-sm font-semibold text-gray-400 mb-2">Features:</h4>
                    <ul class="list-disc list-inside text-gray-300 text-sm space-y-1">
                        ${project.features.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                </div>
                <div class="flex flex-wrap gap-2 mb-4">
                    ${project.tags.map(tag => `
                        <span class="px-2 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs">${tag}</span>
                    `).join('')}
                </div>
                <div class="flex gap-4">
                    <a href="${project.link}" target="_blank" class="text-blue-400 hover:text-blue-300 transition-colors">
                        View Code <i class="fab fa-github ml-1"></i>
                    </a>
                    ${project.liveDemo ? `
                        <a href="${project.liveDemo}" target="_blank" class="text-green-400 hover:text-green-300 transition-colors">
                            Live Demo <i class="fas fa-external-link-alt ml-1"></i>
                        </a>
                    ` : ''}
                </div>
            </div>
        `;
        projectsContainer.appendChild(projectCard);
    });
}

// ═══════════════════════════════════════
// SMOOTH SCROLL FOR NAVIGATION
// ═══════════════════════════════════════
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
