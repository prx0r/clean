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
    float merge=smoothstep(0.12,0.84,u);
    vec2 left=mix(vec2(-0.35,0.0),vec2(0.0),merge);
    vec2 right=mix(vec2(0.35,0.0),vec2(0.0),merge);
    dreamThread(col,p,left,0.34,mix(0.09,0.045,merge),DREAM_INDIGO,q,t,0.2);
    dreamThread(col,p,right,0.34,mix(0.08,0.045,merge),DREAM_COBALT,q,t,1.4);
    float unified=smoothstep(0.42,0.92,u);
    dreamThread(col,p,vec2(0.0),0.69,0.10,DREAM_GOLD,unified,t,0.8);
    pigmentBloom(col,p,vec2(0.0),0.10,DREAM_GOLD,15.0,unified*0.58*ae,t);
    dreamRipple(col,p,vec2(0.0),0.62,DREAM_GOLD,unified*0.48*ae,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
