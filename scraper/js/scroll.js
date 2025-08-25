(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let prev = 0;
  let stableCount = 0;
  const maxStable = 3;
  const tries = __TRIES__;
  for (let i = 0; i < tries; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(__WAIT_MS__);
    const h = document.body.scrollHeight;
    if (__UNTIL_END__) {
      if (h === prev) {
        stableCount++;
        if (stableCount >= maxStable) break;
      } else {
        stableCount = 0;
      }
      prev = h;
    }
  }
})();
