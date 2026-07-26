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
    vec2 origin=vec2(-0.52,-0.02);
    temporalNode(col,p,origin,0.052,TIME_CYAN,ae);
    for (int i=0;i<7;i++) {
        float fi=float(i)/6.0, angle=mix(-0.58,0.58,fi);
        vec2 end=origin+vec2(cos(angle),sin(angle))*1.18;
        float tremor=0.018*sin(t*2.1+float(i)*2.7)*(0.4+u_audioBeat);
        end.y+=tremor;
        temporalLine(col,p,origin,end,TIME_CRIMSON,q*ae*(0.42+0.30*hash11(float(i))));
        for (int j=1;j<5;j++) {
            float s=float(j)/5.0;
            temporalNode(col,p,mix(origin,end,s),0.016,TIME_CRIMSON,q*ae*(0.55-s*0.30));
        }
    }
    float cone=smoothstep(0.62,0.02,abs(p.y)/(max(p.x+0.54,0.01)))*smoothstep(-0.52,0.66,p.x);
    float fracture=step(0.47,noise21(p*13.0+vec2(t*0.04,0.0)));
    col+=TIME_CRIMSON*cone*fracture*q*0.055;
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
