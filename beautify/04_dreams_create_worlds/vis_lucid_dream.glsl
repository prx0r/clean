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
    for (int i=0;i<28;i++) {
        vec2 h=hash22(vec2(float(i),99.0));
        vec2 c=(h*2.0-1.0)*vec2(0.84,0.57);
        dreamDot(col,p,c,0.007+0.007*h.y,DREAM_INDIGO,q*(0.45+0.45*sin(t+float(i)))*ae);
    }
    float lucid=smoothstep(0.18,0.75,u);
    pigmentBloom(col,p,vec2(0.0),0.16,DREAM_GOLD,18.0,lucid*0.55*ae,t);
    float eye=abs(sdEllipse(p,vec2(0.20,0.09)))-0.008;
    col+=DREAM_PEARL*(aaFill(eye)*0.62+glow(eye,0.05)*0.12)*lucid*ae;
    dreamDot(col,p,vec2(0.0),0.045,DREAM_GOLD,lucid*ae);
    for (int i=0;i<12;i++) {
        float a=TAU*float(i)/12.0+t*0.08;
        vec2 tip=vec2(cos(a)*0.52,sin(a)*0.34);
        watercolorLine(col,p,vec2(0.0),tip,DREAM_GOLD,float(i),lucid*0.22*ae);
    }
    dreamRipple(col,p,vec2(0.0),0.72,DREAM_GOLD,lucid*0.52,t);
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
