/* Garnet Events & Production — site behaviour. No dependencies; the site works without it. */
(function () {
  "use strict";

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);
  doc.classList.add("js");

  /* Header border once the page scrolls */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
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
    window.matchMedia("(min-width: 960px)").addEventListener("change", function (mq) { if (mq.matches) setMenu(false); });
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

  /* Hero video: small file on phones, large on wide screens; no autoplay for reduced motion or data saver */
  document.querySelectorAll("video[data-src-lg]").forEach(function (video) {
    var wide = window.matchMedia("(min-width: 900px)").matches;
    var btn = video.parentElement.querySelector(".media-toggle");
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

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
