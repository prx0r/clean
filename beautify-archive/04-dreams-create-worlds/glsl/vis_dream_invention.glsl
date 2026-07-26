#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack04_watercolor.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=dreamBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    dreamThread(col,p,vec2(0.0,0.18),0.76,0.05,DREAM_GOLD,q,t,2.2);
    for (int i=0;i<6;i++) {
        float fi=float(i)/5.0, local=saturate(q*7.0-float(i)-0.3);
        vec2 c=vec2(mix(-0.65,0.65,fi),-0.14+0.035*sin(t+float(i)));
        float d;
        if (i==0) d=sdRing(p-c,0.055,0.012);
        else if (i==1) d=sdBox(rot(0.78)*(p-c),vec2(0.045));
        else if (i==2) d=sdVesica(p-c,0.075,0.035);
        else if (i==3) d=sdCircle(p-c,0.052);
        else if (i==4) d=sdRoundBox(p-c,vec2(0.064,0.040),0.014);
        else d=abs(sdEllipse(p-c,vec2(0.070,0.040)))-0.010;
        vec3 hue=mix(DREAM_COBALT,DREAM_GOLD,fi);
        col+=hue*(aaFill(d)*0.20+aaStroke(d,0.007)*0.62+glow(d,0.045)*0.10)*local*ae;
        pigmentBloom(col,p,c,0.10,hue,float(i),local*0.25,t);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
