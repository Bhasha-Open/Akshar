// Add copy buttons to code blocks and small UX niceties
(function () {
  function addCopyButtons() {
    document.querySelectorAll('div.highlight, pre').forEach(function (block) {
      if (block.classList.contains('ak-copy-added')) return;
      // Avoid adding to inline code containers
      if (block.closest('.literal') || block.matches('code')) return;
      var btn = document.createElement('button');
      btn.className = 'ak-copy-btn';
      btn.type = 'button';
      btn.title = 'Copy';
      btn.innerHTML = '<svg class="ak-copy-ic" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v12h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg><span class="ak-copy-label">Copy</span>';
      btn.addEventListener('click', function () {
        var codeEl = block.querySelector('pre') || block;
        var text = codeEl.innerText;
        navigator.clipboard.writeText(text).then(function () {
          btn.querySelector('.ak-copy-label').textContent = 'Copied';
          btn.classList.add('ak-copied');
          setTimeout(function () {
            btn.querySelector('.ak-copy-label').textContent = 'Copy';
            btn.classList.remove('ak-copied');
          }, 1200);
        });
      });
      btn.setAttribute('aria-label', 'Copy code to clipboard');
      btn.setAttribute('title', 'Copy code');
      block.classList.add('ak-copy-added');
      block.style.position = 'relative';
      block.appendChild(btn);
    });
  }
  function ready(fn){ document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }
  ready(addCopyButtons);
  // In case of SPA-like nav (some themes), observe mutations
  var mo = new MutationObserver(function(){ addCopyButtons(); });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();

// Enhance <details> elements
(function () {
  function styleDetails() {
    document.querySelectorAll('details').forEach(function (d) {
      if (d.classList.contains('ak-details')) return;
      d.classList.add('ak-details');
    });
  }
  if (document.readyState !== 'loading') styleDetails();
  else document.addEventListener('DOMContentLoaded', styleDetails);
})();

