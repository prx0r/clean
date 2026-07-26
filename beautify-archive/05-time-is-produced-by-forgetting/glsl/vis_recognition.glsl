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
    for (int i=0;i<8;i++) {
        float fi=float(i), a=TAU*fi/8.0;
        vec2 offset=vec2(cos(a*1.7),sin(a*2.3))*0.16*(1.0-q);
        float radius=0.10+fi*0.068;
        temporalArc(col,p,offset,radius,0.62,-PI*0.84,PI*0.84,
                    mix(TIME_VIOLET,TIME_GOLD,fi/7.0),q,ae*(0.72-fi*0.058));
    }
    for (int i=0;i<7;i++) {
        float x=mix(-0.57,0.57,float(i)/6.0);
        temporalNode(col,p,vec2(x,0.0),0.024,TIME_CYAN,q*ae*0.78);
    }
    temporalLine(col,p,vec2(-0.62,0.0),vec2(0.62,0.0),TIME_CYAN,q*ae*0.62);
    temporalNode(col,p,vec2(0.0),0.068+0.016*u_audioBeat,TIME_GOLD,q*ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
