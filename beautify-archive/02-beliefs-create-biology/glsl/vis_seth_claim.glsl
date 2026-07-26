#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    vec2 c=vec2(0.0,0.07);

    for (int i=0;i<5;i++) {
        float fi=float(i);
        float local=saturate(q*6.0-fi*0.82);
        float a=TAU*fi/5.0+t*(0.12+0.015*fi);
        vec2 seed=c+vec2(cos(a),sin(a))*vec2(0.55,0.31)*(1.0-0.42*q);
        float flower=bioRosette((p-seed)*rot(-a),5.0+mod(fi,2.0),0.055,0.18);
        vec3 hue=cosinePalette(fi/5.0,vec3(.48,.30,.44),vec3(.40),vec3(1.0),vec3(.05,.26,.58));
        col+=hue*(aaFill(flower)*0.28+aaStroke(flower,0.009)*0.72+glow(flower,0.06)*0.13)*local*ae;
        bioFilament(col,p,seed,c,hue,local*0.48);
    }

    float body=smoothstep(0.48,0.9,u);
    float torso=sdVesica((p-c)/vec2(0.62,0.82),0.54,0.28);
    col+=BIO_GOLD*(aaStroke(torso,0.014)*0.68+glow(torso,0.085)*0.14)*body*ae;
    float heart=sdCircle(p-(c+vec2(0.0,0.02)),0.07+0.012*u_audioBeat);
    col+=BIO_PEARL*aaFill(heart)*body*0.55;
    col+=BIO_GOLD*glow(heart,0.075)*body*0.34*ae;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
