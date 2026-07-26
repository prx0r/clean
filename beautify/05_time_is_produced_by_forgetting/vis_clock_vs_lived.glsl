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
    vec2 left=vec2(-0.42,0.0), right=vec2(0.42,0.0);
    clockGlyph(col,p,left,0.27,t*0.72,TIME_PEARL,ae*0.72);
    for (int i=0;i<7;i++) {
        float fi=float(i), radius=0.08+fi*0.045;
        float wobble=0.78+0.16*sin(t*0.21+fi*1.8)+0.07*fbm(p*3.0+fi);
        temporalRing(col,p,right,radius,wobble,mix(TIME_GOLD,TIME_VIOLET,fi/7.0),
                     q*ae*(0.72-fi*0.07));
    }
    temporalNode(col,p,right,0.050+0.018*u_audioBeat,TIME_GOLD,q*ae);
    temporalLine(col,p,vec2(0.0,-0.43),vec2(0.0,0.43),TIME_ASH,ae*0.42);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
