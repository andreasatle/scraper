(() => {
  function visible(el) {
    const cs = getComputedStyle(el);
    if (!cs || cs.visibility === "hidden" || cs.display === "none") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function getText(node) {
    return (node?.innerText || "").trim().replace(/\s+/g, " ");
  }

  const tables = Array.from(document.querySelectorAll("table"))
    .filter(visible)
    .map(tbl => {
      const headers = [];
      const headRows = tbl.tHead ? Array.from(tbl.tHead.rows) : [];
      for (const tr of headRows) {
        const cells = Array.from(tr.cells).map(getText);
        if (cells.some(Boolean)) headers.push(cells);
      }

      const bodyRows = [];
      const bodies = tbl.tBodies ? Array.from(tbl.tBodies) : [];
      for (const tb of bodies) {
        for (const tr of Array.from(tb.rows)) {
          const cells = Array.from(tr.cells).map(getText);
          if (cells.some(Boolean)) bodyRows.push(cells);
        }
      }

      return { headers, rows: bodyRows };
    })
    .filter(t => (t.headers.length + t.rows.length) > 0);

  return tables;
})();
