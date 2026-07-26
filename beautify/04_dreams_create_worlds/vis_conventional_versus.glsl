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
    vec2 lc=vec2(-0.43,0.0), rc=vec2(0.43,0.0);
    float left=sdRoundBox(p-lc,vec2(0.29,0.27),0.045);
    float right=sdRoundBox(p-rc,vec2(0.29,0.27),0.045);
    col=mix(col,vec3(0.10,0.12,0.19),aaFill(left)*0.72*q);
    col+=DREAM_COBALT*aaStroke(left,0.008)*q*0.48;
    pigmentBloom(col,p,rc,0.31,DREAM_INDIGO,8.0,q*0.58,t);
    col+=DREAM_ROSE*(aaStroke(right,0.008)*0.54+glow(right,0.05)*0.08)*q;
    for (int i=0;i<8;i++) {
        vec2 c=lc+(hash22(vec2(float(i),2.0))*2.0-1.0)*vec2(0.21,0.17);
        dreamDot(col,p,c,0.010,DREAM_COBALT,q*0.65*ae);
    }
    float versus=smoothstep(0.5,0.88,u);
    watercolorLine(col,p,vec2(-0.10,-0.19),vec2(0.10,0.19),DREAM_GOLD,3.0,versus*ae);
    watercolorLine(col,p,vec2(-0.10,0.19),vec2(0.10,-0.19),DREAM_GOLD,4.0,versus*ae);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
