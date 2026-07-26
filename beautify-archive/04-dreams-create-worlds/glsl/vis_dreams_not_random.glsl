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
    for (int i=0;i<14;i++) {
        vec2 a=(hash22(vec2(float(i),44.0))*2.0-1.0)*vec2(0.78,0.52);
        vec2 b=(hash22(vec2(float(i),144.0))*2.0-1.0)*vec2(0.78,0.52);
        float randomPhase=saturate(q*2.1-float(i)/14.0);
        watercolorLine(col,p,a,b,DREAM_ROSE,float(i),randomPhase*0.20*ae);
    }
    float resolve=smoothstep(0.45,0.92,u);
    dreamThread(col,p,vec2(0.0),0.72,0.095,DREAM_COBALT,resolve,t,2.0);
    dreamThread(col,p,vec2(0.0),0.72,0.095,DREAM_GOLD,resolve*0.94,t,2.0+0.06*sin(t));
    for (int i=0;i<8;i++) {
        float x=mix(-0.62,0.62,float(i)/7.0);
        vec2 c=vec2(x,0.095*sin(x*6.0+t*0.47+2.0));
        dreamDot(col,p,c,0.013,DREAM_PEARL,resolve*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
