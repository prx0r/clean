// Signature Film System: shared semantic rendering operators.
//
// These functions do not prescribe a house palette or a fixed composition.
// They encode recurring cinematic relationships: field/focus, trace/event,
// boundary/channel, part/whole, visible/counterfactual, and comparison.
// Pack includes combine them into an essay-specific material world.
#ifndef BEAUTIFY_SIGNATURE_GLSL
#define BEAUTIFY_SIGNATURE_GLSL

struct SignatureTiming {
    float enter;
    float disclose;
    float transform;
    float resolve;
    float drive;
    float beat;
};

SignatureTiming signatureTiming(float u, float volume, float beat) {
    SignatureTiming s;
    s.enter=easeOut(smoothstep(0.00,0.20,u));
    s.disclose=easeInOut(smoothstep(0.10,0.55,u));
    s.transform=easeInOut(smoothstep(0.28,0.82,u));
    s.resolve=easeOut(smoothstep(0.60,0.96,u));
    s.drive=audioEnergy(volume,beat);
    s.beat=saturate(beat);
    return s;
}

vec3 signatureIvoryField(vec2 p, float time, float warmth) {
    float paper=fbm(p*2.4+vec2(0.0,time*0.007));
    float fibers=phaseContour(fbm(p*11.0+17.0),18.0,0.018);
    vec3 cool=vec3(0.885,0.915,0.925);
    vec3 warm=vec3(0.985,0.955,0.875);
    vec3 c=mix(cool,warm,saturate(warmth));
    c*=0.94+0.055*paper;
    c+=vec3(0.02,0.024,0.028)*fibers;
    c-=vec3(0.055,0.045,0.025)*smoothstep(0.3,1.8,length(p));
    return c;
}

vec3 signatureNightField(vec2 p, float time, vec3 undertone) {
    float nebula=fbmWarp(p*0.72+vec2(time*0.004,-time*0.006),time*0.07);
    float dust=pow(noise21(gl_FragCoord.xy*0.41+floor(time*5.0)),18.0);
    return vec3(0.006,0.009,0.018)+undertone*(0.05+0.16*nebula)
        +vec3(0.12,0.16,0.22)*dust;
}

vec3 signatureTwilightField(vec2 p, float time, float polarity) {
    vec3 ivory=signatureIvoryField(p,time,0.58+0.18*polarity);
    vec3 night=signatureNightField(p,time,vec3(0.10,0.16,0.28));
    float horizon=smoothstep(-0.62,0.72,p.y+0.16*sin(p.x*1.4+time*0.018));
    return mix(night,ivory,mix(horizon,1.0-horizon,saturate(polarity)));
}

float signatureContour(float value, float frequency, float width) {
    float cell=abs(fract(value*frequency)-0.5);
    float aa=max(fwidth(value*frequency),0.0015);
    return 1.0-smoothstep(width,width+aa,cell);
}

float signatureRibbon(vec2 p, float phase, float thickness, float turbulence) {
    float y=0.24*sin(p.x*2.6+phase)
        +0.10*sin(p.x*7.0-phase*0.7)
        +turbulence*(fbm(vec2(p.x*2.2,phase*0.11))-0.5);
    return abs(p.y-y)-thickness;
}

float signatureFlowBand(vec2 p, vec2 direction, float frequency, float phase) {
    direction=normalize(direction);
    vec2 normal=vec2(-direction.y,direction.x);
    float along=dot(p,direction);
    float across=dot(p,normal);
    return sin(across*frequency+1.35*sin(along*2.2+phase));
}

float signatureFold(vec2 p, float amount, float phase) {
    vec2 q=p*rot(0.17*sin(phase*0.3));
    float a=atan(q.y,q.x);
    float r=length(q);
    float petal=0.40+0.11*sin(5.0*a+phase)+0.05*sin(11.0*a-phase*0.4);
    float surface=r-petal;
    float crease=abs(sin(5.0*a+phase))*0.038*amount;
    return surface+crease;
}

float signatureShutter(vec2 p, float position, float width, float softness) {
    float slit=abs(p.x-position)-width;
    return 1.0-smoothstep(-softness,softness,slit);
}

float signatureWindow(vec2 p, vec2 halfSize, float radius, float open) {
    vec2 size=mix(vec2(0.018,halfSize.y),halfSize,easeOut(open));
    return sdRoundBox(p,size,radius);
}

float signatureBoundary(vec2 p, float radius, float roughness, float phase) {
    float a=atan(p.y,p.x);
    float contour=radius
        +roughness*0.55*sin(3.0*a+phase)
        +roughness*0.25*sin(7.0*a-phase*0.8)
        +roughness*0.20*sin(13.0*a+phase*0.37);
    return length(p)-contour;
}

void signatureNode(
    inout vec3 color,
    vec2 p,
    vec2 center,
    float radius,
    vec3 hue,
    float energy
) {
    vec2 delta=p-center;
    float d2=dot(delta,delta);
    color+=hue*exp(-d2/max(radius*radius,0.00002))*energy;
    color+=vec3(1.0)*exp(-d2/max(radius*radius*0.045,0.000002))*energy*0.65;
}

void signatureChannel(
    inout vec3 color,
    vec2 p,
    vec2 source,
    vec2 target,
    vec3 hue,
    float energy,
    float pulsePhase
) {
    vec2 v=target-source;
    float vv=max(dot(v,v),0.0001);
    float h=saturate(dot(p-source,v)/vv);
    vec2 nearest=source+v*h;
    float d=length(p-nearest);
    float travelling=0.30+0.70*pow(0.5+0.5*sin(h*18.0-pulsePhase),6.0);
    color+=hue*(exp(-d*d/0.000025)*0.72+exp(-d*d/0.0022)*0.085)
        *energy*(0.62+0.38*travelling);
}

void signatureAgents(
    inout vec3 color,
    vec2 p,
    float time,
    float convergence,
    vec2 target,
    vec3 cold,
    vec3 resolved,
    float energy
) {
    for (int y=-5;y<=5;y++) for (int x=-8;x<=8;x++) {
        vec2 id=vec2(float(x),float(y));
        vec2 start=(id+hash22(id+31.0)-0.5)*vec2(0.16,0.15);
        vec2 curl=0.045*vec2(
            sin(time*0.31+hash21(id)*TAU),
            cos(time*0.27+hash21(id+7.0)*TAU)
        );
        float affinity=0.25+0.75*hash21(id+93.0);
        vec2 goal=target+0.58*(start-target)/max(length(start-target),0.22);
        vec2 position=mix(start+curl,goal+curl*(1.0-convergence),convergence*affinity);
        float d=length(p-position);
        float size=mix(0.010,0.021,convergence*affinity);
        color+=mix(cold,resolved,convergence)*exp(-d*d/(size*size))*energy*(0.18+0.34*affinity);
    }
}

void signatureConstellation(
    inout vec3 color,
    vec2 p,
    float time,
    float phase,
    vec3 hue,
    float energy
) {
    vec2 previous=vec2(0.0);
    for (int i=0;i<13;i++) {
        float fi=float(i);
        float a=fi*2.399963+phase;
        float r=0.13+0.055*fi;
        vec2 node=r*vec2(cos(a),sin(a));
        node+=0.018*vec2(sin(time*0.17+fi),cos(time*0.13-fi));
        signatureNode(color,p,node,0.030,hue,energy*(0.20+0.035*fi));
        if (i>0) signatureChannel(color,p,previous,node,hue,energy*0.22,time*0.8-fi);
        previous=node;
    }
}

void signatureEchoes(
    inout vec3 color,
    vec2 p,
    vec2 current,
    vec2 velocity,
    float spacing,
    float radius,
    vec3 hue,
    float energy
) {
    for (int i=0;i<9;i++) {
        float fi=float(i);
        vec2 center=current-velocity*spacing*fi;
        float d=abs(length(p-center)-radius*(1.0-0.045*fi));
        color+=hue*exp(-d*d/(0.00045+fi*0.00016))*exp(-fi*0.31)*energy;
    }
}

void signatureSplitComparison(
    inout vec3 color,
    vec2 p,
    float seam,
    vec3 leftHue,
    vec3 rightHue,
    float energy
) {
    float left=1.0-smoothstep(seam-0.035,seam+0.035,p.x);
    float right=1.0-left;
    float divider=abs(p.x-seam)-0.004;
    color+=leftHue*left*0.025*energy+rightHue*right*0.025*energy;
    color+=mix(leftHue,rightHue,0.5)
        *(aaStroke(divider,0.004)+glow(divider,0.035)*0.09)*energy;
}

float signatureLens(vec2 p, vec2 center, float radius, float distortion) {
    vec2 q=p-center;
    float r=length(q);
    float warp=r*(1.0+distortion*r*r);
    return warp-radius;
}

vec3 signatureFinish(
    vec3 color,
    vec2 uv,
    vec2 fragCoord,
    float time,
    float exposure,
    float bloom
) {
    color=max(color,0.0)*exposure;
    color+=max(color-0.74,0.0)*bloom;
    color*=0.74+0.26*vignette(uv);
    color+=grain(fragCoord,time)*0.008;
    return pow(acesVision(color),vec3(0.94));
}

#endif
