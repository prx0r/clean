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
    float gather=smoothstep(0.05,0.58,u);
    float recognize=smoothstep(0.52,0.95,u);
    vec2 c=vec2(0.0,0.02);

    for (int i=0;i<36;i++) {
        float fi=float(i);
        float a=TAU*hash11(fi+9.0)+t*(0.08+0.003*fi);
        float start=0.25+0.58*hash11(fi+41.0);
        float r=mix(start,0.075,gather);
        vec2 seed=c+vec2(cos(a)*r,sin(a)*r*0.62);
        vec3 hue=(i%3==0)?BIO_CYAN:BIO_GOLD;
        bioParticle(col,p,seed,0.012+0.009*hash11(fi),hue,q*ae);
        bioFilament(col,p,seed,c,hue,gather*0.10);
    }

    float core=bioRosette(rot(-t*0.035)*(p-c),12.0,0.09+0.07*recognize,0.09);
    col+=BIO_PEARL*aaFill(core)*recognize*0.42;
    col+=BIO_GOLD*(aaStroke(core,0.010)*0.88+glow(core,0.14)*0.28)*recognize*ae;
    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0+t*0.03;
        vec2 tip=c+vec2(cos(a),sin(a))*mix(0.16,0.52,recognize);
        bioFilament(col,p,c,tip,mix(BIO_GOLD,BIO_GREEN,float(i%2)),recognize*0.46*ae);
        bioParticle(col,p,tip,0.020,BIO_GOLD,recognize*ae);
    }
    bioField(col,p,c,0.78,BIO_GOLD,recognize*(0.5+0.45*u_audioBeat),t);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
