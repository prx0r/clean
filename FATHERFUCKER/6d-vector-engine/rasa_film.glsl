// One continuous agency-field learns twelve semantic transformations.
// Every scene uses the same material vocabulary; only its causal topology changes.
#ifndef RASA_INTEGRATED_FILM_GLSL
#define RASA_INTEGRATED_FILM_GLSL

struct AestheticState {
    float metamorphosis;
    float continuity;
    float centricity;
    float coherence;
    float periodicity;
    float density;
    float openness;
    float volume;
    float beat;
};

AestheticState aestheticState(
    vec4 first,
    vec2 second,
    float openness,
    float volume,
    float beat
) {
    AestheticState state;
    state.metamorphosis=saturate(first.x);
    state.continuity=saturate(first.y);
    state.centricity=saturate(first.z);
    state.coherence=saturate(first.w);
    state.periodicity=saturate(second.x);
    state.density=saturate(second.y);
    state.openness=saturate(openness);
    state.volume=saturate(volume);
    state.beat=saturate(beat);
    return state;
}

vec3 indigoBlack() { return vec3(0.004,0.006,0.018); }
vec3 fieldBlue() { return vec3(0.035,0.17,0.42); }
vec3 sensoryCyan() { return vec3(0.08,0.90,0.96); }
vec3 actionGold() { return vec3(1.18,0.51,0.12); }
vec3 possibleMagenta() { return vec3(0.92,0.12,0.62); }
vec3 recognitionPearl() { return vec3(1.12,1.05,0.90); }
vec3 livingGreen() { return vec3(0.10,0.88,0.58); }

float safeGlow(float distanceValue, float radius) {
    float d=abs(distanceValue);
    return exp(-d*d/max(radius*radius,0.000001));
}

float signedBoundary(vec2 p, vec2 center, vec2 axes, float time, float roughness) {
    vec2 q=(p-center)/axes;
    float angle=atan(q.y,q.x);
    float living=roughness*(
        0.54*sin(3.0*angle+time*0.23)
        +0.28*sin(7.0*angle-time*0.17)
        +0.18*sin(13.0*angle+time*0.11)
    );
    return (length(q)-1.0-living)*min(axes.x,axes.y);
}

float spandaMoment(float time, float rate, float coherence) {
    float phase=fract(time*rate);
    float emanate=smoothstep(0.00,0.20,phase);
    float abide=1.0-smoothstep(0.48,0.72,phase);
    float withdraw=1.0-smoothstep(0.72,1.00,phase);
    float organic=0.92+0.08*sin(time*rate*TAU*0.381966);
    return mix(emanate*abide,emanate*withdraw,0.18*(1.0-coherence))*organic;
}

vec2 fieldWarp(vec2 p, float time, AestheticState state) {
    vec2 flow=curlFlow(
        p*(0.52+0.56*state.density)+vec2(0.0,time*0.007),
        time*0.11
    );
    float amplitude=0.025+0.14*state.metamorphosis+0.035*state.volume;
    vec2 anisotropy=vec2(
        1.0+0.28*state.centricity,
        1.0-0.12*state.centricity
    );
    return p+flow*amplitude*anisotropy;
}

float continuityField(vec2 p, float time, AestheticState state) {
    vec2 q=fieldWarp(p,time,state);
    float large=fbmWarp(q*(0.62+0.74*state.density),time*0.055);
    float wave=waveInterference(
        q*(0.62+0.50*state.coherence),
        time*(0.10+0.15*state.periodicity)
    );
    float caustic=causticField(
        q*(0.52+0.36*state.density),
        time*(0.18+0.10*state.metamorphosis)
    );
    return 0.56*large+0.20*(0.5+0.5*wave)+0.24*caustic;
}

float filamentField(vec2 p, float time, AestheticState state) {
    vec2 q=fieldWarp(p*1.14,time,state);
    float phase=fbmWarp(
        q*(1.15+2.15*state.density),
        time*0.13
    );
    float frequency=mix(5.0,18.0,state.density);
    return phaseContour(phase,frequency,mix(0.072,0.028,state.density));
}

vec3 rasaGround(vec2 p, float time, int stage, AestheticState state) {
    float field=continuityField(p,time,state);
    float filaments=filamentField(p,time,state);
    vec3 undertone=fieldBlue();
    if (stage==3 || stage==7) undertone=mix(fieldBlue(),possibleMagenta(),0.24);
    if (stage==4 || stage==8) undertone=mix(fieldBlue(),sensoryCyan(),0.28);
    if (stage==5 || stage==6) undertone=mix(fieldBlue(),possibleMagenta(),0.34);
    if (stage>=9) undertone=mix(fieldBlue(),sensoryCyan(),0.36);

    vec3 color=indigoBlack();
    color+=undertone*(0.035+0.20*field)*(0.64+0.36*state.openness);
    color+=mix(sensoryCyan(),recognitionPearl(),state.coherence)
        *filaments*(0.008+0.022*state.density);
    float dust=pow(noise21(gl_FragCoord.xy*0.37+floor(time*4.0)),23.0);
    color+=recognitionPearl()*dust*(0.035+0.10*state.openness);
    return color;
}

void fieldRay(
    inout vec3 color,
    vec2 p,
    vec2 origin,
    vec2 direction,
    float width,
    vec3 hue,
    float energy
) {
    float beam=softBeam(p,origin,direction,width,0.58);
    float core=softBeam(p,origin,direction,width*0.16,0.84);
    color+=hue*(0.075*beam+0.36*core)*energy;
}

void porousBoundary(
    inout vec3 color,
    vec2 p,
    vec2 center,
    vec2 axes,
    float time,
    float open,
    vec3 hue,
    AestheticState state
) {
    float boundary=signedBoundary(p,center,axes,time,0.016+0.018*state.metamorphosis);
    float membrane=aaStroke(boundary,0.006)+0.14*safeGlow(boundary,0.065);
    float angle=atan((p.y-center.y)/axes.y,(p.x-center.x)/axes.x);
    float pores=pow(max(0.0,cos(angle*7.0-time*0.34)),24.0);
    float poreBand=safeGlow(boundary,0.018)*pores;
    color+=hue*membrane*(0.58+0.34*state.volume);
    color+=recognitionPearl()*poreBand*open*(0.28+0.55*state.beat);
}

void orbitDust(
    inout vec3 color,
    vec2 p,
    vec2 center,
    float radius,
    float time,
    float count,
    vec3 hue,
    float energy
) {
    for (int i=0;i<18;i++) {
        float fi=float(i);
        float enabled=1.0-step(count,fi);
        float a=fi*2.399963+time*(0.06+0.005*fi);
        vec2 c=center+radius*(0.52+0.48*hash11(fi+11.0))
            *vec2(cos(a),sin(a));
        float point=glowPoint(p,c,0.012+0.010*hash11(fi+4.0));
        color+=hue*point*energy*enabled*(0.22+0.18*hash11(fi+19.0));
    }
}

void channelCurve(
    inout vec3 color,
    vec2 p,
    vec2 source,
    vec2 target,
    float bend,
    float phase,
    vec3 hue,
    float energy
) {
    vec2 midpoint=0.5*(source+target);
    vec2 normal=normalize(vec2(source.y-target.y,target.x-source.x)+vec2(0.0001));
    vec2 control=midpoint+normal*bend;
    float distanceValue=10.0;
    vec2 previous=source;
    float travelling=0.0;
    for (int i=1;i<=14;i++) {
        float x=float(i)/14.0;
        vec2 point=mix(mix(source,control,x),mix(control,target,x),x);
        distanceValue=min(distanceValue,sdSegment(p,previous,point));
        travelling+=glowPoint(p,point,0.010)
            *pow(max(0.0,sin(x*TAU-phase)),10.0);
        previous=point;
    }
    color+=hue*(
        safeGlow(distanceValue,0.006)*0.52
        +safeGlow(distanceValue,0.040)*0.055
        +travelling*0.12
    )*energy;
}

vec3 stageUnbounded(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,0,state);
    vec2 q=fieldWarp(p,time,state);
    float slow=continuityField(q*0.70,time*0.42,state);
    float horizon=safeGlow(
        q.y-0.08*sin(q.x*0.72+time*0.025)-0.18*(slow-0.5),
        0.20
    );
    color+=fieldBlue()*horizon*0.038;
    float nowhere=0.0;
    for (int i=0;i<7;i++) {
        float fi=float(i);
        vec2 c=0.78*vec2(
            sin(fi*2.03+time*0.011),
            cos(fi*1.37-time*0.009)
        );
        nowhere+=glowPoint(q,c,0.22+0.05*fi);
    }
    color+=mix(fieldBlue(),sensoryCyan(),0.35)*nowhere*0.015;
    color+=recognitionPearl()*pow(max(0.0,slow-0.62),4.0)*0.08;
    return color;
}

vec3 stageFirstBias(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,1,state);
    vec2 focus=vec2(-0.34+0.06*sin(time*0.043),0.12);
    float reveal=easeInOut(local);
    fieldRay(
        color,p,vec2(-1.35,-0.24),normalize(focus-vec2(-1.35,-0.24)),
        0.22,actionGold(),reveal*(0.58+0.35*state.volume)
    );
    float bias=glowPoint(p,focus,0.10+0.08*(1.0-state.centricity));
    float displacement=continuityField((p-focus)*1.8,time,state);
    color+=actionGold()*bias*(0.10+0.20*reveal);
    color+=sensoryCyan()*bias*pow(displacement,4.0)*0.16;
    vec2 direction=normalize(p-focus+vec2(0.0001));
    float directional=0.5+0.5*dot(direction,normalize(vec2(0.82,0.31)));
    color+=fieldBlue()*directional*safeGlow(length(p-focus)-0.42*reveal,0.11)*0.035;
    return color;
}

vec3 stageLivingBoundary(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,2,state);
    // The first organism is not presented as an icon. Its right-hand edge is
    // assembled by the traffic crossing it; most of the body continues offscreen.
    float breathing=0.018*sin(time*0.61)+0.012*sin(time*0.17);
    float seamX=0.20+breathing
        +0.085*sin(p.y*2.7-time*0.16)
        +0.026*sin(p.y*8.0+time*0.29);
    float boundary=p.x-seamX;
    float inside=1.0-smoothstep(-0.05,0.045,boundary);
    float internal=continuityField(
        vec2((p.x+0.34)*1.45,p.y*1.78),
        time*0.82,
        state
    );
    color+=mix(fieldBlue(),livingGreen(),0.46)
        *inside*(0.020+0.105*internal);

    float porePhase=p.y*17.0-time*0.41;
    float porePermission=0.28+0.72*pow(0.5+0.5*cos(porePhase),10.0);
    float membrane=aaStroke(boundary,0.006)
        +0.14*safeGlow(boundary,0.062);
    color+=mix(sensoryCyan(),livingGreen(),0.36)
        *membrane*(0.42+0.42*porePermission);
    color+=recognitionPearl()*safeGlow(boundary,0.017)
        *porePermission*(0.18+0.34*state.beat);

    for (int i=0;i<9;i++) {
        float fi=float(i);
        float y=-0.68+fi*0.17+0.035*sin(time*0.12+fi*1.7);
        float x=0.20+breathing
            +0.085*sin(y*2.7-time*0.16)
            +0.026*sin(y*8.0+time*0.29);
        vec2 edge=vec2(x,y);
        vec2 exterior=edge+vec2(0.46,0.03*sin(fi));
        vec2 interior=edge-vec2(0.62,-0.04*cos(fi*1.3));
        if (mod(fi,2.0)<1.0) {
            channelCurve(color,p,exterior,interior,0.055*sin(fi*1.9),
                time*0.78-fi,sensoryCyan(),0.36+0.30*state.volume);
        } else {
            channelCurve(color,p,interior,exterior,-0.050*cos(fi*1.4),
                time*0.65+fi,actionGold(),0.28+0.28*state.beat);
        }
    }
    float formerEdge=safeGlow(boundary+0.12,0.035);
    color+=possibleMagenta()*formerEdge*0.028*state.continuity;
    return color;
}

vec3 stageInteroception(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,3,state);
    // The camera is now inside. The boundary is mostly beyond the frame and is
    // known indirectly through pressures arriving at an eccentric locus of need.
    vec2 need=vec2(-0.31,-0.13)
        +0.025*vec2(sin(time*0.17),cos(time*0.13));
    vec2 q=p-need;
    float radius=length(q*vec2(0.86,1.08));
    float pulsePhase=time*(0.36+0.20*state.periodicity);
    float inward=0.0;
    for (int i=0;i<8;i++) {
        float fi=float(i);
        float waveRadius=1.32-fract(0.15*fi+pulsePhase*0.065)*1.24;
        float arc=exp(-pow(radius-waveRadius,2.0)/(0.0022+0.0007*fi));
        float directionality=0.32+0.68*smoothstep(-0.55,0.72,
            dot(normalize(q+vec2(0.0001)),normalize(vec2(0.72,0.34))));
        inward+=arc*directionality*exp(-fi*0.16);
    }
    float interiorFlow=continuityField(
        vec2(q.x*1.18,q.y*1.62),
        time*0.62,
        state
    );
    color+=mix(possibleMagenta(),actionGold(),0.28)
        *inward*(0.030+0.082*state.volume);
    color+=sensoryCyan()*pow(interiorFlow,3.0)*0.082;
    float offscreenBoundary=p.x
        -(0.84+0.045*sin(p.y*3.2-time*0.12));
    color+=mix(sensoryCyan(),possibleMagenta(),0.22)
        *(aaStroke(offscreenBoundary,0.009)+0.10*safeGlow(offscreenBoundary,0.09))
        *0.60;
    signatureNode(color,p,need,0.090,actionGold(),0.28+0.24*state.beat);
    for (int i=0;i<10;i++) {
        float fi=float(i);
        float side=mod(fi,4.0);
        vec2 edge;
        if (side<1.0) edge=vec2(-1.05,-0.72+0.36*mod(fi,5.0));
        else if (side<2.0) edge=vec2(1.05,-0.66+0.30*mod(fi,5.0));
        else if (side<3.0) edge=vec2(-0.82+0.36*mod(fi,5.0),0.82);
        else edge=vec2(-0.68+0.32*mod(fi,5.0),-0.82);
        channelCurve(color,p,edge,need,0.09*sin(fi*2.1),time*0.45-fi,
            sensoryCyan(),0.19+0.19*state.volume);
    }
    float warmCore=glowPoint(p,need,0.23);
    color+=possibleMagenta()*warmCore*inward*0.07;
    return color;
}

vec3 stagePrediction(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,4,state);
    vec2 origin=vec2(-0.72,-0.08);
    signatureNode(color,p,origin,0.070,actionGold(),0.38+0.28*state.beat);
    float reveal=easeOut(local);
    for (int i=0;i<11;i++) {
        float fi=float(i);
        float lane=(fi-5.0)/5.0;
        vec2 target=vec2(0.82,0.66*lane+0.08*sin(fi*2.1));
        float plausibility=0.25+0.75*hash11(fi+4.0);
        float selected=1.0-smoothstep(0.11,0.36,abs(lane-0.16*sin(time*0.07)));
        vec3 hue=mix(possibleMagenta(),sensoryCyan(),plausibility);
        hue=mix(hue,actionGold(),0.70*selected);
        channelCurve(
            color,p,origin,target,0.13*lane+0.05*sin(fi),
            time*(0.45+0.12*state.periodicity)-fi,
            hue,
            reveal*(0.13+0.33*plausibility+0.46*selected)
        );
        signatureNode(color,p,target,0.032,hue,reveal*(0.09+0.23*plausibility));
    }
    float decision=softBeam(
        p,origin,normalize(vec2(1.0,0.12*sin(time*0.07))),
        0.055,0.42
    );
    color+=actionGold()*decision*(0.10+0.16*state.beat);
    return color;
}

vec3 stagePrivateAgency(vec2 p, float time, AestheticState state, float local) {
    vec2 center=vec2(0.02,-0.01);
    float contraction=mix(0.74,0.42,easeInOut(local));
    vec2 q=p/vec2(0.92,1.0);
    float aperture=signedBoundary(q,center,vec2(contraction,contraction*1.08),time,0.009);
    float inside=1.0-smoothstep(-0.04,0.05,aperture);
    vec3 color=rasaGround(p,time,5,state)*(0.36+0.64*inside);
    float internal=continuityField((p-center)*(1.3+1.2*state.centricity),time*1.3,state);
    color+=mix(possibleMagenta(),actionGold(),0.35)
        *inside*(0.025+0.14*pow(internal,3.0));
    porousBoundary(color,p,center,vec2(contraction,contraction*1.08),time,
        0.24,possibleMagenta(),state);
    float inward=softBeam(p,vec2(-1.25,0.0),vec2(1.0,0.0),0.13,0.62)
        +softBeam(p,vec2(1.25,0.0),vec2(-1.0,0.0),0.13,0.62);
    color+=sensoryCyan()*inward*inside*0.065;
    signatureNode(color,p,center,0.105,recognitionPearl(),0.24+0.36*state.centricity);
    float outsideEcho=safeGlow(aperture,0.24)*(1.0-inside);
    color+=fieldBlue()*outsideEcho*0.035*(1.0-local);
    return color;
}

vec3 stageFalseOwner(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,6,state)*0.58;
    vec2 center=vec2(0.02,0.01);
    vec2 q=projectiveWarp(p,0.62+0.22*state.metamorphosis,time*0.021);
    float knot=0.0;
    for (int i=0;i<9;i++) {
        float fi=float(i);
        float arms=2.0+mod(fi,4.0);
        vec2 r=q*rot(fi*0.71+0.08*sin(time*0.13+fi));
        float spiral=logarithmicSpiral(
            r,
            arms,
            2.4+0.31*fi,
            time*(0.34+0.03*fi)
        );
        float envelope=exp(-dot(r,r)*(0.72+0.12*fi));
        float line=1.0-smoothstep(0.035,0.095,spiral);
        knot+=line*envelope*(0.12+0.05*fi);
    }
    float interference=waveInterference(q*1.65,time*0.55);
    vec3 knotHue=mix(possibleMagenta(),actionGold(),0.5+0.5*interference);
    color+=knotHue*knot*(0.10+0.18*state.volume);
    float overclaim=glowPoint(q,center,0.075);
    color+=recognitionPearl()*overclaim*(0.48+0.34*state.centricity);
    color-=vec3(0.10,0.03,0.08)*safeGlow(length(q)-0.46,0.18)*knot;
    orbitDust(
        color,q,center,0.60,time,16.0,
        mix(possibleMagenta(),sensoryCyan(),0.36),
        0.55+0.32*state.beat
    );
    return max(color,0.0);
}

vec3 stageBiologyRemains(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,7,state);
    // Recognition does not abolish regulation. A breathing diagonal seam keeps
    // transporting, remembering and repairing without enclosing a logo-shaped self.
    float seamY=-0.03+0.16*p.x
        +0.055*sin(p.x*3.4+time*0.11)
        +0.020*sin(p.x*10.0-time*0.27);
    float boundary=p.y-seamY;
    float inside=1.0-smoothstep(-0.055,0.045,boundary);
    float alive=spandaMoment(time,0.17+0.05*state.periodicity,state.coherence);
    color+=mix(possibleMagenta(),livingGreen(),0.56)
        *inside*(0.018+0.085*continuityField(
            vec2(p.x*1.50,(p.y+0.32)*1.75),time,state
        ));
    float pore=0.30+0.70*pow(0.5+0.5*cos(p.x*23.0-time*0.39),12.0);
    color+=livingGreen()*(
        aaStroke(boundary,0.006)+0.15*safeGlow(boundary,0.067)
    )*(0.46+0.36*pore);
    color+=recognitionPearl()*safeGlow(boundary,0.019)
        *pore*(0.14+0.33*state.beat);

    for (int i=0;i<11;i++) {
        float fi=float(i);
        float x=-0.88+fi*0.176;
        float y=-0.03+0.16*x
            +0.055*sin(x*3.4+time*0.11)
            +0.020*sin(x*10.0-time*0.27);
        vec2 edge=vec2(x,y);
        vec2 normal=normalize(vec2(-0.16,1.0));
        vec2 outer=edge+normal*0.44;
        vec2 inner=edge-normal*0.46;
        vec3 hue=mod(fi,2.0)<1.0?sensoryCyan():actionGold();
        channelCurve(
            color,p,
            mod(fi,2.0)<1.0?outer:inner,
            mod(fi,2.0)<1.0?inner:outer,
            0.045*sin(fi*2.2),
            time*0.52+fi,
            hue,
            0.22+0.20*alive+0.18*state.volume
        );
    }
    float history=safeGlow(boundary+0.10,0.032)+safeGlow(boundary+0.19,0.048);
    color+=possibleMagenta()*history*0.045*state.continuity;
    return color;
}

vec3 stageNestedAgencies(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,8,state);
    // Agency becomes an ecology: many competent centres at unequal scales, with
    // no privileged container drawn around them.
    float unfold=easeInOut(local);
    vec2 previous=vec2(-0.92,0.18);
    for (int i=0;i<15;i++) {
        float fi=float(i);
        vec2 center=vec2(
            mix(-0.86,0.86,hash11(fi*7.13+2.0)),
            mix(-0.64,0.64,hash11(fi*11.71+9.0))
        );
        center+=0.025*vec2(
            sin(time*(0.031+0.002*fi)+fi),
            cos(time*(0.027+0.003*fi)+fi*1.7)
        )*unfold;
        float competence=0.3+0.7*hash11(fi+17.0);
        vec3 hue=mix(livingGreen(),actionGold(),competence);
        float cellRadius=0.028+0.043*competence;
        float cell=abs(length(p-center)-cellRadius);
        color+=hue*safeGlow(cell,0.009)*(0.17+0.12*state.volume);
        signatureNode(color,p,center,cellRadius*0.66,hue,0.11+0.16*competence);
        vec2 microA=center+cellRadius*0.48*vec2(
            cos(fi*2.4+time*0.06),sin(fi*2.4+time*0.06)
        );
        vec2 microB=center-cellRadius*0.42*vec2(
            sin(fi*1.7-time*0.04),cos(fi*1.7-time*0.04)
        );
        color+=sensoryCyan()*(
            glowPoint(p,microA,0.009)+glowPoint(p,microB,0.008)
        )*(0.10+0.16*state.density);
        if (i>0) {
            signatureChannel(color,p,previous,center,
                mix(sensoryCyan(),hue,0.6),
                (0.055+0.105*state.volume)*unfold,
                time*0.5-fi
            );
        }
        previous=center;
    }
    float micro=voronoi2((p+vec2(0.5))*mix(8.0,18.0,state.density)).y
        -voronoi2((p+vec2(0.5))*mix(8.0,18.0,state.density)).x;
    color+=sensoryCyan()*safeGlow(micro-0.045,0.013)*0.026;
    return color;
}

vec3 stageCameraReversal(vec2 p, float time, AestheticState state, float local) {
    float pull=easeInOut(local);
    vec2 localCenter=vec2(-0.17,0.04);
    vec2 lensCenter=mix(localCenter,vec2(0.28,-0.12),pull);
    float lensRadius=mix(0.56,0.12,pull);
    vec2 world=p*(0.72+0.24*pull);
    vec3 color=rasaGround(world,time,9,state);

    float manifold=continuityField(
        projectiveWarp(world,0.18+0.22*pull,time*0.015),
        time*0.48,
        state
    );
    float contour=phaseContour(
        manifold,
        mix(7.0,15.0,state.density),
        0.045
    );
    color+=mix(fieldBlue(),sensoryCyan(),0.52)
        *contour*(0.020+0.035*pull);

    float lens=sdCircle(p-lensCenter,lensRadius);
    float inside=1.0-smoothstep(-0.02,0.025,lens);
    vec2 refracted=(p-lensCenter)*(1.0+0.78*inside*(1.0-pull));
    float memory=continuityField(refracted*2.2,time*0.87,state);
    color+=possibleMagenta()*inside*pow(memory,3.0)*(0.035+0.055*(1.0-pull));
    color+=recognitionPearl()*(
        aaStroke(lens,0.004)+0.17*safeGlow(lens,0.065)
    )*(0.38+0.42*state.coherence);

    for (int i=0;i<8;i++) {
        float fi=float(i);
        float a=fi*TAU/8.0+time*0.015;
        vec2 remote=0.78*vec2(cos(a),sin(a));
        channelCurve(
            color,p,lensCenter,remote,
            0.11*sin(fi*1.4),
            time*0.24-fi,
            mix(sensoryCyan(),actionGold(),hash11(fi)),
            pull*(0.12+0.13*state.volume)
        );
    }
    return color;
}

vec3 stageCamatkara(vec2 p, float time, AestheticState state, float local) {
    float dissolve=easeInOut(smoothstep(0.00,0.48,local));
    float aperture=smoothstep(0.46,0.72,local);
    float returnSeed=smoothstep(0.60,0.86,local);
    vec2 q=projectiveWarp(p,0.22*(1.0-dissolve),time*0.006);
    vec3 ground=rasaGround(q,time,10,state);
    float field=continuityField(q*(1.0-0.28*dissolve),time*0.21,state);
    float geometry=filamentField(q,time,state);
    vec2 diagonal=normalize(vec2(0.83,0.56));
    float foldCoordinate=dot(q,diagonal)
        +0.10*sin(dot(q,vec2(-diagonal.y,diagonal.x))*4.2+time*0.025);
    float foldA=safeGlow(foldCoordinate-mix(-0.62,0.16,dissolve),0.075);
    float foldB=safeGlow(foldCoordinate-mix(0.58,-0.12,dissolve),0.095);
    float vanishingMesh=phaseContour(
        field+0.16*dot(q,vec2(-diagonal.y,diagonal.x)),
        mix(12.0,3.0,dissolve),
        mix(0.035,0.12,dissolve)
    );
    vec3 pearl=recognitionPearl()*(
        0.30+0.45*field+0.16*cos(TAU*(field+vec3(0.0).x))
    );
    vec3 color=mix(
        ground+mix(sensoryCyan(),actionGold(),field)*geometry*0.045,
        pearl,
        dissolve
    );
    color+=mix(sensoryCyan(),recognitionPearl(),dissolve)
        *(foldA+foldB)*(1.0-dissolve)*0.12;
    color+=recognitionPearl()*vanishingMesh*(1.0-dissolve)*0.045;
    // Silence is not blackness. It is near-uniform radiance with living substructure.
    float breath=0.5+0.5*sin(time*0.07+fbm(q*0.7)*TAU);
    color=mix(color,recognitionPearl()*(0.68+0.08*breath),aperture*0.72);
    vec2 seedCenter=vec2(0.23,-0.11);
    float seed=glowPoint(q,seedCenter,0.035+0.10*returnSeed);
    float seedLens=safeGlow(
        length(q-seedCenter)-mix(0.018,0.070,returnSeed),
        0.008+0.010*returnSeed
    );
    float seedHalo=safeGlow(
        length(q-seedCenter)-mix(0.050,0.120,returnSeed),
        0.020+0.018*returnSeed
    );
    color=mix(
        color,
        mix(fieldBlue(),sensoryCyan(),0.62),
        seedHalo*returnSeed*(0.34+0.18*state.volume)
    );
    color+=mix(sensoryCyan(),recognitionPearl(),0.65)
        *(seed*0.26+seedLens*0.18)
        *returnSeed*(0.62+0.38*state.volume);
    return color;
}

vec3 stageTransparentReturn(vec2 p, float time, AestheticState state, float local) {
    vec3 color=rasaGround(p,time,11,state);
    // The organism returns as an open horizon, not an erased or re-closed self.
    float seamY=0.08+0.12*p.x
        +0.072*sin(p.x*2.8-time*0.07)
        +0.022*sin(p.x*8.5+time*0.19);
    float boundary=p.y-seamY;
    float inside=1.0-smoothstep(-0.06,0.055,boundary);
    float field=continuityField(p,time*0.62,state);
    vec3 sameMaterial=mix(fieldBlue(),sensoryCyan(),0.5+0.34*field);
    color+=sameMaterial*inside*(0.016+0.055*field);
    float pore=0.22+0.78*pow(0.5+0.5*cos(p.x*19.0-time*0.26),14.0);
    color+=mix(sensoryCyan(),recognitionPearl(),0.52)
        *(aaStroke(boundary,0.005)+0.16*safeGlow(boundary,0.078))
        *(0.46+0.40*pore);
    color+=recognitionPearl()*safeGlow(boundary,0.018)
        *pore*(0.16+0.30*state.beat);

    for (int i=0;i<12;i++) {
        float fi=float(i);
        float x=-0.92+fi*0.167;
        float y=0.08+0.12*x
            +0.072*sin(x*2.8-time*0.07)
            +0.022*sin(x*8.5+time*0.19);
        vec2 edge=vec2(x,y);
        vec2 normal=normalize(vec2(-0.12,1.0));
        vec2 remote=edge+normal*0.58;
        vec2 inner=edge-normal*0.58;
        float outward=mod(fi,2.0);
        vec3 hue=mix(sensoryCyan(),actionGold(),outward);
        channelCurve(
            color,p,
            outward<0.5?remote:inner,
            outward<0.5?inner:remote,
            0.07*sin(fi*1.7),
            time*0.33-fi,
            hue,
            0.24+0.22*state.volume
        );
    }
    for (int i=0;i<13;i++) {
        float fi=float(i);
        vec2 point=vec2(
            mix(-0.88,0.88,hash11(fi*5.2+1.0)),
            mix(-0.66,0.66,hash11(fi*8.7+4.0))
        );
        point+=0.022*vec2(sin(time*0.04+fi),cos(time*0.035+fi));
        color+=mix(livingGreen(),sensoryCyan(),hash11(fi+10.0))
            *glowPoint(p,point,0.012)
            *(0.07+0.16*state.beat);
    }
    float history1=safeGlow(boundary+0.12,0.022);
    float history2=safeGlow(boundary+0.23,0.036);
    color+=possibleMagenta()*(history1*0.035+history2*0.020)*state.continuity;
    float diffuseRecognition=glowPoint(p,vec2(0.26,-0.18),0.16)
        +glowPoint(p,vec2(-0.44,0.24),0.13);
    color+=recognitionPearl()*diffuseRecognition*0.048;
    return color;
}

vec3 renderStage(
    int stage,
    vec2 p,
    float time,
    AestheticState state,
    float local
) {
    if (stage<=0) return stageUnbounded(p,time,state,local);
    if (stage==1) return stageFirstBias(p,time,state,local);
    if (stage==2) return stageLivingBoundary(p,time,state,local);
    if (stage==3) return stageInteroception(p,time,state,local);
    if (stage==4) return stagePrediction(p,time,state,local);
    if (stage==5) return stagePrivateAgency(p,time,state,local);
    if (stage==6) return stageFalseOwner(p,time,state,local);
    if (stage==7) return stageBiologyRemains(p,time,state,local);
    if (stage==8) return stageNestedAgencies(p,time,state,local);
    if (stage==9) return stageCameraReversal(p,time,state,local);
    if (stage==10) return stageCamatkara(p,time,state,local);
    return stageTransparentReturn(p,time,state,local);
}

vec3 renderRasaFilm(
    vec2 p,
    vec2 uv,
    vec2 fragCoord,
    float time,
    float progress,
    int stage,
    float local,
    AestheticState state
) {
    int safeStage=clamp(stage,0,11);
    float transition=smoothstep(0.82,0.985,local);
    float morph=transition*transition*(3.0-2.0*transition);

    vec2 continuityWarp=curlFlow(
        p*(0.65+0.25*state.density),
        time*0.043
    )*(0.018+0.034*state.metamorphosis);
    vec3 current=renderStage(
        safeStage,
        p+continuityWarp*transition,
        time,
        state,
        local
    );
    vec3 next=renderStage(
        min(safeStage+1,11),
        p-continuityWarp*(1.0-transition),
        time,
        state,
        0.0
    );
    vec3 color=mix(current,next,morph);

    float spanda=spandaMoment(
        time,
        0.075+0.055*state.periodicity,
        state.coherence
    );
    float edgeBreath=pow(max(0.0,1.0-length(p)*0.34),2.0);
    color+=mix(fieldBlue(),recognitionPearl(),state.openness)
        *edgeBreath*spanda*(0.004+0.010*state.volume);

    // Audio changes field pressure and travelling accents before finishing.
    float pressure=0.93+0.12*state.volume;
    color*=pressure;
    color+=mix(actionGold(),sensoryCyan(),state.coherence)
        *state.beat*filamentField(p*1.6,time,state)
        *(0.006+0.012*state.density);

    float exposure=mix(0.90,1.12,state.openness);
    float bloom=mix(0.42,0.78,state.coherence);
    color=signatureFinish(color,uv,fragCoord,time,exposure,bloom);
    return color;
}

#endif
