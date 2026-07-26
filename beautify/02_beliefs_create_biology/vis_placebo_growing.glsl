#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

vec2 growthCurve(float x) {
    float y=-0.36+0.67*pow(saturate((x+0.67)/1.34),0.68);
    y+=0.018*sin(x*12.0);
    return vec2(x,y);
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    float axis=min(sdSegment(p,vec2(-0.72,-0.42),vec2(0.72,-0.42)),
                   sdSegment(p,vec2(-0.72,-0.42),vec2(-0.72,0.40)));
    col+=BIO_CYAN*(glow(axis,0.014)*0.18+aaStroke(axis,0.004)*0.38);

    vec2 previous=growthCurve(-0.67);
    for (int i=1;i<64;i++) {
        float fi=float(i)/63.0;
        vec2 current=growthCurve(mix(-0.67,0.67,fi));
        float visible=1.0-smoothstep(q,q+0.025,fi);
        float d=sdSegment(p,previous,current);
        col+=BIO_GOLD*(glow(d,0.028)*0.12+aaStroke(d,0.006)*0.72)*visible*ae;
        previous=current;
    }

    for (int i=0;i<4;i++) {
        float fi=float(i)/3.0;
        vec2 node=growthCurve(mix(-0.67,0.67,fi));
        float local=saturate(q*5.0-float(i));
        bioParticle(col,p,node,0.025+0.008*u_audioBeat,BIO_GOLD,local*ae);
        float ring=sdCircle(p-node,0.06+0.015*sin(t+float(i)));
        col+=mix(BIO_VIOLET,BIO_CRIMSON,fi)*glow(ring,0.012)*local*0.20;
    }

    float surge=smoothstep(0.63,0.9,u);
    vec2 tip=growthCurve(0.67);
    bioField(col,p,tip,0.27,BIO_CRIMSON,surge*ae,t);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
