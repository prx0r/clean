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
    vec2 gut=vec2(0.0,0.23), awareness=vec2(0.0,-0.45);
    gutTube(col,p-gut,0.70,0.16,t,0.2,ae);
    for (int i=0;i<9;i++) {
        float fi=float(i)/8.0, x=mix(-0.58,0.58,fi);
        vec2 c=gut+vec2(x,gutCenterline(x,t,0.2));
        gutNeuron(col,p,c,0.025,mix(GUT_CYAN,GUT_AMBER,fi),t*0.2+float(i),q*ae);
    }
    float rise=easeInOut(smoothstep(0.23,0.88,u));
    gutVagus(col,p,gut-vec2(0.0,0.14),awareness+vec2(0.0,0.09),t,GUT_AMBER,rise*ae);
    gutSignal(col,p,mix(gut,awareness,rise),0.034,GUT_AMBER,q*ae);
    float halo=sdRing(p-awareness,0.12+0.025*sin(t*0.7),0.006);
    col+=GUT_PEARL*aaFill(sdCircle(p-awareness,0.055))*rise*0.55;
    col+=GUT_AMBER*(glow(halo,0.035)*0.26+aaStroke(halo,0.006)*0.52)*rise*ae;
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
