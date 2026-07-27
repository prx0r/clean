export function boundsConstraint({ left, top, right, bottom, bounce = 0.4 }) {
  return { apply(particle) {
    if (particle.x<left){particle.x=left;particle.vx=Math.abs(particle.vx)*bounce;}
    if (particle.x>right){particle.x=right;particle.vx=-Math.abs(particle.vx)*bounce;}
    if (particle.y<top){particle.y=top;particle.vy=Math.abs(particle.vy)*bounce;}
    if (particle.y>bottom){particle.y=bottom;particle.vy=-Math.abs(particle.vy)*bounce;}
  }};
}

export function pathAttractorConstraint({ points, maximumDistance = 40, correction = 0.25 }) {
  return { apply(particle) {
    let closest=null, best=Infinity;
    for (const point of points) {
      const d=Math.hypot(particle.x-point.x,particle.y-point.y);
      if (d<best){best=d;closest=point;}
    }
    if (closest && best>maximumDistance) {
      particle.x+=(closest.x-particle.x)*correction;
      particle.y+=(closest.y-particle.y)*correction;
    }
  }};
}
