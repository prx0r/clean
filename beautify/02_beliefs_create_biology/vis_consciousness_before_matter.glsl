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

    float field=fbmWarp(rot(t*0.018)*p*2.7,t);
    col+=mix(BIO_VIOLET,BIO_CYAN,field)*pow(field,3.4)*0.20;
    for (int i=0;i<12;i++) {
        float fi=float(i)/11.0;
        float r=mix(0.12,0.80,fi);
        float d=sdEllipse(p-c,vec2(r,r*0.55));
        col+=mix(BIO_GOLD,BIO_VIOLET,fi)*glow(d,0.012+fi*0.013)*0.045*ae;
    }

    float condense=smoothstep(0.28,0.88,u);
    vec2 previous=c;
    for (int i=1;i<72;i++) {
        float fi=float(i)/71.0;
        float a=fi*TAU*4.3+t*0.12;
        float r=0.58*fi*(1.0-condense)+0.13*fi;
        vec2 current=c+vec2(cos(a)*r,sin(a)*r*0.58);
        bioFilament(col,p,previous,current,mix(BIO_VIOLET,BIO_GOLD,condense),q*0.55*ae);
        previous=current;
    }
    bioParticle(col,p,c,0.055,BIO_GOLD,condense*ae);
    float matter=sdCircle(p-c,0.095*condense);
    col+=BIO_PEARL*aaFill(matter)*condense*0.30;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
