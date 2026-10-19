/* Garnet Events & Production — site behaviour. No dependencies; the site works without it. */
(function () {
  "use strict";

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);
  doc.classList.add("js");

  /* Header: transparent over the hero, solid white once past it */
  var header = document.querySelector(".site-header");
  var hero = document.querySelector(".hero");
  if (header && hero) {
    var onScroll = function () {
      header.classList.toggle("is-solid", window.scrollY > hero.offsetHeight - header.offsetHeight - 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
  }

  /* Mobile menu */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");
  if (toggle && menu) {
    var setMenu = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      menu.classList.toggle("is-open", open);
      menu.inert = !open;
      document.body.classList.toggle("menu-open", open);
      if (open) { var first = menu.querySelector("a"); if (first) first.focus(); }
    };
    menu.inert = true;
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) { setMenu(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 1100px)").addEventListener("change", function (mq) { if (mq.matches) setMenu(false); });
  }

  /* Reveal on scroll */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if (revealEls.length) {
    if (reduceMotion || !("IntersectionObserver" in window)) {
      revealEls.forEach(function (el) { el.classList.add("is-in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { entry.target.classList.add("is-in"); io.unobserve(entry.target); }
        });
      }, { rootMargin: "0px 0px -6% 0px", threshold: 0 });
      revealEls.forEach(function (el) { io.observe(el); });
    }
  }

  /* Hero video: portrait cut for upright phones, 16:9 for anything wide; no autoplay for reduced motion or data saver */
  document.querySelectorAll("video[data-src-lg]").forEach(function (video) {
    var wide = window.matchMedia("(min-width: 900px), (min-aspect-ratio: 1/1)").matches;
    var btn = video.closest(".hero").querySelector(".media-toggle");
    if (wide && video.dataset.posterLg) video.poster = video.dataset.posterLg;
    if (reduceMotion || saveData) {
      if (btn) btn.hidden = true;
      return;
    }
    video.src = wide ? video.dataset.srcLg : video.dataset.srcSm;
    var playPromise = video.play();
    if (playPromise && playPromise.catch) playPromise.catch(function () { if (btn) btn.setAttribute("aria-pressed", "true"); });
    if (btn) {
      btn.addEventListener("click", function () {
        if (video.paused) { video.play(); btn.setAttribute("aria-pressed", "false"); btn.setAttribute("aria-label", "Pause background video"); }
        else { video.pause(); btn.setAttribute("aria-pressed", "true"); btn.setAttribute("aria-label", "Play background video"); }
      });
    }
  });

  /* Gallery filters */
  var chips = document.querySelectorAll(".chip[data-filter]");
  var items = Array.prototype.slice.call(document.querySelectorAll(".gallery__item"));
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var f = chip.dataset.filter;
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
      items.forEach(function (item) { item.hidden = !(f === "all" || item.dataset.cat === f); });
    });
  });

  /* Gallery lightbox (native <dialog>: focus trap and Esc for free) */
  var lb = document.getElementById("lightbox");
  if (lb && items.length && typeof lb.showModal === "function") {
    var lbImg = lb.querySelector("img");
    var lbCap = lb.querySelector(".lightbox__caption");
    var lbCount = lb.querySelector(".lightbox__count");
    var current = 0;
    var visible = function () { return items.filter(function (i) { return !i.hidden; }); };
    var show = function (idx) {
      var list = visible();
      current = (idx + list.length) % list.length;
      var img = list[current].querySelector("img");
      lbImg.src = img.dataset.full || img.currentSrc || img.src;
      lbImg.alt = img.alt;
      lbCap.textContent = list[current].querySelector("figcaption").textContent;
      lbCount.textContent = (current + 1) + " / " + list.length;
    };
    items.forEach(function (item) {
      item.querySelector(".gallery__btn").addEventListener("click", function () {
        show(visible().indexOf(item));
        lb.showModal();
      });
    });
    lb.querySelector("[data-lb-prev]").addEventListener("click", function () { show(current - 1); });
    lb.querySelector("[data-lb-next]").addEventListener("click", function () { show(current + 1); });
    lb.querySelector("[data-lb-close]").addEventListener("click", function () { lb.close(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") show(current + 1);
      if (e.key === "ArrowLeft") show(current - 1);
    });
    var touchX = null;
    lb.addEventListener("touchstart", function (e) { touchX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      touchX = null;
    });
  }

  /* Enquiry form: there is no mail server behind a static site, so hand the
     enquiry to WhatsApp with every field filled in. */
  var form = document.getElementById("enquiry-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var data = new FormData(form);
      var lines = [
        "Hello Garnet Events, I'd like to enquire about an event.",
        "",
        "Name: " + data.get("name"),
        "Phone: " + data.get("phone"),
        "Event: " + data.get("event"),
        data.get("date") ? "Date: " + data.get("date") : "",
        data.get("city") ? "City: " + data.get("city") : "",
        data.get("guests") ? "Guests: " + data.get("guests") : "",
        data.get("message") ? "\n" + data.get("message") : ""
      ].filter(function (l, i) { return l !== "" || i === 1; });
      var url = "https://wa.me/" + form.dataset.whatsapp + "?text=" + encodeURIComponent(lines.join("\n"));
      window.open(url, "_blank", "noopener");
    });
  }

  /* Horizontal rails: buttons, progress bar, mouse drag */
  document.querySelectorAll("[data-rail]").forEach(function (rail) {
    var track = rail.querySelector(".rail__track");
    var prev = rail.querySelector("[data-rail-prev]");
    var next = rail.querySelector("[data-rail-next]");
    var bar = rail.querySelector(".rail__progress span");
    var step = function () {
      var item = track.querySelector(".rail__item");
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return item ? item.getBoundingClientRect().width + gap : track.clientWidth * 0.8;
    };
    var update = function () {
      var max = track.scrollWidth - track.clientWidth;
      var ratio = max > 0 ? track.scrollLeft / max : 1;
      if (bar) bar.style.width = (Math.max(track.clientWidth / track.scrollWidth, 0) * 100 + ratio * (1 - track.clientWidth / track.scrollWidth) * 100) + "%";
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max - 2;
    };
    if (prev) prev.addEventListener("click", function () { track.scrollBy({ left: -step(), behavior: reduceMotion ? "auto" : "smooth" }); });
    if (next) next.addEventListener("click", function () { track.scrollBy({ left: step(), behavior: reduceMotion ? "auto" : "smooth" }); });
    track.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();

    var startX = 0, startLeft = 0, dragging = false, moved = false;
    track.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      dragging = true; moved = false; startX = e.clientX; startLeft = track.scrollLeft;
    });
    window.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 5) { moved = true; track.classList.add("is-dragging"); }
      if (moved) track.scrollLeft = startLeft - dx;
    });
    window.addEventListener("pointerup", function () {
      if (!dragging) return;
      dragging = false;
      if (moved) {
        var s = step();
        var target = Math.round(track.scrollLeft / s) * s;
        track.classList.remove("is-dragging");
        track.scrollTo({ left: target, behavior: reduceMotion ? "auto" : "smooth" });
      }
    });
    track.addEventListener("click", function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
  });

  /* Testimonials: one at a time */
  document.querySelectorAll("[data-quotes]").forEach(function (box) {
    var quotes = box.querySelectorAll(".quote");
    var count = box.querySelector("[data-q-count]");
    var i = 0;
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var go = function (n) {
      quotes[i].classList.remove("is-active");
      i = (n + quotes.length) % quotes.length;
      quotes[i].classList.add("is-active");
      if (count) count.textContent = pad(i + 1) + " / " + pad(quotes.length);
    };
    box.querySelector("[data-q-prev]").addEventListener("click", function () { go(i - 1); });
    box.querySelector("[data-q-next]").addEventListener("click", function () { go(i + 1); });
  });

  /* Services tabs (all panels stay visible without JS) */
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll("[role=tab]"));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute("aria-controls")); });
    var select = function (idx, focus) {
      tabs.forEach(function (t, n) {
        var on = n === idx;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        panels[n].hidden = !on;
        if (on) { panels[n].classList.remove("is-entering"); void panels[n].offsetWidth; panels[n].classList.add("is-entering"); }
      });
      if (focus) tabs[idx].focus();
    };
    tabs.forEach(function (t, n) {
      t.addEventListener("click", function () { select(n); history.replaceState(null, "", "#" + panels[n].id); });
      t.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") select((n + 1) % tabs.length, true);
        if (e.key === "ArrowLeft") select((n - 1 + tabs.length) % tabs.length, true);
      });
    });
    var fromHash = function () {
      var idx = panels.findIndex(function (p) { return "#" + p.id === location.hash; });
      select(idx < 0 ? 0 : idx);
      if (idx >= 0) box.scrollIntoView();
    };
    window.addEventListener("hashchange", fromHash);
    fromHash();
  });

  /* Gentle parallax on large images (wide screens only) */
  var plx = document.querySelectorAll("[data-parallax]");
  if (plx.length && !reduceMotion && window.matchMedia("(min-width: 900px)").matches) {
    var ticking = false;
    var vh = window.innerHeight;
    var run = function () {
      plx.forEach(function (el) {
        var box = el.parentElement.getBoundingClientRect();
        if (box.bottom < -100 || box.top > vh + 100) return;
        var p = (box.top + box.height / 2 - vh / 2) / (vh / 2 + box.height / 2);
        el.style.transform = "translate3d(0," + (p * -6).toFixed(2) + "%,0) scale(1.14)";
      });
      ticking = false;
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(run); } }, { passive: true });
    window.addEventListener("resize", function () { vh = window.innerHeight; run(); });
    run();
  }

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
