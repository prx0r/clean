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
    vec2 head=vec2(mix(-0.66,0.66,q),0.18*sin(q*TAU*1.4));
    vec2 previous=head;
    for (int i=1;i<42;i++) {
        float lag=float(i)/41.0, s=max(q-lag*0.72,0.0);
        vec2 c=vec2(mix(-0.66,0.66,s),0.18*sin(s*TAU*1.4));
        temporalLine(col,p,previous,c,mix(TIME_GOLD,TIME_VIOLET,lag),ae*(1.0-lag)*0.88);
        temporalNode(col,p,c,0.018,TIME_VIOLET,ae*(1.0-lag)*0.36);
        previous=c;
    }
    temporalNode(col,p,head,0.058+0.015*u_audioBeat,TIME_GOLD,ae);
    float sediment=fbm(p*7.0+vec2(t*0.018,0.0))*smoothstep(head.x,p.x-0.7,p.x);
    col+=TIME_ASH*sediment*0.045;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
