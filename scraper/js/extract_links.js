(() => {
  function visible(el) {
    const cs = getComputedStyle(el);
    if (!cs || cs.visibility === "hidden" || cs.display === "none") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  return Array.from(document.querySelectorAll("a[href]"))
    .filter(visible)
    .map(a => ({ text: a.innerText.trim().replace(/\s+/g," "), href: a.getAttribute("href") }));
})();
