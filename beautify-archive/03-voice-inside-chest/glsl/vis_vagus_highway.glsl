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
    vec2 brain=vec2(0.0,-0.48), gut=vec2(0.0,0.46);
    float skull=sdEllipse(p-brain,vec2(0.19,0.13));
    col+=GUT_BLUE*(aaFill(skull)*0.12+aaStroke(skull,0.008)*0.62+glow(skull,0.07)*0.12)*ae;
    vec2 gp=p-gut;
    gutTube(col,gp,0.48,0.12,t,0.7,ae);
    gutVagus(col,p,brain+vec2(0.0,0.13),gut-vec2(0.0,0.10),t,GUT_AMBER,q*ae);
    for (int i=0;i<4;i++) {
        float fi=(float(i)+0.5)/4.0;
        vec2 b=vec2((float(i)-1.5)*0.08,mix(-0.28,0.25,fi));
        gutNerve(col,p,b,b+vec2(sign(float(i)-1.5)*0.19,0.08*sin(fi*TAU)),GUT_CYAN,q*0.32);
    }
    float travel=easeInOut(smoothstep(0.22,0.95,u));
    vec2 signal=mix(gut-vec2(0.0,0.09),brain+vec2(0.0,0.12),travel);
    signal.x+=0.035*sin(travel*TAU*3.0+t*0.8)*sin(PI*travel);
    gutSignal(col,p,signal,0.035,GUT_AMBER,q*ae);
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
