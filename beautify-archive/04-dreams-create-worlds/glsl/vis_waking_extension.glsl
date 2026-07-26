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
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0, r=mix(0.10,0.82,fi);
        float d=sdEllipse(p,vec2(r,r*0.60));
        vec3 hue=mix(DREAM_ROSE,DREAM_COBALT,fi);
        col+=hue*(aaStroke(d,0.005)*0.26+glow(d,0.025+fi*0.012)*0.035)*q*ae;
    }
    float emerge=smoothstep(0.48,0.92,u);
    float waking=sdRoundBox(p,vec2(0.32,0.21),0.04);
    col+=DREAM_GOLD*(aaStroke(waking,0.008)*0.56+glow(waking,0.055)*0.09)*emerge*ae;
    float ocean=fbmWarp(p*2.8+vec2(0.0,t*0.03),t);
    col+=DREAM_INDIGO*pow(ocean,4.0)*(1.0-emerge)*0.15;
    pigmentBloom(col,p,vec2(0.0),0.13,DREAM_PEARL,4.0,emerge*0.35,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
