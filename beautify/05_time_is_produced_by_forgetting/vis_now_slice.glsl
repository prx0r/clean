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
    float now=mix(-0.78,0.78,q);
    for (int i=0;i<15;i++) {
        float x=mix(-0.78,0.78,float(i)/14.0);
        vec3 hue=x<now ? TIME_VIOLET : TIME_CYAN;
        temporalNode(col,p,vec2(x,0.13*sin(x*11.0)),0.018,hue,ae*0.48);
    }
    float slab=temporalWindow(p,vec2(now,0.0),vec2(0.038,0.52),0.012);
    col+=mix(TIME_GOLD,TIME_PEARL,slab)*slab*(0.16+0.22*u_audioBeat)*ae;
    temporalLine(col,p,vec2(now,-0.55),vec2(now,0.55),TIME_GOLD,ae);
    temporalNode(col,p,vec2(now,0.13*sin(now*11.0)),0.052,TIME_PEARL,ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
