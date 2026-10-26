/**
 * HaggLab site interactions (v2.1).
 * No dependencies. CSP safe: no inline handlers; styles are set through the CSSOM only.
 * Every animation plays once and is skipped when the visitor prefers reduced motion.
 */
(() => {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  document.addEventListener('DOMContentLoaded', () => {
    window.hagglabReady = true;
    const header = document.querySelector('.site-header');

    /* ---------- 1. Desktop menus (Services, Company) ---------- */
    const drops = Array.from(document.querySelectorAll('[data-drop]')).map((wrap) => ({
      wrap,
      button: wrap.querySelector('button'),
      panel: document.getElementById(wrap.querySelector('button').getAttribute('aria-controls')),
      timer: null,
    }));

    const setDrop = (d, open) => {
      d.button.setAttribute('aria-expanded', String(open));
      d.panel.classList.toggle('is-open', open);
    };
    const closeAll = (except) => drops.forEach((d) => { if (d !== except) setDrop(d, false); });
    const anyOpen = () => drops.some((d) => d.button.getAttribute('aria-expanded') === 'true');

    drops.forEach((d) => {
      d.button.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = d.button.getAttribute('aria-expanded') !== 'true';
        closeAll(d);
        setDrop(d, open);
      });
      // Keyboard: arrow down moves into the menu
      d.button.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
          e.preventDefault(); closeAll(d); setDrop(d, true);
          d.panel.querySelector('a')?.focus();
        }
      });
      d.panel.addEventListener('focusout', (e) => {
        if (!d.wrap.contains(e.relatedTarget)) setDrop(d, false);
      });
      // Hover intent: a short delay so menus do not flicker as the mouse passes
      if (finePointer) {
        const enter = () => { clearTimeout(d.timer); d.timer = setTimeout(() => { closeAll(d); setDrop(d, true); }, 90); };
        const leave = () => { clearTimeout(d.timer); d.timer = setTimeout(() => setDrop(d, false), 180); };
        d.wrap.addEventListener('mouseenter', enter);
        d.wrap.addEventListener('mouseleave', leave);
        d.panel.addEventListener('mouseenter', () => clearTimeout(d.timer));
        d.panel.addEventListener('mouseleave', leave);
      }
    });
    document.addEventListener('click', (e) => {
      drops.forEach((d) => { if (!d.wrap.contains(e.target)) setDrop(d, false); });
    });

    /* ---------- 2. Mobile menu ---------- */
    const toggle = document.querySelector('.menu-toggle');
    const panel = document.getElementById('mobile-panel');
    const setMenu = (open) => {
      if (!toggle || !panel) return;
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      panel.classList.toggle('is-open', open);
      document.body.classList.toggle('menu-open', open);
      if (open) header?.classList.remove('is-hidden');
    };
    if (toggle && panel) {
      toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
      panel.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
    }

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      const openDrop = drops.find((d) => d.button.getAttribute('aria-expanded') === 'true');
      if (openDrop) { setDrop(openDrop, false); openDrop.button.focus(); }
      if (toggle && toggle.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); }
    });

    /* ---------- 3. Header: border once scrolled, hide on the way down ---------- */
    if (header) {
      let lastY = window.scrollY;
      let ticking = false;
      const update = () => {
        const y = window.scrollY;
        header.classList.toggle('is-scrolled', y > 8);
        const menuOpen = document.body.classList.contains('menu-open') || anyOpen();
        if (!menuOpen && y > 360 && y > lastY + 4) header.classList.add('is-hidden');
        else if (y < lastY - 4 || y <= 360) header.classList.remove('is-hidden');
        lastY = y;
        ticking = false;
      };
      window.addEventListener('scroll', () => {
        if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
      }, { passive: true });
      // Keyboard users must always see where focus is
      header.addEventListener('focusin', () => header.classList.remove('is-hidden'));
      update();
    }

    /* ---------- 4. Smooth open/close for <details> (FAQ, mobile sections) ---------- */
    document.querySelectorAll('.faq details, .m-acc').forEach((details) => {
      const summary = details.querySelector('summary');
      const body = details.querySelector('.faq__a, .m-acc__body');
      if (!summary || !body || reduceMotion || !body.animate) return;
      let anim = null;
      summary.addEventListener('click', (e) => {
        e.preventDefault();
        if (anim) anim.cancel();
        if (!details.open) {
          details.open = true;
          const h = body.scrollHeight;
          anim = body.animate(
            [{ height: '0px', opacity: 0 }, { height: h + 'px', opacity: 1 }],
            { duration: 260, easing: 'cubic-bezier(0.2, 0.7, 0.2, 1)' }
          );
        } else {
          const h = body.scrollHeight;
          anim = body.animate(
            [{ height: h + 'px', opacity: 1 }, { height: '0px', opacity: 0 }],
            { duration: 200, easing: 'ease-in' }
          );
          anim.onfinish = () => { details.open = false; };
        }
        anim.addEventListener('finish', () => { anim = null; });
      });
    });

    /* ---------- 5. Reveal on scroll (once) ---------- */
    const revealSelectors = [
      '.hero__kicker', '.hero .display', '.hero .lead', '.hero__cta', '.hero__promise', '.hero__checks', '.hero-stage',
      '.page-head .eyebrow', '.page-head h1', '.page-head .lead', '.page-head__aside', '.page-head .btn-row',
      '.section-head', '.split__sticky', '.proof__intro', '.proof__item', '.svc', '.index-row', '.feature',
      '.p-card', '.s-row', '.phase', '.rail__step', '.handover__item', '.principle', '.layer', '.not-yet',
      '.sec-item', '.lifecycle__step', '.card', '.spec__row', '.result', '.compare__col', '.steps3 li',
      '.gig', '.faq details', '.final-cta > *', '.fiverr-band > *', '.legend__item', '.brief', '.aside-card',
      '.demo-stage', '.check-list li', '.cross-list li', '.prose section', '.form-card',
    ].join(',');

    const targets = Array.from(document.querySelectorAll(revealSelectors))
      .filter((el) => !el.closest('.mega, .drop, .mobile-panel, .ui'));

    if (reduceMotion || !('IntersectionObserver' in window)) {
      root.classList.add('reveal-all');
    } else {
      // Stagger siblings that share a parent (capped so long lists do not drag)
      const counts = new Map();
      targets.forEach((el) => {
        el.classList.add('rv');
        const n = counts.get(el.parentElement) || 0;
        counts.set(el.parentElement, n + 1);
        el.style.setProperty('--d', Math.min(n, 6) * 70 + 'ms');
      });
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
      targets.forEach((el) => io.observe(el));
    }

    /* ---------- 6. Product previews play once when seen ---------- */
    const previews = document.querySelectorAll('.ui');
    if (reduceMotion || !('IntersectionObserver' in window)) {
      previews.forEach((ui) => ui.classList.add('is-live'));
    } else {
      const uiObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-live');
            uiObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.35 });
      previews.forEach((ui) => uiObserver.observe(ui));
    }

    /* ---------- 7. Copy-to-clipboard (Fiverr brief checklist) ---------- */
    document.querySelectorAll('.btn-copy-trigger').forEach((button) => {
      const label = button.querySelector('[data-copy-label]');
      const original = label ? label.textContent : '';
      button.addEventListener('click', () => {
        const target = document.querySelector(button.getAttribute('data-copy-target'));
        if (!target || !navigator.clipboard) return;
        const text = Array.from(target.querySelectorAll('li'))
          .map((li) => li.innerText.replace(/\s+/g, ' ').trim())
          .join('\n');
        navigator.clipboard.writeText(text || target.innerText.trim()).then(() => {
          button.classList.add('is-copied');
          if (label) label.textContent = 'Copied';
          setTimeout(() => {
            button.classList.remove('is-copied');
            if (label) label.textContent = original;
          }, 2200);
        });
      });
    });
  });
})();
