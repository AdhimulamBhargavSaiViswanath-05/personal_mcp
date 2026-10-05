(function () {
  "use strict";

  const RENDER_HEALTH = "https://personal-mcp-husu.onrender.com/health";
  const HEALTH_FALLBACK = {
    ok: true,
    service: "personal-mcp",
    version: "v0",
    transport: "streamable-http",
  };
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function initGrid() {
    const canvas = document.getElementById("grid-canvas");
    if (!canvas || reducedMotion) return;

    const ctx = canvas.getContext("2d");
    let w = 0;
    let h = 0;
    const nodes = [];

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
      nodes.length = 0;
      const count = Math.min(48, Math.floor((w * h) / 28000));
      for (let i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.35,
          vy: (Math.random() - 0.5) * 0.35,
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = "rgba(56, 189, 248, 0.06)";
      const step = 48;
      for (let x = 0; x < w; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        a.x += a.vx;
        a.y += a.vy;
        if (a.x < 0 || a.x > w) a.vx *= -1;
        if (a.y < 0 || a.y > h) a.vy *= -1;

        ctx.fillStyle = "rgba(167, 139, 250, 0.85)";
        ctx.beginPath();
        ctx.arc(a.x, a.y, 1.8, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dist = Math.hypot(a.x - b.x, a.y - b.y);
          if (dist < 120) {
            ctx.strokeStyle = `rgba(56, 189, 248, ${0.15 * (1 - dist / 120)})`;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    }

    window.addEventListener("resize", resize);
    resize();
    draw();
  }

  function showTerminal(data, animate) {
    const el = document.getElementById("typed-output");
    if (!el) return;
    const text = JSON.stringify(data, null, 2);
    if (!animate || reducedMotion) {
      el.textContent = text;
      return;
    }
    let i = 0;
    function tick() {
      if (i <= text.length) {
        el.textContent = text.slice(0, i);
        i++;
        setTimeout(tick, 10 + Math.random() * 12);
      }
    }
    tick();
  }

  async function checkHealth() {
    const pill = document.getElementById("health-pill");
    const label = document.getElementById("health-label");
    if (!pill || !label) return;

    try {
      const res = await fetch(RENDER_HEALTH, { mode: "cors", cache: "no-store" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      pill.classList.add("ok");
      label.textContent =
        "Render live · " + (data.service || "personal-mcp") + " · " + (data.version || "v0");
      showTerminal(data, true);
    } catch {
      pill.classList.add("err");
      label.textContent =
        "Could not reach Render from browser — open /health directly (cold start or redeploy CORS)";
      showTerminal(HEALTH_FALLBACK, false);
    }
  }

  document.querySelectorAll("[data-tilt]").forEach((card) => {
    if (reducedMotion) return;
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      card.style.transform = `perspective(600px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-4px)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });

  initGrid();
  checkHealth();
})();
