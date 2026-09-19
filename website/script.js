/* ═══════════════════════════════════════════════════════════════════
   Morphora — Showcase Website Scripts
   WebGL particle background, scroll animations, navigation
   ═══════════════════════════════════════════════════════════════════ */

// ── WebGL Particle Background ─────────────────────────────────────
class ParticleBackground {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.particleCount = Math.min(120, Math.floor(window.innerWidth / 12));
        this.colors = [
            { r: 0, g: 194, b: 255 },   // Cyan
            { r: 255, g: 30, b: 45 },    // Red
            { r: 194, g: 24, b: 91 },    // Pink
        ];
        this.animationId = null;

        this.init();
        this.bindEvents();
        this.animate();
    }

    init() {
        this.resize();
        this.particles = [];
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push(this.createParticle());
        }
    }

    createParticle() {
        const color = this.colors[Math.floor(Math.random() * this.colors.length)];
        return {
            x: Math.random() * this.canvas.width,
            y: Math.random() * this.canvas.height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            size: Math.random() * 2 + 0.5,
            opacity: Math.random() * 0.4 + 0.1,
            color: color,
            pulse: Math.random() * Math.PI * 2,
            pulseSpeed: Math.random() * 0.02 + 0.005,
        };
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.particleCount = Math.min(120, Math.floor(window.innerWidth / 12));
        });

        window.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (const p of this.particles) {
            // Update position
            p.x += p.vx;
            p.y += p.vy;

            // Subtle mouse interaction
            const dx = this.mouseX - p.x;
            const dy = this.mouseY - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 200) {
                const force = (200 - dist) / 200 * 0.02;
                p.vx -= dx * force * 0.01;
                p.vy -= dy * force * 0.01;
            }

            // Damping
            p.vx *= 0.999;
            p.vy *= 0.999;

            // Wrap around
            if (p.x < -10) p.x = this.canvas.width + 10;
            if (p.x > this.canvas.width + 10) p.x = -10;
            if (p.y < -10) p.y = this.canvas.height + 10;
            if (p.y > this.canvas.height + 10) p.y = -10;

            // Pulse opacity
            p.pulse += p.pulseSpeed;
            const currentOpacity = p.opacity * (0.6 + 0.4 * Math.sin(p.pulse));

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${currentOpacity})`;
            this.ctx.fill();

            // Draw glow
            const gradient = this.ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4);
            gradient.addColorStop(0, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${currentOpacity * 0.3})`);
            gradient.addColorStop(1, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, 0)`);
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size * 4, 0, Math.PI * 2);
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
        }

        // Draw connections
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const a = this.particles[i];
                const b = this.particles[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {
                    const opacity = (1 - dist / 130) * 0.08;
                    this.ctx.beginPath();
                    this.ctx.moveTo(a.x, a.y);
                    this.ctx.lineTo(b.x, b.y);
                    this.ctx.strokeStyle = `rgba(0, 194, 255, ${opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.stroke();
                }
            }
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }
}

// ── Navigation ────────────────────────────────────────────────────
function initNavigation() {
    const nav = document.getElementById('main-nav');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    // Scroll-based nav styling
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                if (window.scrollY > 50) {
                    nav.classList.add('scrolled');
                } else {
                    nav.classList.remove('scrolled');
                }
                ticking = false;
            });
            ticking = true;
        }
    });

    // Mobile menu toggle
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        const spans = mobileMenuBtn.querySelectorAll('span');
        if (navLinks.classList.contains('open')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offset = nav.offsetHeight + 20;
                const top = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
                navLinks.classList.remove('open');
            }
        });
    });
}

// ── Scroll Animations ─────────────────────────────────────────────
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Stagger delay based on sibling index
                    const siblings = entry.target.parentElement.children;
                    let siblingIndex = 0;
                    for (let i = 0; i < siblings.length; i++) {
                        if (siblings[i] === entry.target) {
                            siblingIndex = i;
                            break;
                        }
                    }
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, siblingIndex * 100);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    document.querySelectorAll(
        '.about-card, .form-card, .gesture-step, .tech-card, .setup-step, .arch-box'
    ).forEach(el => observer.observe(el));
}

// ── Typing Counter Animation ──────────────────────────────────────
function initCounterAnimation() {
    const statValues = document.querySelectorAll('.stat-value');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    statValues.forEach(el => observer.observe(el));
}

function animateCounter(el) {
    const text = el.textContent;
    const numMatch = text.match(/[\d.]+/);
    if (!numMatch) return;

    const targetNum = parseFloat(numMatch[0]);
    const suffix = text.replace(numMatch[0], '');
    const duration = 1500;
    const start = performance.now();

    function update(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = targetNum * eased;

        if (Number.isInteger(targetNum)) {
            el.textContent = Math.round(current) + suffix;
        } else {
            el.textContent = current.toFixed(1) + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = text;
        }
    }

    requestAnimationFrame(update);
}

// ── Code Copy ─────────────────────────────────────────────────────
function copyCode(button) {
    const codeBlock = button.closest('.code-block');
    const code = codeBlock.querySelector('code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        button.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>';
        button.style.color = '#00c2ff';
        setTimeout(() => {
            button.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>';
            button.style.color = '';
        }, 2000);
    });
}

// ── Active Nav Link Highlighting ──────────────────────────────────
function initActiveNavTracking() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + entry.target.id) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        },
        { threshold: 0.3, rootMargin: '-100px 0px -50% 0px' }
    );

    sections.forEach(section => observer.observe(section));
}

// ── Parallax Effect on Hero ───────────────────────────────────────
function initParallax() {
    const heroImage = document.querySelector('.hero-image-container');
    const heroContent = document.querySelector('.hero-content');

    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;
                if (scrollY < window.innerHeight) {
                    const progress = scrollY / window.innerHeight;
                    if (heroImage) {
                        heroImage.style.transform = `translateY(${progress * 40}px) scale(${1 - progress * 0.05})`;
                        heroImage.style.opacity = 1 - progress * 0.5;
                    }
                    if (heroContent) {
                        heroContent.style.transform = `translateY(${progress * 30}px)`;
                        heroContent.style.opacity = 1 - progress * 0.6;
                    }
                }
                ticking = false;
            });
            ticking = true;
        }
    });
}

// ── Initialize Everything ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Particle background
    const canvas = document.getElementById('particle-bg');
    if (canvas) {
        new ParticleBackground(canvas);
    }

    initNavigation();
    initScrollAnimations();
    initCounterAnimation();
    initActiveNavTracking();
    initParallax();

    // Reveal hero with slight delay
    requestAnimationFrame(() => {
        document.body.style.opacity = '1';
    });
});

// Make copyCode global for inline onclick
window.copyCode = copyCode;
