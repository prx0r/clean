#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack04_watercolor.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=dreamBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    vec2 waking=vec2(-0.46,0.0), dreaming=vec2(0.46,0.0);
    pigmentBloom(col,p,waking,0.22,DREAM_COBALT,4.0,q*0.54,t);
    pigmentBloom(col,p,dreaming,0.22,DREAM_ROSE,8.0,q*0.54,t);
    float wa=sdEllipse(p-waking,vec2(0.16,0.12));
    float dr=sdEllipse(p-dreaming,vec2(0.16,0.12));
    col+=DREAM_PEARL*(aaStroke(wa,0.008)+aaStroke(dr,0.008))*q*0.46;
    float speak=smoothstep(0.24,0.82,u);
    dreamThread(col,p,vec2(0.0),0.29,0.055,DREAM_GOLD,speak,t,0.8);
    for (int i=0;i<6;i++) {
        float travel=fract(t*0.13+float(i)/6.0);
        vec2 c=mix(waking,dreaming,i%2==0?travel:1.0-travel);
        c.y+=0.055*sin(travel*TAU*3.0+t)*sin(PI*travel);
        dreamDot(col,p,c,0.017,DREAM_GOLD,speak*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
