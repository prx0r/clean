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
    for (int k=0;k<7;k++) {
        float fk=float(k)-3.0;
        vec2 previous=vec2(-0.82,fk*0.045+0.10*sin(-4.5+t*0.28+fk));
        for (int i=1;i<72;i++) {
            float s=float(i)/71.0, x=mix(-0.82,0.82,s);
            float y=fk*0.045+0.10*sin(x*5.5+t*0.28+fk*0.62)+0.025*sin(x*19.0-fk);
            vec2 current=vec2(x,y);
            float reveal=1.0-smoothstep(q,q+0.025,s);
            temporalLine(col,p,previous,current,mix(TIME_VIOLET,TIME_CYAN,s),reveal*ae*0.38);
            previous=current;
        }
    }
    float x=mix(-0.78,0.78,fract(q+t*0.025));
    vec2 bead=vec2(x,0.10*sin(x*5.5+t*0.28));
    temporalNode(col,p,bead,0.052+0.014*u_audioBeat,TIME_GOLD,ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
