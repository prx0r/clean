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
    pigmentBloom(col,p,vec2(0.0),0.15,DREAM_INDIGO,5.0,q*0.42,t);
    for (int i=0;i<8;i++) {
        float a=TAU*float(i)/8.0+t*0.07;
        float r=0.51+0.05*sin(t*0.4+float(i));
        vec2 c=vec2(cos(a)*r,sin(a)*r*0.58);
        float local=saturate(q*5.0-float(i)*0.31);
        watercolorLine(col,p,vec2(0.0),c,mix(DREAM_GOLD,DREAM_COBALT,float(i%2)),float(i),local*0.34*ae);
        pigmentBloom(col,p,c,0.065,i%2==0?DREAM_GOLD:DREAM_COBALT,float(i),local*0.48,t);
        dreamDot(col,p,c,0.014,DREAM_PEARL,local*ae);
    }
    float inner=sdRing(p,0.18+0.015*u_audioBeat,0.007);
    col+=DREAM_GOLD*(aaFill(inner)*0.58+glow(inner,0.045)*0.12)*q*ae;
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
