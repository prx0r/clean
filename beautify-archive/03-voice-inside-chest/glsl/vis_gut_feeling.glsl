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
    vec2 gut=vec2(0.0,0.38), insula=vec2(0.0,-0.48);
    gutTube(col,p-gut,0.52,0.13,t,0.0,ae);
    float brain=sdEllipse(p-insula,vec2(0.18,0.11));
    col+=GUT_BLUE*(aaFill(brain)*0.11+aaStroke(brain,0.008)*0.62+glow(brain,0.06)*0.11)*smoothstep(0.48,0.84,u)*ae;
    gutVagus(col,p,gut-vec2(0.0,0.12),insula+vec2(0.0,0.10),t,GUT_AMBER,q*0.62);
    float rise=easeInOut(smoothstep(0.12,0.92,u));
    for (int i=0;i<8;i++) {
        float delay=float(i)/8.0;
        float local=saturate(rise*1.35-delay*0.42);
        vec2 c=mix(gut,insula,saturate(rise-delay*0.12));
        float a=TAU*float(i)/8.0+t*0.23;
        c+=vec2(cos(a),sin(a))*0.10*bell(rise);
        gutSignal(col,p,c,0.018+0.011*u_audioBeat,mix(GUT_RED,GUT_AMBER,rise),local*ae);
    }
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
