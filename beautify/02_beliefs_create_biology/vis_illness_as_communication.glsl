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
    float distress=pulse(smoothstep(0.05,0.69,u),0.18);
    float repair=smoothstep(0.53,0.95,u);
    vec2 c=vec2(0.0,0.02);

    bioCell(col,p,c,vec2(0.39,0.32),mix(BIO_CRIMSON,BIO_GREEN,repair),repair,t);
    for (int i=0;i<7;i++) {
        float a=TAU*float(i)/7.0+0.21*sin(t+float(i));
        float crackLength=mix(0.09,0.30,distress)*(0.75+0.25*hash11(float(i)));
        vec2 tip=c+vec2(cos(a),sin(a))*crackLength;
        bioFilament(col,p,c,tip,BIO_CRIMSON,distress*(1.0-repair)*ae);
        vec2 restored=c+vec2(cos(a+t*0.08),sin(a+t*0.08))*mix(0.18,0.36,repair);
        bioFilament(col,p,c,restored,BIO_GREEN,repair*0.48*ae);
        bioParticle(col,p,restored,0.018,BIO_GREEN,repair*ae);
    }

    bioField(col,p,c,mix(0.22,0.62,repair),BIO_GREEN,repair*ae,t);
    float alarm=sdRing(p-c,0.47+0.018*sin(t*2.0),0.006);
    col+=BIO_CRIMSON*glow(alarm,0.026)*distress*(1.0-repair)*0.38*ae;
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
