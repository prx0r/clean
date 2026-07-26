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
    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0+t*0.018;
        vec2 c=vec2(cos(a),sin(a))*0.39;
        vec3 hue=mix(TIME_GOLD,TIME_CYAN,0.5+0.5*sin(a*2.0));
        temporalLine(col,p,vec2(0.0),c,hue,q*ae*0.36);
        temporalNode(col,p,c,0.030,hue,q*ae);
    }
    for (int i=0;i<6;i++) {
        float r=0.10+float(i)*0.078;
        temporalRing(col,p,vec2(0.0),r,1.0,mix(TIME_VIOLET,TIME_GOLD,float(i)/5.0),
                     q*ae*(0.70-float(i)*0.065));
    }
    temporalNode(col,p,vec2(0.0),0.075+0.025*u_audioBeat,TIME_PEARL,q*ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
