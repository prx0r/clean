#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

vec2 gridCell(int i) {
    int x=i%3, y=i/3;
    return vec2(-0.48+float(x)*0.48,-0.35+float(y)*0.35);
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    for (int i=0;i<9;i++) {
        vec2 c=gridCell(i);
        float local=saturate(q*4.5-float(i)*0.23);
        float activation=0.5+0.5*sin(t*1.6-float(i)*0.9);
        vec3 hue=mix(BIO_CYAN,BIO_GREEN,activation);
        bioCell(col,p,c,vec2(0.125,0.105),hue,activation*u_audioBeat,t+float(i));
        bioParticle(col,p,c,0.018,hue,local*ae*(0.6+0.45*activation));
        if (i%3<2) bioFilament(col,p,c,gridCell(i+1),BIO_GOLD,local*0.28);
        if (i<6) bioFilament(col,p,c,gridCell(i+3),BIO_VIOLET,local*0.24);
    }

    float signal=fract(t*0.22);
    for (int i=0;i<8;i++) {
        vec2 a=gridCell(i), b=gridCell(i+1);
        if (i%3==2) b=gridCell((i+3)%9);
        vec2 s=mix(a,b,fract(signal+float(i)*0.19));
        bioParticle(col,p,s,0.024,BIO_GOLD,q*ae);
    }
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
