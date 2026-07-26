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
    float repair=smoothstep(0.14,0.88,u);
    gutTube(col,p,0.76,0.18,t,0.4,mix(0.45,1.0,repair)*ae);
    for (int i=0;i<5;i++) {
        float fi=float(i)/4.0;
        vec2 wound=vec2(mix(-0.49,0.49,fi),gutCenterline(mix(-0.49,0.49,fi),t,0.4));
        float a=0.7+float(i)*1.2;
        vec2 axis=vec2(cos(a),sin(a))*0.055*(1.0-repair);
        gutNerve(col,p,wound-axis,wound+axis,GUT_RED,(1.0-repair)*ae);
        float local=saturate(repair*7.0-float(i));
        gutNeuron(col,p,wound,0.012+0.020*local,GUT_GREEN,t+float(i),local*ae);
        float ring=sdCircle(p-wound,0.055+0.025*repair);
        col+=GUT_GREEN*glow(ring,0.016)*local*0.18*ae;
    }
    float seal=abs(p.y-gutCenterline(p.x,t,0.4))-0.17;
    col+=GUT_GREEN*glow(seal,0.012)*repair*0.08*ae;
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
