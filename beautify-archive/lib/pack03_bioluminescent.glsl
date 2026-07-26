// Pack 03: abyssal bioluminescent anatomy.
#ifndef PACK03_BIOLUMINESCENT_GLSL
#define PACK03_BIOLUMINESCENT_GLSL

const vec3 GUT_ABYSS=vec3(0.002,0.018,0.028);
const vec3 GUT_DEEP=vec3(0.008,0.075,0.092);
const vec3 GUT_CYAN=vec3(0.030,0.930,0.920);
const vec3 GUT_BLUE=vec3(0.080,0.380,1.000);
const vec3 GUT_AMBER=vec3(1.000,0.620,0.100);
const vec3 GUT_GREEN=vec3(0.180,1.000,0.520);
const vec3 GUT_RED=vec3(1.000,0.090,0.210);
const vec3 GUT_PEARL=vec3(0.740,1.000,0.960);

vec3 gutBackground(vec2 uv, vec2 p, float time) {
    float current=fbmWarp(p*1.45+vec2(0.0,time*0.025),time);
    float depth=saturate(0.58-0.34*p.y);
    vec3 col=mix(GUT_ABYSS,GUT_DEEP,current*0.55);
    col+=vec3(0.0,0.08,0.10)*pow(current,4.0)*depth;
    for (int i=0;i<24;i++) {
        vec2 h=hash22(vec2(float(i),31.0));
        vec2 s=(h*2.0-1.0)*vec2(0.95,0.65);
        s.y=mod(s.y+t*(0.008+0.012*h.x)+0.72,1.44)-0.72;
        col+=GUT_CYAN*glowPoint(p,s,0.004+0.008*h.y)*0.055;
    }
    return col*(0.58+0.42*vignette(uv));
}

float gutCenterline(float x, float time, float phase) {
    return 0.055*sin(x*5.2+time*0.55+phase)
         + 0.025*sin(x*11.0-time*0.31+phase*1.7);
}
float gutTubeSdf(vec2 p, float halfLength, float width, float time, float phase) {
    float y=gutCenterline(p.x,time,phase);
    float body=abs(p.y-y)-width*(1.0+0.09*sin(p.x*9.0-time));
    float caps=abs(p.x)-halfLength;
    return max(body,caps);
}
void gutTube(inout vec3 col, vec2 p, float halfLength, float width, float time, float phase, float energy) {
    float d=gutTubeSdf(p,halfLength,width,time,phase);
    float inside=aaFill(d);
    float caustic=fbmWarp(vec2(p.x*4.0,(p.y-gutCenterline(p.x,time,phase))*16.0),time);
    col=mix(col,mix(GUT_DEEP,GUT_BLUE,0.13+0.12*caustic),inside*0.74);
    col+=GUT_CYAN*(aaStroke(d,0.008)*0.62+glow(d,0.055)*0.10)*energy;
    float inner=abs(p.y-gutCenterline(p.x,time,phase))-width*0.54;
    col+=GUT_BLUE*glow(inner,0.018)*inside*0.12;
}

void gutSignal(inout vec3 col, vec2 p, vec2 c, float size, vec3 hue, float energy) {
    float d=length(p-c);
    col+=hue*exp(-d*d/(size*size))*energy;
    col+=GUT_PEARL*exp(-d*d/(size*size*0.09))*energy*0.75;
}
void gutNerve(inout vec3 col, vec2 p, vec2 a, vec2 b, vec3 hue, float energy) {
    float d=sdSegment(p,a,b);
    col+=hue*(exp(-d*d/0.000055)*0.42+exp(-d*d/0.0014)*0.08)*energy;
}
void gutNeuron(inout vec3 col, vec2 p, vec2 c, float radius, vec3 hue, float phase, float energy) {
    float d=sdCircle(p-c,radius);
    col+=hue*(aaFill(d)*0.18+aaStroke(d,0.006)*0.72+glow(d,0.05)*0.15)*energy;
    for (int i=0;i<6;i++) {
        float a=TAU*float(i)/6.0+phase;
        float reach=radius*(2.2+0.55*sin(phase*1.7+float(i)));
        gutNerve(col,p,c+vec2(cos(a),sin(a))*radius,c+vec2(cos(a),sin(a))*reach,hue,energy*0.38);
    }
    gutSignal(col,p,c,radius*0.45,GUT_PEARL,energy);
}
void gutVagus(inout vec3 col, vec2 p, vec2 a, vec2 b, float time, vec3 hue, float energy) {
    vec2 previous=a;
    for (int i=1;i<48;i++) {
        float q=float(i)/47.0;
        vec2 current=mix(a,b,q);
        current.x+=0.035*sin(q*TAU*3.0+time*0.8)*sin(PI*q);
        gutNerve(col,p,previous,current,hue,energy);
        previous=current;
    }
}
vec3 gutFinish(vec3 col, vec2 uv, vec2 fragCoord, float time) {
    col*=0.80+0.20*vignette(uv);
    col+=grain(fragCoord,time)*0.012;
    return filmic(col);
}

#endif
