// Shared GLSL 3.30 primitives for every beautify pack.
// Self-contained by design: the repository can compile without vendored Lygia.
#ifndef BEAUTIFY_PRIMITIVES_GLSL
#define BEAUTIFY_PRIMITIVES_GLSL

#define PI 3.14159265358979323846
#define TAU 6.28318530717958647692

float saturate(float x) { return clamp(x, 0.0, 1.0); }
vec2 saturate(vec2 x) { return clamp(x, 0.0, 1.0); }
vec3 saturate(vec3 x) { return clamp(x, 0.0, 1.0); }
float easeInOut(float x) {
    x = saturate(x);
    return x < 0.5 ? 4.0*x*x*x : 1.0-pow(-2.0*x+2.0, 3.0)*0.5;
}
float easeOut(float x) { return 1.0-pow(1.0-saturate(x), 3.0); }
float easeIn(float x) { x=saturate(x); return x*x*x; }
float bell(float x) { return sin(PI*saturate(x)); }
float pulse(float x, float width) {
    return smoothstep(0.0, width, x) * (1.0-smoothstep(1.0-width, 1.0, x));
}

mat2 rot(float a) {
    float c=cos(a), s=sin(a);
    return mat2(c,-s,s,c);
}
vec2 aspectUV(vec2 uv, vec2 resolution) {
    vec2 p=uv*2.0-1.0;
    p.x*=resolution.x/resolution.y;
    return p;
}

float hash11(float p) {
    p=fract(p*0.1031);
    p*=p+33.33;
    p*=p+p;
    return fract(p);
}
float hash21(vec2 p) {
    vec3 p3=fract(vec3(p.xyx)*0.1031);
    p3+=dot(p3,p3.yzx+33.33);
    return fract((p3.x+p3.y)*p3.z);
}
vec2 hash22(vec2 p) {
    float n=hash21(p);
    return vec2(n,hash21(p+n+19.19));
}
float noise21(vec2 p) {
    vec2 i=floor(p), f=fract(p);
    vec2 w=f*f*(3.0-2.0*f);
    float a=hash21(i);
    float b=hash21(i+vec2(1.0,0.0));
    float c=hash21(i+vec2(0.0,1.0));
    float d=hash21(i+vec2(1.0,1.0));
    return mix(mix(a,b,w.x),mix(c,d,w.x),w.y);
}
float fbm(vec2 p) {
    float f=0.0, a=0.5;
    mat2 m=mat2(0.80,0.60,-0.60,0.80);
    for (int i=0;i<6;i++) {
        f+=a*noise21(p);
        p=m*p*2.03+vec2(11.7,7.9);
        a*=0.5;
    }
    return f;
}
float fbmWarp(vec2 p, float time) {
    vec2 q=vec2(fbm(p+vec2(0.0,time*0.07)),fbm(p+vec2(5.2,1.3)-time*0.05));
    vec2 r=vec2(fbm(p+3.8*q+vec2(1.7,9.2)),fbm(p+3.8*q+vec2(8.3,2.8)));
    return fbm(p+4.2*r);
}
float ridgedFbm(vec2 p) {
    float n=fbm(p);
    return 1.0-abs(2.0*n-1.0);
}

float sdCircle(vec2 p, float r) { return length(p)-r; }
float sdEllipse(vec2 p, vec2 ab) {
    p=abs(p);
    if (p.x>p.y) { p=p.yx; ab=ab.yx; }
    float l=ab.y*ab.y-ab.x*ab.x;
    float m=ab.x*p.x/l;
    float m2=m*m;
    float n=ab.y*p.y/l;
    float n2=n*n;
    float c=(m2+n2-1.0)/3.0;
    float c3=c*c*c;
    float q=c3+m2*n2*2.0;
    float d=c3+m2*n2;
    float g=m+m*n2;
    float co;
    if (d<0.0) {
        float h=acos(q/c3)/3.0;
        float s=cos(h);
        float t=sin(h)*sqrt(3.0);
        float rx=s+t;
        float ry=s-t;
        co=(ry+sign(l)*rx+abs(g)/(rx*ry)-m)/2.0;
    } else {
        float h=2.0*m*n*sqrt(d);
        float s=sign(q+h)*pow(abs(q+h),1.0/3.0);
        float u=sign(q-h)*pow(abs(q-h),1.0/3.0);
        float rx=-s-u-c*4.0+2.0*m2;
        float ry=(s-u)*sqrt(3.0);
        float rm=sqrt(rx*rx+ry*ry);
        co=(ry/sqrt(rm-rx)+2.0*g/rm-m)/2.0;
    }
    float si=sqrt(1.0-co*co);
    vec2 r=ab*vec2(co,si);
    return length(r-p)*sign(p.y-r.y);
}
float sdBox(vec2 p, vec2 b) {
    vec2 d=abs(p)-b;
    return length(max(d,0.0))+min(max(d.x,d.y),0.0);
}
float sdRoundBox(vec2 p, vec2 b, float r) { return sdBox(p,b-r)-r; }
float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa=p-a, ba=b-a;
    float h=saturate(dot(pa,ba)/dot(ba,ba));
    return length(pa-ba*h);
}
float sdRing(vec2 p, float r, float w) { return abs(length(p)-r)-w; }
float sdVesica(vec2 p, float r, float d) {
    p=abs(p);
    float b=sqrt(max(r*r-d*d,0.0));
    return ((p.y-b)*d>p.x*b)
        ? length(p-vec2(0.0,b))
        : length(p-vec2(-d,0.0))-r;
}

float aaFill(float d) {
    float w=max(fwidth(d),0.0007);
    return 1.0-smoothstep(-w,w,d);
}
float aaStroke(float d, float width) {
    float w=max(fwidth(d),0.0007);
    return 1.0-smoothstep(width-w,width+w,abs(d));
}
float glow(float d, float radius) {
    return exp(-max(abs(d),0.0)*max(abs(d),0.0)/(radius*radius));
}
float glowPoint(vec2 p, vec2 c, float radius) {
    vec2 d=p-c;
    return exp(-dot(d,d)/(radius*radius));
}
float glowLine(vec2 p, vec2 a, vec2 b, float radius) {
    float d=sdSegment(p,a,b);
    return exp(-(d*d)/(radius*radius));
}

vec3 screenBlend(vec3 base, vec3 light) { return 1.0-(1.0-base)*(1.0-light); }
vec3 softLight(vec3 base, vec3 blend) {
    return mix(
        2.0*base*blend+base*base*(1.0-2.0*blend),
        sqrt(max(base,0.0))*(2.0*blend-1.0)+2.0*base*(1.0-blend),
        step(0.5,blend)
    );
}
vec3 cosinePalette(float x, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a+b*cos(TAU*(c*x+d));
}
vec3 filmic(vec3 x) {
    x=max(vec3(0.0),x-0.004);
    return saturate((x*(6.2*x+0.5))/(x*(6.2*x+1.7)+0.06));
}
float vignette(vec2 uv) {
    vec2 q=uv*(1.0-uv);
    return pow(saturate(16.0*q.x*q.y),0.18);
}
float grain(vec2 fragCoord, float time) {
    return hash21(fragCoord+fract(time)*vec2(113.1,317.7))-0.5;
}

vec3 compositeGlow(vec3 col, vec3 lightColor, float energy) {
    return col+lightColor*energy;
}
float audioEnergy(float volume, float beat) {
    return 0.72+0.55*saturate(volume)+0.45*saturate(beat);
}

#endif
