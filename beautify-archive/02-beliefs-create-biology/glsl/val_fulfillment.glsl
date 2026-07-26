#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

vec2 livingPath(float x, float time) {
    return vec2(x,0.11*sin(x*7.2+time*0.35)-0.03*cos(x*13.0-time*0.2));
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    vec2 prev=livingPath(-0.74,t);
    for (int i=1;i<70;i++) {
        float fi=float(i)/69.0;
        vec2 cur=livingPath(mix(-0.74,0.74,fi),t);
        float visible=1.0-smoothstep(q,q+0.04,fi);
        bioFilament(col,p,prev,cur,mix(BIO_CYAN,BIO_GOLD,fi),visible*0.78*ae);
        prev=cur;
    }

    for (int i=0;i<5;i++) {
        float fi=(float(i)+0.5)/5.0;
        vec2 c=livingPath(mix(-0.62,0.62,fi),t);
        float local=saturate(q*7.0-float(i)-1.0);
        float bloom=0.045+0.035*local+0.012*u_audioBeat;
        float flower=bioRosette(rot(t*0.07+float(i))*(p-c),5.0+float(i),bloom,0.20);
        vec3 hue=cosinePalette(fi,vec3(.45),vec3(.44),vec3(1.0),vec3(.06,.28,.58));
        col+=hue*(aaFill(flower)*0.28+aaStroke(flower,0.008)*0.7+glow(flower,0.05)*0.12)*local*ae;
        bioField(col,p,c,0.18,hue,local*0.5,t+float(i));
    }
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
