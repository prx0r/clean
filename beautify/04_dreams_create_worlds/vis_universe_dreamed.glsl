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
    pigmentBloom(col,p,vec2(0.0),mix(0.04,0.20,q),DREAM_GOLD,17.0,q*0.52*ae,t);
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0, r=mix(0.08,0.82,fi)*q;
        float d=sdEllipse(p,vec2(r,r*0.58));
        col+=mix(DREAM_GOLD,DREAM_INDIGO,fi)*(aaStroke(d,0.005)*0.24+glow(d,0.025)*0.045)*q*ae;
    }
    float stars=smoothstep(0.35,0.88,u);
    for (int i=0;i<38;i++) {
        vec2 h=hash22(vec2(float(i),17.0));
        float a=TAU*h.x+t*0.025, r=mix(0.16,0.78,h.y)*stars;
        vec2 c=vec2(cos(a)*r,sin(a)*r*0.58);
        dreamDot(col,p,c,0.007+0.008*h.x,i%3==0?DREAM_GOLD:DREAM_PEARL,stars*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
