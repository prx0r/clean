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
    dreamThread(col,p,vec2(0.0),0.78,0.10,DREAM_INDIGO,q,t,0.5);
    dreamThread(col,p,vec2(0.0),0.78,0.07,DREAM_COBALT,q,t,1.6);
    float awake=smoothstep(0.28,0.94,u);
    pigmentBloom(col,p,vec2(0.0),mix(0.04,0.24,awake),DREAM_GOLD,25.0,awake*0.62*ae,t);
    dreamRipple(col,p,vec2(0.0),0.79,DREAM_GOLD,awake*(0.50+0.35*u_audioBeat),t);
    float eye=abs(sdEllipse(p,vec2(0.21,0.085)))-0.008;
    col+=DREAM_PEARL*(aaFill(eye)*0.66+glow(eye,0.05)*0.12)*awake*ae;
    dreamDot(col,p,vec2(0.0),0.045,DREAM_GOLD,awake*ae);
    for (int i=0;i<24;i++) {
        float a=TAU*float(i)/24.0+t*0.03;
        float r=0.28+0.48*hash11(float(i));
        dreamDot(col,p,vec2(cos(a)*r,sin(a)*r*0.56),0.008,DREAM_PEARL,awake*ae);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
