// Avalon Volunteer Fire Department — nav, lightbox, ticket search

(function () {
  // Mobile navigation
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Footer year
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  // Lightbox: any <button data-full="..."> inside a [data-lightbox] group
  var groups = document.querySelectorAll("[data-lightbox]");
  if (groups.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Photo viewer");
    box.innerHTML =
      '<button class="lb-close" aria-label="Close">&times;</button>' +
      '<button class="lb-prev" aria-label="Previous photo">&#8249;</button>' +
      '<img alt="">' +
      '<div class="cap"></div>' +
      '<button class="lb-next" aria-label="Next photo">&#8250;</button>';
    document.body.appendChild(box);

    var img = box.querySelector("img");
    var cap = box.querySelector(".cap");
    var items = [];
    var index = 0;
    var opener = null;

    function show(i) {
      index = (i + items.length) % items.length;
      var b = items[index];
      var thumb = b.querySelector("img");
      img.src = b.getAttribute("data-full");
      img.alt = thumb ? thumb.alt : "";
      cap.textContent = (b.getAttribute("data-cap") || img.alt) + "  ·  " + (index + 1) + " of " + items.length;
    }
    function close() {
      box.classList.remove("open");
      document.body.style.overflow = "";
      if (opener) opener.focus();
    }

    groups.forEach(function (group) {
      var buttons = Array.prototype.slice.call(group.querySelectorAll("button[data-full]"));
      buttons.forEach(function (b, i) {
        b.addEventListener("click", function () {
          items = buttons;
          opener = b;
          show(i);
          box.classList.add("open");
          document.body.style.overflow = "hidden";
          box.querySelector(".lb-close").focus();
        });
      });
    });

    box.querySelector(".lb-close").addEventListener("click", close);
    box.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
    box.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    document.addEventListener("keydown", function (e) {
      if (!box.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });
  }

  // Raffle ticket search
  var search = document.getElementById("ticket-search");
  if (search) {
    var rows = document.querySelectorAll(".tickets li");
    var count = document.getElementById("ticket-count");
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (li) {
        var hit = !q || li.textContent.toLowerCase().indexOf(q) !== -1;
        li.hidden = !hit;
        if (hit) shown++;
      });
      if (count) count.textContent = q ? shown + " matching tickets" : "";
    });
  }
})();
