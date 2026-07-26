// Pack 04: wet dream-watercolor.
#ifndef PACK04_WATERCOLOR_GLSL
#define PACK04_WATERCOLOR_GLSL

const vec3 DREAM_NIGHT=vec3(0.025,0.026,0.090);
const vec3 DREAM_PAPER=vec3(0.180,0.145,0.260);
const vec3 DREAM_INDIGO=vec3(0.160,0.130,0.720);
const vec3 DREAM_COBALT=vec3(0.060,0.570,0.940);
const vec3 DREAM_ROSE=vec3(0.920,0.180,0.560);
const vec3 DREAM_GOLD=vec3(1.000,0.660,0.180);
const vec3 DREAM_MINT=vec3(0.180,0.900,0.650);
const vec3 DREAM_PEARL=vec3(0.940,0.890,1.000);

vec3 dreamBackground(vec2 uv, vec2 p, float time) {
    float paper=fbm(p*8.0+vec2(11.0,4.0));
    float tide=fbmWarp(p*1.2+vec2(time*0.018,-time*0.012),time);
    vec3 col=mix(DREAM_NIGHT,DREAM_PAPER,tide*0.42);
    col+=mix(DREAM_INDIGO,DREAM_ROSE,tide)*pow(tide,3.5)*0.10;
    col+=vec3(paper-0.5)*0.035;
    return col*(0.62+0.38*vignette(uv));
}

float pigmentShape(vec2 p, vec2 c, float radius, float seed, float time) {
    vec2 q=p-c;
    float a=atan(q.y,q.x);
    float edge=radius*(1.0
        +0.10*sin(a*5.0+seed)
        +0.055*sin(a*11.0-time*0.12+seed*2.0)
        +0.035*noise21(vec2(a*2.0,seed)));
    return length(q)-edge;
}
void pigmentBloom(inout vec3 col, vec2 p, vec2 c, float radius, vec3 hue, float seed, float energy, float time) {
    float d=pigmentShape(p,c,radius,seed,time);
    float wet=fbmWarp((p-c)*5.0+seed,time);
    float body=aaFill(d);
    float rim=aaStroke(d,0.009+0.008*wet);
    col=mix(col,hue,body*energy*(0.12+0.16*wet));
    col+=hue*(rim*0.22+glow(d,0.065)*0.05)*energy;
}
void dreamDot(inout vec3 col, vec2 p, vec2 c, float size, vec3 hue, float energy) {
    float d=length(p-c);
    col+=hue*exp(-d*d/(size*size))*energy;
    col+=DREAM_PEARL*exp(-d*d/(size*size*0.07))*energy*0.64;
}
void watercolorLine(inout vec3 col, vec2 p, vec2 a, vec2 b, vec3 hue, float seed, float energy) {
    float d=sdSegment(p,a,b);
    float bleed=0.70+0.30*noise21(p*29.0+seed);
    col+=hue*(exp(-d*d/0.000045)*0.34+exp(-d*d/0.0016)*0.075)*bleed*energy;
}
vec2 dreamCurve(float x, float time, float phase, float amplitude) {
    return vec2(x,
        amplitude*sin(x*6.0+time*0.47+phase)
       +amplitude*0.32*sin(x*15.0-time*0.23+phase*1.7));
}
void dreamThread(inout vec3 col, vec2 p, vec2 center, float lengthLine, float amplitude, vec3 hue, float reveal, float time, float phase) {
    vec2 previous=center+dreamCurve(-lengthLine,time,phase,amplitude);
    for (int i=1;i<64;i++) {
        float q=float(i)/63.0;
        vec2 current=center+dreamCurve(mix(-lengthLine,lengthLine,q),time,phase,amplitude);
        float visible=1.0-smoothstep(reveal,reveal+0.035,q);
        watercolorLine(col,p,previous,current,hue,phase,visible);
        previous=current;
    }
}
void dreamRipple(inout vec3 col, vec2 p, vec2 c, float radius, vec3 hue, float energy, float time) {
    float e=length((p-c)/vec2(1.0,0.62));
    float bands=pow(0.5+0.5*cos(e*38.0-time*0.8),12.0);
    col+=hue*bands*exp(-e*e/(radius*radius))*energy*0.28;
}
vec3 dreamFinish(vec3 col, vec2 uv, vec2 fragCoord, float time) {
    col*=0.80+0.20*vignette(uv);
    col+=grain(fragCoord,time)*0.020;
    return filmic(col);
}

#endif
