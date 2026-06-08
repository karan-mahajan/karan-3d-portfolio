/**
 * One-shot confetti + streamer celebration that rains from the top of the
 * screen. Used as the unmistakable "you did something!" payoff when a visitor
 * sends a like (the sky spark is the ambient link; this is the immediate
 * on-screen reward). Pure DOM + CSS keyframes — cheap, GC-friendly, and fired
 * rarely (a like is once per visitor), so no canvas/rAF loop is needed.
 */
const COLORS = [
  "#ffd86a", "#ff9944", "#ff8866", "#fbbf24", "#ffe6b8",
  "#ffb347", "#f6a945", "#7ed0a0", "#7fb8ff",
];

export class Confetti {
  /** Rain `count` pieces (a quarter render as longer curling streamers). */
  burst({ count = 80 } = {}) {
    const root = document.createElement("div");
    root.className = "confetti-root";

    for (let i = 0; i < count; i++) {
      const p = document.createElement("i");
      const streamer = Math.random() < 0.28;
      p.className = streamer ? "confetti-piece streamer" : "confetti-piece";
      const dx = (Math.random() * 2 - 1) * 26; // horizontal drift (vw)
      const spin = (Math.random() * 2 - 1) * 900; // total rotation (deg)
      p.style.left = `${Math.random() * 100}vw`;
      p.style.setProperty("--dx", `${dx}vw`);
      p.style.setProperty("--spin", `${spin}deg`);
      p.style.animationDuration = `${2.6 + Math.random() * 1.8}s`;
      p.style.animationDelay = `${Math.random() * 0.35}s`;
      p.style.background = COLORS[(Math.random() * COLORS.length) | 0];
      if (streamer) p.style.height = `${18 + Math.random() * 26}px`;
      root.appendChild(p);
    }

    document.body.appendChild(root);
    // Longest piece = ~4.4s fall + 0.35s delay; clear comfortably after.
    setTimeout(() => root.remove(), 5200);
  }
}
