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
    for (int i=0;i<11;i++) {
        float fi=float(i)/10.0, r=mix(0.08,0.84,fi);
        float d=sdEllipse(p,vec2(r,r*0.55));
        vec3 hue=cosinePalette(fi,vec3(.45),vec3(.42),vec3(1.0),vec3(.08,.30,.60));
        col+=hue*(aaStroke(d,0.004)*0.24+glow(d,0.018+fi*0.012)*0.04)*q*ae;
    }
    float coexist=smoothstep(0.38,0.90,u);
    for (int i=0;i<24;i++) {
        float a=TAU*float(i)/24.0+t*0.04;
        float r=0.12+0.66*hash11(float(i)+5.0);
        vec2 c=vec2(cos(a)*r,sin(a)*r*0.55);
        dreamDot(col,p,c,0.009+0.008*u_audioBeat,DREAM_GOLD,coexist*ae);
    }
    pigmentBloom(col,p,vec2(0.0),0.10,DREAM_PEARL,6.0,coexist*0.38,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
