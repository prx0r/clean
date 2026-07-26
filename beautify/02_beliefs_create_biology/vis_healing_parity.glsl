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
    vec2 c=vec2(0.0,0.04);

    float cocoon=sdVesica((p-c)/vec2(0.62,0.88),0.56,0.26);
    float sleeping=smoothstep(0.05,0.48,u);
    col+=BIO_VIOLET*(aaFill(cocoon)*0.10+aaStroke(cocoon,0.010)*0.50+glow(cocoon,0.11)*0.10)*sleeping;

    for (int i=0;i<18;i++) {
        float fi=float(i);
        float a=TAU*fi/18.0+t*(0.07+0.004*fi);
        float r=0.30+0.15*sin(fi*2.7+t*0.21);
        vec2 spore=c+vec2(cos(a)*r,sin(a)*r*0.63);
        float contribution=saturate(q*2.4-fi/18.0);
        bioParticle(col,p,spore,0.016+0.008*sin(t+fi),mix(BIO_VIOLET,BIO_GREEN,fi/18.0),contribution*ae);
        bioFilament(col,p,spore,c,BIO_GREEN,contribution*0.13);
    }

    float healing=smoothstep(0.48,0.93,u);
    float heart=bioRosette(rot(t*0.04)*(p-c),8.0,0.09+0.055*healing,0.10);
    col+=BIO_GREEN*(aaFill(heart)*0.26+aaStroke(heart,0.009)*0.74+glow(heart,0.12)*0.24)*healing*ae;
    bioField(col,p,c,0.65,BIO_GREEN,healing*(0.5+0.4*u_audioBeat),t);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
