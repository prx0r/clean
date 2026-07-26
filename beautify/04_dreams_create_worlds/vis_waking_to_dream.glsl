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
    float waking=sdRoundBox(p,vec2(0.48,0.28),0.045);
    col+=DREAM_COBALT*aaStroke(waking,0.008)*(1.0-q)*0.52;
    dreamThread(col,p,vec2(0.0),0.68,mix(0.02,0.11,q),mix(DREAM_COBALT,DREAM_INDIGO,q),q,t,1.0);
    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0+q*PI+t*0.04;
        float r=mix(0.21,0.57,q);
        vec2 c=vec2(cos(a)*r,sin(a)*r*0.56);
        vec3 hue=mix(DREAM_COBALT,DREAM_GOLD,q);
        dreamDot(col,p,c,0.012+0.009*q,hue,q*ae);
        watercolorLine(col,p,vec2(0.0),c,hue,float(i),q*0.10);
    }
    pigmentBloom(col,p,vec2(0.0),0.12,DREAM_ROSE,5.0,q*0.38,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
