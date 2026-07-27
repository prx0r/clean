import { rgba } from "../../math.mjs";

export function orbRenderer({ color = "#f7df83", glow = 8, blend = "screen" } = {}) {
  return { draw(ctx, particles) {
    ctx.save(); ctx.globalCompositeOperation=blend;
    for (const p of particles) {
      const life=Math.max(0,1-p.age/p.life), alpha=p.alpha*life;
      const gradient=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.size*3);
      gradient.addColorStop(0,rgba(p.color ?? color,alpha));
      gradient.addColorStop(1,rgba(p.color ?? color,0));
      ctx.fillStyle=gradient; ctx.shadowColor=p.color ?? color; ctx.shadowBlur=glow;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.size*3,0,Math.PI*2); ctx.fill();
    }
    ctx.restore();
  }};
}

export function trailRenderer({ color = "#f7df83", width = 1.4, blend = "screen" } = {}) {
  return { draw(ctx, particles) {
    ctx.save(); ctx.globalCompositeOperation=blend; ctx.lineCap="round";
    for (const p of particles) {
      if (!p.trail?.length) continue;
      ctx.beginPath(); ctx.moveTo(p.trail[0].x,p.trail[0].y);
      for (const q of p.trail.slice(1)) ctx.lineTo(q.x,q.y);
      ctx.strokeStyle=rgba(p.color ?? color,0.45*Math.max(0,1-p.age/p.life));
      ctx.lineWidth=width; ctx.stroke();
    }
    ctx.restore();
  }};
}
export function compositeParticleRenderer(...renderers) {
  return { draw(ctx, particles, context) { for (const renderer of renderers) renderer.draw(ctx,particles,context); } };
}
