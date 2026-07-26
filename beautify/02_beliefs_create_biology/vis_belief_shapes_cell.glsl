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
    vec2 c=vec2(0.13,0.05);
    float transform=smoothstep(0.55,0.94,u);

    bioCell(col,p,c,vec2(0.38,0.32),mix(BIO_CYAN,BIO_GREEN,transform),transform,t);

    float travel=easeInOut(smoothstep(0.08,0.62,u));
    vec2 seed=mix(vec2(-0.74,-0.31),c,travel);
    seed.y+=0.13*sin(travel*PI);
    bioParticle(col,p,seed,0.035,BIO_GOLD,ae);

    vec2 previous=vec2(-0.74,-0.31);
    for (int i=1;i<34;i++) {
        float fi=float(i)/33.0;
        vec2 current=mix(vec2(-0.74,-0.31),c,fi);
        current.y+=0.13*sin(fi*PI);
        float visible=1.0-smoothstep(travel,travel+0.04,fi);
        bioFilament(col,p,previous,current,BIO_GOLD,visible*0.45);
        previous=current;
    }

    float nucleus=bioRosette((p-c)*rot(t*0.05),8.0,mix(0.09,0.16,transform),0.14*transform);
    col+=BIO_GOLD*(aaFill(nucleus)*0.16+aaStroke(nucleus,0.009)*0.78+glow(nucleus,0.06)*0.18)*transform*ae;
    for (int i=0;i<8;i++) {
        float a=TAU*float(i)/8.0+t*0.08;
        vec2 tip=c+vec2(cos(a),sin(a))*mix(0.11,0.22,transform);
        bioFilament(col,p,c,tip,BIO_GREEN,transform*(0.35+u_audioBeat*0.25));
    }
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
