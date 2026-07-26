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

    for (int i=0;i<8;i++) {
        float fi=float(i)/7.0;
        float r=mix(0.16,0.78,fi);
        float d=sdEllipse(p,vec2(r,r*0.57));
        col+=BIO_VIOLET*(aaStroke(d,0.003)*0.18+glow(d,0.018)*0.025)*ae;
    }

    for (int i=0;i<5;i++) {
        float fi=float(i)/4.0;
        float local=saturate(q*7.0-float(i)-0.5);
        vec2 c=vec2(mix(-0.52,0.52,fi),0.12*sin(fi*9.0+t*0.23));
        vec2 size=vec2(0.105,0.055)*(0.6+0.4*local);
        float seed=sdRoundBox(rot(0.22*sin(fi*5.0))*(p-c),size,0.025);
        col+=BIO_GOLD*(aaFill(seed)*0.24+aaStroke(seed,0.008)*0.62+glow(seed,0.055)*0.13)*local*ae;
        float dent=glowPoint(p,c,0.16)*local;
        col=mix(col,col*0.72+BIO_WINE*0.18,dent*0.22);
        for (int j=0;j<4;j++) {
            float a=TAU*float(j)/4.0+t*0.06;
            bioFilament(col,p,c,c+vec2(cos(a),sin(a))*0.14,BIO_GOLD,local*0.25);
        }
    }
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
