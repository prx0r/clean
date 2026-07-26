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
    gutTube(col,p,0.76,0.20,t,0.0,0.65*ae);
    for (int i=0;i<7;i++) {
        float fi=float(i)/6.0;
        float emerge=saturate(q*5.0-float(i)*0.52);
        float x=mix(-0.55,0.55,fi);
        vec2 seed=vec2(x,gutCenterline(x,t,0.0)+0.08*sin(t*0.3+float(i)));
        float radius=mix(0.006,0.034,easeOut(emerge));
        gutSignal(col,p,seed,radius,GUT_AMBER,emerge*ae);
        gutNeuron(col,p,seed,radius,mix(GUT_AMBER,GUT_CYAN,emerge),t*0.2+float(i),emerge*ae);
        float birthRing=sdCircle(p-seed,radius*(2.0+0.4*sin(t+float(i))));
        col+=GUT_GREEN*glow(birthRing,0.016)*emerge*0.16*ae;
    }
    float bloom=smoothstep(0.62,0.95,u);
    for (int i=0;i<5;i++) {
        float ring=sdEllipse(p,vec2(0.24+float(i)*0.11,0.12+float(i)*0.065));
        col+=GUT_GREEN*glow(ring,0.018)*bloom*0.055*ae;
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
