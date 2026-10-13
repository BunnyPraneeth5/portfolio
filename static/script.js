/*
 * Site-wide behaviour: background layers and the navigation.
 * (Phase 7: scroll fade-ins, page-fade on navigation, count-ups, the roadmap timeline
 * and the 180 ms background timer were removed; content now shows immediately.)
 */
document.addEventListener('DOMContentLoaded', () => {
    setupAtmosphere();
    setupNavigation();
    window.setTimeout(() => document.body.classList.add('title-settled'), 520);
});

function setupAtmosphere() {
    let container = document.getElementById('atmosphere-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'atmosphere-container';
        container.className = 'atmosphere-container';
        document.body.prepend(container);
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
        });

        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
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
