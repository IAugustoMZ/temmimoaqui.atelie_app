(() => {
  const menu = document.querySelector('.mobile-nav');
  const summary = menu?.querySelector('summary');

  if (menu && summary) {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        summary.focus();
      }
    });
    document.addEventListener('click', (event) => {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    window.addEventListener('pageshow', (event) => {
      if (event.persisted) menu.open = false;
    });
  }

  const filters = document.querySelector('.filters');
  if (!filters) return;

  const results = document.querySelector('#catalog-results');
  const empty = document.querySelector('#catalog-empty');
  const status = document.querySelector('#catalog-status');
  const sections = [...results.querySelectorAll('[data-edition]')].map((section) => ({
    section,
    cards: [...section.querySelectorAll('[data-category]')],
  }));
  const buttons = [...filters.querySelectorAll('button')];
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let pending;

  function show(category) {
    let count = 0;
    const entering = [];
    sections.forEach(({ section, cards }) => {
      let sectionCount = 0;
      cards.forEach((card) => {
        const visible = category === 'todos' || card.dataset.category === category;
        if (visible && card.hidden) entering.push(card);
        card.hidden = !visible;
        if (visible) sectionCount += 1;
      });
      section.hidden = sectionCount === 0;
      count += sectionCount;
    });
    empty.hidden = count !== 0;
    status.textContent = count === 1 ? '1 mimo encontrado.' : `${count} mimos encontrados.`;
    results.classList.remove('filter-away');
    if (!motion.matches) results.classList.add('filter-in');
    results.dispatchEvent(new CustomEvent('catalog:updated', { bubbles: true, detail: entering }));
  }

  filters.addEventListener('click', (event) => {
    const selected = event.target.closest('button[data-filter]');
    if (!selected || selected.getAttribute('aria-pressed') === 'true') return;
    buttons.forEach((button) => button.setAttribute('aria-pressed', String(button === selected)));
    clearTimeout(pending);
    results.classList.remove('filter-in');
    if (motion.matches) {
      show(selected.dataset.filter);
    } else {
      results.classList.add('filter-away');
      pending = setTimeout(() => show(selected.dataset.filter), 115);
    }
  });
  results.addEventListener('animationend', (event) => {
    if (event.animationName === 'filter-in') results.classList.remove('filter-in');
  });
  filters.hidden = false;
})();
