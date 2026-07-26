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
    dreamThread(col,p,vec2(0.0,-0.12),0.76,0.09,DREAM_COBALT,q,t,0.4);
    vec3 hue[4]=vec3[](DREAM_COBALT,DREAM_GOLD,DREAM_MINT,DREAM_ROSE);
    for (int i=0;i<4;i++) {
        float fi=float(i)/3.0, local=saturate(q*6.0-float(i)-0.5);
        vec2 c=vec2(mix(-0.57,0.57,fi),0.22+0.04*sin(t+float(i)));
        float glyph=i==0?sdCircle(p-c,0.06):(
            i==1?sdRing(p-c,0.06,0.012):(
            i==2?sdBox(rot(0.5)*(p-c),vec2(0.05)):sdVesica(p-c,0.08,0.04)
        ));
        col+=hue[i]*(aaFill(glyph)*0.20+aaStroke(glyph,0.007)*0.60+glow(glyph,0.045)*0.10)*local*ae;
        pigmentBloom(col,p,c,0.10,hue[i],float(i),local*0.30,t);
    }
    fragColor=vec4(dreamFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
