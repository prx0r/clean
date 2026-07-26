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
    vec2 center=vec2(0.0);
    for (int i=0;i<8;i++) {
        float a=TAU*float(i)/8.0+t*0.06;
        vec2 c=center+vec2(cos(a)*0.58,sin(a)*0.35);
        float local=saturate(q*5.0-float(i)*0.35);
        vec3 hue=cosinePalette(float(i)/8.0,vec3(.48,.38,.52),vec3(.42),vec3(1.0),vec3(.06,.30,.58));
        pigmentBloom(col,p,c,0.09,hue,float(i),local*0.55*ae,t);
        watercolorLine(col,p,c,center,hue,float(i),local*0.28);
        dreamDot(col,p,c,0.016,DREAM_PEARL,local*ae);
    }
    float communion=smoothstep(0.44,0.90,u);
    pigmentBloom(col,p,center,0.17,DREAM_GOLD,21.0,communion*0.58*ae,t);
    dreamRipple(col,p,center,0.63,DREAM_MINT,communion*0.65,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
