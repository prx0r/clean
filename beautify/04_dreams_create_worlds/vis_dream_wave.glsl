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
    for (int i=0;i<6;i++) {
        float fi=float(i)/5.0;
        vec3 hue=mix(DREAM_ROSE,DREAM_COBALT,fi);
        vec2 center=vec2(0.0,mix(-0.36,0.36,fi));
        dreamThread(col,p,center,0.72,mix(0.11,0.045,fi),hue,q,t,fi*1.3);
        float wash=fbmWarp((p-center)*3.0+fi,t);
        col+=hue*pow(wash,4.0)*0.035*(1.0-fi)*q*ae;
    }
    dreamRipple(col,p,vec2(0.0),0.82,DREAM_INDIGO,q*(0.35+0.35*u_audioBeat),t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
