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
    gutTube(col,p,0.76,0.20,t,0.0,0.72*ae);
    for (int i=0;i<10;i++) {
        float fi=float(i)/9.0;
        float x=mix(-0.60,0.60,fi);
        vec2 c=vec2(x,gutCenterline(x,t,0.0)+0.08*sin(fi*TAU+t*0.4));
        float local=saturate(q*5.0-float(i)*0.34);
        float ring=sdRing(p-c,0.027+0.005*sin(t+float(i)),0.004);
        col+=GUT_AMBER*(aaFill(ring)*0.66+glow(ring,0.035)*0.20)*local*ae;
        for (int j=0;j<3;j++) {
            float a=TAU*float(j)/3.0+t*0.1;
            gutSignal(col,p,c+vec2(cos(a),sin(a))*0.038,0.009,GUT_PEARL,local*ae);
        }
    }
    float reservoir=sdRoundBox(p,vec2(0.72,0.30),0.08);
    col+=GUT_AMBER*(aaStroke(reservoir,0.006)*0.36+glow(reservoir,0.04)*0.06)*smoothstep(0.52,0.84,u)*ae;
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
