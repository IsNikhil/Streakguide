// Tells the CSS that JavaScript is on, so the scroll animations can start hidden.
document.documentElement.classList.add('js');

(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. Missing pictures: show the "Photo coming soon" box ---------- */
  // The onerror in the HTML does this too. This also catches pictures that failed before this script ran.
  document.querySelectorAll('.shot img').forEach(function (img) {
    if (img.complete && img.naturalWidth === 0) img.closest('figure').classList.add('missing');
  });

  // Mac screenshots have 2 pixels per screen dot. A new photo without a width
  // gets half its pixel width, so it looks the same size as on your screen.
  document.querySelectorAll('.shot img:not([width])').forEach(function (img) {
    function fit() { if (img.naturalWidth) img.width = Math.round(img.naturalWidth / 2); }
    if (img.complete) fit(); else img.addEventListener('load', fit);
  });

  /* ---------- 2. Progress bar at the top that fills as you scroll ---------- */
  var bar = document.getElementById('scrollBar');
  var ticking = false;
  function updateBar() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var amount = max > 0 ? window.scrollY / max : 0;
    bar.style.transform = 'scaleX(' + Math.min(1, Math.max(0, amount)) + ')';
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(updateBar); }
  }, { passive: true });
  window.addEventListener('resize', updateBar);
  updateBar();

  /* ---------- 3. Cards fade in and slide up when you scroll to them ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { revealer.observe(el); });
  }

  /* ---------- 4. Side menu: highlight the step you are reading ---------- */
  var navLinks = document.querySelectorAll('.sidenav a[data-target]');
  var linkFor = {};
  navLinks.forEach(function (a) { linkFor[a.dataset.target] = a; });
  var watched = Object.keys(linkFor).map(function (id) { return document.getElementById(id); }).filter(Boolean);

  function setActive(id) {
    navLinks.forEach(function (a) { a.classList.toggle('active', a.dataset.target === id); });
    var link = linkFor[id];
    // keep the active link visible inside the side menu
    if (link && link.offsetParent) {
      var nav = link.closest('nav');
      var top = link.offsetTop - nav.offsetTop;
      if (top < nav.scrollTop || top > nav.scrollTop + nav.clientHeight - 40) nav.scrollTop = top - nav.clientHeight / 2;
    }
  }
  if ('IntersectionObserver' in window) {
    // A step counts as "current" when it crosses a line about 35% down the screen.
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setActive(entry.target.id);
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    watched.forEach(function (el) { spy.observe(el); });
  }

  /* ---------- 5. "Done" checkboxes, saved in localStorage ---------- */
  var KEY = 'streak-guide-done';
  var boxes = document.querySelectorAll('.done input[type="checkbox"]');
  var counter = document.getElementById('doneCount');
  var ring = document.querySelector('.done-ring');

  function loadDone() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
    catch (e) { return {}; } // storage blocked: just start empty
  }
  function saveDone(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); }
    catch (e) { /* storage blocked: the page still works, it just will not remember */ }
  }
  function refreshCount() {
    var done = 0;
    boxes.forEach(function (box) {
      var card = box.closest('.step');
      card.classList.toggle('is-done', box.checked);
      var link = linkFor[box.dataset.step];
      if (link) link.classList.toggle('is-done', box.checked);
      if (box.checked) done++;
    });
    counter.textContent = done + ' of ' + boxes.length + ' steps done';
    ring.style.setProperty('--p', Math.round(done / boxes.length * 100));
  }

  var state = loadDone();
  boxes.forEach(function (box) {
    box.checked = !!state[box.dataset.step];
    box.addEventListener('change', function () {
      state[box.dataset.step] = box.checked;
      saveDone(state);
      refreshCount();
    });
  });
  refreshCount();

  /* ---------- 6. Lightbox: click a picture to see it big ---------- */
  var lightbox = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightboxImg');
  var lbCap = document.getElementById('lightboxCap');
  var closeBtn = lightbox.querySelector('.lightbox-close');
  var lastFocus = null;

  function openLightbox(img, caption) {
    lastFocus = document.activeElement;
    lbImg.src = img.src;
    lbImg.alt = img.alt;
    lbCap.textContent = caption;
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }
  function closeLightbox() {
    lightbox.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }

  document.querySelectorAll('.shot-btn').forEach(function (btn) {
    var img = btn.querySelector('img');
    var cap = btn.closest('figure').querySelector('figcaption');
    btn.setAttribute('aria-label', 'Show bigger: ' + img.alt);
    btn.addEventListener('click', function () { openLightbox(img, cap ? cap.textContent : ''); });
  });
  closeBtn.addEventListener('click', closeLightbox);
  // click the dark area around the picture to close
  lightbox.addEventListener('click', function (e) { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !lightbox.hidden) closeLightbox();
  });
})();
