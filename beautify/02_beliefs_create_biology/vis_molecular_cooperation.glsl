#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

vec2 molecule(int i, float time) {
    float fi=float(i);
    vec2 h=hash22(vec2(fi,73.0));
    float a=TAU*h.x+0.08*time*(0.4+h.y);
    float r=0.08+0.62*pow(h.y,0.65);
    return vec2(cos(a),sin(a))*vec2(r,r*0.62);
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    for (int i=0;i<48;i++) {
        vec2 a=molecule(i,t);
        float local=saturate(q*2.2-float(i)/48.0);
        vec3 hue=(i%3==0)?BIO_GOLD:BIO_CYAN;
        bioParticle(col,p,a,0.011+0.010*hash11(float(i)),hue,local*(0.48+0.38*ae));
        for (int j=1;j<=2;j++) {
            int target=(i+j*7)%48;
            vec2 b=molecule(target,t);
            float near=1.0-smoothstep(0.12,0.34,length(a-b));
            bioFilament(col,p,a,b,mix(BIO_VIOLET,BIO_GOLD,float(j-1)),near*local*0.22);
        }
    }

    float unity=smoothstep(0.60,0.96,u);
    float envelope=sdEllipse(p,vec2(0.76,0.48));
    col+=BIO_GREEN*(aaStroke(envelope,0.008)*0.26+glow(envelope,0.08)*0.08)*unity*ae;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
