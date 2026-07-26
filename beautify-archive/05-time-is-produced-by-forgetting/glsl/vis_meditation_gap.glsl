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
    float breath=0.5+0.5*sin(t*0.45);
    temporalLine(col,p,vec2(-0.72,0.0),vec2(-0.13,0.0),TIME_VIOLET,q*ae*0.72);
    temporalLine(col,p,vec2(0.13,0.0),vec2(0.72,0.0),TIME_CYAN,q*ae*0.72);
    for (int i=0;i<5;i++) {
        float fi=float(i), r=0.14+fi*0.080+breath*0.008;
        temporalRing(col,p,vec2(0.0),r,0.66,mix(TIME_GOLD,TIME_VIOLET,fi/5.0),
                     q*ae*(0.46-fi*0.055));
    }
    float silence=1.0-smoothstep(0.08,0.15,length(p));
    col=mix(col,TIME_VOID,silence*0.76);
    temporalRing(col,p,vec2(0.0),0.115,1.0,TIME_GOLD,q*ae);
    temporalNode(col,p,vec2(0.0),0.028,TIME_PEARL,q*ae*(0.66+0.24*breath));
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
