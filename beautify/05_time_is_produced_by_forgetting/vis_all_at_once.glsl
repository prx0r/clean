#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack05_temporal.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=temporalBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    for (int i=0;i<8;i++) {
        float fi=float(i), r=0.12+fi*0.075;
        temporalArc(col,p,vec2(0.0),r,0.58,-PI,PI,TIME_GOLD,q,ae*(0.72-fi*0.055));
    }
    for (int i=0;i<32;i++) {
        float h=hash11(float(i)*7.31), a=TAU*hash11(float(i)*2.17);
        vec2 c=vec2(cos(a),sin(a)*0.58)*(0.10+0.57*h);
        vec3 hue=mix(TIME_CYAN,TIME_VIOLET,hash11(float(i)+4.0));
        temporalNode(col,p,c,0.015+0.012*u_audioBeat,hue,q*ae);
    }
    temporalNode(col,p,vec2(0.0),0.055,TIME_GOLD,q*ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
