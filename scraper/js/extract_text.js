(() => {
  function visible(el) {
    const cs = getComputedStyle(el);
    if (!cs || cs.visibility === "hidden" || cs.display === "none") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  const sels = ["main","article","section","h1","h2","h3","h4","h5","h6","p"];
  const nodes = Array.from(document.querySelectorAll(sels.join(",")))
    .filter(visible)
    .map(n => n.innerText.trim())
    .filter(Boolean);
  const out = [];
  const seen = new Set();
  for (const line of nodes) {
    const norm = line.replace(/\s+/g, " ").slice(0, 200);
    if (!seen.has(norm)) {
      seen.add(norm);
      out.push(line);
    }
  }
  return out.join("\n");
})();
