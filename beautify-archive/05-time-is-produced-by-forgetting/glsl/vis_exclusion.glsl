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
    vec2 focus=vec2(0.14,-0.04);
    float aperture=mix(0.82,0.16,q);
    for (int i=0;i<36;i++) {
        vec2 h=hash22(vec2(float(i),8.0));
        vec2 c=(h*2.0-1.0)*vec2(0.78,0.47);
        float selected=1.0-smoothstep(aperture,aperture+0.13,length(c-focus));
        vec3 hue=mix(TIME_VIOLET,TIME_CYAN,h.x);
        temporalNode(col,p,c,0.018,hue,ae*mix(0.035,0.90,selected));
    }
    temporalRing(col,p,focus,aperture,1.0,TIME_GOLD,q*ae);
    temporalNode(col,p,focus,0.050,TIME_PEARL,q*ae);
    float outside=smoothstep(aperture,aperture+0.20,length(p-focus));
    col=mix(col,col*0.24,outside*q*0.74);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
