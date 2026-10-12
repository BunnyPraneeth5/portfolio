try {
    if (window.AOS) {
        AOS.init({
            duration: 900,
            easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
            once: true,
            mirror: false
        });
    }
} catch (error) {}

document.body.classList.add('dark-mode');
localStorage.setItem('darkMode', 'true');

document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    setupAtmosphere();
    setupNavigation();
    setupReveals();
    setupMaterialResponse();
    setupSkillEnvironment();
    setupContactFocus();
    setupInternalPageFade();
    setupMetricCountUps();
    setupRoadmap();

    window.setTimeout(() => body.classList.add('title-settled'), 520);
});

function setupAtmosphere() {
    let container = document.getElementById('atmosphere-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'atmosphere-container';
        container.className = 'atmosphere-container';
        document.body.prepend(container);
    } else {
        container.id = 'atmosphere-container';
        container.classList.add('atmosphere-container');
    }

    if (!container.querySelector('.atmosphere-depth')) {
        const depth = document.createElement('div');
        depth.className = 'atmosphere-depth';
        container.appendChild(depth);
    }

    if (!container.querySelector('.guiding-stream')) {
        const stream = document.createElement('div');
        stream.className = 'guiding-stream';
        container.appendChild(stream);
    }

    let drift = 0;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduceMotion) {
        window.setInterval(() => {
            drift = (drift + 1) % 80;
            document.documentElement.style.setProperty('--chapter-drift', String(Math.sin(drift / 18) * 12));
        }, 180);
    }
}

function setupNavigation() {
    const nav = document.querySelector('nav');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        mobileMenuToggle.addEventListener('click', () => {
            const open = mobileMenu.classList.toggle('active');
            mobileMenuToggle.setAttribute('aria-expanded', String(open));
            const icon = mobileMenuToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });

        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });
    }

    if (nav) {
        const updateNav = () => {
            const scrolled = window.scrollY > 40;
            nav.classList.toggle('nav-scrolled', scrolled);
            nav.classList.toggle('scrolled', scrolled);
        };
        updateNav();
        window.addEventListener('scroll', updateNav, { passive: true });
    }
}

function setupReveals() {
    document.querySelectorAll('[data-aos]').forEach(element => {
        const delay = Number(element.getAttribute('data-aos-delay') || 0);
        if (delay > 0) {
            element.style.setProperty('--reveal-delay', `${Math.round(delay * 1.8)}ms`);
        }
        element.removeAttribute('data-aos');
        element.classList.add('reveal');
    });

    const revealTargets = document.querySelectorAll('.reveal, .glass-card, .skill-card, .project-card, .blog-card, .section-rule, .roadmap-card, .stat-card, .engineering-visual');
    if (!('IntersectionObserver' in window)) {
        revealTargets.forEach(element => element.classList.add('visible', 'in-view'));
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible', 'in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    revealTargets.forEach(element => {
        element.classList.add('reveal');
        observer.observe(element);
    });
}

function setupMaterialResponse() {
    document.querySelectorAll('.glass-card, .skill-card, .project-card, .blog-card').forEach((surface, index) => {
        surface.style.setProperty('--reveal-index', String(index % 6));
    });
}

function setupSkillEnvironment() {
    const skillSurfaces = document.querySelectorAll('body[data-chapter="skills"] .glass-card, body[data-chapter="skills"] li');
    if (!skillSurfaces.length) return;

    skillSurfaces.forEach(surface => {
        surface.addEventListener('mouseenter', () => document.body.classList.add('skill-environment-active'));
        surface.addEventListener('mouseleave', () => document.body.classList.remove('skill-environment-active'));
        surface.addEventListener('focusin', () => document.body.classList.add('skill-environment-active'));
        surface.addEventListener('focusout', () => document.body.classList.remove('skill-environment-active'));
    });
}

function setupContactFocus() {
    const fields = document.querySelectorAll('body[data-chapter="contact"] input, body[data-chapter="contact"] textarea');
    if (!fields.length) return;

    fields.forEach(field => {
        field.addEventListener('focus', () => document.body.classList.add('env-listening'));
        field.addEventListener('blur', () => {
            if (!document.querySelector('body[data-chapter="contact"] input:focus, body[data-chapter="contact"] textarea:focus')) {
                document.body.classList.remove('env-listening');
            }
        });
    });
}

function setupInternalPageFade() {
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', event => {
            const href = link.getAttribute('href');
            const target = link.getAttribute('target');
            const isExternal = target === '_blank' || !href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || /^https?:\/\//i.test(href);
            if (isExternal) return;

            const url = new URL(href, window.location.href);
            if (url.hash && url.pathname === window.location.pathname) return;

            event.preventDefault();
            document.body.style.transition = 'opacity 280ms ease';
            document.body.style.opacity = '0';
            window.setTimeout(() => {
                window.location.href = href;
            }, 230);
        });
    });
}

function setupMetricCountUps() {
    const metrics = document.querySelectorAll('[data-count-to]');
    if (!metrics.length) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const easeOutQuart = t => 1 - Math.pow(1 - t, 4);

    const formatValue = (value, decimals, suffix) => `${value.toFixed(decimals)}${suffix}`;

    const animateMetric = element => {
        if (element.dataset.counted === 'true') return;
        element.dataset.counted = 'true';

        const target = parseFloat(element.dataset.countTo || '0');
        const decimals = Number(element.dataset.countDecimals || 0);
        const suffix = element.dataset.countSuffix || '';

        if (reduceMotion) {
            element.textContent = formatValue(target, decimals, suffix);
            return;
        }

        const start = performance.now();
        const duration = 1400;

        const tick = now => {
            const progress = Math.min((now - start) / duration, 1);
            const value = target * easeOutQuart(progress);
            element.textContent = formatValue(value, decimals, suffix);
            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        };

        requestAnimationFrame(tick);
    };

    if (!('IntersectionObserver' in window)) {
        metrics.forEach(animateMetric);
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateMetric(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    metrics.forEach(metric => observer.observe(metric));
}

function setupRoadmap() {
    const roadmaps = document.querySelectorAll('.roadmap');
    if (!roadmaps.length) return;

    const clamp = value => Math.min(Math.max(value, 0), 1);

    const updateRoadmaps = () => {
        roadmaps.forEach(roadmap => {
            const progress = roadmap.querySelector('.timeline-progress');
            const items = Array.from(roadmap.querySelectorAll('.roadmap-item'));
            if (!progress || !items.length) return;

            const roadmapTop = roadmap.getBoundingClientRect().top + window.scrollY;
            const roadmapHeight = roadmap.offsetHeight || 1;
            const scrollHead = window.scrollY + window.innerHeight * 0.6;
            const fill = Math.min(Math.max(scrollHead - roadmapTop, 0), roadmapHeight);

            progress.style.height = `${clamp(fill / roadmapHeight) * 100}%`;

            let currentIndex = -1;

            items.forEach((item, index) => {
                const dot = item.querySelector('.roadmap-dot');
                const card = item.querySelector('.roadmap-card');
                if (!dot || !card) return;

                const dotCenter = item.offsetTop + dot.offsetTop + dot.offsetHeight / 2;
                const reached = fill >= dotCenter - 4;
                item.classList.toggle('is-lit', reached);
                dot.classList.toggle('dot-reached', reached);
                if (reached) currentIndex = index;
            });

            items.forEach((item, index) => {
                const dot = item.querySelector('.roadmap-dot');
                const card = item.querySelector('.roadmap-card');
                const isCurrent = index === currentIndex;
                item.classList.toggle('is-current', isCurrent);
                dot?.classList.toggle('dot-active', isCurrent);
                card?.classList.toggle('card-active', isCurrent);
            });
        });
    };

    updateRoadmaps();
    window.addEventListener('scroll', updateRoadmaps, { passive: true });
    window.addEventListener('resize', updateRoadmaps);
}
