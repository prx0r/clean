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
    vec2 gp=p-vec2(0.0,0.34);
    gutTube(col,gp,0.62,0.11,t,1.1,0.65*ae);
    gutVagus(col,p,vec2(0.0,-0.64),vec2(0.0,0.18),t,GUT_BLUE,0.32);
    for (int i=0;i<13;i++) {
        float fi=float(i)/12.0;
        float travel=easeOut(saturate(q*1.35-fi*0.33));
        vec2 start=vec2(0.0,-0.61+fi*0.10);
        vec2 target=vec2(0.48*sin(fi*PI*1.3),0.30+0.05*sin(fi*TAU));
        vec2 c=mix(start,target,travel);
        c.x+=0.018*sin(t+float(i));
        gutSignal(col,p,c,0.018+0.010*travel,mix(GUT_BLUE,GUT_CYAN,travel),ae*(0.4+0.6*travel));
        if (travel>0.7) gutNeuron(col,p,c,0.018,GUT_CYAN,float(i),travel*0.44);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
