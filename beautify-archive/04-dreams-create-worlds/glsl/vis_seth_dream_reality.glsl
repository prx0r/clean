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
    vec2 left=vec2(-0.42,0.03), right=vec2(0.42,0.03);
    pigmentBloom(col,p,left,0.23,DREAM_COBALT,11.0,q*0.72,t);
    pigmentBloom(col,p,right,0.23,DREAM_ROSE,17.0,q*0.72,t);
    float lf=sdEllipse(p-left,vec2(0.16,0.22));
    float rf=sdEllipse(p-right,vec2(0.16,0.22));
    col+=DREAM_PEARL*(aaStroke(lf,0.008)+aaStroke(rf,0.008))*q*0.38;
    dreamDot(col,p,left+vec2(-0.045,-0.035),0.015,DREAM_GOLD,q*ae);
    dreamDot(col,p,right+vec2(0.045,-0.035),0.015,DREAM_GOLD,q*ae);
    float bridge=smoothstep(0.25,0.78,u);
    dreamThread(col,p,vec2(0.0,0.03),0.28,0.045,DREAM_INDIGO,bridge,t,0.2);
    dreamRipple(col,p,vec2(0.0,0.03),0.42,DREAM_GOLD,bridge*ae,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
