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
    vec2 previous=vec2(-0.72,-0.22);
    for (int i=0;i<11;i++) {
        float fi=float(i)/10.0;
        vec2 c=vec2(mix(-0.72,0.72,fi),0.19*sin(fi*8.7)-0.08*cos(fi*18.0));
        float local=smoothstep(fi-0.08,fi+0.025,q);
        if (i>0) temporalLine(col,p,previous,c,mix(TIME_VIOLET,TIME_CYAN,fi),local*ae);
        temporalNode(col,p,c,0.025+0.010*u_audioBeat,mix(TIME_GOLD,TIME_CYAN,fi),local*ae);
        previous=c;
    }
    float scanner=mix(-0.72,0.72,q);
    temporalLine(col,p,vec2(scanner,-0.48),vec2(scanner,0.48),TIME_GOLD,ae*0.40);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
