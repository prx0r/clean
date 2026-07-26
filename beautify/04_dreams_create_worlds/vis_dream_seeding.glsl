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
    float seed=smoothstep(0.05,0.37,u), grow=smoothstep(0.33,0.75,u), manifest=smoothstep(0.70,0.98,u);
    vec2 origin=vec2(-0.38,0.20);
    pigmentBloom(col,p,origin,0.055,DREAM_GOLD,2.0,seed*ae,t);
    dreamDot(col,p,origin,0.018,DREAM_PEARL,seed*ae);
    dreamThread(col,p,vec2(-0.02,0.06),0.37,0.08,DREAM_MINT,grow,t,1.1);
    vec2 event=vec2(0.38,-0.20);
    pigmentBloom(col,p,event,mix(0.04,0.18,manifest),DREAM_ROSE,9.0,manifest*0.82*ae,t);
    watercolorLine(col,p,origin,event,DREAM_GOLD,6.0,grow*0.32);
    for (int i=0;i<7;i++) {
        float a=TAU*float(i)/7.0+t*0.05;
        vec2 petal=event+vec2(cos(a),sin(a))*0.17*manifest;
        watercolorLine(col,p,event,petal,DREAM_GOLD,float(i),manifest*0.34*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
