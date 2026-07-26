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
    vec2 event=vec2(0.0,-0.31);
    for (int i=0;i<36;i++) {
        vec2 h=hash22(vec2(float(i),88.0));
        float a=TAU*h.x, r=0.65*sqrt(h.y);
        vec2 start=vec2(cos(a)*r,sin(a)*r*0.66);
        float gather=smoothstep(0.35,0.88,u)*pow(h.y,1.6);
        vec2 c=mix(start,event,gather);
        vec3 hue=i%3==0?DREAM_INDIGO:(i%3==1?DREAM_COBALT:DREAM_GOLD);
        dreamDot(col,p,c,0.009+0.009*h.y,hue,q*ae);
    }
    float physical=smoothstep(0.48,0.93,u);
    pigmentBloom(col,p,event,0.13,DREAM_GOLD,14.0,physical*0.76*ae,t);
    float frame=sdRoundBox(p-event,vec2(0.16,0.09),0.025);
    col+=DREAM_PEARL*aaStroke(frame,0.008)*physical*0.66;
    watercolorLine(col,p,vec2(0.0,0.26),event,DREAM_GOLD,5.0,physical*0.58*ae);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
