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
    for (int i=0;i<4;i++) {
        float fi=float(i)/3.0, y=mix(0.33,-0.33,fi);
        float local=smoothstep(fi-0.18,fi+0.06,q);
        vec3 hue=i<2 ? mix(TIME_GOLD,TIME_CYAN,float(i)) : TIME_CRIMSON;
        float panel=abs(sdRoundBox(p-vec2(0.0,y),vec2(0.68,0.060),0.022));
        col+=hue*(aaStroke(panel,0.006)*0.58+glow(panel,0.035)*0.065)*local*ae;
        for (int j=0;j<9;j++) {
            float x=mix(-0.54,0.26,float(j)/8.0);
            temporalNode(col,p,vec2(x,y),0.010,hue,local*ae*0.48);
        }
        vec2 mark=vec2(0.50,y);
        if (i<2) {
            temporalLine(col,p,mark+vec2(-0.045,0.0),mark+vec2(-0.010,-0.030),hue,local*ae);
            temporalLine(col,p,mark+vec2(-0.010,-0.030),mark+vec2(0.055,0.040),hue,local*ae);
        } else {
            temporalLine(col,p,mark+vec2(-0.040,-0.040),mark+vec2(0.040,0.040),hue,local*ae);
            temporalLine(col,p,mark+vec2(-0.040,0.040),mark+vec2(0.040,-0.040),hue,local*ae);
        }
    }
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
