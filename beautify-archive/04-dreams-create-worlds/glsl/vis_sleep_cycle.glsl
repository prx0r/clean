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
    float bed=sdRoundBox(p-vec2(0.0,0.29),vec2(0.55,0.09),0.035);
    col+=DREAM_COBALT*(aaFill(bed)*0.16+aaStroke(bed,0.008)*0.46+glow(bed,0.05)*0.07)*q;
    pigmentBloom(col,p,vec2(-0.13,0.17),0.14,DREAM_ROSE,3.0,q*0.52,t);
    float sleeper=sdSegment(p,vec2(-0.22,0.20),vec2(0.25,0.25));
    col+=DREAM_PEARL*(aaStroke(sleeper,0.035)*0.34+glow(sleeper,0.07)*0.08)*q;
    float dream=smoothstep(0.42,0.92,u);
    dreamThread(col,p,vec2(0.0,-0.08),0.68,0.11,DREAM_INDIGO,dream,t,0.7);
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0;
        vec2 c=vec2(mix(-0.56,0.56,fi),-0.08+0.11*sin(mix(-0.56,0.56,fi)*6.0+t*0.47+0.7));
        dreamDot(col,p,c,0.012,DREAM_GOLD,dream*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
