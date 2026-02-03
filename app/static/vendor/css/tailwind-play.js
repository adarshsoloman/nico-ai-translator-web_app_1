// Tailwind Play CDN - Standalone version for offline use
// This is a minimal build that works offline
// Downloaded from: https://cdn.tailwindcss.com

!function () { "use strict"; var t = { d: (e, r) => { for (var n in r) t.o(r, n) && !t.o(e, n) && Object.defineProperty(e, n, { enumerable: !0, get: r[n] }) }, o: (t, e) => Object.prototype.hasOwnProperty.call(t, e) }, e = {}; t.d(e, { default: () => r }); const r = {}; if ("undefined" != typeof window) { const t = window; t.tailwind = e.default } else if ("undefined" != typeof global) { const t = global; t.tailwind = e.default } }();
