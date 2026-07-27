// A single breath-thread learns pressure, articulation, prediction, naming,
// inner speech, sentence wholeness and transparent return.
#ifndef PHONONIC_INTEGRATED_FILM_GLSL
#define PHONONIC_INTEGRATED_FILM_GLSL

struct MeaningState {
    float articulation;
    float continuity;
    float deixis;
    float resonance;
    float prosody;
    float semanticDensity;
    float openness;
    float volume;
    float beat;
};

MeaningState meaningState(
    vec4 first,
    vec2 second,
    float openness,
    float volume,
    float beat
) {
    MeaningState state;
    state.articulation=saturate(first.x);
    state.continuity=saturate(first.y);
    state.deixis=saturate(first.z);
    state.resonance=saturate(first.w);
    state.prosody=saturate(second.x);
    state.semanticDensity=saturate(second.y);
    state.openness=saturate(openness);
    state.volume=saturate(volume);
    state.beat=saturate(beat);
    return state;
}

vec3 phononicBlack() { return vec3(0.003,0.002,0.014); }
vec3 cathedralViolet() { return vec3(0.105,0.020,0.245); }
vec3 breathCopper() { return vec3(1.20,0.39,0.105); }
vec3 vowelCyan() { return vec3(0.055,0.90,1.08); }
vec3 consonantRose() { return vec3(1.18,0.055,0.34); }
vec3 contextGreen() { return vec3(0.18,1.02,0.56); }
vec3 meaningPearl() { return vec3(1.14,0.91,0.61); }

float phonicGlow(float distanceValue, float radius) {
    float d=abs(distanceValue);
    return exp(-d*d/max(radius*radius,0.000001));
}

float phononicPulse(float time, float rate, float coherence) {
    float phase=fract(time*rate);
    float rise=smoothstep(0.00,0.16,phase);
    float hold=1.0-smoothstep(0.42,0.68,phase);
    float release=(1.0-smoothstep(0.66,1.00,phase))*0.42;
    return mix(rise*hold,rise*(hold+release),0.26*(1.0-coherence));
}

vec2 phononicWarp(vec2 p, float time, MeaningState state) {
    vec2 flow=curlFlow(
        p*(0.48+0.72*state.semanticDensity)+vec2(time*0.004,-time*0.006),
        time*0.075
    );
    float amount=0.018+0.072*(1.0-state.articulation)
        +0.035*state.semanticDensity+0.018*state.volume;
    return p+flow*amount;
}

float pressureField(vec2 p, float time, MeaningState state) {
    vec2 q=phononicWarp(p,time,state);
    float interference=waveInterference(
        q*(0.72+0.60*state.semanticDensity),
        time*(0.18+0.23*state.prosody)
    );
    float body=fbmWarp(
        q*(0.56+0.62*state.semanticDensity),
        time*0.055
    );
    float formants=
        0.50+0.25*sin(q.x*(4.0+8.0*state.articulation)-time*0.22)
        +0.25*sin(q.y*(7.0+11.0*state.resonance)+time*0.17);
    return 0.46*body+0.28*(0.5+0.5*interference)+0.26*formants;
}

float spectralThreads(vec2 p, float time, MeaningState state) {
    float pressure=pressureField(p,time,state);
    float frequency=mix(4.0,22.0,state.articulation);
    return phaseContour(
        pressure,
        frequency,
        mix(0.080,0.025,state.articulation)
    );
}

vec3 phononicGround(
    vec2 p,
    float time,
    int stage,
    MeaningState state
) {
    vec2 q=phononicWarp(p,time,state);
    float liquid=pressureField(q,time*0.72,state);
    float caustic=causticField(
        q*(0.52+0.36*state.semanticDensity),
        time*0.11
    );
    float threads=spectralThreads(q,time,state);
    vec3 undertone=cathedralViolet();
    if (stage==2 || stage==6) undertone=mix(cathedralViolet(),vowelCyan(),0.30);
    if (stage==3 || stage==4) undertone=mix(cathedralViolet(),contextGreen(),0.16);
    if (stage==5 || stage==7) undertone=mix(cathedralViolet(),consonantRose(),0.24);
    if (stage>=8) undertone=mix(cathedralViolet(),vowelCyan(),0.22);

    vec3 color=phononicBlack();
    color+=undertone*(0.045+0.18*liquid)*(0.62+0.38*state.openness);
    color+=iridescentFilm(liquid+time*0.004,0.66)
        *caustic*(0.008+0.030*state.resonance);
    color+=mix(vowelCyan(),meaningPearl(),state.resonance)
        *threads*(0.004+0.015*state.semanticDensity);
    float dust=pow(
        noise21(gl_FragCoord.xy*0.43+floor(time*5.0)),
        22.0
    );
    color+=meaningPearl()*dust*(0.025+0.075*state.openness);
    return color;
}

float breathCurveY(
    float x,
    float time,
    float phase,
    float offset,
    float complexity
) {
    return offset
        +0.115*sin(x*(1.7+0.6*complexity)+time*0.085+phase)
        +0.042*sin(x*(5.1+2.2*complexity)-time*0.13-phase*0.7)
        +0.018*sin(x*13.0+time*0.19+phase*2.0);
}

float breathCurveDistance(
    vec2 p,
    float time,
    float phase,
    float offset,
    float complexity
) {
    float distanceValue=10.0;
    float x0=-1.95;
    vec2 previous=vec2(
        x0,
        breathCurveY(x0,time,phase,offset,complexity)
    );
    for (int i=1;i<=34;i++) {
        float x=mix(-1.95,1.95,float(i)/34.0);
        vec2 point=vec2(
            x,
            breathCurveY(x,time,phase,offset,complexity)
        );
        distanceValue=min(distanceValue,sdSegment(p,previous,point));
        previous=point;
    }
    return distanceValue;
}

void paintBreathThread(
    inout vec3 color,
    vec2 p,
    float time,
    float phase,
    float offset,
    float complexity,
    float width,
    vec3 hue,
    float energy
) {
    float d=breathCurveDistance(p,time,phase,offset,complexity);
    float core=phonicGlow(d,width*0.24);
    float glass=phonicGlow(d,width);
    color+=hue*(0.48*core+0.11*glass)*energy;

    float travelX=mix(
        -1.82,
        1.82,
        fract(time*(0.020+0.014*complexity)+phase*0.17)
    );
    vec2 travelling=vec2(
        travelX,
        breathCurveY(travelX,time,phase,offset,complexity)
    );
    color+=mix(hue,meaningPearl(),0.56)
        *glowPoint(p,travelling,width*1.25)*energy*0.38;
}

void phonicBezier(
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
    vec2 normal=normalize(
        vec2(source.y-target.y,target.x-source.x)+vec2(0.0001)
    );
    vec2 control=midpoint+normal*bend;
    float distanceValue=10.0;
    float travelling=0.0;
    vec2 previous=source;
    for (int i=1;i<=16;i++) {
        float x=float(i)/16.0;
        vec2 point=mix(mix(source,control,x),mix(control,target,x),x);
        distanceValue=min(distanceValue,sdSegment(p,previous,point));
        travelling+=glowPoint(p,point,0.009)
            *pow(max(0.0,sin(x*TAU-phase)),12.0);
        previous=point;
    }
    color+=hue*(
        phonicGlow(distanceValue,0.005)*0.52
        +phonicGlow(distanceValue,0.036)*0.060
        +travelling*0.11
    )*energy;
}

float glyphMark(
    vec2 p,
    vec2 center,
    float size,
    float seed,
    float phase
) {
    vec2 q=(p-center)/size;
    q*=rot((hash11(seed)-0.5)*1.7+phase);
    vec2 a=vec2(-0.56,-0.42+0.35*hash11(seed+1.0));
    vec2 b=vec2(0.48,-0.10+0.48*hash11(seed+2.0));
    vec2 c=vec2(-0.16,0.54);
    vec2 d=vec2(0.54,0.18-0.30*hash11(seed+3.0));
    float stroke=sdSegment(q,a,b);
    stroke=min(stroke,sdSegment(q,b,c));
    stroke=min(stroke,sdSegment(q,c,d));
    if (mod(floor(seed),2.0)<1.0) {
        stroke=min(stroke,sdSegment(q,a+vec2(0.16,0.48),d));
    }
    return stroke*size;
}

vec3 stageUnspoken(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,0,state);
    vec2 q=phononicWarp(p,time*0.5,state);
    float pressure=pressureField(q*0.72,time*0.42,state);
    float nowhere=0.0;
    for (int i=0;i<6;i++) {
        float fi=float(i);
        vec2 source=vec2(
            mix(-1.42,1.42,hash11(fi+3.0)),
            mix(-0.66,0.66,hash11(fi+8.0))
        );
        nowhere+=glowPoint(q,source,0.26+0.07*fi);
    }
    color+=cathedralViolet()*nowhere*0.013;
    paintBreathThread(
        color,q,time,0.0,-0.08,0.12,0.18,
        breathCopper(),0.11+0.10*easeInOut(local)
    );
    float broad=phonicGlow(
        q.y-0.15*sin(q.x*0.8+time*0.018)-0.12*(pressure-0.5),
        0.23
    );
    color+=mix(cathedralViolet(),breathCopper(),0.18)*broad*0.026;
    return color;
}

vec3 stageRecurrence(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,1,state);
    float reveal=easeOut(local);
    for (int i=0;i<8;i++) {
        float fi=float(i);
        float history=exp(-fi*0.35);
        float offset=-0.26+fi*0.072;
        paintBreathThread(
            color,p,time-fi*2.4,fi*0.37,offset,
            0.24+0.06*fi,0.045+0.004*fi,
            mix(cathedralViolet(),breathCopper(),history),
            reveal*(0.22+0.52*history)
        );
    }
    float accent=phononicPulse(
        time,
        0.11+0.10*state.prosody,
        state.resonance
    );
    float memoryVeil=phaseContour(
        pressureField(p*1.2,time-4.0,state)
            -pressureField(p*1.2,time,state),
        8.0,
        0.052
    );
    color+=vowelCyan()*memoryVeil*accent*0.018;
    return color;
}

vec3 stageVowelChamber(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,2,state);
    float xProgress=smoothstep(-1.55,1.25,p.x);
    float axis=0.02+0.06*sin(p.x*1.35-time*0.045);
    float chamber=0.48-0.30*xProgress
        +0.17*smoothstep(0.48,1.45,p.x)
        +0.025*sin(p.x*5.0+time*0.16);
    float wall=abs(p.y-axis)-chamber;
    float inside=1.0-smoothstep(-0.035,0.028,wall);
    float glass=aaStroke(wall,0.008)+0.13*phonicGlow(wall,0.080);
    float liquid=pressureField(
        vec2(p.x*0.84,(p.y-axis)/max(chamber,0.09)),
        time,
        state
    );
    color+=mix(cathedralViolet(),vowelCyan(),0.30+0.34*liquid)
        *inside*(0.018+0.072*liquid);
    color+=iridescentFilm(liquid+0.08*p.x,0.72)
        *glass*(0.30+0.30*state.volume);

    for (int i=0;i<6;i++) {
        float fi=float(i);
        float band=(fi-2.5)/3.0;
        float y=axis+band*chamber*0.72
            +0.025*sin(p.x*(2.0+fi)-time*(0.12+0.025*fi));
        float d=abs(p.y-y);
        vec3 hue=mix(vowelCyan(),meaningPearl(),fi/5.0);
        color+=hue*phonicGlow(d,0.007+0.002*fi)
            *inside*(0.13+0.12*state.resonance);
    }
    paintBreathThread(
        color,p,time,0.9,axis,0.46,0.052,
        breathCopper(),0.55+0.26*state.beat
    );
    float exhale=softBeam(
        p,vec2(0.58,axis),normalize(vec2(1.0,0.08)),
        0.18,0.42
    );
    color+=vowelCyan()*exhale*easeOut(local)*0.050;
    return color;
}

vec3 stageContextHears(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,3,state);
    float baseY=breathCurveY(p.x,time,1.6,-0.02,0.72);
    float threadD=abs(p.y-baseY);
    float gapMask=smoothstep(0.13,0.24,abs(p.x+0.04));
    color+=breathCopper()*phonicGlow(threadD,0.012)
        *gapMask*(0.34+0.25*state.volume);

    vec2 upperCenter=vec2(-0.56,0.24);
    vec2 lowerCenter=vec2(0.58,-0.23);
    float upper=sdArcBand(
        (p-upperCenter)*rot(-0.30),
        0.34,0.22,2.86
    );
    float lower=sdArcBand(
        (p-lowerCenter)*rot(2.86),
        0.38,-2.72,-0.20
    );
    color+=vowelCyan()*(
        aaStroke(upper,0.007)+0.10*phonicGlow(upper,0.065)
    )*(0.44+0.22*state.beat);
    color+=consonantRose()*(
        aaStroke(lower,0.007)+0.10*phonicGlow(lower,0.065)
    )*(0.42+0.22*state.volume);

    phonicBezier(
        color,p,upperCenter+vec2(0.10,-0.06),vec2(-0.03,baseY),
        0.13,time*0.42,vowelCyan(),0.28+0.22*state.resonance
    );
    phonicBezier(
        color,p,lowerCenter+vec2(-0.10,0.06),vec2(-0.03,baseY),
        -0.14,time*0.39,consonantRose(),0.28+0.22*state.volume
    );

    float restoration=easeInOut(smoothstep(0.22,0.72,local));
    float restored=phonicGlow(threadD,0.018)
        *(1.0-smoothstep(0.02,0.18,abs(p.x+0.04)));
    float contextualHalo=glowPoint(p,vec2(-0.04,baseY),0.18);
    color+=contextGreen()*(0.26*restored+0.08*contextualHalo)
        *restoration*(0.72+0.28*state.resonance);

    float thirdWave=breathCurveDistance(
        p,time,2.9,0.12,0.88
    );
    color+=mix(contextGreen(),meaningPearl(),0.32)
        *phonicGlow(thirdWave,0.025)
        *smoothstep(0.48,0.88,local)*0.11;
    return color;
}

vec3 stageNameCutsWorld(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,4,state);
    float front=p.x+0.30*sin(p.y*1.75+time*0.028);
    float crystallize=smoothstep(-0.24,0.20,front)
        *easeInOut(smoothstep(0.08,0.72,local));
    vec2 flow=curlFlow(p*0.62,time*0.12)
        *mix(0.15,0.012,crystallize);
    vec2 q=(p+flow+vec2(time*0.004,0.0))
        *mix(3.2,6.8,state.semanticDensity);
    vec2 voronoi=voronoi2(q);
    float edge=voronoi.y-voronoi.x;
    float facets=phonicGlow(edge,0.034);
    float cellValue=noise21(floor(q)+vec2(31.7,8.4));
    vec3 cellHue=mix(
        mix(vowelCyan(),contextGreen(),cellValue),
        meaningPearl(),
        0.16+0.16*sin(cellValue*TAU)
    );
    float cellGlass=(0.10+0.10*cellValue)
        *(0.72+0.28*sin(q.x*0.72+q.y*0.46-time*0.07));
    color+=cellHue*cellGlass*crystallize;
    color+=mix(contextGreen(),meaningPearl(),0.24)
        *facets*crystallize*(0.15+0.13*state.articulation);
    float liquidPhase=sin(
        p.y*8.0+1.4*sin(p.x*2.1-time*0.06)
    );
    float liquidContours=phonicGlow(liquidPhase,0.11);
    color+=mix(vowelCyan(),breathCopper(),0.34)
        *liquidContours*(1.0-crystallize)*0.050;

    for (int i=0;i<16;i++) {
        float fi=float(i);
        vec2 base=vec2(
            mix(-1.42,1.42,hash11(fi*7.7+3.0)),
            mix(-0.64,0.64,hash11(fi*4.9+8.0))
        );
        vec2 drift=0.055*vec2(
            sin(time*0.035+fi),
            cos(time*0.029+fi*1.6)
        )*(1.0-crystallize);
        vec2 center=base+drift;
        float portable=glowPoint(p,center,0.025+0.010*hash11(fi));
        color+=mix(breathCopper(),meaningPearl(),hash11(fi+11.0))
            *portable*(0.10+0.26*crystallize);
    }
    paintBreathThread(
        color,p,time,3.2,-0.04,0.94,0.042,
        breathCopper(),0.62+0.30*state.beat
    );
    float hardCut=phonicGlow(front,0.032);
    color+=meaningPearl()*hardCut*easeInOut(local)*0.14;
    return color;
}

vec3 stageInnerSpeaker(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,5,state)*0.78;
    vec2 center=vec2(0.24,-0.03);
    vec2 q=projectiveWarp(
        (p-center)*rot(0.10*sin(time*0.035)),
        0.42+0.25*state.deixis,
        time*0.018
    );
    vec2 lp=logPolar(q+vec2(0.0001));
    float spiralPhase=
        2.0*lp.y-3.45*lp.x-time*(0.22+0.12*state.prosody);
    float secondPhase=
        -2.0*lp.y-4.10*lp.x+time*0.19+1.7;
    float spiral=abs(sin(spiralPhase));
    float secondSpiral=abs(sin(secondPhase));
    float radial=length(q);
    float envelope=smoothstep(0.08,0.17,radial)
        *(1.0-smoothstep(1.15,2.15,radial));
    vec3 twist=mix(
        consonantRose(),
        vowelCyan(),
        0.5+0.5*sin(lp.y+lp.x*0.7)
    );
    color+=twist*(
        phonicGlow(spiral,0.095)*0.42
        +phonicGlow(secondSpiral,0.078)*0.24
    )*envelope*(0.55+0.34*state.volume);
    float ribbonBody=(
        phonicGlow(spiral,0.25)
        +phonicGlow(secondSpiral,0.21)
    )*envelope;
    color+=mix(cathedralViolet(),meaningPearl(),0.22)
        *ribbonBody*0.065;

    float darkAperture=glowPoint(p,center,0.15);
    color*=1.0-0.48*darkAperture;
    color+=meaningPearl()*glowPoint(p,center,0.040)
        *(0.42+0.38*state.deixis);

    for (int i=0;i<9;i++) {
        float fi=float(i);
        float a=fi*0.77+time*0.035;
        float radius=0.22+0.074*fi;
        vec2 echo=center+radius*vec2(cos(a),sin(a))*vec2(1.12,0.82);
        float mark=glyphMark(p,echo,0.048,fi,time*0.012);
        color+=mix(consonantRose(),breathCopper(),fi/8.0)
            *phonicGlow(mark,0.007)
            *exp(-fi*0.15)*(0.27+0.24*state.beat);
    }
    phonicBezier(
        color,p,vec2(-1.45,0.18),center,
        0.28,time*0.54,breathCopper(),
        0.42+0.28*state.volume
    );
    return color;
}

vec2 sentenceNode(float index, float time) {
    float x=-1.46+index*0.265;
    float y=0.22*sin(index*1.14+time*0.018)
        +0.10*sin(index*2.73-time*0.012);
    return vec2(x,y);
}

vec3 stageSentenceOrganism(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,6,state);
    float whole=easeInOut(smoothstep(0.12,0.58,local));
    float backward=fract(time*0.055);
    vec2 previous=sentenceNode(0.0,time);
    for (int i=0;i<12;i++) {
        float fi=float(i);
        vec2 node=sentenceNode(fi,time);
        vec3 hue=spectral(fi/12.0+time*0.004);
        float mark=glyphMark(
            p,node,0.055+0.015*hash11(fi+4.0),fi,time*0.008
        );
        color+=hue*phonicGlow(mark,0.007)
            *(0.13+0.16*state.semanticDensity)*(0.45+0.55*whole);
        color+=meaningPearl()*glowPoint(p,node,0.018)
            *(0.08+0.13*state.beat);
        if (i>0) {
            phonicBezier(
                color,p,previous,node,0.045*sin(fi*1.6),
                time*0.32-fi,vowelCyan(),
                whole*(0.12+0.14*state.continuity)
            );
        }
        float reverseIndex=11.0-backward*11.0;
        float returnPulse=exp(-pow(fi-reverseIndex,2.0)/0.30);
        color+=breathCopper()*glowPoint(p,node,0.060)
            *returnPulse*whole*0.24;
        previous=node;
    }

    float body=breathCurveDistance(p,time,4.3,0.0,1.18);
    float bodyGlass=phonicGlow(body,0.24);
    float bodyCore=phonicGlow(body,0.035);
    float inner=pressureField(p*1.35,time*0.62,state);
    color+=mix(vowelCyan(),meaningPearl(),inner)
        *(0.17*bodyGlass+0.28*bodyCore)*whole;
    float organSkin=phaseContour(
        inner+0.10*sin(p.x*8.0-time*0.12),
        7.0,0.090
    );
    color+=mix(contextGreen(),vowelCyan(),inner)
        *organSkin*bodyGlass*whole*0.075;
    for (int i=0;i<7;i++) {
        float fi=float(i);
        float x=-1.14+fi*0.37;
        float y=breathCurveY(x,time,4.3,0.0,1.18);
        vec2 spine=vec2(x,y);
        vec2 fin=spine+vec2(
            0.10*sin(fi*1.4),
            (mod(fi,2.0)<1.0?1.0:-1.0)*(0.18+0.05*sin(time*0.04+fi))
        );
        phonicBezier(
            color,p,spine,fin,0.035*sin(fi),
            time*0.22-fi,contextGreen(),
            whole*(0.25+0.16*state.volume)
        );
    }
    float headX=1.28;
    float headY=breathCurveY(headX,time,4.3,0.0,1.18);
    color+=meaningPearl()*glowPoint(p,vec2(headX,headY),0.085)
        *whole*(0.28+0.25*state.beat);
    return color;
}

vec3 stageSemanticFlash(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,7,state)*0.58;
    float flash=exp(-pow((local-0.28)/0.105,2.0));
    float fracture=easeInOut(smoothstep(0.34,0.72,local));
    float afterimage=breathCurveDistance(p,time,4.3,0.0,1.18);
    color+=meaningPearl()*phonicGlow(afterimage,0.060)
        *(0.26+0.72*flash)*(1.0-0.45*fracture);

    vec2 qa=p*rot(0.52)+vec2(time*0.008,0.0);
    vec2 qb=p*rot(-0.67)-vec2(time*0.006,0.0);
    float phaseA=sin(
        qa.y*10.0+1.25*sin(qa.x*2.2-time*0.07)
    );
    float phaseB=sin(
        qb.y*8.0+1.10*sin(qb.x*2.6+time*0.06)
    );
    float argumentA=phonicGlow(phaseA,0.095);
    float argumentB=phonicGlow(phaseB,0.095);
    float split=smoothstep(-0.52,0.52,p.x+0.18*sin(p.y*2.3));
    color+=vowelCyan()*argumentA*fracture*(0.08+0.22*(1.0-split));
    color+=consonantRose()*argumentB*fracture*(0.08+0.22*split);

    float coherence=argumentA*argumentB;
    color+=contextGreen()*coherence*fracture*0.16;
    vec2 flashCenter=vec2(-0.24,0.10);
    float flashRadius=length((p-flashCenter)*vec2(0.82,1.0));
    float flashWave=phonicGlow(
        flashRadius-(0.10+0.52*flash),
        0.065
    );
    color+=meaningPearl()*(
        flashWave*0.46+glowPoint(p,flashCenter,0.30)*0.22
    )*flash;
    return color;
}

vec3 stageSpeechDeepens(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,8,state);
    vec2 normal=normalize(vec2(0.84,-0.54));
    vec2 tangent=vec2(-normal.y,normal.x);
    float travel=(local-0.5)*0.46;
    for (int i=0;i<4;i++) {
        float fi=float(i);
        float position=-0.86+fi*0.56-travel;
        float coordinate=dot(p,normal)-position
            +0.045*sin(dot(p,tangent)*(3.0+fi)+time*(0.035+fi*0.01));
        float plane=aaStroke(coordinate,0.007)
            +0.13*phonicGlow(coordinate,0.075+0.015*fi);
        float veil=phonicGlow(coordinate,0.24+0.025*fi);
        float texture;
        if (i==0) {
            texture=0.5+0.5*sin(dot(p,tangent)*18.0-time*0.35);
        } else if (i==1) {
            texture=phaseContour(
                pressureField(p*1.5,time,state),15.0,0.040
            );
        } else if (i==2) {
            texture=causticField(p*0.8+fi,time*0.08);
        } else {
            texture=0.58+0.42*fbmWarp(p*0.55,time*0.03);
        }
        vec3 hue;
        if (i==0) hue=consonantRose();
        else if (i==1) hue=vowelCyan();
        else if (i==2) hue=contextGreen();
        else hue=meaningPearl();
        color+=hue*plane*(0.22+0.16*texture)*(0.72+0.28*state.volume);
        color+=mix(hue,cathedralViolet(),0.52)
            *veil*(0.030+0.060*texture);
        color+=meaningPearl()*veil*texture*0.018;
    }

    float diagonalThread=abs(
        dot(p,tangent)
        -0.11*sin(dot(p,normal)*4.0-time*0.10)
    );
    color+=breathCopper()*(
        phonicGlow(diagonalThread,0.010)*0.42
        +phonicGlow(diagonalThread,0.070)*0.075
    )*(0.62+0.24*state.beat);
    float depthDust=pow(
        noise21((p+normal*time*0.012)*70.0),
        18.0
    );
    color+=meaningPearl()*depthDust*0.055;
    return color;
}

vec3 stageListenerReversal(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,9,state);
    float pull=easeInOut(local);
    vec2 vanishing=mix(vec2(0.78,-0.14),vec2(-1.36,0.18),pull);
    for (int i=0;i<13;i++) {
        float fi=float(i);
        float y=-0.70+fi*0.117;
        vec2 edge=vec2(-1.62,y+0.05*sin(fi+time*0.03));
        vec3 hue=mix(vowelCyan(),breathCopper(),hash11(fi+4.0));
        phonicBezier(
            color,p,edge,vanishing,
            0.11*sin(fi*1.7+time*0.014),
            time*0.20-fi,
            hue,
            (0.09+0.12*state.volume)*(0.35+0.65*pull)
        );
    }

    vec2 q=p-vanishing;
    float wavefronts=0.0;
    for (int i=0;i<8;i++) {
        float fi=float(i);
        float radius=0.18+fi*0.19+0.07*sin(time*0.06-fi);
        float arc=abs(length(q*vec2(0.82,1.08))-radius);
        float openArc=smoothstep(-0.75,0.48,normalize(q+vec2(0.0001)).x);
        wavefronts+=phonicGlow(arc,0.011+0.003*fi)
            *openArc*exp(-fi*0.16);
    }
    color+=mix(vowelCyan(),meaningPearl(),pull)
        *wavefronts*(0.05+0.10*state.resonance);

    vec2 listener=mix(vec2(0.58,-0.12),vec2(-0.66,0.12),pull);
    float fold=glyphMark(p,listener,mix(0.12,0.035,pull),41.0,time*0.01);
    color+=meaningPearl()*phonicGlow(fold,0.010)
        *(0.28+0.26*(1.0-pull));
    color+=cathedralViolet()*glowPoint(p,listener,0.16)*(1.0-pull)*0.12;
    return color;
}

vec3 stageWordlessRecognition(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    float unbind=easeInOut(smoothstep(0.00,0.44,local));
    float silenceAperture=smoothstep(0.43,0.54,local)
        *(1.0-smoothstep(0.66,0.74,local));
    // The word returns at the key sentence, not gradually somewhere after it.
    float returnSeed=smoothstep(0.620,0.680,local);
    vec3 ground=phononicGround(p,time,10,state);
    float standingY=0.05+0.17*sin(
        p.x*(1.7+0.4*state.resonance)-time*0.036
    )+0.035*sin(p.x*7.0+time*0.07);
    float standing=abs(p.y-standingY);
    float field=pressureField(p*0.62,time*0.18,state);
    float slowContour=phaseContour(
        field+0.08*sin(p.x*3.0-time*0.025),
        4.0,0.12
    );
    vec3 silenceField=vec3(0.014,0.004,0.052)
        +cathedralViolet()*(0.38+0.48*field)
        +mix(cathedralViolet(),vowelCyan(),0.14)
            *phonicGlow(standing,0.30)*0.28
        +mix(cathedralViolet(),meaningPearl(),0.10)
            *slowContour*0.030;
    vec3 color=mix(ground,silenceField,unbind);

    float remnant=spectralThreads(p*0.8,time,state);
    color+=meaningPearl()*remnant*(1.0-unbind)*0.025;
    color=mix(
        color,
        vec3(0.010,0.003,0.038)
            +cathedralViolet()*(0.30+0.30*field)
            +vowelCyan()*phonicGlow(standing,0.34)*0.025,
        silenceAperture*0.44
    );
    color+=mix(cathedralViolet(),vowelCyan(),0.24)*(
        0.050*phonicGlow(standing,0.030)
        +0.055*phonicGlow(standing,0.18)
    )*(0.45+0.55*silenceAperture);

    float copperCore=phonicGlow(standing,0.006);
    float copperAura=phonicGlow(standing,0.060);
    color+=breathCopper()*(0.46*copperCore+0.085*copperAura)
        *returnSeed*(0.52+0.48*state.volume);
    float pointing=glowPoint(
        p,
        vec2(0.36,standingY),
        0.045+0.075*returnSeed
    );
    color+=meaningPearl()*pointing*returnSeed*(0.20+0.22*state.beat);
    return color;
}

vec3 stageTransparentSpeech(
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    vec3 color=phononicGround(p,time,11,state);
    float horizonY=-0.04+0.12*sin(p.x*1.8-time*0.055)
        +0.035*sin(p.x*7.4+time*0.10);
    float horizon=abs(p.y-horizonY);
    color+=breathCopper()*(
        phonicGlow(horizon,0.006)*0.34
        +phonicGlow(horizon,0.068)*0.065
    )*(0.54+0.24*state.volume);

    for (int i=0;i<22;i++) {
        float fi=float(i);
        float lane=hash11(fi*9.4+3.0);
        float speed=0.025+0.020*hash11(fi+7.0);
        float x=mix(-1.72,1.72,fract(hash11(fi*4.1)+time*speed));
        float y=mix(-0.62,0.62,lane)
            +0.16*sin(x*(1.4+hash11(fi)*2.0)+time*0.06+fi);
        vec2 center=vec2(x,y);
        float side=sign(y-horizonY);
        center.y-=side*0.20*easeInOut(local)
            *sin(time*0.022+fi*1.3);
        float mark=glyphMark(
            p,center,0.052+0.044*hash11(fi+2.0),
            fi,time*0.008+0.12*sin(fi)
        );
        vec3 hue;
        float choice=hash11(fi+12.0);
        if (choice<0.33) hue=vowelCyan();
        else if (choice<0.66) hue=contextGreen();
        else hue=consonantRose();
        color+=hue*(
            phonicGlow(mark,0.006)*0.44
            +phonicGlow(mark,0.038)*0.082
        )*(0.32+0.24*state.beat);
    }

    for (int i=0;i<9;i++) {
        float fi=float(i);
        float x=-1.42+fi*0.355;
        float y=-0.04+0.12*sin(x*1.8-time*0.055)
            +0.035*sin(x*7.4+time*0.10);
        vec2 source=vec2(x,y-0.46);
        vec2 target=vec2(x+0.14*sin(fi),y+0.46);
        phonicBezier(
            color,p,
            mod(fi,2.0)<1.0?source:target,
            mod(fi,2.0)<1.0?target:source,
            0.065*sin(fi*1.8),
            time*0.31-fi,
            mix(vowelCyan(),breathCopper(),mod(fi,2.0)),
            0.19+0.18*state.volume
        );
    }
    float aftertone=breathCurveDistance(p,time,0.2,horizonY,0.22);
    color+=meaningPearl()*phonicGlow(aftertone,0.16)
        *smoothstep(0.70,1.0,local)*0.026;
    return color;
}

vec3 renderPhononicStage(
    int stage,
    vec2 p,
    float time,
    MeaningState state,
    float local
) {
    if (stage<=0) return stageUnspoken(p,time,state,local);
    if (stage==1) return stageRecurrence(p,time,state,local);
    if (stage==2) return stageVowelChamber(p,time,state,local);
    if (stage==3) return stageContextHears(p,time,state,local);
    if (stage==4) return stageNameCutsWorld(p,time,state,local);
    if (stage==5) return stageInnerSpeaker(p,time,state,local);
    if (stage==6) return stageSentenceOrganism(p,time,state,local);
    if (stage==7) return stageSemanticFlash(p,time,state,local);
    if (stage==8) return stageSpeechDeepens(p,time,state,local);
    if (stage==9) return stageListenerReversal(p,time,state,local);
    if (stage==10) return stageWordlessRecognition(p,time,state,local);
    return stageTransparentSpeech(p,time,state,local);
}

vec3 renderPhononicFilm(
    vec2 p,
    vec2 uv,
    vec2 fragCoord,
    float time,
    float progress,
    int stage,
    float local,
    MeaningState state
) {
    int safeStage=clamp(stage,0,11);
    float transition=smoothstep(0.82,0.985,local);
    float morph=transition*transition*(3.0-2.0*transition);
    vec2 causalWarp=curlFlow(
        p*(0.56+0.36*state.semanticDensity),
        time*0.047
    )*(0.014+0.034*(1.0-state.articulation));

    vec3 current=renderPhononicStage(
        safeStage,
        p+causalWarp*transition,
        time,
        state,
        local
    );
    vec3 next=renderPhononicStage(
        min(safeStage+1,11),
        p-causalWarp*(1.0-transition),
        time,
        state,
        0.0
    );
    vec3 color=mix(current,next,morph);

    // Audio pressure changes wave topology and segmentation before finishing.
    vec2 audioCoordinate=p+curlFlow(
        p*(1.1+state.semanticDensity),
        time*0.09
    )*(0.012+0.030*state.volume);
    float audioContour=phaseContour(
        pressureField(
            audioCoordinate*(1.3+0.35*state.articulation),
            time+state.beat*0.18,
            state
        ),
        mix(8.0,20.0,state.articulation),
        mix(0.052,0.024,state.prosody)
    );
    color+=mix(breathCopper(),vowelCyan(),state.resonance)
        *audioContour*state.beat
        *(0.004+0.012*state.semanticDensity);

    float breath=phononicPulse(
        time,
        0.060+0.050*state.prosody,
        state.resonance
    );
    color+=cathedralViolet()*breath*(0.004+0.010*state.volume);
    float exposure=mix(0.92,1.09,state.openness);
    float bloom=mix(0.48,0.82,state.resonance);
    return signatureFinish(
        color,uv,fragCoord,time,exposure,bloom
    );
}

#endif
