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
    vec2 centers[3]=vec2[3](vec2(-0.48,0.0),vec2(0.0,0.0),vec2(0.48,0.0));
    vec3 hues[3]=vec3[3](TIME_VIOLET,TIME_GOLD,TIME_CYAN);
    for (int i=0;i<3;i++) {
        float fi=float(i)/2.0, local=smoothstep(fi-0.22,fi+0.06,q);
        float frame=abs(sdRoundBox(p-centers[i],vec2(0.17,0.28),0.035));
        col+=hues[i]*(aaStroke(frame,0.006)*0.62+glow(frame,0.050)*0.10)*local*ae;
        for (int j=0;j<3;j++) {
            float y=(float(j)-1.0)*0.085;
            temporalLine(col,p,centers[i]+vec2(-0.09,y),centers[i]+vec2(0.09-0.03*float(j),y),
                         hues[i],local*ae*0.62);
        }
        temporalNode(col,p,centers[i],0.026,TIME_PEARL,local*ae);
        if (i<2) temporalLine(col,p,centers[i]+vec2(0.19,0.0),centers[i+1]-vec2(0.19,0.0),
                              TIME_ASH,q*ae*0.45);
    }
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
