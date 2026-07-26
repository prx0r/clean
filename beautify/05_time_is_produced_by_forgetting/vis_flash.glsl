#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack05_temporal.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=temporalBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    float strike=exp(-pow((u-0.54)/0.13,2.0));
    for (int i=0;i<32;i++) {
        float a=TAU*hash11(float(i)*4.17), len=mix(0.16,0.82,hash11(float(i)+2.4))*q;
        vec2 v=vec2(cos(a),sin(a))*len;
        temporalLine(col,p,vec2(0.0),v,mix(TIME_GOLD,TIME_PEARL,hash11(float(i))),strike*ae*0.62);
    }
    for (int i=0;i<8;i++) {
        float r=0.05+float(i)*0.080*q;
        temporalRing(col,p,vec2(0.0),r,0.64,TIME_GOLD,strike*ae*(0.82-float(i)*0.08));
    }
    float core=exp(-dot(p,p)/(0.035+0.18*strike));
    col+=mix(TIME_GOLD,TIME_PEARL,core)*core*strike*ae*1.45;
    temporalNode(col,p,vec2(0.0),0.075,TIME_PEARL,strike*ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
