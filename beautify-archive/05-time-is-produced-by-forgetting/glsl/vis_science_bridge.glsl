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
    vec2 left=vec2(-0.48,-0.08), right=vec2(0.48,-0.08);
    for (int i=0;i<4;i++) {
        float fi=float(i)/3.0;
        vec2 c=left+vec2((fi-0.5)*0.34,0.13*sin(fi*PI));
        temporalNode(col,p,c,0.030,mix(TIME_VIOLET,TIME_CYAN,fi),ae);
        if (i>0) {
            float fp=float(i-1)/3.0;
            vec2 previous=left+vec2((fp-0.5)*0.34,0.13*sin(fp*PI));
            temporalLine(col,p,previous,c,TIME_CYAN,ae*0.70);
        }
    }
    for (int i=0;i<5;i++) {
        temporalRing(col,p,right,0.08+float(i)*0.055,0.65,TIME_GOLD,
                     q*ae*(0.64-float(i)*0.075));
    }
    vec2 previous=left+vec2(0.17,0.0);
    for (int i=1;i<48;i++) {
        float s=float(i)/47.0;
        vec2 current=mix(left+vec2(0.17,0.0),right-vec2(0.22,0.0),s);
        current.y+=0.35*sin(PI*s);
        temporalLine(col,p,previous,current,mix(TIME_CYAN,TIME_GOLD,s),
                     (1.0-smoothstep(q,q+0.025,s))*ae);
        previous=current;
    }
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
