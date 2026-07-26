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
    gutTube(col,p,0.62,0.13,t,0.6,0.42*ae);
    vec2 center=vec2(0.0,0.0);
    for (int i=0;i<8;i++) {
        float a=TAU*float(i)/8.0+t*0.10;
        vec2 c=center+vec2(cos(a)*0.57,sin(a)*0.35);
        float activation=0.62+0.38*sin(t*1.3+float(i)*1.4);
        vec3 hue=mix(GUT_CYAN,GUT_GREEN,float(i%2));
        gutNeuron(col,p,c,0.030,hue,a,activation*q*ae);
        gutNerve(col,p,c,center,GUT_AMBER,smoothstep(0.28,0.74,u)*activation*0.30);
    }
    float hub=smoothstep(0.35,0.86,u);
    gutNeuron(col,p,center,0.050,GUT_AMBER,t*0.2,hub*ae);
    for (int i=0;i<6;i++) {
        float travel=fract(t*0.13+float(i)/6.0);
        float a=TAU*float(i)/6.0+t*0.1;
        vec2 edge=vec2(cos(a)*0.57,sin(a)*0.35);
        gutSignal(col,p,mix(edge,center,travel),0.017,GUT_AMBER,hub*ae);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
