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

    float mist=fbmWarp(p*2.2+vec2(0.0,t*0.04),t);
    col+=mix(BIO_VIOLET,BIO_CYAN,mist)*pow(mist,3.2)*0.16*q;
    vec2 event=vec2(0.22*sin(t*0.23),0.12*cos(t*0.19));

    for (int i=0;i<42;i++) {
        vec2 h=hash22(vec2(float(i),55.0));
        vec2 star=(h*2.0-1.0)*vec2(0.82,0.55);
        float born=saturate(q*2.0-h.x*0.6);
        vec2 gathered=mix(star,event,smoothstep(0.38,0.92,u)*pow(h.y,1.8));
        bioParticle(col,p,gathered,0.008+0.008*h.y,BIO_VIOLET,born*ae);
    }

    float physical=smoothstep(0.54,0.9,u);
    float portal=sdRing(p-event,0.075+0.012*sin(t),0.008);
    col+=BIO_GOLD*(aaFill(portal)*0.54+glow(portal,0.055)*0.22)*physical*ae;
    vec2 outcome=event+vec2(0.31,-0.17);
    bioFilament(col,p,event,outcome,BIO_GOLD,physical*0.75);
    bioParticle(col,p,outcome,0.035,BIO_GREEN,physical*ae);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
