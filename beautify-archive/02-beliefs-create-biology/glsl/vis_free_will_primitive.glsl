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
    vec2 c=vec2(0.0,0.02);

    float sphere=sdCircle(p-c,0.27);
    col+=BIO_VIOLET*(aaFill(sphere)*0.10+aaStroke(sphere,0.008)*0.35+glow(sphere,0.15)*0.10)*q;
    for (int i=0;i<24;i++) {
        float fi=float(i);
        float a=TAU*fi/24.0+0.12*sin(t*0.2+fi);
        float choose=smoothstep(0.58,0.94,u);
        float chosen=1.0-smoothstep(0.12,0.38,abs(a-0.72));
        float lengthRay=mix(0.37,0.69,choose*chosen);
        vec2 a0=c+vec2(cos(a),sin(a))*0.28;
        vec2 b0=c+vec2(cos(a),sin(a))*lengthRay;
        vec3 hue=mix(BIO_VIOLET,BIO_GOLD,chosen*choose);
        bioFilament(col,p,a0,b0,hue,q*(0.22+0.72*chosen*choose)*ae);
        if (chosen>0.5) bioParticle(col,p,b0,0.032,BIO_GOLD,choose*ae);
    }

    float origin=sdCircle(p-c,0.055+0.012*u_audioBeat);
    col+=BIO_PEARL*aaFill(origin)*0.55*q;
    col+=BIO_GOLD*glow(origin,0.09)*q*0.30*ae;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
