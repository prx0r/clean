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
    float squash=mix(0.72,0.075,q);
    for (int i=0;i<10;i++) {
        float fi=float(i), r=0.09+fi*0.066;
        temporalRing(col,p,vec2(0.0),r,squash,TIME_GOLD,ae*(0.76-fi*0.055));
    }
    for (int i=0;i<7;i++) {
        float x=mix(-0.62,0.62,float(i)/6.0);
        vec3 hue=mix(TIME_VIOLET,TIME_CYAN,float(i)/6.0);
        temporalNode(col,p,vec2(x,0.0),0.025,hue,q*ae);
    }
    float frame=abs(sdRoundBox(p,vec2(0.70,0.12),0.045));
    col+=TIME_CYAN*(aaStroke(frame,0.007)*0.52+glow(frame,0.040)*0.08)*q*ae;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
