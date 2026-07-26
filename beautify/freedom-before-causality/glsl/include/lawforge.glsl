#ifndef BEAUTIFY_LAWFORGE_GLSL
#define BEAUTIFY_LAWFORGE_GLSL

const vec3 LF_INK=vec3(0.012,0.024,0.060);
const vec3 LF_BLUE=vec3(0.10,0.58,1.08);
const vec3 LF_CYAN=vec3(0.12,1.05,0.92);
const vec3 LF_GOLD=vec3(1.34,0.56,0.12);
const vec3 LF_IVORY=vec3(1.05,0.94,0.72);

float lfPhase(float u,float a,float b){return smoothstep(a,b,u);}

vec3 lfBackground(vec2 p,float time){
    float neb=fbmWarp(p*1.25+vec2(0,time*0.018),time*0.22);
    float strata=.5+.5*sin(3.*p.y+neb*4.-time*.09);
    vec3 c=LF_INK+vec3(.018,.025,.08)*neb+vec3(.012,.045,.08)*strata;
    c+=vec3(.06,.12,.22)*pow(max(0.,1.-length(p)*.42),5.);
    return c;
}

float lfScalar(vec2 p,float time,float kind){
    vec2 q=p*rot(.15*sin(time*.07));
    float n=fbmWarp(q*1.6,time*.16)-.5;
    float interference=waveInterference(q*1.18,time*.7);
    float lattice=sin(q.x*(8.+kind))*sin(q.y*(7.+kind*.7));
    float radial=sin(length(q-vec2(.16*sin(time*.1),0))*15.-time);
    return mix(interference,lattice,.18+.08*kind)+n*.52+radial*.13;
}

vec3 lfSurface(vec2 p,float time,float kind,float drive){
    float e=.009,h=lfScalar(p,time,kind);
    vec2 g=vec2(
        lfScalar(p+vec2(e,0),time,kind)-lfScalar(p-vec2(e,0),time,kind),
        lfScalar(p+vec2(0,e),time,kind)-lfScalar(p-vec2(0,e),time,kind)
    )/(2.*e);
    vec3 n=normalize(vec3(-g*.32,1)),l=normalize(vec3(-.55,.72,.85));
    float diffuse=max(dot(n,l),0.),rim=pow(1.-n.z,2.4);
    float contour=phaseContour(h+.09*time,7.+kind,.06);
    vec3 c=mix(vec3(.012,.035,.11),LF_BLUE,.20+.45*diffuse);
    c+=LF_CYAN*contour*(.15+rim*.72)*drive;
    c+=LF_GOLD*pow(max(dot(reflect(-l,n),vec3(0,0,1)),0.),42.)*drive;
    return c;
}

vec2 lfFlow(vec2 x,float seed,float time){
    float a=2.1*sin(x.y*1.9+seed*2.7+time*.08)
        +1.3*cos(x.x*2.6-seed+time*.11)+.8*sin((x.x+x.y)*4.1+seed);
    return vec2(cos(a),sin(a));
}

float lfStream(vec2 p,float seed,float time,float bend){
    vec2 x=vec2(-1.34,-.74+seed*.30);
    x+=.08*vec2(sin(seed*9.2+time*.1),cos(seed*6.7-time*.08));
    float d=9.;
    for(int i=0;i<28;i++){
        vec2 prev=x,v=normalize(mix(vec2(1,0),lfFlow(x,seed,time),bend));
        x+=v*.085; d=min(d,sdSegment(p,prev,x));
    }
    return d;
}

void lfStreams(inout vec3 c,vec2 p,float time,float drive,float selected){
    for(int i=0;i<7;i++){
        float fi=float(i),seed=fi/6.,d=lfStream(p,seed,time,.62);
        vec3 hue=mix(LF_BLUE,LF_CYAN,seed);
        float emphasis=1.+selected*3.2*exp(-pow(fi-3.,2.));
        c+=hue*glow(d,.018)*.085*drive;
        c+=mix(hue,LF_GOLD,selected)*aaStroke(d,.005)*.62*emphasis;
    }
}

void lfCausalChain(inout vec3 c,vec2 p,float time,float drive,float broken){
    vec2 previous=vec2(-1.18,0);
    for(int i=0;i<9;i++){
        float fi=float(i);
        vec2 node=vec2(-1.18+fi*.30,.18*sin(fi*1.37+time*.18));
        if(i>0){
            float d=sdSegment(p,previous,node);
            float gap=broken*smoothstep(3.4,4.3,fi)*smoothstep(5.6,4.8,fi);
            c+=LF_BLUE*aaStroke(d,.006)*(1.-gap)+LF_CYAN*glow(d,.025)*.18;
        }
        float r=length(p-node),pulseRing=abs(r-(.075+.014*sin(time*1.2-fi)))-.006;
        c+=mix(LF_BLUE,LF_IVORY,fi/8.)*aaFill(r-.045);
        c+=LF_GOLD*glow(pulseRing,.012)*drive*.34;
        previous=node;
    }
}

float lfCrystal(vec2 p,float time,float growth,float fracture){
    vec2 q=p; q.x+=.10*sin(q.y*5.+time*.08)*fracture;
    float cells=hexEdge(q,5.4,.008),front=smoothstep(.09,-.03,length(q)-growth);
    float facet=phaseContour(lfScalar(q,time,1.),4.,.08)*front;
    return cells*front+facet*.25;
}

void lfBranch(inout vec3 c,vec2 p,vec2 root,float time,float opening,vec3 hue){
    for(int i=0;i<15;i++){
        float fi=float(i),gen=floor(log2(fi+1.)),idx=fi-(exp2(gen)-1.);
        float count=exp2(gen),parent=floor(idx*.5),span=.62/(gen+1.);
        vec2 a=root+vec2(gen*.31,(parent-(count*.25-.5))*span);
        vec2 b=root+vec2((gen+1.)*.31,(idx-(count*.5-.5))*span*opening);
        a.y+=.04*sin(fi*2.1+time*.2); b.y+=.04*sin(fi*1.7-time*.18);
        float d=sdSegment(p,a,b);
        c+=hue*aaStroke(d,.005)*(.52+.48/(gen+1.))+hue*glow(d,.03)*.08;
    }
}

float lfAttractor(vec2 p,float time,float unlock){
    float d=9.;
    for(int i=0;i<42;i++){
        float fi=float(i)/41.,a=fi*TAU*3.+time*.08;
        float r=(.17+fi*.60)*(1.+.18*sin(a*3.));
        vec2 q=vec2(cos(a),sin(a))*r; q.x+=unlock*fi*.72;
        d=min(d,length(p-q));
    }
    return d;
}

void lfCenterNetwork(inout vec3 c,vec2 p,float time,float drive,float reciprocity){
    for(int i=0;i<7;i++){
        float fi=float(i),a=fi*TAU/7.+.12*sin(time*.13);
        vec2 node=.58*vec2(cos(a),sin(a));
        radiantNode(c,p,node,.14,mix(LF_BLUE,LF_GOLD,fi/6.),.32*drive);
        if(i<6){
            float fj=mod(fi+1.+floor(2.*reciprocity),7.);
            vec2 other=.58*vec2(cos(fj*TAU/7.+.12*sin(time*.13)),sin(fj*TAU/7.+.12*sin(time*.13)));
            lightFilament(c,p,node,other,mix(LF_CYAN,LF_GOLD,reciprocity),.62*drive);
        }
    }
}

vec3 renderLawforge(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    float drive=audioEnergy(volume,beat),breathe=.5+.5*sin(time*.72);
    float enter=easeOut(min(u*1.45,1.));
    vec3 c=lfBackground(p,time);

    if(mode==0){
        c+=lfSurface(p,time,0.,drive)*.82;
        vec2 q=p*rot(time*.025);
        for(int i=0;i<6;i++){
            float fi=float(i),a=fi*TAU/6.;
            vec2 n=.63*vec2(cos(a),sin(a));
            float gear=abs(sdRegularPolygon((q-n)*rot(-time*.13*(1.-2.*mod(fi,2.))),.13,12.,0.))-.012;
            c+=LF_IVORY*aaFill(gear)*.34+LF_BLUE*glow(gear,.03)*.12;
        }
    }else if(mode==1){
        lfCausalChain(c,p,time,drive,0.);
        float w=fract(time*.18);
        radiantNode(c,p,vec2(-1.18+w*2.4,.18*sin(w*11.+time*.18)),.09,LF_GOLD,drive);
    }else if(mode==2){
        lfCausalChain(c,p,time,drive,1.);
        float voidRing=abs(length(p-vec2(.03,0))-.36)-.008;
        c*=1.-.74*exp(-dot(p,p)/.085);
        c+=LF_GOLD*glow(voidRing,.03)*.48+LF_IVORY*softBeam(p,vec2(.03,-.1),vec2(0,1),.18,.7)*.18;
    }else if(mode==3){
        vec2 q=projectiveWarp(p,.72,.3+time*.05);
        float field=fbmWarp(q*1.7,time*.32);
        float folds=phaseContour(field+.14*atan(q.y,q.x),9.,.075);
        c+=interferencePalette(field,.04)*folds*(.34+.75*drive);
        c+=LF_GOLD*causticField(q*.72,time)*.50;
        c+=LF_CYAN*pow(max(0.,1.-length(q)*.52),7.)*.18;
    }else if(mode==4){
        float r=length(p),a=atan(p.y,p.x);
        float membrane=abs(r-(.30+.045*sin(9.*a-time*1.2)*breathe))-.008;
        for(int i=0;i<7;i++){
            float fi=float(i),ring=abs(r-(.18+fi*.095+.018*sin(a*(5.+fi)+time*(.7+fi*.1))))-.004;
            c+=mix(LF_GOLD,LF_CYAN,fi/6.)*(aaStroke(ring,.004)+glow(ring,.025)*.13)*drive;
        }
        c+=LF_IVORY*glow(membrane,.024)*.75;
    }else if(mode==5){
        lfStreams(c,p,time,drive,1.);
        float chosen=lfStream(p,.5,time,.62);
        c+=LF_IVORY*glow(chosen,.012)*.80+LF_GOLD*glow(chosen,.055)*.28;
    }else if(mode==6){
        float alignment=lfPhase(u,.2,.78);
        for(int i=0;i<11;i++){
            float fi=float(i),y=-.82+fi*.164,phase=mix(fi*1.73,fi*.12,alignment);
            float curve=abs(p.y-y-.055*sin(p.x*7.+phase-time*.42))-.004;
            c+=mix(LF_BLUE,LF_GOLD,alignment)*aaStroke(curve,.004)*(.45+.55*alignment);
            c+=LF_CYAN*glow(curve,.022)*.08;
        }
    }else if(mode==7){
        float growth=mix(.12,1.34,enter),crystal=lfCrystal(p,time,growth,0.);
        c+=mix(LF_BLUE,LF_CYAN,.62)*crystal*(.6+drive*.5);
        c+=LF_GOLD*glow(length(p)-growth,.026)*.56;
        c+=lfSurface(p,time,2.,drive)*.22*lfPhase(u,.35,.9);
    }else if(mode==8){
        vec2 q=p;q.x+=.13*sin(p.y*5.+time*.14);
        float bars=phaseContour(q.x+.10*sin(q.y*3.),6.,.055);
        float chamber=abs(sdRoundBox(q,vec2(.60,.72),.22))-.008;
        c+=LF_BLUE*bars*.32+LF_CYAN*glow(chamber,.04)*.42;
        radiantNode(c,p,vec2(0,.05*sin(time)),.24,LF_GOLD,.65*drive);
    }else if(mode==9){
        float boundary=abs(sdRoundBox(p,vec2(1.02,.69),.18))-.008;
        c+=LF_BLUE*aaStroke(boundary,.008)+LF_CYAN*glow(boundary,.04)*.2;
        lfBranch(c,p,vec2(-.86,0),time,.70,LF_CYAN);
        float path=lfStream(p,.52,time,.34);
        c+=LF_GOLD*(aaStroke(path,.006)+glow(path,.04)*.32)*drive;
    }else if(mode==10){
        float groove=lfAttractor(p,time,0.);
        for(int i=0;i<5;i++){float fi=float(i);c+=mix(LF_BLUE,LF_GOLD,fi/4.)*glow(groove-fi*.022,.012)*(.08+fi*.09);}
        radiantNode(c,p,.20*vec2(cos(time),sin(time)),.12,LF_IVORY,.32*drive);
    }else if(mode==11){
        vec2 q=p*rot(-.2);float attract=lfAttractor(q,time,.05*beat);
        float basin=smoothstep(.8,0.,length(q))*phaseContour(lfScalar(q,time,3.),9.,.035);
        c+=vec3(.36,.05,.24)*basin*.36+LF_GOLD*glow(attract,.035)*.44+LF_IVORY*aaStroke(attract,.005);
        c+=LF_CYAN*softBeam(p,vec2(-1.25,.55),vec2(1.,-.18),.08,.8)*.18*lfPhase(u,.55,.95);
    }else if(mode==12){
        float seam=abs(p.x+.10*sin(p.y*7.+time*.2))-.007;
        vec2 left=p+vec2(.72,0),right=p-vec2(.72,0);
        float tear=phaseContour(fbmWarp(left*2.,time),12.,.025)*step(p.x,0.);
        float lawful=lfCrystal(right,time,.72,.28)*step(0.,p.x);
        c+=vec3(.52,.08,.23)*tear*.55+LF_CYAN*lawful*.72;
        c+=LF_GOLD*(aaStroke(seam,.005)+glow(seam,.04)*.30);
    }else if(mode==13){
        c+=LF_BLUE*lfCrystal(p,time,1.5,0.)*.34;
        lfBranch(c,p,vec2(-.62,-.40),time,1.05+.28*breathe,LF_GOLD);
        float bloomShape=abs(sdStar(p-vec2(.45,.18),.28,7.,.72,time*.05))-.008;
        c+=LF_CYAN*glow(bloomShape,.045)*.48+LF_IVORY*aaStroke(bloomShape,.006);
    }else if(mode==14){
        vec2 q=kaleido(p,7.,.12*time);
        float flower=abs(q.y-(.14+.24*q.x*q.x+.03*sin(q.x*18.-time)))-.007;
        float caustic=causticField(p*.62,time);
        c+=LF_GOLD*glow(flower,.035)*.72+interferencePalette(caustic+length(p),.11)*caustic*.56;
        lfStreams(c,p*rot(.25),time,.38*drive,0.);
    }else if(mode==15){
        vec2 v=voronoi2((p+vec2(.06*sin(time*.1),0))*3.1);
        c+=LF_BLUE*smoothstep(.08,0.,v.y-v.x)*.22;
        lfCenterNetwork(c,p,time,drive,1.);
        float central=abs(length(p)-.22)-.006;
        c+=LF_IVORY*aaStroke(central,.006)+LF_GOLD*glow(central,.05)*.28;
    }else if(mode==16){
        float reveal=lfPhase(u,.28,.82);vec2 q=projectiveWarp(p,.62*reveal,time*.04);
        float grid=hexEdge(q,4.7,.007),field=phaseContour(lfScalar(q,time,1.),8.,.055);
        c+=LF_BLUE*grid*(1.-.46*reveal)+LF_GOLD*field*reveal*.42;
        c+=LF_CYAN*causticField(q,time)*.34*reveal;
    }else if(mode==17){
        c+=LF_BLUE*lfCrystal(p,time,1.45,.08)*.28;
        for(int i=0;i<5;i++){
            float fi=float(i)/4.,d=lfStream(p,fi,time,.25+.3*enter);
            float travelling=.5+.5*sin(18.*p.x-time*3.-fi*7.);
            c+=mix(LF_GOLD,LF_CYAN,fi)*(aaStroke(d,.005)+glow(d,.025)*travelling*.28)*drive;
        }
    }else if(mode==18){
        vec2 left=p+vec2(.70,0),right=p-vec2(.70,0);
        float attract=lfAttractor(left,time,0.)*step(p.x,0.);
        float field=phaseContour(lfScalar(right,time,2.),8.,.05)*step(0.,p.x);
        c+=LF_CYAN*glow(attract,.028)*.48+LF_BLUE*field*.42;
        float bridge=sdSegment(p,vec2(-.25,0),vec2(.25,0));
        c+=LF_GOLD*(aaStroke(bridge,.006)+glow(bridge,.05)*.42);
        radiantNode(c,p,vec2(-.24,0),.12,LF_GOLD,.4*drive);
        radiantNode(c,p,vec2(.24,0),.12,LF_GOLD,.4*drive);
    }else if(mode==19){
        for(int i=0;i<4;i++){
            float fi=float(i);vec2 center=vec2((mod(fi,2.)-.5)*1.12,(floor(fi/2.)-.5)*.92),q=p-center;
            float lens=abs(length(q)-.29)-.006;
            float content=phaseContour(lfScalar(q*2.,time,fi),5.+fi,.06);
            c+=mix(LF_BLUE,LF_GOLD,fi/3.)*(aaStroke(lens,.006)+content*smoothstep(.30,.25,length(q))*.23);
        }
    }else{
        float reveal=lfPhase(u,.22,.82);vec2 q=projectiveWarp(p,.46*reveal,time*.03);
        c+=LF_BLUE*lfCrystal(q,time,1.48,.10*(1.-reveal))*.30;
        lfStreams(c,q,time,drive,1.);
        float pulseRing=abs(length(q)-(.18+.38*reveal+.04*beat))-.007;
        c+=LF_GOLD*glow(pulseRing,.042)*.55+LF_IVORY*aaStroke(pulseRing,.006);
        c+=LF_CYAN*causticField(q*.7,time)*.28*reveal;
    }
    c*=enter;
    return cinemaFinish(c,uv,gl_FragCoord.xy,time,.18+.15*drive);
}

#endif
