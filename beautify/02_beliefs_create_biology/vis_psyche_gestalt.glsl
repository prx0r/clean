#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack02_psychobiology.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    vec3 col=bioBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);

    vec2 v[3]=vec2[](
        vec2(0.0,-0.39),
        vec2(-0.47,0.31),
        vec2(0.47,0.31)
    );
    vec3 hue[3]=vec3[](BIO_GOLD,BIO_CYAN,BIO_VIOLET);
    for (int i=0;i<3;i++) {
        float local=saturate(q*4.0-float(i)*0.55);
        float r=0.085+0.014*sin(t+float(i)*2.0);
        float lobe=bioRosette(rot(t*0.06+float(i))*(p-v[i]),6.0+float(i),r,0.15);
        col+=hue[i]*(aaFill(lobe)*0.23+aaStroke(lobe,0.009)*0.72+glow(lobe,0.06)*0.12)*local*ae;
        bioFilament(col,p,v[i],v[(i+1)%3],BIO_GOLD,local*0.40);
    }

    float emerge=smoothstep(0.44,0.88,u);
    vec2 center=vec2(0.0,0.08*sin(t*0.2));
    float gestalt=bioRosette(rot(-t*0.05)*(p-center),9.0,0.10+0.05*emerge,0.11);
    col+=BIO_PEARL*aaFill(gestalt)*emerge*0.36;
    col+=BIO_GOLD*(aaStroke(gestalt,0.010)*0.84+glow(gestalt,0.10)*0.24)*emerge*ae;
    bioField(col,p,center,0.38,BIO_GOLD,emerge*0.7,t);
    fragColor=vec4(bioFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
