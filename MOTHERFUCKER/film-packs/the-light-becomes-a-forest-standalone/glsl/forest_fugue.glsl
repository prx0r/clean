// The Light Becomes a Forest
// One five-lobed seed becomes constraint, metabolism, appetite, nested agency,
// conflict, reciprocity, ecosystem, recognition, and open abundance.
#ifndef FOREST_FUGUE_GLSL
#define FOREST_FUGUE_GLSL

struct AbundanceState {
    float radiance;
    float localization;
    float appetite;
    float reciprocity;
    float fecundity;
    float recognition;
    vec4 voices;
    float tension;
    float subject;
    float openness;
    float volume;
    float beat;
};

AbundanceState abundanceState(
    vec4 first,
    vec2 second,
    vec4 musicA,
    vec2 musicB,
    float openness,
    float volume,
    float beat
) {
    AbundanceState state;
    state.radiance=saturate(first.x);
    state.localization=saturate(first.y);
    state.appetite=saturate(first.z);
    state.reciprocity=saturate(first.w);
    state.fecundity=saturate(second.x);
    state.recognition=saturate(second.y);
    state.voices=clamp(musicA,0.0,1.0);
    state.tension=saturate(musicB.x);
    state.subject=saturate(musicB.y);
    state.openness=saturate(openness);
    state.volume=saturate(volume);
    state.beat=saturate(beat);
    return state;
}

vec3 forestVoid() { return vec3(0.003,0.008,0.030); }
vec3 mineralBlue() { return vec3(0.025,0.090,0.255); }
vec3 seedGold() { return vec3(1.18,0.73,0.20); }
vec3 willCoral() { return vec3(1.16,0.13,0.10); }
vec3 knowingSky() { return vec3(0.055,0.72,1.12); }
vec3 actionGreen() { return vec3(0.18,1.04,0.40); }
vec3 earthViolet() { return vec3(0.27,0.08,0.88); }
vec3 careRose() { return vec3(1.10,0.34,0.70); }
vec3 afterLight() { return vec3(1.14,1.02,0.73); }

float forestGlow(float distanceValue,float radius) {
    float d=abs(distanceValue);
    return exp(-d*d/max(radius*radius,0.000001));
}

float subjectPulse(float time,AbundanceState state) {
    float phrase=0.5+0.5*sin(time*0.23+state.subject*PI);
    return saturate(state.subject*(0.54+0.46*phrase)+state.beat*0.14);
}

vec2 livingWarp(vec2 p,float time,AbundanceState state) {
    vec2 flow=curlFlow(
        p*(0.54+0.46*state.fecundity)+vec2(time*0.003,-time*0.004),
        time*0.046
    );
    float amount=0.018+0.050*state.reciprocity
        +0.025*state.fecundity-0.018*state.localization;
    return p+flow*amount;
}

float seedShape(vec2 p,float radius,float opening) {
    float angle=atan(p.y,p.x);
    float r=length(p);
    float petals=radius*(0.74+0.19*cos(angle*5.0+opening*0.65));
    float notch=0.025*sin(angle*10.0-opening);
    return r-petals-notch;
}

float leafShape(vec2 p,vec2 center,float size,float angle) {
    vec2 q=(p-center)*rot(angle);
    q/=max(size,0.0001);
    float body=sdVesica(q,0.72,0.82);
    return body*size;
}

float branchY(float x,float seed,float time,float drive) {
    return 0.13*sin(x*(1.5+seed*0.23)+seed*1.8+time*0.020)
        +0.055*sin(x*(4.6+seed*0.17)-time*0.033+seed)
        +drive*0.025*sin(x*9.0+time*0.12+seed*2.0);
}

float branchDistance(
    vec2 p,
    vec2 origin,
    float angle,
    float lengthValue,
    float bend,
    float seed,
    float time,
    float drive
) {
    float distanceValue=10.0;
    vec2 previous=origin;
    for (int i=1;i<=22;i++) {
        float x=float(i)/22.0;
        vec2 local=vec2(
            x*lengthValue,
            bend*x*x+branchY(x*lengthValue,seed,time,drive)*x
        );
        vec2 point=origin+local*rot(angle);
        distanceValue=min(distanceValue,sdSegment(p,previous,point));
        previous=point;
    }
    return distanceValue;
}

void paintBranch(
    inout vec3 color,
    vec2 p,
    vec2 origin,
    float angle,
    float lengthValue,
    float bend,
    float seed,
    float time,
    float drive,
    float width,
    vec3 hue,
    float energy
) {
    float d=branchDistance(
        p,origin,angle,lengthValue,bend,seed,time,drive
    );
    color+=hue*(
        0.50*forestGlow(d,width*0.24)
        +0.095*forestGlow(d,width)
    )*energy;
    float traveller=fract(time*(0.018+0.012*drive)+seed*0.19);
    vec2 local=vec2(
        traveller*lengthValue,
        bend*traveller*traveller
        +branchY(traveller*lengthValue,seed,time,drive)*traveller
    );
    vec2 point=origin+local*rot(angle);
    color+=mix(hue,afterLight(),0.58)
        *glowPoint(p,point,width*1.8)*energy*(0.15+0.22*drive);
}

void paintLeaf(
    inout vec3 color,
    vec2 p,
    vec2 center,
    float size,
    float angle,
    vec3 hue,
    float energy,
    float veinDrive
) {
    float leaf=leafShape(p,center,size,angle);
    float body=1.0-smoothstep(-0.020,0.030,leaf);
    float edge=forestGlow(leaf,0.008+size*0.025);
    vec2 q=(p-center)*rot(angle)/max(size,0.0001);
    float mid=forestGlow(q.y,0.035)*(1.0-smoothstep(0.72,0.95,abs(q.x)));
    float veins=0.0;
    for (int i=0;i<5;i++) {
        float fi=float(i);
        float x=-0.48+fi*0.24;
        float side=mod(fi,2.0)<1.0?1.0:-1.0;
        float line=abs(q.y-side*(q.x-x)*0.30);
        veins+=forestGlow(line,0.022)
            *(1.0-smoothstep(0.35,0.82,abs(q.x-x)));
    }
    float texture=0.58+0.42*fbm(
        q*2.6+vec2(veinDrive*0.8,veinDrive*0.3)
    );
    color+=mix(hue,afterLight(),0.14)*body*texture*energy*0.095;
    color+=hue*edge*energy*0.25;
    color+=mix(hue,afterLight(),0.52)
        *(mid*0.17+veins*0.045)*body*energy;
}

float counterpointRibbon(
    vec2 p,
    float phase,
    float time,
    float voice,
    float tension
) {
    float y=(voice-1.5)*0.25
        +0.15*sin(p.x*(1.5+voice*0.22)+phase+time*(0.025+voice*0.008))
        +0.055*sin(p.x*(4.0+voice)-time*0.041+phase*1.7)
        +tension*0.06*sin(p.x*9.0+time*0.10+voice);
    return abs(p.y-y);
}

vec3 forestGround(
    vec2 p,
    float time,
    int stage,
    AbundanceState state
) {
    vec2 q=livingWarp(p,time,state);
    float deep=fbmWarp(q*0.52,time*0.025);
    float current=waveInterference(
        q*(0.50+0.44*state.fecundity),
        time*(0.06+0.06*state.appetite)
    );
    float roots=phaseContour(
        fbmWarp(q*0.86,time*0.035)+0.09*q.y,
        8.0+7.0*state.fecundity,
        0.055
    );
    vec3 color=forestVoid();
    color+=mix(mineralBlue(),earthViolet(),0.28+0.28*state.localization)
        *(0.035+0.13*deep)*(0.62+0.38*state.openness);
    color+=mix(knowingSky(),actionGreen(),state.reciprocity)
        *(0.5+0.5*current)*0.012*(0.25+0.75*state.radiance);
    color+=seedGold()*roots*0.010*(0.25+0.75*state.recognition);

    float stars=pow(
        noise21(gl_FragCoord.xy*0.51+floor(time*4.0)),
        24.0-8.0*state.fecundity
    );
    color+=afterLight()*stars*(0.015+0.065*state.radiance);

    // The four music groups deform the material before color finishing.
    for (int i=0;i<4;i++) {
        float fi=float(i);
        float voice=state.voices[i];
        float d=counterpointRibbon(
            p,fi*1.47,time,fi,state.tension
        );
        vec3 hue;
        if (i==0) hue=earthViolet();
        else if (i==1) hue=actionGreen();
        else if (i==2) hue=knowingSky();
        else hue=seedGold();
        color+=hue*forestGlow(d,0.026+0.012*fi)
            *voice*(0.012+0.024*state.fecundity);
    }
    return color;
}

vec3 stageRadiance(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,0,state);
    vec2 q=livingWarp(p,time*0.55,state);
    float opening=fbmWarp(q*0.40,time*0.018);
    float absence=1.0-smoothstep(0.34,0.82,opening);
    color+=afterLight()*absence*(0.018+0.060*state.radiance);
    for (int i=0;i<13;i++) {
        float fi=float(i);
        vec2 center=vec2(
            mix(-1.55,1.55,hash11(fi*7.3+2.0)),
            mix(-0.72,0.72,hash11(fi*4.9+9.0))
        );
        center+=0.05*vec2(
            sin(time*0.013+fi),
            cos(time*0.011+fi*1.7)
        );
        float mote=glowPoint(p,center,0.015+0.018*hash11(fi+3.0));
        color+=seedGold()*mote*(0.025+0.080*easeOut(local));
    }
    float preSubject=seedShape(
        (p-vec2(-0.82,0.18))*rot(-0.24),
        0.11+0.03*state.subject,
        time*0.03
    );
    color+=seedGold()*forestGlow(preSubject,0.070)
        *smoothstep(0.62,0.98,local)*0.040;
    return color;
}

vec3 stageGermination(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,1,state);
    vec2 seedCenter=vec2(-0.72,-0.10);
    vec2 seedP=(p-seedCenter)*rot(-0.22+0.04*sin(time*0.03));
    float seed=seedShape(
        seedP,0.20+0.025*state.subject,time*0.06
    );
    float seedBody=1.0-smoothstep(-0.025,0.035,seed);
    color+=mix(seedGold(),afterLight(),0.34)
        *seedBody*(0.10+0.14*state.radiance);
    color+=seedGold()*forestGlow(seed,0.018)*(0.34+0.24*state.subject);

    float grow=easeInOut(smoothstep(0.10,0.72,local));
    paintBranch(
        color,p,seedCenter,0.13,1.65,0.18,1.1,time,
        state.voices.z+state.subject,0.045,actionGreen(),grow
    );
    paintBranch(
        color,p,seedCenter,-2.0,0.88,-0.30,3.2,time,
        state.voices.x,0.035,earthViolet(),grow*0.72
    );
    for (int i=0;i<5;i++) {
        float fi=float(i);
        float x=-0.12+fi*0.30;
        float y=0.02+branchY(x+0.72,1.1,time,state.subject);
        paintLeaf(
            color,p,vec2(x,y+0.08*sin(fi+time*0.03)),
            0.10+0.015*fi,0.55*sin(fi*1.3),
            mix(actionGreen(),knowingSky(),fi/5.0),
            grow*(0.45+0.55*state.voices.z),state.subject
        );
    }
    return color;
}

vec3 stageThreePowers(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,2,state);
    vec2 origin=vec2(-1.20,-0.18);
    float disclose=easeInOut(smoothstep(0.02,0.58,local));
    paintBranch(
        color,p,origin,0.28,2.45,0.38,1.0,time,
        state.voices.y,0.060,willCoral(),disclose
    );
    paintBranch(
        color,p,origin,0.05,2.55,0.02,2.0,time,
        state.voices.z,0.055,knowingSky(),disclose
    );
    paintBranch(
        color,p,origin,-0.23,2.45,-0.34,3.0,time,
        state.voices.w,0.060,actionGreen(),disclose
    );
    for (int i=0;i<12;i++) {
        float fi=float(i);
        float x=mix(-1.06,1.22,fi/11.0);
        float y=0.18*sin(x*1.7+time*0.02)
            +0.08*sin(x*4.6-time*0.04);
        vec2 center=vec2(x,y);
        vec3 hue;
        if (mod(fi,3.0)<1.0) hue=willCoral();
        else if (mod(fi,3.0)<2.0) hue=knowingSky();
        else hue=actionGreen();
        float seed=seedShape(
            (p-center)*rot(fi),0.038+0.012*state.fecundity,
            time*0.09+fi
        );
        color+=hue*forestGlow(seed,0.012)
            *disclose*(0.12+0.18*state.subject);
    }
    return color;
}

vec3 stageContract(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,3,state)*0.78;
    vec2 q=projectiveWarp(
        p*rot(0.06*sin(time*0.02)),
        0.36+0.50*state.localization,
        time*0.012
    );
    vec2 cells=voronoi2(
        q*(3.4+2.5*state.localization)+vec2(time*0.004,0.0)
    );
    float edge=cells.y-cells.x;
    float armor=forestGlow(edge,0.028);
    float chamber=0.0;
    for (int i=0;i<7;i++) {
        float fi=float(i);
        vec2 center=vec2(
            -1.26+fi*0.42,
            0.25*sin(fi*1.4+time*0.018)
        );
        float aperture=sdRegularPolygon(
            (p-center)*rot(fi*0.27),0.21,6.0,0.0
        );
        chamber+=forestGlow(aperture,0.016);
        float inside=1.0-smoothstep(-0.02,0.035,aperture);
        vec3 hue=mix(mineralBlue(),seedGold(),fi/7.0);
        color+=hue*inside*(0.028+0.055*state.radiance);
    }
    color+=mix(earthViolet(),knowingSky(),0.32)
        *armor*(0.10+0.18*state.localization);
    color+=afterLight()*chamber*(0.12+0.12*state.subject);
    paintBranch(
        color,p,vec2(-1.55,-0.46),0.20,3.05,0.10,5.0,time,
        state.voices.y,0.032,seedGold(),0.50+0.35*state.recognition
    );
    return color;
}

vec3 stageMetabolism(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,4,state);
    for (int i=0;i<8;i++) {
        float fi=float(i);
        vec2 center=vec2(
            mix(-1.34,1.34,hash11(fi*4.7+2.0)),
            mix(-0.55,0.55,hash11(fi*7.1+5.0))
        );
        center+=0.035*vec2(
            sin(time*0.026+fi),
            cos(time*0.022+fi*1.4)
        );
        vec2 q=(p-center)*rot(fi*0.37);
        float radius=0.15+0.08*hash11(fi+9.0);
        float membrane=seedShape(
            q,radius,time*0.025+fi
        );
        float body=1.0-smoothstep(-0.015,0.035,membrane);
        vec3 hue=mix(actionGreen(),knowingSky(),hash11(fi+3.0));
        color+=hue*body*(0.035+0.045*state.radiance);
        color+=hue*forestGlow(membrane,0.012)
            *(0.17+0.18*state.localization);
        float cycle=abs(length(q)-radius*(0.34+0.10*sin(time*0.08+fi)));
        color+=mix(hue,seedGold(),0.44)*forestGlow(cycle,0.016)
            *body*(0.08+0.14*state.voices.y);
        vec2 packet=center+radius*0.74*vec2(
            cos(time*0.09+fi*2.1),sin(time*0.09+fi*2.1)
        );
        color+=afterLight()*glowPoint(p,packet,0.024)
            *(0.08+0.18*state.voices.w);
    }
    float exchange=phaseContour(
        fbm(p*2.2+vec2(time*0.02,0.0))+p.x*0.11,
        10.0,0.050
    );
    color+=careRose()*exchange*state.reciprocity*0.035;
    return color;
}

vec3 stageSeek(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,5,state)*0.72;
    vec2 source=vec2(
        1.22+0.10*sin(time*0.018),
        0.38+0.18*cos(time*0.014)
    );
    color+=seedGold()*lensFlare(p,source)*(0.11+0.15*state.appetite);
    for (int i=0;i<13;i++) {
        float fi=float(i);
        vec2 origin=vec2(
            -1.52,
            -0.66+fi*0.11
        );
        vec2 direction=normalize(source-origin);
        float angle=atan(direction.y,direction.x)
            +0.19*sin(fi*1.8+time*0.021)*(1.0-state.appetite);
        vec3 hue=mix(earthViolet(),actionGreen(),fi/13.0);
        paintBranch(
            color,p,origin,angle,2.2+0.35*hash11(fi),
            0.10*sin(fi),fi,time,
            state.appetite+state.voices.x,
            0.028+0.008*hash11(fi+3.0),hue,
            0.30+0.48*state.appetite
        );
    }
    float hungerFront=dot(
        p-source,normalize(vec2(-0.88,-0.24))
    );
    color+=willCoral()*forestGlow(hungerFront,0.15)
        *state.tension*0.050;
    return color;
}

vec3 stageNest(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,6,state);
    float zoom=mix(0.82,1.36,easeInOut(local));
    vec2 q=(p-vec2(-0.12,0.02))*zoom;
    // Three homologous membranes make scale itself visible: cell, organism,
    // collective.  Each encloses the next without erasing its boundary.
    float outer=seedShape(q,0.92,time*0.010);
    float middle=seedShape(q-vec2(-0.13,0.01),0.53,-time*0.018);
    float inner=seedShape(q-vec2(-0.20,0.02),0.23,time*0.035);
    float leafBody=1.0-smoothstep(-0.03,0.04,outer);
    float middleBody=1.0-smoothstep(-0.02,0.03,middle);
    float innerBody=1.0-smoothstep(-0.015,0.022,inner);
    color+=mix(actionGreen(),knowingSky(),0.22)
        *leafBody*(0.030+0.060*state.radiance);
    color+=mix(knowingSky(),careRose(),0.28)
        *middleBody*(0.025+0.040*state.reciprocity);
    color+=afterLight()*innerBody*(0.018+0.032*state.recognition);
    color+=actionGreen()*forestGlow(outer,0.018)*0.30;
    color+=knowingSky()*forestGlow(middle,0.014)*0.32;
    color+=careRose()*forestGlow(inner,0.010)*0.38;

    // Reciprocal flux crosses every membrane. The same pulse is conserved
    // through the three scales, turning hierarchy into coordination.
    float fluxPhase=fract(time*0.028);
    vec2 fluxPoint=mix(vec2(-0.88,-0.02),vec2(0.72,0.08),fluxPhase);
    color+=afterLight()*glowPoint(q,fluxPoint,0.025)
        *(0.16+0.22*state.voices.w);

    for (int i=0;i<15;i++) {
        float fi=float(i);
        float x=-0.66+fi*0.094;
        float y=0.07*sin(fi*1.7+time*0.025);
        vec2 center=vec2(x,y);
        float cell=seedShape(
            q-center,0.055+0.018*hash11(fi),time*0.04+fi
        );
        float inside=1.0-smoothstep(-0.010,0.022,cell);
        vec3 hue=mix(knowingSky(),careRose(),hash11(fi+2.0));
        color+=hue*inside*leafBody*0.075;
        color+=hue*forestGlow(cell,0.010)*leafBody*0.12;
    }
    paintBranch(
        color,q,vec2(-0.72,0.0),0.02,1.48,0.02,7.0,time,
        state.voices.y,0.040,seedGold(),leafBody
    );
    for (int i=0;i<6;i++) {
        float fi=float(i);
        float x=-0.55+fi*0.22;
        float y=branchY(x+0.70,7.0,time,state.subject);
        paintBranch(
            color,q,vec2(x,y),0.65*(mod(fi,2.0)<1.0?1.0:-1.0),
            0.30,0.04*sin(fi),fi,time,state.voices.z,
            0.020,knowingSky(),0.50
        );
    }
    return color;
}

vec3 stageContend(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,7,state)*0.67;
    for (int i=0;i<18;i++) {
        float fi=float(i);
        float side=mod(fi,2.0)<1.0?-1.0:1.0;
        vec2 origin=vec2(side*1.52,-0.64+fi*0.071);
        float angle=side<0.0?0.18:PI-0.18;
        angle+=0.22*sin(fi*1.5+time*0.027);
        vec3 hue=side<0.0?willCoral():knowingSky();
        paintBranch(
            color,p,origin,angle,1.75+0.30*hash11(fi),
            side*0.13*sin(fi),fi,time,
            state.tension+state.voices.z,0.026,hue,
            0.20+0.36*state.appetite
        );
    }
    vec2 qa=p*rot(0.48);
    vec2 qb=p*rot(-0.62);
    float claimA=forestGlow(
        sin(qa.y*9.0+sin(qa.x*2.0+time*0.05)),0.11
    );
    float claimB=forestGlow(
        sin(qb.y*8.0+sin(qb.x*2.4-time*0.06)),0.11
    );
    color+=willCoral()*claimA*state.tension*0.055;
    color+=earthViolet()*claimB*state.tension*0.060;
    color+=afterLight()*claimA*claimB*state.reciprocity*0.035;
    return color;
}

vec3 stageReciprocate(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,8,state);
    for (int i=0;i<20;i++) {
        float fi=float(i);
        vec2 a=vec2(
            mix(-1.42,1.42,hash11(fi*5.7+1.0)),
            mix(-0.62,0.62,hash11(fi*8.3+2.0))
        );
        vec2 b=vec2(
            mix(-1.42,1.42,hash11(fi*3.9+8.0)),
            mix(-0.62,0.62,hash11(fi*6.1+9.0))
        );
        float d=sdSegment(p,a,b);
        vec3 hue=mix(actionGreen(),careRose(),hash11(fi+7.0));
        color+=hue*(
            0.20*forestGlow(d,0.008)
            +0.030*forestGlow(d,0.045)
        )*state.reciprocity;
        float travel=fract(
            time*(0.021+0.011*hash11(fi))+fi*0.13
        );
        vec2 packet=mix(a,b,travel);
        color+=mix(hue,afterLight(),0.50)
            *glowPoint(p,packet,0.025)
            *state.reciprocity*(0.18+0.24*state.voices.y);
    }
    for (int i=0;i<12;i++) {
        float fi=float(i);
        vec2 center=vec2(
            mix(-1.26,1.26,hash11(fi*9.2+2.0)),
            mix(-0.52,0.52,hash11(fi*4.4+6.0))
        );
        float node=seedShape(
            p-center,0.045+0.025*hash11(fi),time*0.04+fi
        );
        color+=seedGold()*forestGlow(node,0.012)
            *(0.18+0.22*state.subject);
    }
    return color;
}

vec3 stageOrchestrate(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,9,state);
    // River: the continuo becomes landscape, not an underline.
    float riverY=-0.44
        +0.14*sin(p.x*1.3-time*0.035)
        +0.06*sin(p.x*4.7+time*0.061);
    float river=abs(p.y-riverY);
    color+=mix(knowingSky(),afterLight(),0.25)*(
        0.26*forestGlow(river,0.028)
        +0.055*forestGlow(river,0.16)
    )*(0.46+0.54*state.voices.w);

    for (int i=0;i<9;i++) {
        float fi=float(i);
        float x=-1.38+fi*0.35;
        float base=riverY-0.05+0.03*sin(fi);
        float height=0.78+0.36*hash11(fi+3.0);
        vec2 origin=vec2(x,base);
        paintBranch(
            color,p,origin,PI*0.50+0.11*sin(fi),
            height,0.08*sin(fi*1.4),fi,time,
            state.voices.z+state.subject,0.035,
            mix(actionGreen(),seedGold(),fi/9.0),
            0.38+0.34*state.fecundity
        );
        for (int j=0;j<3;j++) {
            float fj=float(j);
            vec2 leafCenter=origin+vec2(
                0.10*sin(fi*1.8+fj),
                height*(0.36+fj*0.20)
            );
            paintLeaf(
                color,p,leafCenter,0.10+0.025*hash11(fi*4.0+fj),
                0.7*sin(fi+fj),mix(actionGreen(),knowingSky(),fj/3.0),
                0.34+0.38*state.voices.z,state.subject
            );
        }
    }
    // Wind and animal traces are independent melodic arcs.
    for (int i=0;i<8;i++) {
        float fi=float(i);
        vec2 origin=vec2(-1.55,-0.05+fi*0.10);
        paintBranch(
            color,p,origin,0.10+0.09*sin(fi),3.1,
            0.17*sin(fi*1.3),fi+22.0,time,
            state.voices.z,0.018,
            mix(knowingSky(),careRose(),fi/8.0),
            0.16+0.28*state.voices.z
        );
    }
    return color;
}

vec3 stageRemember(
    vec2 p,float time,AbundanceState state,float local
) {
    float unbind=easeInOut(smoothstep(0.00,0.62,local));
    float silence=smoothstep(0.735,0.755,local)
        *(1.0-smoothstep(0.895,0.915,local));
    // The seed must be unmistakably present on the 545-second recognition
    // line (local ~= .90625), not lost inside the general scene transition.
    float returnSeed=easeOut(smoothstep(0.875,0.906,local));
    vec3 ground=forestGround(p,time,10,state);
    vec2 q=livingWarp(p,time*0.30,state);
    float deep=fbmWarp(q*0.44,time*0.014);
    vec3 stillField=forestVoid()
        +mineralBlue()*(0.12+0.22*deep)
        +earthViolet()*(0.08+0.13*(1.0-deep));
    vec3 color=mix(ground,stillField,unbind);

    for (int i=0;i<24;i++) {
        float fi=float(i);
        vec2 center=vec2(
            mix(-1.52,1.52,hash11(fi*6.3+4.0)),
            mix(-0.68,0.68,hash11(fi*3.7+8.0))
        );
        float scale=0.025+0.030*hash11(fi+2.0);
        float seed=seedShape(
            p-center,scale,time*0.025+fi
        );
        color+=mix(seedGold(),afterLight(),hash11(fi+10.0))
            *forestGlow(seed,0.012)
            *(0.06+0.12*state.recognition)*(0.42+0.58*unbind);
    }

    float standing=abs(
        p.y-0.06*sin(p.x*1.4-time*0.018)
        -0.025*sin(p.x*5.0+time*0.032)
    );
    color+=mix(mineralBlue(),afterLight(),0.16)*(
        0.060*forestGlow(standing,0.026)
        +0.035*forestGlow(standing,0.18)
    )*(0.38+0.62*silence);

    vec2 focus=vec2(0.28,-0.04);
    float recognitionSeed=seedShape(
        (p-focus)*rot(0.18),0.20+0.06*returnSeed,time*0.05
    );
    color+=seedGold()*forestGlow(recognitionSeed,0.016)
        *returnSeed*0.92;
    float recognitionBody=1.0-smoothstep(-0.025,0.035,recognitionSeed);
    color+=mix(seedGold(),afterLight(),0.44)*recognitionBody
        *returnSeed*0.16;
    color+=afterLight()*glowPoint(p,focus,0.090)
        *returnSeed*(0.44+0.30*state.subject);
    return color;
}

vec3 stageAbound(
    vec2 p,float time,AbundanceState state,float local
) {
    vec3 color=forestGround(p,time,11,state);
    // A small amount of the forest is already latent at the boundary so the
    // cut after recognition feels like release, not a dropped frame.
    float reveal=easeOut(smoothstep(-0.08,0.28,local));
    // A diagonal forest preserves movement; no centred crown is allowed.
    for (int i=0;i<12;i++) {
        float fi=float(i);
        float x=-1.48+fi*0.27;
        float base=-0.58+0.10*sin(fi*1.1+time*0.012);
        float height=0.74+0.56*hash11(fi*2.7+3.0);
        float sway=0.09*sin(time*0.023+fi*1.7);
        vec3 trunkHue=mix(earthViolet(),seedGold(),0.25+0.55*fi/12.0);
        paintBranch(
            color,p,vec2(x,base),PI*0.5+sway,height,
            0.06*sin(fi),fi,time,
            state.voices.x+state.subject,
            0.034,trunkHue,reveal*(0.34+0.34*state.fecundity)
        );
        for (int j=0;j<4;j++) {
            float fj=float(j);
            float side=mod(fj,2.0)<1.0?-1.0:1.0;
            vec2 branchOrigin=vec2(
                x+sway*(0.3+fj*0.1),
                base+height*(0.30+fj*0.16)
            );
            paintBranch(
                color,p,branchOrigin,
                PI*0.5+side*(0.65+0.08*fj),
                0.26+0.10*hash11(fi*5.0+fj),
                side*0.04,fi*4.0+fj,time,
                state.voices.y+state.voices.z,
                0.020,
                mix(actionGreen(),knowingSky(),fj/4.0),
                reveal*(0.28+0.38*state.reciprocity)
            );
            vec2 leafCenter=branchOrigin+vec2(
                side*(0.19+0.05*fj),
                0.16+0.04*fj
            );
            paintLeaf(
                color,p,leafCenter,0.085+0.020*hash11(fi+fj),
                side*(0.52+0.13*fj),
                mix(actionGreen(),careRose(),hash11(fi*2.0+fj)),
                reveal*(0.30+0.42*state.voices.z),state.subject
            );
        }
    }
    // Subject seeds at several scales make recognition an invariant.
    for (int i=0;i<28;i++) {
        float fi=float(i);
        float golden=fi*2.39996323;
        float radius=0.08*sqrt(fi);
        vec2 center=vec2(0.55,-0.08)
            +radius*vec2(cos(golden),sin(golden))*vec2(1.2,0.74);
        float seed=seedShape(
            p-center,0.020+0.012*hash11(fi),time*0.04+fi
        );
        vec3 hue=mix(seedGold(),afterLight(),fi/28.0);
        color+=hue*forestGlow(seed,0.009)
            *reveal*(0.08+0.18*state.subject);
    }
    float riverY=-0.62+0.12*sin(p.x*1.2-time*0.025);
    color+=knowingSky()*forestGlow(abs(p.y-riverY),0.055)
        *reveal*(0.025+0.060*state.voices.w);
    return color;
}

vec3 renderForestStage(
    int stage,
    vec2 p,
    float time,
    AbundanceState state,
    float local
) {
    if (stage<=0) return stageRadiance(p,time,state,local);
    if (stage==1) return stageGermination(p,time,state,local);
    if (stage==2) return stageThreePowers(p,time,state,local);
    if (stage==3) return stageContract(p,time,state,local);
    if (stage==4) return stageMetabolism(p,time,state,local);
    if (stage==5) return stageSeek(p,time,state,local);
    if (stage==6) return stageNest(p,time,state,local);
    if (stage==7) return stageContend(p,time,state,local);
    if (stage==8) return stageReciprocate(p,time,state,local);
    if (stage==9) return stageOrchestrate(p,time,state,local);
    if (stage==10) return stageRemember(p,time,state,local);
    return stageAbound(p,time,state,local);
}

vec3 renderForestFugue(
    vec2 p,
    vec2 uv,
    vec2 fragCoord,
    float time,
    float progress,
    int stage,
    float local,
    AbundanceState state
) {
    int safeStage=clamp(stage,0,11);
    // Stage ten owns the recognition line; defer its crossfade until after
    // the returned seed is fully legible.
    float transitionStart=safeStage==10?0.950:0.82;
    float transition=smoothstep(transitionStart,0.995,local);
    float morph=transition*transition*(3.0-2.0*transition);
    vec2 causalWarp=curlFlow(
        p*(0.62+0.28*state.fecundity),
        time*0.041
    )*(0.016+0.030*state.reciprocity);
    vec3 current=renderForestStage(
        safeStage,p+causalWarp*transition,time,state,local
    );
    vec3 next=renderForestStage(
        min(safeStage+1,11),
        p-causalWarp*(1.0-transition),
        time,state,0.0
    );
    vec3 color=mix(current,next,morph);

    float scoreSubject=subjectPulse(time,state);
    float seedContour=seedShape(
        livingWarp(p,time,state)*(
            0.72+0.12*state.localization
        ),
        0.92+0.04*sin(time*0.02),
        time*0.025
    );
    color+=mix(seedGold(),afterLight(),state.radiance)
        *forestGlow(seedContour,0.035)
        *scoreSubject*(0.005+0.014*state.recognition);

    float exposure=mix(0.90,1.12,state.radiance);
    float bloom=mix(0.42,0.80,state.recognition);
    return signatureFinish(
        color,uv,fragCoord,time,exposure,bloom
    );
}

#endif
