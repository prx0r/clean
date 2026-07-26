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
    for (int i=0;i<9;i++) {
        float fi=float(i), radius=0.09+fi*0.066;
        temporalArc(col,p,vec2(0.0),radius,0.62,-PI,PI,TIME_GOLD,q,
                    ae*(0.76-fi*0.061));
    }
    vec2 previous=vec2(-0.66,0.0);
    for (int i=0;i<8;i++) {
        float fi=float(i)/7.0;
        vec2 c=vec2(mix(-0.66,0.66,fi),0.045*sin(fi*TAU+t*0.12));
        float local=smoothstep(fi-0.12,fi+0.035,q);
        if (i>0) temporalLine(col,p,previous,c,TIME_CYAN,local*ae);
        temporalNode(col,p,c,0.026,mix(TIME_VIOLET,TIME_GOLD,fi),local*ae);
        previous=c;
    }
    float remember=smoothstep(0.62,0.94,u);
    temporalNode(col,p,vec2(0.0),0.090+0.026*u_audioBeat,TIME_PEARL,remember*ae);
    float halo=glow(sdRing(p,0.31,0.006),0.11);
    col+=mix(TIME_VIOLET,TIME_GOLD,q)*halo*remember*0.14*ae;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
