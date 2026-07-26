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
    vec2 origin=vec2(-0.62,-0.02);
    temporalNode(col,p,origin,0.055,TIME_GOLD,ae);
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0, bend=mix(-0.46,0.46,fi);
        vec2 previous=origin;
        for (int j=1;j<24;j++) {
            float s=float(j)/23.0;
            vec2 c=origin+vec2(1.28*s,bend*s+0.12*sin(s*5.0+fi*8.0)*s);
            temporalLine(col,p,previous,c,mix(TIME_VIOLET,TIME_CYAN,fi),ae*q*(1.0-fi*0.18)*0.48);
            previous=c;
        }
        temporalNode(col,p,previous,0.025,TIME_CYAN,ae*q);
    }
    float haze=smoothstep(-0.56,0.72,p.x)*fbmWarp(p*2.3+vec2(t*0.02,0.0),t);
    col+=mix(TIME_VIOLET,TIME_CYAN,haze)*haze*q*0.055;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
