#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

float capsule(vec2 p) {
    return sdRoundBox(p,vec2(0.19,0.075),0.072);
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    vec2 pillCenter=vec2(0.0,mix(-0.48,-0.14,easeOut(smoothstep(0.05,0.52,u))));
    vec2 cp=rot(-0.18)*(p-pillCenter);
    float pill=capsule(cp);
    float split=step(0.0,cp.x);
    vec3 pillCol=mix(BIO_PEARL,BIO_CRIMSON,split);
    col=mix(col,pillCol,aaFill(pill)*0.92);
    col+=pillCol*(aaStroke(pill,0.008)*0.7+glow(pill,0.08)*0.12*ae);

    vec2 head=vec2(0.0,0.25);
    float skull=sdEllipse(p-head,vec2(0.31,0.27));
    col+=BIO_VIOLET*(aaStroke(skull,0.011)*0.52+glow(skull,0.09)*0.08);

    float activate=smoothstep(0.34,0.78,u);
    vec2 regions[5]=vec2[](
        vec2(-0.13,0.18),vec2(0.12,0.14),vec2(-0.06,0.31),
        vec2(0.15,0.31),vec2(0.0,0.23)
    );
    for (int i=0;i<5;i++) {
        float local=saturate(activate*6.0-float(i)*0.72);
        float beat=0.72+0.28*sin(t*2.1+float(i)*1.7)+u_audioBeat*0.45;
        bioParticle(col,p,regions[i],0.055+0.012*beat,mix(BIO_GOLD,BIO_GREEN,float(i)/5.0),local*ae);
    }

    float expectation=glowLine(p,pillCenter,head,0.026)*activate;
    col+=BIO_GOLD*expectation*0.32*ae;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
