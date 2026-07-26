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
    pigmentBloom(col,p,vec2(0.0),0.28,DREAM_PEARL,12.0,q*0.32,t);
    float face=sdEllipse(p,vec2(0.22,0.30));
    col+=DREAM_INDIGO*(aaStroke(face,0.009)*0.62+glow(face,0.07)*0.08)*q;
    vec2 left=vec2(-0.075,-0.055), right=vec2(0.075,-0.055);
    dreamDot(col,p,left,0.026,DREAM_INDIGO,q*ae);
    dreamDot(col,p,right,0.026,DREAM_GOLD,q*ae);
    float focus=smoothstep(0.35,0.90,u);
    vec2 leftFar=vec2(-0.72,-0.27), rightFar=vec2(0.72,-0.27);
    watercolorLine(col,p,left,leftFar,DREAM_INDIGO,2.0,focus*0.42*ae);
    watercolorLine(col,p,right,rightFar,DREAM_GOLD,6.0,focus*0.42*ae);
    pigmentBloom(col,p,leftFar,0.11,DREAM_INDIGO,7.0,focus*0.40,t);
    pigmentBloom(col,p,rightFar,0.11,DREAM_GOLD,9.0,focus*0.40,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
