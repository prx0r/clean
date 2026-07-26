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
    gutTube(col,p,0.76,0.20,t,0.8,0.62*ae);
    for (int i=0;i<11;i++) {
        float fi=float(i)/10.0;
        float x=mix(-0.62,0.62,fi);
        vec2 c=vec2(x,gutCenterline(x,t,0.8)+0.10*sin(fi*TAU*2.0+t*0.17));
        float local=saturate(q*4.0-float(i)*0.28);
        float phase=t*0.2+float(i)*1.31;
        gutNeuron(col,p,c,0.023,GUT_GREEN,phase,local*ae);
        float barrier=abs(p.y-gutCenterline(p.x,t,0.8))-0.16;
        col+=GUT_GREEN*glow(barrier,0.014)*local*0.028*ae;
    }
    float shield=sdRoundBox(p,vec2(0.71,0.27),0.09);
    col+=GUT_GREEN*(aaStroke(shield,0.005)*0.22+glow(shield,0.04)*0.04)*smoothstep(0.56,0.9,u)*ae;
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
