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
    gutTube(col,p,0.76,0.18,t,0.5,ae);
    float wave=mix(-0.62,0.62,easeInOut(smoothstep(0.08,0.85,u)));
    float centerY=gutCenterline(wave,t,0.5);
    vec2 c=vec2(wave,centerY);
    float contraction=exp(-pow((p.x-wave)/0.085,2.0));
    float tubeY=abs(p.y-gutCenterline(p.x,t,0.5));
    col+=mix(GUT_RED,GUT_CYAN,smoothstep(0.48,0.82,u))
        *contraction*exp(-tubeY*tubeY/0.015)*0.48*ae;
    for (int i=0;i<9;i++) {
        float a=TAU*float(i)/9.0+t*0.4;
        vec2 s=c+vec2(cos(a)*0.075,sin(a)*0.125);
        gutSignal(col,p,s,0.016,mix(GUT_RED,GUT_AMBER,q),q*ae);
    }
    vec2 autonomous=c+vec2(0.0,-0.25);
    gutNeuron(col,p,autonomous,0.035,GUT_AMBER,t,q*ae);
    gutNerve(col,p,autonomous,c,GUT_AMBER,q*0.52);
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
