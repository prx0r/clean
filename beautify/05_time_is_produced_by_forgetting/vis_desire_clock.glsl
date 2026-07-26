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
    vec2 c=vec2(-0.16,0.0), target=vec2(0.58,0.06);
    float aim=atan(target.y-c.y,target.x-c.x);
    float hand=mix(-PI*0.5,aim,q)+sin(t*0.8)*0.025;
    clockGlyph(col,p,c,0.34,hand,TIME_GOLD,ae);
    temporalNode(col,p,target,0.070+0.025*u_audioBeat,TIME_CRIMSON,ae);
    for (int i=0;i<5;i++) {
        float off=(float(i)-2.0)*0.020;
        temporalLine(col,p,c+vec2(0.0,off),target+vec2(0.0,off*0.20),
                     mix(TIME_GOLD,TIME_CRIMSON,float(i)/4.0),q*ae*0.30);
    }
    float pull=glowLine(p,c,target,0.19);
    col+=TIME_CRIMSON*pull*q*0.045*ae;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
