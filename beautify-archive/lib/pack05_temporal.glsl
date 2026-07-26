// Pack 05: abstract temporal geometry on obsidian.
#ifndef PACK05_TEMPORAL_GLSL
#define PACK05_TEMPORAL_GLSL

const vec3 TIME_VOID=vec3(0.006,0.008,0.017);
const vec3 TIME_OBSIDIAN=vec3(0.018,0.024,0.046);
const vec3 TIME_GOLD=vec3(1.000,0.650,0.170);
const vec3 TIME_CYAN=vec3(0.070,0.790,0.940);
const vec3 TIME_VIOLET=vec3(0.500,0.230,0.940);
const vec3 TIME_CRIMSON=vec3(0.950,0.150,0.330);
const vec3 TIME_ASH=vec3(0.330,0.390,0.470);
const vec3 TIME_PEARL=vec3(0.900,0.940,1.000);

vec3 temporalBackground(vec2 uv, vec2 p, float time) {
    float strata=fbm(vec2(p.x*2.1,p.y*5.4)+vec2(time*0.012,0.0));
    float ink=fbmWarp(p*1.05+vec2(-time*0.008,time*0.005),time);
    vec3 col=mix(TIME_VOID,TIME_OBSIDIAN,0.52+0.38*ink);
    col+=TIME_VIOLET*pow(max(strata-0.63,0.0),3.0)*0.38;
    col+=TIME_CYAN*pow(max(ink-0.72,0.0),4.0)*0.18;
    return col*(0.68+0.32*vignette(uv));
}

void temporalLine(inout vec3 col, vec2 p, vec2 a, vec2 b, vec3 hue, float energy) {
    float d=sdSegment(p,a,b);
    col+=hue*(exp(-d*d/0.000018)*0.72+exp(-d*d/0.0014)*0.095)*energy;
}
void temporalNode(inout vec3 col, vec2 p, vec2 c, float radius, vec3 hue, float energy) {
    float d=length(p-c);
    col+=hue*exp(-d*d/(radius*radius))*energy;
    col+=TIME_PEARL*exp(-d*d/(radius*radius*0.055))*energy*0.88;
}
void temporalRing(inout vec3 col, vec2 p, vec2 c, float radius, float squash, vec3 hue, float energy) {
    float d=abs(length((p-c)/vec2(1.0,squash))-radius);
    col+=hue*(exp(-d*d/0.000025)*0.48+exp(-d*d/0.0019)*0.075)*energy;
}
void temporalArc(inout vec3 col, vec2 p, vec2 c, float radius, float squash,
                 float a0, float a1, vec3 hue, float reveal, float energy) {
    vec2 previous=c+vec2(cos(a0),sin(a0)*squash)*radius;
    for (int i=1;i<64;i++) {
        float q=float(i)/63.0;
        float a=mix(a0,a1,q);
        vec2 current=c+vec2(cos(a),sin(a)*squash)*radius;
        float shown=1.0-smoothstep(reveal,reveal+0.025,q);
        temporalLine(col,p,previous,current,hue,energy*shown);
        previous=current;
    }
}
void clockGlyph(inout vec3 col, vec2 p, vec2 c, float radius, float phase,
                vec3 hue, float energy) {
    temporalRing(col,p,c,radius,1.0,hue,energy);
    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0;
        vec2 v=vec2(cos(a),sin(a));
        temporalLine(col,p,c+v*radius*0.84,c+v*radius,hue,energy*0.45);
    }
    vec2 hand=vec2(cos(phase),sin(phase));
    temporalLine(col,p,c,c+hand*radius*0.72,TIME_PEARL,energy);
    temporalNode(col,p,c,radius*0.14,hue,energy);
}
float temporalWindow(vec2 p, vec2 center, vec2 halfSize, float softness) {
    return 1.0-smoothstep(-softness,softness,sdRoundBox(p-center,halfSize,0.025));
}
float inkDissolve(vec2 p, float progress, float time) {
    float torn=fbmWarp(p*3.1+vec2(time*0.018,-time*0.011),time);
    return smoothstep(progress-0.12,progress+0.12,torn+p.x*0.16);
}
vec3 temporalFinish(vec3 col, vec2 uv, vec2 fragCoord, float time) {
    col*=0.76+0.24*vignette(uv);
    col+=grain(fragCoord,time)*0.014;
    return filmic(col);
}

#endif
