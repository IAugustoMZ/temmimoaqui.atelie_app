(() => {
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const nodes = [...document.querySelectorAll('[data-reveal]')];

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const entering = entries.filter(({ isIntersecting, target }) => isIntersecting && !target.closest('[hidden]'));
      entering.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top
        || a.boundingClientRect.left - b.boundingClientRect.left);
      entering.forEach(({ target }, index) => {
        target.style.setProperty('--reveal-delay', `${Math.min(index, 3) * 80}ms`);
        target.classList.remove('reveal-ready');
        target.classList.add('reveal-visible');
        observer.unobserve(target);
      });
    }, { threshold: 0.08 });

    function observe(items) {
      if (motion.matches) return;
      items.forEach((item) => {
        item.classList.remove('reveal-visible');
        item.classList.add('reveal-ready');
        observer.observe(item);
      });
    }

    document.addEventListener('catalog:updated', (event) => observe(event.detail));
    motion.addEventListener('change', () => {
      if (!motion.matches) return;
      observer.disconnect();
      nodes.forEach((item) => item.classList.remove('reveal-ready', 'reveal-visible'));
    });
    observe(nodes);
  }

  const root = document.documentElement;
  const nativePages = 'onpageswap' in window && 'CSSViewTransitionRule' in window;
  if (nativePages) return;

  // Preserve browser navigation for downloads, anchors, external links and modified clicks.
  const pages = ['index.html', 'catalogo.html', 'sobre.html', 'contato.html'];
  const directory = new URL('./', window.location.href);
  let pendingNavigation;

  document.addEventListener('click', (event) => {
    if (motion.matches || event.defaultPrevented || event.button !== 0
      || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;

    const link = event.target.closest('a[href]');
    if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download')) return;

    const url = new URL(link.href);
    if (url.origin !== directory.origin || url.hash
      || !pages.some((page) => url.pathname === new URL(page, directory).pathname)
      || url.href === window.location.href) return;

    event.preventDefault();
    clearTimeout(pendingNavigation);
    root.classList.remove('page-fallback-in');
    root.classList.add('page-fallback-out');
    pendingNavigation = setTimeout(() => {
      window.location.href = url.href;
      // Keep the page visible if the browser cancels or stalls the navigation.
      pendingNavigation = setTimeout(() => root.classList.remove('page-fallback-out'), 450);
    }, 125);
  });

  window.addEventListener('pageshow', (event) => {
    clearTimeout(pendingNavigation);
    root.classList.remove('page-fallback-out', 'page-fallback-in');
    if (!event.persisted && !motion.matches) root.classList.add('page-fallback-in');
  });
})();
