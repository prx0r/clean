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
    vec2 previous=vec2(-0.72,-0.34);
    for (int i=0;i<10;i++) {
        float fi=float(i)/9.0;
        vec2 c=vec2(mix(-0.72,0.72,fi),mix(-0.34,0.34,fi));
        float local=smoothstep(fi-0.10,fi+0.025,q);
        vec2 corner=vec2(c.x,previous.y);
        if (i>0) {
            temporalLine(col,p,previous,corner,TIME_CYAN,local*ae);
            temporalLine(col,p,corner,c,TIME_GOLD,local*ae);
        }
        temporalNode(col,p,c,0.030,mix(TIME_VIOLET,TIME_GOLD,fi),local*ae);
        previous=c;
    }
    float level=floor(q*9.0)/9.0;
    temporalLine(col,p,vec2(-0.80,mix(-0.34,0.34,level)),vec2(0.80,mix(-0.34,0.34,level)),
                 TIME_PEARL,ae*0.18);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
