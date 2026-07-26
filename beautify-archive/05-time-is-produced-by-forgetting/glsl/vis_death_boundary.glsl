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
    float edge=0.48+0.045*(noise21(vec2(p.y*7.0,t*0.05))-0.5);
    temporalLine(col,p,vec2(-0.76,0.0),vec2(edge,0.0),TIME_CYAN,q*ae);
    for (int i=0;i<8;i++) {
        float fi=float(i)/7.0;
        vec2 c=vec2(mix(-0.68,edge-0.05,fi),0.0);
        temporalNode(col,p,c,0.024,mix(TIME_VIOLET,TIME_GOLD,fi),q*ae);
    }
    float boundary=abs(p.x-edge);
    col+=TIME_CRIMSON*(exp(-boundary*boundary/0.00008)*0.74+
                       exp(-boundary*boundary/0.006)*0.09)*ae;
    float beyond=smoothstep(edge-0.02,edge+0.12,p.x);
    float wash=inkDissolve(p-vec2(edge,0.0),q*0.62+0.14,t);
    col=mix(col,TIME_VOID,beyond*(0.45+0.45*wash));
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
