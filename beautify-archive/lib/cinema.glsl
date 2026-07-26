// Queue batch 3: reusable cinematic mathematics.
// Original implementations informed by the modular spirit of LYGIA and
// the generative vocabulary of The Book of Shaders.
#ifndef BEAUTIFY_CINEMA_GLSL
#define BEAUTIFY_CINEMA_GLSL

vec2 complexMul(vec2 a, vec2 b) {
    return vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x);
}

vec2 complexDiv(vec2 a, vec2 b) {
    float d=max(dot(b,b),0.00002);
    return vec2(a.x*b.x+a.y*b.y, a.y*b.x-a.x*b.y)/d;
}

// A controllable projective warp: finite, animated, and useful as a camera lens.
vec2 projectiveWarp(vec2 p, float bend, float angle) {
    vec2 a=0.34*bend*vec2(cos(angle),sin(angle));
    vec2 z=complexDiv(p-a,vec2(1.0,0.0)-complexMul(a,p));
    return z/(1.0+0.14*bend*dot(z,z));
}

vec2 curlFlow(vec2 p, float time) {
    const float e=0.018;
    float nx1=fbmWarp(p+vec2(e,0.0),time);
    float nx0=fbmWarp(p-vec2(e,0.0),time);
    float ny1=fbmWarp(p+vec2(0.0,e),time);
    float ny0=fbmWarp(p-vec2(0.0,e),time);
    return normalize(vec2(ny1-ny0,nx0-nx1)+vec2(0.0001));
}

float gyroidField(vec3 p, float scale) {
    p*=scale;
    return dot(sin(p),cos(p.yzx))/scale;
}

float waveInterference(vec2 p, float time) {
    float v=0.0;
    for (int i=0;i<5;i++) {
        float fi=float(i);
        vec2 source=0.72*vec2(cos(fi*2.399+time*0.07),sin(fi*1.731-time*0.05));
        v+=sin(length(p-source)*(10.0+fi*1.7)-time*(0.6+fi*0.08));
    }
    return v/5.0;
}

float phaseContour(float value, float frequency, float width) {
    float d=abs(fract(value*frequency)-0.5);
    return 1.0-smoothstep(width,width+max(fwidth(value*frequency),0.002),d);
}

float causticField(vec2 p, float time) {
    vec2 q=p;
    float sum=0.0;
    for (int i=0;i<4;i++) {
        float fi=float(i);
        q=abs(q)/max(dot(q,q),0.17)-vec2(0.82,0.74);
        q*=rot(0.24+fi*0.17+time*0.013);
        sum+=exp(-9.0*abs(length(q)-0.52-fi*0.035));
    }
    return sum*0.25;
}

vec2 hexCell(vec2 p) {
    const vec2 scale=vec2(1.0,1.7320508);
    vec2 a=mod(p,scale)-0.5*scale;
    vec2 b=mod(p-0.5*scale,scale)-0.5*scale;
    return dot(a,a)<dot(b,b)?a:b;
}

float hexEdge(vec2 p, float scale, float width) {
    vec2 h=hexCell(p*scale)/scale;
    vec2 q=abs(h);
    float d=max(q.x*0.8660254+q.y*0.5,q.y)-0.288675/scale;
    return aaStroke(d,width);
}

float sdRegularPolygon(vec2 p, float radius, float sides, float spin) {
    float a=atan(p.y,p.x)+spin;
    float sector=TAU/sides;
    return cos(floor(0.5+a/sector)*sector-a)*length(p)-radius;
}

float sdStar(vec2 p, float radius, float points, float sharpness, float spin) {
    float a=atan(p.y,p.x)+spin;
    float sector=TAU/points;
    float tooth=cos(floor(0.5+a/sector)*sector-a);
    float inner=mix(0.24,0.78,saturate(sharpness));
    float modulation=mix(inner,1.0,smoothstep(0.0,0.5,abs(fract(a/sector)-0.5)));
    return length(p)*tooth-radius*modulation;
}

float sdArcBand(vec2 p, float radius, float startAngle, float endAngle) {
    float a=atan(p.y,p.x);
    float mid=0.5*(startAngle+endAngle);
    float halfSpan=0.5*(endAngle-startAngle);
    float da=abs(mod(a-mid+PI,TAU)-PI)-halfSpan;
    float radial=abs(length(p)-radius);
    return max(radial,da*radius);
}

float logarithmicSpiral(vec2 p, float arms, float pitch, float time) {
    float r=max(length(p),0.0001);
    float a=atan(p.y,p.x);
    return abs(sin(arms*a-pitch*log(r)-time));
}

vec3 interferencePalette(float x, float phase) {
    return 0.48+0.52*cos(TAU*(x+phase+vec3(0.00,0.28,0.61)));
}

vec3 iridescentFilm(float phase, float facing) {
    vec3 c=interferencePalette(phase+0.34*(1.0-facing),0.08);
    return pow(max(c,0.0),vec3(1.25))*(0.55+0.65*facing);
}

vec3 pressurePalette(float heat) {
    return mix(vec3(0.015,0.025,0.065),vec3(0.18,0.015,0.08),saturate(heat))
        +blackbodyGold(pow(saturate(heat),1.8))*0.58;
}

vec3 bioglassPalette(float state) {
    vec3 cold=vec3(0.015,0.10,0.15);
    vec3 living=vec3(0.08,0.88,0.78);
    vec3 trace=vec3(1.15,0.48,0.18);
    return mix(cold,living,smoothstep(0.05,0.72,state))
        +trace*pow(saturate(state),6.0);
}

float depthFog(float distanceTravelled, float density) {
    return 1.0-exp(-distanceTravelled*density);
}

float softBeam(vec2 p, vec2 origin, vec2 direction, float spread, float lengthScale) {
    direction=normalize(direction);
    vec2 q=p-origin;
    float along=dot(q,direction);
    float across=abs(dot(q,vec2(-direction.y,direction.x)));
    float aperture=max(0.012,spread*max(along,0.0));
    return exp(-across*across/(aperture*aperture))
        *smoothstep(0.0,0.08,along)
        *exp(-max(along,0.0)*lengthScale);
}

float temporalEcho(vec2 p, vec2 center, vec2 velocity, float time, float spacing, float radius) {
    float value=0.0;
    for (int i=0;i<7;i++) {
        float fi=float(i);
        vec2 c=center-velocity*fi*spacing;
        float d=length(p-c)-radius*(1.0-0.055*fi);
        value+=exp(-d*d/(0.0012+fi*0.00038))*exp(-fi*0.33);
    }
    return value*(0.82+0.18*sin(time));
}

vec3 cinemaFinish(vec3 color, vec2 uv, vec2 fragCoord, float time, float bloom) {
    color+=max(color-0.72,0.0)*bloom;
    color*=0.72+0.28*vignette(uv);
    color+=grain(fragCoord,time)*0.009;
    return pow(acesVision(color),vec3(0.92));
}

#endif
