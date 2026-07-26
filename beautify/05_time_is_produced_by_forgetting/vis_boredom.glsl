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
    for (int y=0;y<3;y++) {
        for (int x=0;x<7;x++) {
            vec2 c=vec2(mix(-0.72,0.72,float(x)/6.0),mix(-0.31,0.31,float(y)/2.0));
            float phase=-PI*0.5+(1.0-q)*sin(t*0.55+float(x+y))*0.65;
            clockGlyph(col,p,c,0.070,phase,TIME_ASH,ae*(0.26+0.10*(1.0-q)));
        }
    }
    float voidBand=temporalWindow(p,vec2(0.0),vec2(0.79,mix(0.02,0.27,q)),0.04);
    col=mix(col,mix(col,TIME_OBSIDIAN,0.54),voidBand*q*0.62);
    temporalLine(col,p,vec2(-0.76,0.0),vec2(0.76,0.0),TIME_PEARL,(1.0-q)*ae*0.22);
    fragColor=vec4(temporalFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
