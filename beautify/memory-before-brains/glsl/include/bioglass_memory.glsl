#ifndef BEAUTIFY_BIOGLASS_MEMORY_GLSL
#define BEAUTIFY_BIOGLASS_MEMORY_GLSL

const vec3 MB_DEEP=vec3(.006,.028,.045);
const vec3 MB_TEAL=vec3(.04,.78,.72);
const vec3 MB_BLUE=vec3(.10,.42,1.08);
const vec3 MB_AMBER=vec3(1.32,.39,.08);
const vec3 MB_PEARL=vec3(.76,1.06,1.02);
const vec3 MB_VIOLET=vec3(.52,.13,.88);

vec3 mbBackground(vec2 p,float time){
    float water=fbmWarp(p*.92+vec2(0,time*.012),time*.14);
    float rays=softBeam(p,vec2(-1.4,.8),vec2(1.,-.34),.24,.33);
    vec3 c=MB_DEEP+vec3(.012,.09,.10)*water+MB_BLUE*.025*(.5+.5*sin(p.y*4.+water*3.));
    c+=MB_TEAL*rays*.055;
    return c;
}

float mbStressField(vec2 p,float time){
    float warp=fbmWarp(p*1.7,time*.16)-.5;
    return sin(p.x*8.+warp*3.+time*.12)*sin(p.y*7.-warp*2.);
}

void mbGlassCell(inout vec3 c,vec2 p,vec2 center,float radius,float state,float time,float drive){
    vec2 q=p-center;float r=length(q),d=r-radius;
    float inside=aaFill(d),z=sqrt(max(radius*radius-dot(q,q),0.))/radius;
    vec3 n=normalize(vec3(q/max(radius,.001),z));
    vec3 l=normalize(vec3(-.45,.62,.74));
    float fres=pow(1.-z,2.4),spec=pow(max(dot(reflect(-l,n),vec3(0,0,1)),0.),48.);
    float membrane=aaStroke(d,.009)+glow(d,.033)*.17;
    float inner=fbmWarp(q*4.+center*5.,time*.12);
    vec3 hue=bioglassPalette(state);
    c+=mix(MB_BLUE,hue,.68)*membrane*(.55+.35*drive);
    c+=hue*inside*(.035+.08*inner+.12*state);
    c+=MB_PEARL*(spec*.65+fres*.08)*inside;
    float nucleus=length(q-.14*radius*vec2(cos(time*.13+center.x*4.),sin(time*.11+center.y*3.)))-radius*.18;
    c+=mix(MB_TEAL,MB_AMBER,state)*(glow(nucleus,.018)*.18+aaStroke(nucleus,.004)*.34)*drive;
}

void mbTissue(inout vec3 c,vec2 p,float time,float state,float drive,float distortion){
    for(int y=-2;y<=2;y++)for(int x=-3;x<=3;x++){
        vec2 id=vec2(float(x),float(y));
        vec2 center=id*vec2(.34,.31);
        center.x+=mod(float(y),2.)*.17;
        center+=distortion*.045*(hash22(id+8.)-.5)*sin(time*.17+hash21(id)*TAU);
        float radius=.16+distortion*.02*sin(time*.4+hash21(id)*6.);
        float localState=saturate(state+.18*(hash21(id)-.5));
        mbGlassCell(c,p,center,radius,localState,time,drive);
        if(x<3){
            vec2 next=center+vec2(.34,0);
            lightFilament(c,p,center,next,mix(MB_BLUE,MB_TEAL,state),.10*drive);
        }
    }
}

float mbStateOrb(vec2 p,vec2 center,float radius,float phase,float time){
    vec2 q=p-center;
    float field=fbmWarp(q*2.7+phase*3.,time*.18);
    float boundary=abs(length(q)-(radius+.055*sin(atan(q.y,q.x)*6.+phase+time*.25)))-.007;
    return glow(boundary,.028)+phaseContour(field+phase,7.,.045)*(1.-smoothstep(.12,radius,length(q)));
}

void mbHysteresisLoop(inout vec3 c,vec2 p,float time,float drive,float separation){
    for(int branch=0;branch<2;branch++){
        float b=float(branch),d=9.;
        for(int i=0;i<48;i++){
            float fi=float(i)/47.;
            float x=-1.05+fi*2.1;
            float y=.38*tanh((x+mix(.34,-.34,b))*3.2)+(b-.5)*separation;
            y+=.035*sin(fi*16.+time*.2+b);
            vec2 q=vec2(x,y);
            d=min(d,length(p-q));
        }
        vec3 hue=mix(MB_AMBER,MB_TEAL,b);
        c+=hue*(aaStroke(d,.006)+glow(d,.033)*.24)*drive;
    }
}

void mbTraceTrail(inout vec3 c,vec2 p,float time,float persistence,float drive){
    vec2 velocity=vec2(.19,.05*sin(time*.2));
    float headPhase=fract(time*.12);
    vec2 head=vec2(-1.15+2.3*headPhase,.26*sin(headPhase*TAU));
    float trail=temporalEcho(p,head,velocity,time,.62,.065);
    c+=MB_AMBER*trail*(.18+.62*persistence)*drive;
    radiantNode(c,p,head,.09,MB_PEARL,.55*drive);
}

float mbMorphogen(vec2 p,float time,float target){
    vec2 q=p;q.x*=1.1;
    float core=sdCapsule3(vec3(q,0),vec3(-.55,0,0),vec3(.32,0,0),.12);
    float branch=9.;
    for(int i=0;i<5;i++){
        float fi=float(i),a=mix(-1.1,1.1,fi/4.)+time*.015;
        vec2 root=vec2(.12,-.02+.025*sin(fi+time));
        vec2 tip=root+mix(.18,.58,target)*vec2(cos(a),sin(a));
        branch=min(branch,sdSegment(q,root,tip)-mix(.045,.075,target));
    }
    return smoothUnion(core,branch,.10);
}

void mbBraid(inout vec3 c,vec2 p,float time,float drive,float editing){
    for(int strand=0;strand<3;strand++){
        float s=float(strand),d=9.;
        for(int i=0;i<55;i++){
            float fi=float(i)/54.,x=-1.18+fi*2.36;
            float y=.22*sin(fi*TAU*3.+s*TAU/3.+time*.12);
            y+=editing*.10*sin(fi*TAU*7.+time+s);
            d=min(d,length(p-vec2(x,y)));
        }
        vec3 hue=s<1.?MB_AMBER:(s<2.?MB_TEAL:MB_VIOLET);
        c+=hue*(aaStroke(d,.006)+glow(d,.028)*.18)*drive;
    }
}

void mbTensegrity(inout vec3 c,vec2 p,float time,float drive,float memory){
    for(int i=0;i<10;i++){
        float fi=float(i),a=fi*TAU/10.+time*.025;
        vec2 n=(.45+.14*sin(fi*2.3))*vec2(cos(a),sin(a));
        float fj=mod(fi+3.+floor(memory*2.),10.);
        vec2 m=(.45+.14*sin(fj*2.3))*vec2(cos(fj*TAU/10.+time*.025),sin(fj*TAU/10.+time*.025));
        lightFilament(c,p,n,m,mix(MB_BLUE,MB_AMBER,memory),.42*drive);
        radiantNode(c,p,n,.075,MB_PEARL,.22*drive);
    }
}

void mbNeuralInheritance(inout vec3 c,vec2 p,float time,float drive,float specialization){
    vec2 root=vec2(-1.1,0);
    for(int i=0;i<24;i++){
        float fi=float(i),gen=floor(log2(fi+1.)),idx=fi-(exp2(gen)-1.),count=exp2(gen);
        vec2 a=root+vec2(gen*.29,(floor(idx*.5)-(count*.25-.5))*.38/(gen+1.));
        vec2 b=root+vec2((gen+1.)*.29,(idx-(count*.5-.5))*.38/(gen+1.)*specialization);
        b.y+=.04*sin(fi+time*.2);
        float d=sdSegment(p,a,b);
        c+=mix(MB_TEAL,MB_AMBER,gen/4.)*(aaStroke(d,.004)+glow(d,.024)*.13)*drive;
    }
}

vec3 renderBioglassMemory(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    float drive=audioEnergy(volume,beat),enter=easeOut(min(1.,u*1.5));
    float reveal=smoothstep(.18,.82,u),pulseBeat=.5+.5*sin(time*.7);
    vec3 c=mbBackground(p,time);

    if(mode==0){
        mbGlassCell(c,p,vec2(0),.52,.78,time,drive);
        mbTraceTrail(c,p,time,reveal,drive);
        float wake=abs(sdSegment(p,vec2(-.9,-.3),vec2(.6,.35)))-.008;
        c+=MB_TEAL*glow(wake,.04)*.12*reveal;
    }else if(mode==1){
        float switcher=smoothstep(.35,.72,u);
        c+=mix(MB_BLUE,MB_AMBER,switcher)*mbStateOrb(p,vec2(-.42,0),.42,0.,time)*.34;
        c+=mix(MB_AMBER,MB_TEAL,switcher)*mbStateOrb(p,vec2(.42,0),.42,1.7,time)*.34;
        lightFilament(c,p,vec2(-.18,0),vec2(.18,0),MB_PEARL,.42*drive);
    }else if(mode==2){
        mbTissue(c,p,time,.72*reveal,drive,.7);
        mbTraceTrail(c,p,time,reveal,drive*.42);
    }else if(mode==3){
        mbHysteresisLoop(c,p,time,drive,.18+.24*reveal);
        radiantNode(c,p,vec2(mix(-.85,.82,fract(time*.1)),.28),.075,MB_AMBER,.42*drive);
        c+=MB_BLUE*phaseContour(p.x*.32+p.y*.12,9.,.05)*.05;
    }else if(mode==4){
        mbTissue(c,p,time,.34,drive,.45);
        float before=abs(sdSegment(p,vec2(-1.1,-.42),vec2(1.1,-.42)))-.005;
        float after=abs(p.y-.28-.17*sin(p.x*4.+time*.3))- .006;
        c+=MB_BLUE*aaStroke(before,.005)*.48;
        c+=MB_AMBER*(aaStroke(after,.006)+glow(after,.028)*.18)*reveal;
    }else if(mode==5){
        float target=mbMorphogen(p,time,reveal);
        c+=MB_TEAL*(aaStroke(target,.010)+glow(target,.045)*.30);
        c+=MB_AMBER*phaseContour(target+fbmWarp(p*1.6,time)*.1,8.,.045)*aaFill(target)*.32;
        for(int i=0;i<9;i++){float fi=float(i);vec2 n=vec2(-.78+fi*.19,.10*sin(fi+time));radiantNode(c,p,n,.055,MB_PEARL,.15*drive);}
    }else if(mode==6){
        mbTissue(c,p,time,.18,drive,.3);
        float hidden=mbMorphogen(p,time,1.);
        c+=MB_AMBER*(aaStroke(hidden,.006)+glow(hidden,.04)*.22)*reveal*.55;
        c+=MB_VIOLET*phaseContour(fbmWarp(p*2.,time),10.,.035)*(1.-reveal)*.12;
    }else if(mode==7){
        float second=smoothstep(.32,.68,u),target=mbMorphogen(p,time,1.);
        c+=MB_TEAL*(aaStroke(target,.009)+glow(target,.04)*.22)*second;
        float cut=abs(p.x+.35)-.008;
        c+=MB_PEARL*aaStroke(cut,.008)*(1.-second)+MB_AMBER*glow(cut,.035)*.2;
        mbTraceTrail(c,p,time,second,drive*.5);
    }else if(mode==8){
        mbTissue(c,p,time,mix(.85,.12,reveal),drive,.5*(1.-reveal));
        float resetRing=abs(length(p)-mix(.18,1.28,reveal))- .008;
        c+=MB_PEARL*(aaStroke(resetRing,.008)+glow(resetRing,.05)*.24)*drive;
    }else if(mode==9){
        mbBraid(c,p,time,drive,reveal);
        for(int i=0;i<8;i++){float fi=float(i);float x=-1.05+fi*.30;float tag=abs(sdRegularPolygon(p-vec2(x,.48),.055,4.,fi*.2))-.005;c+=mix(MB_AMBER,MB_TEAL,fi/7.)*aaStroke(tag,.005);}
    }else if(mode==10){
        mbTensegrity(c,p,time,drive,reveal);
        float stress=phaseContour(mbStressField(p,time),7.,.04);
        c+=MB_VIOLET*stress*.08;
        c+=MB_AMBER*causticField(p*.6,time)*.16*reveal;
    }else if(mode==11){
        for(int i=0;i<15;i++){
            float fi=float(i),a=fi*TAU/15.+time*.09;
            vec2 cell=.68*vec2(cos(a),sin(a));
            mbGlassCell(c,p,cell,.085,mod(fi,3.)/2.,time,drive);
        }
        radiantNode(c,p,vec2(.15*cos(time*.4),.15*sin(time*.4)),.18,MB_AMBER,.52*drive);
    }else if(mode==12){
        mbTissue(c,p,time,.38,drive*.55,.25);
        for(int i=0;i<7;i++){
            float fi=float(i),x=-1.15+fi*.38;
            float strength=exp(-fi*.32)*(1.-reveal)+.08;
            float ring=abs(length(p-vec2(x,.38*sin(fi+time*.2)))-(.12+.025*pulseBeat))- .005;
            c+=MB_AMBER*(aaStroke(ring,.005)+glow(ring,.025)*strength)*strength;
        }
    }else if(mode==13){
        mbTissue(c,p+vec2(.65,0),time,.45,drive*.45,.5);
        mbNeuralInheritance(c,p,time,drive,reveal);
        float wave=softBeam(p,vec2(-1.2,0),vec2(1,.08),.10,.3);
        c+=MB_AMBER*wave*.16;
    }else if(mode==14){
        for(int i=0;i<22;i++){
            float fi=float(i),a=fi*2.399+time*.015;
            vec2 home=.72*sqrt(fi/21.)*vec2(cos(a),sin(a));
            vec2 recall=home+.15*vec2(sin(fi*3.1),cos(fi*2.2))*(1.-reveal);
            radiantNode(c,p,recall,.065,mix(MB_BLUE,MB_AMBER,reveal),.18*drive);
            if(i>0)lightFilament(c,p,recall,.62*recall*rot(.7),MB_TEAL,.08*reveal);
        }
    }else if(mode==15){
        mbGlassCell(c,p,vec2(-.46,0),.36,.52,time,drive);
        mbGlassCell(c,p,vec2(.46,0),.36,.52,time,drive);
        float halo=abs(length(p-vec2(.46,0))-(.43+.04*sin(time*.4)))-.007;
        c+=MB_AMBER*(aaStroke(halo,.006)+glow(halo,.04)*.23)*reveal;
        lightFilament(c,p,vec2(-.10,0),vec2(.10,0),MB_PEARL,.28*drive);
    }else if(mode==16){
        for(int i=0;i<4;i++){
            float fi=float(i),x=-.84+fi*.56;
            float layer=abs(sdRoundBox(p-vec2(x,0),vec2(.20,.58-.07*fi),.12))-.006;
            c+=mix(MB_BLUE,MB_AMBER,fi/3.)*(aaStroke(layer,.006)+glow(layer,.025)*.12);
        }
    }else if(mode==17){
        mbTissue(c,p+vec2(.58,0),time,.62,drive*.42,.35);
        float field=abs(sdVesica(p-vec2(.46,0),.66,.34))-.007;
        c+=MB_AMBER*(aaStroke(field,.007)+glow(field,.055)*.26)*reveal;
        radiantNode(c,p,vec2(.46,0),.22,MB_PEARL,.55*drive);
        lightFilament(c,p,vec2(-.05,0),vec2(.25,0),MB_TEAL,.4*drive);
    }else{
        vec2 centers[4]=vec2[4](vec2(-.92,0),vec2(-.31,0),vec2(.31,0),vec2(.92,0));
        for(int i=0;i<4;i++){
            float fi=float(i),r=.13+.05*fi;
            mbGlassCell(c,p,centers[i],r,fi/3.,time,drive);
            if(i<3)lightFilament(c,p,centers[i]+vec2(r,0),centers[i+1]-vec2(r+.02,0),mix(MB_TEAL,MB_AMBER,fi/3.),.48*drive);
        }
        mbTraceTrail(c,p,time,reveal,drive*.32);
        float encompassing=abs(sdVesica(p,.98,.52))-.007;
        c+=MB_PEARL*glow(encompassing,.04)*.20+MB_AMBER*aaStroke(encompassing,.006)*reveal;
    }
    c*=enter;
    return cinemaFinish(c,uv,gl_FragCoord.xy,time,.18+.12*drive);
}

#endif
