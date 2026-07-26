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
    float stress=pulse(smoothstep(0.04,0.71,u),0.18);
    float recover=smoothstep(0.56,0.95,u);
    float narrowed=mix(0.19,0.085,stress*(1.0-recover));
    gutTube(col,p,0.76,narrowed,t,0.1,mix(0.78,1.0,recover)*ae);
    float flare=fbmWarp(p*4.0+vec2(t*0.08),t);
    col+=GUT_RED*pow(flare,4.0)*stress*(1.0-recover)*0.34*ae;
    for (int i=0;i<7;i++) {
        float a=TAU*float(i)/7.0+t*0.34;
        vec2 edge=vec2(cos(a)*0.53,sin(a)*0.24);
        gutNerve(col,p,edge,vec2(0.0),GUT_RED,stress*(1.0-recover)*0.52);
    }
    gutVagus(col,p,vec2(0.0,-0.58),vec2(0.0,0.0),t,GUT_GREEN,recover*ae);
    for (int i=0;i<6;i++) {
        float travel=fract(t*0.12+float(i)/6.0);
        vec2 s=mix(vec2(0.0,-0.52),vec2(0.0,0.0),travel);
        gutSignal(col,p,s,0.018,GUT_GREEN,recover*ae);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
