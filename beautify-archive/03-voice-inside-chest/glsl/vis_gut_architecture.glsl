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
    gutTube(col,p,0.78,0.19,t,0.0,ae);
    for (int i=0;i<7;i++) {
        float fi=float(i)/6.0;
        vec2 c=vec2(mix(-0.64,0.64,fi),gutCenterline(mix(-0.64,0.64,fi),t,0.0));
        float local=saturate(q*4.5-float(i)*0.42);
        float activation=0.55+0.45*sin(t*1.4+float(i)*1.8)+u_audioBeat*0.25;
        gutNeuron(col,p,c,0.030+0.005*activation,mix(GUT_CYAN,GUT_AMBER,fi),t*0.2+float(i),local*ae);
        if (i<6) {
            float nx=mix(-0.64,0.64,float(i+1)/6.0);
            gutNerve(col,p,c,vec2(nx,gutCenterline(nx,t,0.0)),GUT_CYAN,local*0.36);
        }
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
