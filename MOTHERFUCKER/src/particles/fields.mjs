export function combineFields(...fields) {
  return { sample(particle, context) {
    return fields.reduce((sum, field) => {
      const value = field.sample(particle, context);
      return { x:sum.x+(value.x ?? 0), y:sum.y+(value.y ?? 0) };
    }, { x:0, y:0 });
  }};
}

export function radialField({ cx, cy, strength = 20, inward = false }) {
  return { sample(particle) {
    const dx=cx-particle.x, dy=cy-particle.y, length=Math.hypot(dx,dy)||1, sign=inward?1:-1;
    return { x:sign*strength*dx/length, y:sign*strength*dy/length };
  }};
}

export function orbitalField({ cx, cy, strength = 18, radialPull = 0 }) {
  return { sample(particle) {
    const dx=particle.x-cx, dy=particle.y-cy, length=Math.hypot(dx,dy)||1;
    return { x:-dy/length*strength-dx*radialPull, y:dx/length*strength-dy*radialPull };
  }};
}

export function noiseField({ strength = 10, frequency = 0.01 }) {
  return { sample(particle, { time }) {
    const angle=Math.sin(particle.x*frequency+time*0.7)+Math.cos(particle.y*frequency*1.3-time*0.4);
    return { x:Math.cos(angle)*strength, y:Math.sin(angle)*strength };
  }};
}

export function pathFollowField({ points, strength = 50, attraction = 1.2 }) {
  return { sample(particle) {
    let best=0, bestDistance=Infinity;
    for (let i=0;i<points.length-1;i+=1) {
      const a=points[i], b=points[i+1], dx=b.x-a.x, dy=b.y-a.y, length2=dx*dx+dy*dy||1;
      const u=Math.max(0,Math.min(1,((particle.x-a.x)*dx+(particle.y-a.y)*dy)/length2));
      const px=a.x+dx*u, py=a.y+dy*u, d=Math.hypot(particle.x-px,particle.y-py);
      if (d<bestDistance) { bestDistance=d; best=i; }
    }
    const a=points[best], b=points[best+1], dx=b.x-a.x, dy=b.y-a.y, length=Math.hypot(dx,dy)||1;
    const midpoint={ x:(a.x+b.x)/2, y:(a.y+b.y)/2 };
    return { x:dx/length*strength+(midpoint.x-particle.x)*attraction, y:dy/length*strength+(midpoint.y-particle.y)*attraction };
  }};
}
