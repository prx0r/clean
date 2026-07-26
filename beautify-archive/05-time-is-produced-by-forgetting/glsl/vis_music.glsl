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
    for (int k=0;k<5;k++) {
        float fk=float(k)-2.0;
        vec2 previous=vec2(-0.82,fk*0.075);
        for (int i=1;i<80;i++) {
            float s=float(i)/79.0, x=mix(-0.82,0.82,s);
            float envelope=sin(PI*s);
            float y=fk*0.075+envelope*(0.10+0.025*fk)*sin(x*11.0+t*(0.65+fk*0.03));
            vec2 current=vec2(x,y);
            temporalLine(col,p,previous,current,mix(TIME_VIOLET,TIME_CYAN,s),
                         (1.0-smoothstep(q,q+0.02,s))*ae*0.38);
            previous=current;
        }
    }
    float play=mix(-0.80,0.80,q);
    temporalLine(col,p,vec2(play,-0.42),vec2(play,0.42),TIME_GOLD,ae*(0.54+u_audioBeat));
    temporalNode(col,p,vec2(play,0.10*sin(play*11.0+t*0.65)),0.055,TIME_GOLD,ae);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
