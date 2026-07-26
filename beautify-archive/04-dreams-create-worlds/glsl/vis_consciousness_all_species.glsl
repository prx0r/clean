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
    for (int i=0;i<22;i++) {
        vec2 h=hash22(vec2(float(i),31.0));
        vec2 c=(h*2.0-1.0)*vec2(0.82,0.54);
        float local=saturate(q*2.3-h.y*0.8);
        vec3 hue=i%3==0?DREAM_MINT:(i%3==1?DREAM_COBALT:DREAM_GOLD);
        float size=0.025+0.045*h.x;
        pigmentBloom(col,p,c,size,hue,float(i),local*0.43*ae,t);
        dreamDot(col,p,c,size*0.20,DREAM_PEARL,local*ae);
        int target=(i*7+5)%22;
        vec2 ht=hash22(vec2(float(target),31.0));
        vec2 b=(ht*2.0-1.0)*vec2(0.82,0.54);
        float near=1.0-smoothstep(0.25,0.70,length(c-b));
        watercolorLine(col,p,c,b,DREAM_GOLD,float(i),near*local*0.12);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
