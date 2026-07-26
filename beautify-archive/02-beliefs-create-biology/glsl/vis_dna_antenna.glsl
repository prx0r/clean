#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

vec2 helix(float x, float side, float time) {
    return vec2(x,0.16*sin(x*14.0+time*0.65)+side*0.055*cos(x*14.0+time*0.65));
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    vec2 prevA=helix(-0.68,-1.0,t), prevB=helix(-0.68,1.0,t);
    for (int i=1;i<76;i++) {
        float fi=float(i)/75.0;
        float x=mix(-0.68,0.68,fi);
        vec2 a=helix(x,-1.0,t), b=helix(x,1.0,t);
        float visible=1.0-smoothstep(q,q+0.035,fi);
        bioFilament(col,p,prevA,a,BIO_CYAN,visible*0.72*ae);
        bioFilament(col,p,prevB,b,BIO_VIOLET,visible*0.72*ae);
        if (i%5==0) bioFilament(col,p,a,b,BIO_GOLD,visible*0.42);
        prevA=a; prevB=b;
    }

    float receive=smoothstep(0.46,0.9,u);
    for (int i=0;i<7;i++) {
        float a=TAU*float(i)/7.0+t*0.1;
        vec2 source=vec2(cos(a)*0.82,sin(a)*0.50);
        float wave=0.5+0.5*sin(t*1.2+float(i)*1.4);
        bioParticle(col,p,source,0.018+0.012*wave,BIO_GOLD,receive*ae);
        bioFilament(col,p,source,vec2(0.0),BIO_GOLD,receive*0.26*wave);
    }
    bioField(col,p,vec2(0.0),0.72,BIO_GOLD,receive*(0.45+0.35*u_audioBeat),t);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
