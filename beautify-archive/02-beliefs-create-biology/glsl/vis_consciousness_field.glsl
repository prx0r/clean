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
    vec2 c=vec2(0.0,0.03);

    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0;
        float r=mix(0.16,0.84,fi)*(0.96+0.025*sin(t+fi*9.0));
        float d=sdEllipse(p-c,vec2(r,r*0.58));
        vec3 hue=mix(BIO_GOLD,BIO_VIOLET,fi);
        col+=hue*(aaStroke(d,0.004+fi*0.002)*0.21+glow(d,0.018+fi*0.012)*0.035)*q*ae;
    }

    float self=smoothstep(0.37,0.74,u);
    float body=sdVesica((p-c)/vec2(0.44,0.62),0.55,0.28);
    col+=BIO_PEARL*aaFill(body)*self*0.10;
    col+=BIO_GOLD*(aaStroke(body,0.012)*0.68+glow(body,0.09)*0.15)*self*ae;

    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0+t*(0.08+0.01*float(i));
        vec2 s=c+vec2(cos(a)*0.67,sin(a)*0.39);
        bioParticle(col,p,s,0.020,BIO_VIOLET,q*ae);
        bioFilament(col,p,s,c,BIO_GOLD,self*0.12);
    }
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
