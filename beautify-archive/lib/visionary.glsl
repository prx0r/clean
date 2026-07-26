// Advanced original primitives for the queue-era visionary shader packs.
// Technique study: LYGIA's granular architecture, not copied implementation.
#ifndef BEAUTIFY_VISIONARY_GLSL
#define BEAUTIFY_VISIONARY_GLSL

vec3 hash33(vec3 p) {
    p=fract(p*vec3(0.1031,0.1030,0.0973));
    p+=dot(p,p.yxz+33.33);
    return fract((p.xxy+p.yxx)*p.zyx);
}
float noise31(vec3 p) {
    vec3 i=floor(p), f=fract(p);
    f=f*f*(3.0-2.0*f);
    float n000=hash33(i).x;
    float n100=hash33(i+vec3(1,0,0)).x;
    float n010=hash33(i+vec3(0,1,0)).x;
    float n110=hash33(i+vec3(1,1,0)).x;
    float n001=hash33(i+vec3(0,0,1)).x;
    float n101=hash33(i+vec3(1,0,1)).x;
    float n011=hash33(i+vec3(0,1,1)).x;
    float n111=hash33(i+vec3(1,1,1)).x;
    return mix(
        mix(mix(n000,n100,f.x),mix(n010,n110,f.x),f.y),
        mix(mix(n001,n101,f.x),mix(n011,n111,f.x),f.y),
        f.z
    );
}
float fbm3(vec3 p) {
    float sum=0.0, amp=0.52;
    mat3 basis=mat3(
         0.00, 0.80, 0.60,
        -0.80, 0.36,-0.48,
        -0.60,-0.48, 0.64
    );
    for (int i=0;i<6;i++) {
        sum+=amp*noise31(p);
        p=basis*p*2.03+vec3(7.1,11.7,3.9);
        amp*=0.49;
    }
    return sum;
}
vec2 voronoi2(vec2 p) {
    vec2 cell=floor(p), local=fract(p);
    float nearest=9.0, second=9.0;
    for (int y=-1;y<=1;y++) for (int x=-1;x<=1;x++) {
        vec2 g=vec2(float(x),float(y));
        vec2 point=g+hash22(cell+g)-local;
        float d=dot(point,point);
        if (d<nearest) { second=nearest; nearest=d; }
        else if (d<second) second=d;
    }
    return sqrt(vec2(nearest,second));
}
vec2 kaleido(vec2 p, float sectors, float drift) {
    float radius=length(p);
    float angle=atan(p.y,p.x)+drift;
    float wedge=TAU/sectors;
    angle=abs(mod(angle+wedge*0.5,wedge)-wedge*0.5);
    return vec2(cos(angle),sin(angle))*radius;
}
vec2 logPolar(vec2 p) {
    return vec2(log(max(length(p),0.0001)),atan(p.y,p.x));
}

float sdSphere3(vec3 p,float r) { return length(p)-r; }
float sdBox3(vec3 p,vec3 b) {
    vec3 q=abs(p)-b;
    return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0);
}
float sdRoundBox3(vec3 p,vec3 b,float r) { return sdBox3(p,b)-r; }
float sdTorus3(vec3 p,vec2 radii) {
    vec2 q=vec2(length(p.xz)-radii.x,p.y);
    return length(q)-radii.y;
}
float sdCapsule3(vec3 p,vec3 a,vec3 b,float r) {
    vec3 pa=p-a, ba=b-a;
    float h=clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
    return length(pa-ba*h)-r;
}
float sdOctahedron3(vec3 p,float s) {
    p=abs(p);
    return (p.x+p.y+p.z-s)*0.5773502692;
}
float smoothUnion(float a,float b,float k) {
    float h=clamp(0.5+0.5*(b-a)/k,0.0,1.0);
    return mix(b,a,h)-k*h*(1.0-h);
}
float smoothSubtract(float a,float b,float k) {
    float h=clamp(0.5-0.5*(b+a)/k,0.0,1.0);
    return mix(b,-a,h)+k*h*(1.0-h);
}
mat3 rotateX(float a) {
    float c=cos(a),s=sin(a);
    return mat3(1,0,0,0,c,-s,0,s,c);
}
mat3 rotateY(float a) {
    float c=cos(a),s=sin(a);
    return mat3(c,0,s,0,1,0,-s,0,c);
}
mat3 cameraBasis(vec3 eye,vec3 target) {
    vec3 forward=normalize(target-eye);
    vec3 right=normalize(cross(forward,vec3(0,1,0)));
    return mat3(right,cross(right,forward),forward);
}

vec3 spectral(float x) {
    x=fract(x);
    vec3 c=0.56+0.44*cos(TAU*(x+vec3(0.02,0.35,0.68)));
    return pow(max(c,0.0),vec3(1.35));
}
vec3 blackbodyGold(float x) {
    return mix(vec3(0.18,0.015,0.003),vec3(1.45,0.72,0.16),saturate(x))
        +vec3(1.0,0.82,0.52)*pow(saturate(x),5.0);
}
float fresnelTerm(vec3 viewDir,vec3 normal,float power) {
    return pow(1.0-saturate(dot(-viewDir,normal)),power);
}
vec3 acesVision(vec3 x) {
    x=max(x,0.0);
    return saturate((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14));
}
vec3 visionaryFinish(vec3 color,vec2 uv,vec2 fragCoord,float time) {
    color*=0.76+0.24*vignette(uv);
    color+=grain(fragCoord,time)*0.012;
    return pow(acesVision(color),vec3(0.94));
}
void lightFilament(inout vec3 color,vec2 p,vec2 a,vec2 b,vec3 hue,float energy) {
    float d=sdSegment(p,a,b);
    color+=hue*(exp(-d*d/0.000014)*0.82+exp(-d*d/0.0018)*0.095)*energy;
}
void radiantNode(inout vec3 color,vec2 p,vec2 c,float radius,vec3 hue,float energy) {
    vec2 delta=p-c;
    float d2=dot(delta,delta);
    color+=hue*exp(-d2/(radius*radius))*energy;
    color+=vec3(1.0)*exp(-d2/(radius*radius*0.035))*energy;
}
float lensFlare(vec2 p,vec2 source) {
    vec2 q=p-source;
    float core=0.006/max(dot(q,q),0.006);
    float ray=pow(max(0.0,1.0-abs(q.x*q.y)*28.0),18.0);
    return core+ray*0.12;
}

#endif
