// Initialize AOS
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');

mobileMenuToggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('active');
    const icon = mobileMenuToggle.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('#mobileMenu a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        const icon = mobileMenuToggle.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    });
});

// Dark Mode Management
function updateDarkMode(isDark) {
    const icon = darkModeToggle.querySelector('i');
    if (isDark) {
        document.body.classList.add('dark-mode');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        document.body.classList.remove('dark-mode');
        icon.classList.add('fa-moon');
        icon.classList.remove('fa-sun');
    }
    localStorage.setItem('darkMode', isDark);
}

// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
darkModeToggle.addEventListener('click', () => {
    const isDark = !document.body.classList.contains('dark-mode');
    updateDarkMode(isDark);
});

// Skills Data with proficiency levels
const skills = [
    {
        category: 'Languages',
        items: [
            { name: 'Python', level: 90, icon: 'fab fa-python' },
            { name: 'SQL', level: 85, icon: 'fas fa-database' },
            { name: 'Java', level: 80, icon: 'fab fa-java' }
        ]
    },
    {
        category: 'ML/AI',
        items: [
            { name: 'TensorFlow', level: 85, icon: 'fas fa-brain' },
            { name: 'Keras', level: 80, icon: 'fas fa-network-wired' },
            { name: 'Scikit-Learn', level: 90, icon: 'fas fa-chart-line' },
            { name: 'Pandas', level: 95, icon: 'fas fa-table' },
            { name: 'NumPy', level: 90, icon: 'fas fa-calculator' }
        ]
    },
    {
        category: 'Web',
        items: [
            { name: 'Django', level: 85, icon: 'fab fa-python' },
            { name: 'HTML/CSS', level: 90, icon: 'fab fa-html5' },
            { name: 'JavaScript', level: 80, icon: 'fab fa-js' }
        ]
    },
    {
        category: 'Tools',
        items: [
            { name: 'Git', level: 90, icon: 'fab fa-git-alt' },
            { name: 'VS Code', level: 95, icon: 'fas fa-code' },
            { name: 'Jupyter', level: 90, icon: 'fas fa-book' },
            { name: 'Figma', level: 75, icon: 'fab fa-figma' }
        ]
    }
];

// Projects Data
const projects = [
    {
        title: 'College Gate Pass System',
        description: 'A secure, web-based system using QR code authentication to manage student passes.',
        link: 'https://github.com/BunnyPraneeth5/college-gate-pass',
        tags: ['Django', 'QR Code', 'Security'],
        image: 'path-to-image.jpg',
        features: [
            'QR Code Authentication',
            'Real-time Tracking',
            'Secure Database'
        ]
    },
    {
        title: 'Car Sales Price Prediction',
        description: 'Neural network built using TensorFlow that predicts car prices with 88% accuracy.',
        link: 'https://github.com/BunnyPraneeth5/car-price-prediction',
        tags: ['TensorFlow', 'Machine Learning', 'Python'],
        image: 'path-to-image.jpg',
        features: [
            'Neural Network Model',
            'Data Analysis',
            'Price Prediction'
        ]
    },
    {
        title: 'AI-Generated Fitness Website',
        description: 'A futuristic fitness UI built using v0.dev and AI tools — backend API integration coming soon.',
        link: '#',
        tags: ['AI', 'Web Design', 'Fitness'],
        image: 'path-to-image.jpg',
        features: [
            'AI Integration',
            'Modern UI',
            'Fitness Tracking'
        ]
    }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode from localStorage or system preference
    const savedDarkMode = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedDarkMode === 'true' || (savedDarkMode === null && prefersDark);
    updateDarkMode(shouldBeDark);

    // Initialize AOS
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // Initialize particles.js
    if (document.querySelector('.particles-container')) {
        particlesJS('particles-container', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: '#ffffff' },
                shape: { type: 'circle' },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#ffffff',
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

    // Initialize skills and projects
    const skillsContainer = document.querySelector('#skills .grid');
    const projectsContainer = document.querySelector('#projects .grid');

    if (skillsContainer) {
        renderSkills();
        // Initialize skill bars animation
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.querySelectorAll('.skill-progress').forEach(bar => {
                        const level = bar.getAttribute('data-level');
                        setTimeout(() => {
                            bar.style.width = `${level}%`;
                        }, 200);
                    });
                }
            });
        }, { threshold: 0.2 });

        document.querySelectorAll('.skill-card').forEach(card => {
            observer.observe(card);
        });
    }

    if (projectsContainer) {
        renderProjects();
    }
});

// Render Skills with Progress Bars
function renderSkills() {
    const skillsContainer = document.querySelector('#skills .grid');
    if (!skillsContainer) return;

    skillsContainer.innerHTML = ''; // Clear existing content
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

// Render Projects
function renderProjects() {
    const projectsContainer = document.querySelector('#projects .grid');
    if (!projectsContainer) return;

    projectsContainer.innerHTML = ''; // Clear existing content
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
                        ${project.features.map(feature => `
                            <li>${feature}</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="flex flex-wrap gap-2 mb-4">
                    ${project.tags.map(tag => `
                        <span class="px-2 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs">
                            ${tag}
                        </span>
                    `).join('')}
                </div>
                <a href="${project.link}" target="_blank" class="text-blue-400 hover:text-blue-300 transition-colors">
                    View Project <i class="fas fa-external-link-alt ml-1"></i>
                </a>
            </div>
        `;
        projectsContainer.appendChild(projectCard);
    });
}

// Smooth Scroll for Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Contact Form Handler
const contactForm = document.getElementById('contactForm');
contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // Add your form submission logic here
    alert('Thank you for your message! I will get back to you soon.');
    contactForm.reset();
}); 