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
    vec3 hue[5]=vec3[](GUT_CYAN,GUT_AMBER,GUT_RED,GUT_BLUE,GUT_GREEN);
    for (int i=0;i<5;i++) {
        float fi=float(i);
        float local=saturate(q*6.0-fi*0.82);
        vec2 c=vec2(0.0,mix(-0.46,0.46,fi/4.0));
        float panel=sdRoundBox(p-c,vec2(0.60,0.065),0.032);
        float confidence=i<4?1.0:0.58+0.20*sin(t);
        col+=hue[i]*(aaFill(panel)*0.065+aaStroke(panel,0.006)*0.54+glow(panel,0.032)*0.08)
            *local*confidence*ae;
        for (int j=0;j<7;j++) {
            vec2 dot=c+vec2(mix(-0.47,0.47,float(j)/6.0),0.0);
            gutSignal(col,p,dot,0.009,hue[i],local*confidence*ae);
        }
        float status=sdRing(p-(c+vec2(0.50,0.0)),0.025,0.004);
        col+=hue[i]*(aaFill(status)*0.64+glow(status,0.025)*0.16)*local*confidence;
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
