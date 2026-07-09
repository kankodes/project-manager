/* Garnet Events — shared interactions */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---------------- Preloader ---------------- */
  window.addEventListener("load", function () {
    var pre = document.querySelector(".preloader");
    if (pre) {
      setTimeout(function () {
        pre.classList.add("is-done");
        document.body.classList.remove("pre-load");
      }, 400);
    } else {
      document.body.classList.remove("pre-load");
    }
  });
  // safety fallback in case load event is delayed by video
  setTimeout(function () {
    var pre = document.querySelector(".preloader");
    if (pre) pre.classList.add("is-done");
    document.body.classList.remove("pre-load");
  }, 2600);

  /* ---------------- Custom cursor ---------------- */
  var isTouch = matchMedia("(hover: none), (pointer: coarse)").matches;
  if (!isTouch) {
    var dot = document.createElement("div");
    dot.className = "cursor-dot";
    var ring = document.createElement("div");
    ring.className = "cursor-ring";
    document.body.appendChild(dot);
    document.body.appendChild(ring);

    var mx = 0, my = 0, rx = 0, ry = 0;
    window.addEventListener("mousemove", function (e) {
      mx = e.clientX; my = e.clientY;
      dot.style.left = mx + "px";
      dot.style.top = my + "px";
    });
    (function loop() {
      rx += (mx - rx) * 0.16;
      ry += (my - ry) * 0.16;
      ring.style.left = rx + "px";
      ring.style.top = ry + "px";
      requestAnimationFrame(loop);
    })();

    document.addEventListener("mouseover", function (e) {
      if (e.target.closest("a, button, .tilt, input, textarea, select, .masonry__item")) {
        ring.classList.add("is-active");
      }
    });
    document.addEventListener("mouseout", function (e) {
      if (e.target.closest("a, button, .tilt, input, textarea, select, .masonry__item")) {
        ring.classList.remove("is-active");
      }
    });
  } else {
    document.body.classList.add("no-hover");
  }

  /* ---------------- Nav: scroll state + mobile toggle ---------------- */
  var nav = document.querySelector(".nav");
  var onScroll = function () {
    if (!nav) return;
    if (window.scrollY > 40) nav.classList.add("is-scrolled");
    else nav.classList.remove("is-scrolled");

    var backTop = document.querySelector(".back-to-top");
    if (backTop) {
      if (window.scrollY > 700) backTop.classList.add("is-visible");
      else backTop.classList.remove("is-visible");
    }
  };
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var toggle = document.querySelector(".nav__toggle");
  var links = document.querySelector(".nav__links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("is-open");
      toggle.classList.toggle("is-open");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("is-open"); });
    });
  }

  /* ---------------- Scroll reveal ---------------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------------- Animated counters ---------------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    var countIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        countIo.unobserve(entry.target);
        var el = entry.target;
        var target = parseFloat(el.getAttribute("data-count"));
        var suffix = el.getAttribute("data-suffix") || "";
        var dur = 1800, start = null;
        function step(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          var val = target < 10 ? (target * eased).toFixed(1) : Math.floor(target * eased);
          el.textContent = val + suffix;
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = target + suffix;
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { countIo.observe(el); });
  }

  /* ---------------- Hero particles ---------------- */
  document.querySelectorAll(".hero__particles").forEach(function (field) {
    var count = 22;
    for (var i = 0; i < count; i++) {
      var s = document.createElement("span");
      s.style.left = Math.random() * 100 + "%";
      s.style.animationDuration = 8 + Math.random() * 10 + "s";
      s.style.animationDelay = Math.random() * 12 + "s";
      s.style.opacity = 0.3 + Math.random() * 0.5;
      field.appendChild(s);
    }
  });

  /* ---------------- Tilt cards ---------------- */
  document.querySelectorAll(".tilt").forEach(function (card) {
    card.addEventListener("mousemove", function (e) {
      var r = card.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform = "perspective(900px) rotateY(" + (px * 8) + "deg) rotateX(" + (py * -8) + "deg) translateY(-4px)";
    });
    card.addEventListener("mouseleave", function () {
      card.style.transform = "perspective(900px) rotateY(0) rotateX(0) translateY(0)";
    });
  });

  /* ---------------- Testimonial slider ---------------- */
  var track = document.querySelector(".testi-track");
  if (track) {
    var slides = track.querySelectorAll(".testi-slide");
    var dotsWrap = document.querySelector(".testi-nav");
    var idx = 0;
    slides.forEach(function (_, i) {
      var d = document.createElement("button");
      d.className = "testi-dot" + (i === 0 ? " is-active" : "");
      d.setAttribute("aria-label", "Go to testimonial " + (i + 1));
      d.addEventListener("click", function () { goTo(i); });
      dotsWrap.appendChild(d);
    });
    function goTo(i) {
      idx = (i + slides.length) % slides.length;
      track.style.transform = "translateX(-" + (idx * 100) + "%)";
      dotsWrap.querySelectorAll(".testi-dot").forEach(function (d, di) {
        d.classList.toggle("is-active", di === idx);
      });
    }
    var auto = setInterval(function () { goTo(idx + 1); }, 6000);
    track.closest(".testi-wrap").addEventListener("mouseenter", function () { clearInterval(auto); });
  }

  /* ---------------- Gallery filters ---------------- */
  var filterBtns = document.querySelectorAll(".filter-btn");
  var items = document.querySelectorAll(".masonry__item");
  if (filterBtns.length) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filterBtns.forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        var f = btn.getAttribute("data-filter");
        items.forEach(function (item) {
          var match = f === "all" || item.getAttribute("data-cat") === f;
          item.style.display = match ? "" : "none";
        });
      });
    });
  }
  if (items.length) {
    var gIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-shown");
          gIo.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    items.forEach(function (el) { gIo.observe(el); });
  }

  /* ---------------- Lightbox ---------------- */
  var lightbox = document.querySelector(".lightbox");
  if (lightbox && items.length) {
    var lbImg = lightbox.querySelector("img");
    var visibleItems = function () { return Array.prototype.filter.call(items, function (i) { return i.style.display !== "none"; }); };
    var curIndex = 0;
    items.forEach(function (item, i) {
      item.addEventListener("click", function () {
        var vi = visibleItems();
        curIndex = vi.indexOf(item);
        open(vi);
      });
    });
    function open(vi) {
      lbImg.src = vi[curIndex].querySelector("img").src;
      lightbox.classList.add("is-open");
    }
    function close() { lightbox.classList.remove("is-open"); }
    lightbox.querySelector(".lightbox__close").addEventListener("click", close);
    lightbox.addEventListener("click", function (e) { if (e.target === lightbox) close(); });
    lightbox.querySelector(".lightbox__nav--prev").addEventListener("click", function () {
      var vi = visibleItems(); curIndex = (curIndex - 1 + vi.length) % vi.length; open(vi);
    });
    lightbox.querySelector(".lightbox__nav--next").addEventListener("click", function () {
      var vi = visibleItems(); curIndex = (curIndex + 1) % vi.length; open(vi);
    });
    document.addEventListener("keydown", function (e) {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowRight") lightbox.querySelector(".lightbox__nav--next").click();
      if (e.key === "ArrowLeft") lightbox.querySelector(".lightbox__nav--prev").click();
    });
  }

  /* ---------------- Floating label form fields ---------------- */
  document.querySelectorAll(".field select").forEach(function (sel) {
    var check = function () { sel.closest(".field").classList.toggle("has-value", !!sel.value); };
    sel.addEventListener("change", check);
    check();
  });

  var contactForm = document.querySelector("#contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = contactForm.querySelector("button[type=submit]");
      var original = btn.innerHTML;
      btn.innerHTML = "<span>Sending…</span>";
      setTimeout(function () {
        contactForm.reset();
        contactForm.querySelectorAll(".field").forEach(function (f) { f.classList.remove("has-value"); });
        btn.innerHTML = "<span>Message Sent ✦</span>";
        setTimeout(function () { btn.innerHTML = original; }, 2600);
      }, 900);
    });
  }

  var newsletterForm = document.querySelector(".newsletter");
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = newsletterForm.querySelector("input");
      input.placeholder = "Thank you ✦";
      input.value = "";
    });
  }

  /* ---------------- Back to top ---------------- */
  var backTop = document.querySelector(".back-to-top");
  if (backTop) {
    backTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------------- Set active nav link ---------------- */
  var path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav__links a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === path || (path === "" && href === "index.html")) a.classList.add("is-active");
  });
})();
