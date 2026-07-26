#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack03_bioluminescent.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=gutBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    gutTube(col,p,0.70,0.22,t,0.3,0.75*ae);
    for (int i=0;i<34;i++) {
        vec2 h=hash22(vec2(float(i),93.0));
        float x=mix(-0.58,0.58,h.x);
        vec2 c=vec2(x,gutCenterline(x,t,0.3)+mix(-0.14,0.14,h.y));
        float local=saturate(q*2.0-h.x*0.7);
        float angle=TAU*hash11(float(i)+7.0)+t*0.08;
        vec2 axis=vec2(cos(angle),sin(angle))*0.025;
        float rod=sdSegment(p,c-axis,c+axis);
        vec3 hue=(i%3==0)?GUT_AMBER:GUT_GREEN;
        col+=hue*(aaStroke(rod,0.008)*0.62+glow(rod,0.035)*0.11)*local*ae;
    }
    for (int i=0;i<7;i++) {
        float travel=fract(t*0.16+float(i)/7.0);
        float x=mix(-0.58,0.58,travel);
        vec2 s=vec2(x,gutCenterline(x,t,0.3)+0.10*sin(travel*TAU*3.0));
        gutSignal(col,p,s,0.022,(i%2==0)?GUT_AMBER:GUT_CYAN,q*ae);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
