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

    vec2 matter=vec2(0.0,-0.16);
    float cortex=bioMembrane(p,matter,vec2(0.34,0.25),0.025,t*0.7);
    float folds=abs(sin((p.x+0.08*sin(p.y*8.0))*34.0))*aaFill(cortex);
    col+=BIO_CYAN*(aaStroke(cortex,0.012)*0.65+glow(cortex,0.07)*0.11);
    col+=BIO_VIOLET*pow(1.0-folds,10.0)*aaFill(cortex)*0.32;

    float stem=sdSegment(p,vec2(0.0,0.07),vec2(0.0,0.28));
    col+=BIO_PEARL*glow(stem,0.017)*0.16;
    vec2 mind=vec2(0.0,mix(0.55,0.37,easeOut(q)));
    float md=sdCircle(p-mind,0.105);
    col+=BIO_GOLD*(aaStroke(md,0.009)*0.65+glow(md,0.10)*0.14*q*ae);

    for (int i=0;i<9;i++) {
        float fi=float(i);
        float travel=fract(t*0.10+fi/9.0);
        vec2 s=mix(matter+vec2(0.0,0.05),mind,travel);
        s.x+=sin(fi*2.3+t)*0.025*bell(travel);
        bioParticle(col,p,s,0.018,BIO_GOLD,q*ae);
    }
    float rupture=smoothstep(0.55,0.78,u);
    col+=BIO_CRIMSON*glow(sdRoundBox(p,vec2(0.67,0.57),0.04),0.022)*rupture*0.42;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
