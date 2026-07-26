#ifndef BEAUTIFY_LOCALIZATION_LENS_GLSL
#define BEAUTIFY_LOCALIZATION_LENS_GLSL

const vec3 RL_VOID=vec3(.004,.008,.026);
const vec3 RL_BLUE=vec3(.08,.32,1.18);
const vec3 RL_CYAN=vec3(.06,.92,1.08);
const vec3 RL_MAGENTA=vec3(.84,.08,.72);
const vec3 RL_ORANGE=vec3(1.28,.34,.06);
const vec3 RL_WHITE=vec3(.78,.92,1.14);

vec3 rlBackground(vec2 p,float time){
    float space=fbmWarp(p*.68+vec2(time*.008,0),time*.12);
    vec3 c=RL_VOID+vec3(.014,.018,.09)*space;
    c+=RL_MAGENTA*.018*causticField(p*.42,time);
    return c;
}

void rlPointField(inout vec3 c,vec2 p,float time,float lens,float drive){
    for(int y=-4;y<=4;y++)for(int x=-7;x<=7;x++){
        vec2 id=vec2(float(x),float(y));
        vec2 n=(id+hash22(id+17.)-.5)*vec2(.22,.23);
        vec2 q=n;
        float r2=dot(q,q);
        q+=lens*q/max(r2,.08)*.045;
        q*=rot(.035*time*hash21(id));
        float size=.012+.012*hash21(id+4.);
        float d=length(p-q);
        vec3 hue=interferencePalette(hash21(id),.03);
        c+=hue*exp(-d*d/(size*size))*(.18+.18*drive);
    }
}

float rlGrid(vec2 p,float time,float bend){
    vec2 q=projectiveWarp(p,bend,.25+time*.025);
    float radial=max(.08,length(q));
    q+=bend*.11*q/radial*sin(radial*7.-time*.2);
    vec2 lineDist=abs(fract(q*4.)-.5);
    return 1.-smoothstep(.025,.045,min(lineDist.x,lineDist.y));
}

void rlPortal(inout vec3 c,vec2 p,vec2 center,float radius,float time,vec3 hue,float drive,float depth){
    vec2 q=p-center;
    float ring=abs(length(q)-radius)-.007;
    c+=hue*(aaStroke(ring,.006)+glow(ring,.038)*.22)*drive;
    for(int i=0;i<5;i++){
        float fi=float(i),r=radius*(.18+.14*fi);
        float d=abs(length(q)-r-.015*sin(atan(q.y,q.x)*(4.+fi)+time*.3))- .004;
        c+=mix(hue,RL_WHITE,fi/4.)*glow(d,.018)*.08*depth;
    }
    c+=hue*causticField(q/max(radius,.1)*.34,time)*.055*depth*(1.-smoothstep(radius*.25,radius,length(q)));
}

float rlConeMask(vec2 p,vec2 origin,vec2 direction,float aperture,float range){
    direction=normalize(direction);
    vec2 q=p-origin;
    float along=dot(q,direction),across=abs(dot(q,vec2(-direction.y,direction.x)));
    return (1.-smoothstep(0.,aperture*max(along,.01),across))
        *smoothstep(0.,.06,along)*(1.-smoothstep(range*.72,range,along));
}

void rlCone(inout vec3 c,vec2 p,vec2 origin,vec2 direction,float aperture,float range,vec3 hue,float drive){
    direction=normalize(direction);
    vec2 ortho=vec2(-direction.y,direction.x);
    vec2 end=origin+direction*range;
    lightFilament(c,p,origin,end+ortho*aperture*range,hue,.42*drive);
    lightFilament(c,p,origin,end-ortho*aperture*range,hue,.42*drive);
    c+=hue*rlConeMask(p,origin,direction,aperture,range)*.045*drive;
}

void rlSensoryOrbit(inout vec3 c,vec2 p,float time,float drive,float integration){
    for(int i=0;i<8;i++){
        float fi=float(i),a=fi*TAU/8.+time*.035*(1.+mod(fi,2.));
        vec2 node=(.56+.06*sin(fi*2.1))*vec2(cos(a),sin(a));
        vec3 hue=interferencePalette(fi/8.,.08);
        radiantNode(c,p,node,.095,hue,.22*drive);
        if(integration>0.)lightFilament(c,p,node,vec2(0),mix(hue,RL_WHITE,integration),.38*drive*integration);
    }
    rlPortal(c,p,vec2(0),.18,time,RL_ORANGE,drive,.7);
}

void rlLandmarks(inout vec3 c,vec2 p,float time,float drive,float model){
    for(int i=0;i<11;i++){
        float fi=float(i),a=fi*2.399;
        vec2 n=(.24+.052*fi)*vec2(cos(a),sin(a));
        n=projectiveWarp(n,.28*model,time*.02);
        float shape=abs(sdRegularPolygon(p-n,.055+.012*mod(fi,3.),3.+mod(fi,5.),a))-.005;
        vec3 hue=mix(RL_CYAN,RL_ORANGE,hash11(fi));
        c+=hue*(aaStroke(shape,.005)+glow(shape,.022)*.14)*drive;
        if(i>0)lightFilament(c,p,n,.72*n*rot(.43),RL_BLUE,.09*model);
    }
}

void rlPredictionLoop(inout vec3 c,vec2 p,float time,float drive,float correction){
    for(int lane=0;lane<3;lane++){
        float l=float(lane),d=9.;
        for(int i=0;i<54;i++){
            float fi=float(i)/53.,a=fi*TAU;
            float r=.38+.12*l+.05*sin(a*3.+time*.2+l);
            vec2 q=r*vec2(cos(a),sin(a));
            q+=correction*.12*vec2(sin(a*2.+time),cos(a*3.-time));
            d=min(d,length(p-q));
        }
        c+=mix(RL_CYAN,RL_ORANGE,l/2.)*(aaStroke(d,.005)+glow(d,.026)*.14)*drive;
    }
    radiantNode(c,p,.43*vec2(cos(time*.45),sin(time*.45)),.075,RL_WHITE,.28*drive);
}

void rlMemoryThread(inout vec3 c,vec2 p,float time,float drive,float biography){
    vec2 prev=vec2(-1.22,-.44);
    for(int i=1;i<15;i++){
        float fi=float(i)/14.;
        vec2 next=vec2(-1.22+fi*2.44,.38*sin(fi*TAU*1.5+time*.05)+.12*sin(fi*17.));
        lightFilament(c,p,prev,next,mix(RL_BLUE,RL_ORANGE,fi),.48*drive);
        if(fi<biography)radiantNode(c,p,next,.07,mix(RL_CYAN,RL_ORANGE,fi),.24*drive);
        prev=next;
    }
}

void rlSelfShell(inout vec3 c,vec2 p,float time,float drive,float defense){
    vec2 q=projectiveWarp(p,.22*defense,time*.025);
    for(int i=0;i<6;i++){
        float fi=float(i),r=.20+fi*.105;
        float d=abs(sdRegularPolygon(q,r,5.+mod(fi,3.),fi*.12+time*.01))- .006;
        c+=mix(RL_CYAN,RL_MAGENTA,defense)*(aaStroke(d,.006)+glow(d,.025)*.13)*(1.-fi*.08);
    }
    radiantNode(c,p,vec2(0),.18,RL_ORANGE,.38*drive);
}

void rlFiveLimits(inout vec3 c,vec2 p,float time,float drive,float contraction){
    for(int i=0;i<5;i++){
        float fi=float(i),r=.76-fi*.12*contraction;
        vec2 q=p*rot(fi*.23+time*.012);
        float shell=abs(sdRegularPolygon(q,r,4.+fi,fi*.3))- .006;
        c+=interferencePalette(fi/5.,.11)*(aaStroke(shell,.006)+glow(shell,.027)*.12)*drive;
    }
}

void rlTriad(inout vec3 c,vec2 p,float time,float drive,float fusion){
    vec2 a=vec2(-.58,-.30),b=vec2(.58,-.30),k=vec2(0,.56);
    lightFilament(c,p,a,b,RL_BLUE,.45*drive);
    lightFilament(c,p,b,k,RL_MAGENTA,.45*drive);
    lightFilament(c,p,k,a,RL_ORANGE,.45*drive);
    radiantNode(c,p,a,.14,mix(RL_BLUE,RL_WHITE,fusion),.38*drive);
    radiantNode(c,p,b,.14,mix(RL_MAGENTA,RL_WHITE,fusion),.38*drive);
    radiantNode(c,p,k,.14,mix(RL_ORANGE,RL_WHITE,fusion),.38*drive);
    c+=RL_WHITE*phaseContour(fbmWarp(p*1.2,time),8.,.04)*smoothstep(.55,.12,length(p))*.09*fusion;
}

void rlNestedFrames(inout vec3 c,vec2 p,float time,float drive,float recursion){
    for(int i=0;i<7;i++){
        float fi=float(i),scale=1.-fi*.12;
        vec2 q=(p-vec2(.04*fi,-.025*fi))*rot(fi*.055*recursion);
        float frame=abs(sdRoundBox(q,vec2(.98,.68)*scale,.12*scale))-.006;
        c+=mix(RL_BLUE,RL_ORANGE,fi/6.)*(aaStroke(frame,.006)+glow(frame,.022)*.09)*drive;
    }
}

void rlNeuralObject(inout vec3 c,vec2 p,float time,float drive,float growth){
    vec2 root=vec2(-.72,0);
    for(int i=0;i<24;i++){
        float fi=float(i),gen=floor(log2(fi+1.)),idx=fi-(exp2(gen)-1.),count=exp2(gen);
        vec2 a=root+vec2(gen*.25,(floor(idx*.5)-(count*.25-.5))*.34/(gen+1.));
        vec2 b=root+vec2((gen+1.)*.25,(idx-(count*.5-.5))*.34/(gen+1.)*growth);
        b.y+=.035*sin(fi+time*.18);
        float d=sdSegment(p,a,b);
        c+=mix(RL_BLUE,RL_MAGENTA,gen/4.)*(aaStroke(d,.004)+glow(d,.022)*.12)*drive;
    }
}

void rlFlowLocalization(inout vec3 c,vec2 p,float time,float drive,float focus){
    for(int i=0;i<9;i++){
        float fi=float(i),y=-.8+fi*.20,d=9.;vec2 prev=vec2(-1.35,y);
        for(int j=1;j<24;j++){
            float fj=float(j)/23.,x=-1.35+fj*2.7;
            vec2 next=vec2(x,mix(y,.05*sin(fi),focus*bell(fj))+.05*sin(fj*12.+fi+time*.15));
            d=min(d,sdSegment(p,prev,next));prev=next;
        }
        c+=mix(RL_CYAN,RL_ORANGE,focus)*(aaStroke(d,.004)+glow(d,.023)*.10)*drive;
    }
}

vec3 renderLocalizationLens(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    float drive=audioEnergy(volume,beat),enter=easeOut(min(1.,u*1.55));
    float reveal=smoothstep(.18,.84,u),breath=.5+.5*sin(time*.57);
    vec3 c=rlBackground(p,time);

    if(mode==0){
        rlPointField(c,p,time,0.,drive);
        rlPortal(c,p,vec2(-.78,0),.20,time,RL_ORANGE,drive,.8);
        rlCone(c,p,vec2(-.58,0),vec2(1,0),.22,1.65,RL_CYAN,drive);
        rlPortal(c,p,vec2(.72,.05),.18,time,RL_MAGENTA,drive,.7);
    }else if(mode==1){
        rlTriad(c,p,time,drive,reveal);
        rlPointField(c,p,time,.26*reveal,drive*.65);
        float field=abs(length(p)-(.82+.04*sin(time*.25)))-.006;
        c+=RL_CYAN*glow(field,.04)*.15;
    }else if(mode==2){
        rlPointField(c,p,time,.62*reveal,drive);
        vec2 focus=mix(vec2(-.9,.4),vec2(0),reveal);
        rlPortal(c,p,focus,mix(.08,.31,reveal),time,RL_ORANGE,drive,1.);
        c+=RL_WHITE*lensFlare(p,focus)*.045*reveal;
    }else if(mode==3){
        rlSensoryOrbit(c,p,time,drive,reveal);
        float body=abs(sdVesica(p,.72,.36))-.007;
        c+=RL_ORANGE*(aaStroke(body,.006)+glow(body,.035)*.14)*reveal;
    }else if(mode==4){
        vec2 origin=vec2(-.88,-.10);
        rlPortal(c,p,origin,.14,time,RL_ORANGE,drive,.7);
        rlCone(c,p,origin,vec2(1,.15),mix(.46,.16,reveal),1.85,RL_CYAN,drive);
        rlLandmarks(c,p-vec2(.35,.08),time,drive*.72,reveal);
    }else if(mode==5){
        rlPointField(c,p,time,.18,drive*.52);
        rlCone(c,p,vec2(-.9,0),vec2(1,0),mix(.55,.08,reveal),1.9,RL_ORANGE,drive);
        float target=abs(sdRegularPolygon(p-vec2(.58,0),.16,5.,time*.05))-.006;
        c+=RL_WHITE*(aaStroke(target,.006)+glow(target,.035)*.25)*reveal;
    }else if(mode==6){
        rlSensoryOrbit(c,p,time,drive,reveal);
        float body=abs(sdVesica(projectiveWarp(p,.38*reveal,time*.03),.62,.30))-.008;
        c+=RL_CYAN*aaStroke(body,.008)+RL_ORANGE*glow(body,.045)*.22;
    }else if(mode==7){
        c+=RL_BLUE*rlGrid(p,time,.48*reveal)*.26;
        rlLandmarks(c,p,time,drive,reveal);
        rlPortal(c,p,vec2(0),.68,time,RL_CYAN,drive*.65,.6);
    }else if(mode==8){
        rlPredictionLoop(c,p,time,drive,reveal);
        rlCone(c,p,.42*vec2(cos(time*.45),sin(time*.45)),normalize(-vec2(cos(time*.45),sin(time*.45))),.18,.8,RL_ORANGE,drive);
    }else if(mode==9){
        rlMemoryThread(c,p,time,drive,reveal);
        c+=RL_BLUE*rlGrid(p,time,.15)*.07;
    }else if(mode==10){
        rlSelfShell(c,p,time,drive,reveal);
        rlMemoryThread(c,p,time,drive*.35,reveal);
    }else if(mode==11){
        rlFiveLimits(c,p,time,drive,reveal);
        c+=RL_BLUE*rlGrid(p,time,.48)*.12;
        rlPortal(c,p,vec2(0),mix(.34,.12,reveal),time,RL_ORANGE,drive,.8);
    }else if(mode==12){
        rlTriad(c,p,time,drive,.45);
        rlPointField(c,p,time,.22,drive*.52);
        c+=RL_CYAN*causticField(p*.5,time)*.12;
    }else if(mode==13){
        rlNestedFrames(c,p,time,drive,reveal);
        rlPortal(c,p,vec2(0),.20,time,RL_ORANGE,drive,1.);
        c+=RL_WHITE*causticField(p*.36,time)*.10*reveal;
    }else if(mode==14){
        rlPointField(c,p,time,.18,drive*.45);
        float screen=abs(sdRoundBox(p,vec2(.95,.63),.12))-.007;
        c+=RL_WHITE*aaStroke(screen,.007)*.65;
        rlNeuralObject(c,p+vec2(.65,0),time,drive*.6,reveal);
        rlPortal(c,p,vec2(.48,0),.28,time,RL_MAGENTA,drive,.6);
    }else if(mode==15){
        float aperture=abs(sdRegularPolygon(p-vec2(-.65,0),.19,8.,time*.02))-.007;
        c+=RL_ORANGE*(aaStroke(aperture,.006)+glow(aperture,.035)*.18);
        rlCone(c,p,vec2(-.46,0),vec2(1,0),.31,1.6,RL_CYAN,drive);
        c+=RL_MAGENTA*rlGrid(p-vec2(.42,0),time,.35)*.17;
        rlPointField(c,p,time,.22,drive*.52);
    }else if(mode==16){
        rlNestedFrames(c,p,time,drive,1.-reveal);
        rlPointField(c,p,time,.38*reveal,drive);
        for(int i=0;i<6;i++){
            float fi=float(i),a=fi*TAU/6.+time*.04;
            radiantNode(c,p,.52*vec2(cos(a),sin(a)),.08,interferencePalette(fi/6.,.02),.22*drive*reveal);
        }
    }else if(mode==17){
        rlFlowLocalization(c,p,time,drive,reveal);
        rlPortal(c,p,vec2(0),.15+.12*beat,time,RL_ORANGE,drive,1.);
    }else if(mode==18){
        float warm=smoothstep(.14,.85,u);
        vec2 q=projectiveWarp(p,.62*warm,PI+time*.03);
        c+=mix(RL_BLUE,RL_MAGENTA,warm)*rlGrid(q,time,.45)*.18;
        rlPointField(c,q,time,.36*warm,drive*.7);
        radiantNode(c,p,vec2(.34*sin(time*.18),.18*cos(time*.22)),.26,mix(RL_CYAN,RL_ORANGE,warm),.48*drive);
    }else if(mode==19){
        rlFlowLocalization(c,p,time,drive,.25*reveal);
        for(int i=0;i<8;i++){
            float fi=float(i),x=-1.08+fi*.31;
            float token=abs(sdRegularPolygon(p-vec2(x,.38*sin(fi)),.07,3.+mod(fi,5.),fi*.4))-.005;
            c+=mix(RL_CYAN,RL_ORANGE,reveal)*(aaStroke(token,.005)+glow(token,.02)*.10)*reveal;
        }
    }else if(mode==20){
        float freeze=smoothstep(.22,.78,u);
        for(int i=0;i<28;i++){
            float fi=float(i),a=fi*2.399+time*.10*(1.-freeze);
            vec2 moving=(.18+.024*fi)*vec2(cos(a),sin(a));
            vec2 shape=.55*vec2(cos(fi*TAU/28.),sin(fi*TAU/28.));
            vec2 n=mix(moving,shape,freeze);
            radiantNode(c,p,n,.055,mix(RL_MAGENTA,RL_ORANGE,freeze),.14*drive);
        }
        float object=abs(sdRegularPolygon(p,.55,9.,0.))-.006;
        c+=RL_WHITE*aaStroke(object,.006)*freeze;
    }else if(mode==21){
        for(int i=0;i<5;i++){
            float fi=float(i),a=fi*TAU/5.+time*.025;
            vec2 n=.64*vec2(cos(a),sin(a));
            rlPortal(c,p,n,.15,time,interferencePalette(fi/5.,.08),drive,.9);
            rlCone(c,p,n,-n,.16,.64,mix(RL_CYAN,RL_ORANGE,fi/4.),drive*.55);
        }
    }else if(mode==22){
        vec2 object=vec2(.32,.05);
        for(int i=0;i<5;i++){
            float fi=float(i),a=PI+mix(-.7,.7,fi/4.);
            vec2 observer=object+.95*vec2(cos(a),sin(a));
            rlPortal(c,p,observer,.10,time,interferencePalette(fi/5.,.04),drive,.7);
            rlCone(c,p,observer,object-observer,.14,.94,RL_CYAN,drive*.52);
        }
        rlPortal(c,p,object,.19,time,RL_ORANGE,drive,1.);
    }else if(mode==23){
        float widen=smoothstep(.18,.82,u);
        rlCone(c,p,vec2(-.82,0),vec2(1,0),mix(.10,.72,widen),1.7,RL_CYAN,drive);
        rlPointField(c,p,time,.52*widen,drive);
        rlPortal(c,p,vec2(-.82,0),mix(.13,.30,widen),time,mix(RL_ORANGE,RL_WHITE,widen),drive,1.);
        c+=RL_MAGENTA*rlGrid(p,time,.42*widen)*.10*widen;
    }else if(mode==24){
        vec2 left=p+vec2(.66,0),right=p-vec2(.66,0);
        c+=RL_BLUE*rlGrid(left,time,.28)*.20*step(p.x,0.);
        rlPredictionLoop(c,left,time,drive*.55,reveal);
        rlPointField(c,right,time,.55,drive*.62);
        float seam=abs(p.x)-.006;c+=RL_ORANGE*(aaStroke(seam,.006)+glow(seam,.035)*.2);
    }else if(mode==25){
        for(int i=0;i<4;i++){
            float fi=float(i);vec2 n=vec2((mod(fi,2.)-.5)*1.12,(floor(fi/2.)-.5)*.88);
            rlPortal(c,p,n,.22,time,interferencePalette(fi/4.,.07),drive,.5+.12*fi);
        }
        float boundary=abs(sdRoundBox(p,vec2(1.18,.77),.18))-.006;
        c+=RL_WHITE*aaStroke(boundary,.006)*.38;
    }else{
        float widen=smoothstep(.16,.84,u);
        vec2 observer=vec2(-.72+.38*widen,0);
        rlPointField(c,p,time,.62*widen,drive);
        c+=RL_BLUE*rlGrid(p,time,.40*widen)*.12;
        rlPortal(c,p,observer,mix(.13,.28,widen),time,RL_ORANGE,drive,1.);
        rlCone(c,p,observer,vec2(1,.10),mix(.13,.48,widen),1.65,RL_CYAN,drive);
        rlPortal(c,p,vec2(.62,.12),.17,time,RL_MAGENTA,drive,.8);
        float universe=abs(length(p)-(.92+.04*sin(time*.22)))-.006;
        c+=RL_WHITE*glow(universe,.04)*.18*widen;
    }
    c*=enter;
    return cinemaFinish(c,uv,gl_FragCoord.xy,time,.18+.13*drive);
}

#endif
