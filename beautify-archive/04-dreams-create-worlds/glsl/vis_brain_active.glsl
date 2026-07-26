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
    float brain=sdEllipse(p,vec2(0.47,0.31));
    col=mix(col,DREAM_INDIGO,aaFill(brain)*0.12*q);
    col+=DREAM_COBALT*(aaStroke(brain,0.010)*0.48+glow(brain,0.08)*0.09)*q;
    for (int i=0;i<24;i++) {
        vec2 h=hash22(vec2(float(i),71.0));
        float a=TAU*h.x, r=0.34*sqrt(h.y);
        vec2 c=vec2(cos(a)*r,sin(a)*r*0.62);
        float local=saturate(q*2.2-h.x*0.8);
        float activation=0.65+0.35*sin(t*1.8+float(i)*0.73)+0.35*u_audioBeat;
        pigmentBloom(col,p,c,0.025+0.018*activation,i%2==0?DREAM_GOLD:DREAM_COBALT,float(i),local*activation*0.46*ae,t);
    }
    for (int i=0;i<6;i++) {
        float y=mix(-0.18,0.18,float(i)/5.0);
        dreamThread(col,p,vec2(0.0,y),0.37,0.025,DREAM_PEARL,q*0.55,t,float(i));
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
