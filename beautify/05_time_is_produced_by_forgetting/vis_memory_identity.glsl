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
    vec2 previous=vec2(-0.66,0.18*sin(-5.0));
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0;
        vec2 c=vec2(mix(-0.66,0.66,fi),0.18*sin(fi*7.2-2.0));
        if (i>0) temporalLine(col,p,previous,c,TIME_GOLD,q*ae*0.58);
        vec3 hue=mix(TIME_VIOLET,TIME_CYAN,fi);
        temporalNode(col,p,c,0.032,hue,smoothstep(fi-0.14,fi+0.04,q)*ae);
        previous=c;
    }
    float enclosure=smoothstep(0.45,0.82,q);
    temporalArc(col,p,vec2(0.0),0.73,0.47,-PI*0.94,PI*0.94,TIME_CRIMSON,enclosure,ae*0.65);
    temporalRing(col,p,vec2(0.0),0.24,0.74,TIME_PEARL,enclosure*ae*0.45);
    temporalNode(col,p,vec2(0.0),0.055,TIME_GOLD,enclosure*ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
