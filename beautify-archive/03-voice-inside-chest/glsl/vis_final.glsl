#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack03_bioluminescent.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=gutBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    float gather=smoothstep(0.08,0.58,u), listen=smoothstep(0.52,0.96,u);
    gutTube(col,p,0.72,0.17,t,0.1,mix(0.45,0.85,listen)*ae);
    for (int i=0;i<16;i++) {
        float fi=float(i);
        float a=TAU*fi/16.0+t*(0.08+fi*0.002);
        vec2 start=vec2(cos(a)*0.70,sin(a)*0.42);
        vec2 c=mix(start,vec2(0.0),gather);
        gutSignal(col,p,c,0.016+0.009*hash11(fi),i%3==0?GUT_CYAN:GUT_AMBER,q*ae);
        gutNerve(col,p,c,vec2(0.0),GUT_AMBER,gather*0.12);
    }
    float aperture=abs(sdEllipse(p,vec2(0.25,0.12)))-0.012;
    col+=GUT_CYAN*(aaFill(aperture)*0.62+glow(aperture,0.055)*0.16)*listen*ae;
    float pupil=sdCircle(p,0.060+0.015*u_audioBeat);
    col+=GUT_PEARL*aaFill(pupil)*listen*0.72;
    col+=GUT_AMBER*glow(pupil,0.11)*listen*0.28*ae;
    for (int i=0;i<10;i++) {
        float a=TAU*float(i)/10.0+t*0.04;
        gutNerve(col,p,vec2(0.0),vec2(cos(a)*0.55,sin(a)*0.34),GUT_AMBER,listen*0.27*ae);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
