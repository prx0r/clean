#ifndef BEAUTIFY_INFINITY_OPTICS_GLSL
#define BEAUTIFY_INFINITY_OPTICS_GLSL

const vec3 MO_BLACK=vec3(.004,.006,.016);
const vec3 MO_GOLD=vec3(1.40,.65,.09);
const vec3 MO_VIOLET=vec3(.48,.16,1.10);
const vec3 MO_CYAN=vec3(.00,.88,1.04);
const vec3 MO_GREEN=vec3(.02,.70,.42);
const vec3 MO_RED=vec3(1.04,.05,.16);
const vec3 MO_WHITE=vec3(.95,.98,1.08);

vec3 moField(vec2 p,float time){
    vec3 c=signatureNightField(p,time,vec3(.12,.07,.26));
    float vertical=exp(-p.x*p.x*2.5);
    float horizontal=exp(-p.y*p.y*2.5);
    c+=MO_VIOLET*.025*vertical+MO_CYAN*.018*horizontal;
    return c;
}

void moSource(inout vec3 c,vec2 p,float time,float transcend,float drive){
    for(int i=0;i<7;i++){
        float fi=float(i);
        float r=.10+fi*.075;
        float ring=abs(length(p)-r-.012*sin(fi*2.+time*.12))-.005;
        c+=mix(MO_GOLD,MO_VIOLET,fi/7.)
            *(aaStroke(ring,.005)+glow(ring,.025)*.08)*drive*exp(-fi*.16);
    }
    c+=MO_WHITE*lensFlare(p,vec2(0))*.12*(.5+.5*transcend);
}

void moProcession(inout vec3 c,vec2 p,float time,float descent,float drive){
    vec2 previous=vec2(0,.82);
    for(int i=0;i<8;i++){
        float fi=float(i),y=.82-fi*.235;
        vec2 n=vec2(.12*sin(fi*.9+time*.04),y);
        float strength=exp(-fi*.20*descent);
        vec3 hue=mix(MO_GOLD,MO_VIOLET,fi/7.);
        signatureNode(c,p,n,.075,hue,.34*drive*strength);
        if(i>0)signatureChannel(c,p,previous,n,hue,.28*drive*strength,time+fi);
        previous=n;
    }
}

void moMirrorField(inout vec3 c,vec2 p,float time,float freedom,float drive){
    for(int i=0;i<9;i++){
        float fi=float(i),a=fi*TAU/9.+time*.018;
        vec2 n=(.22+.055*fi)*vec2(cos(a),sin(a));
        vec2 reflected=n*vec2(-1,1);
        vec3 hue=interferencePalette(fi/9.+freedom*.13,.08);
        signatureNode(c,p,n,.036,hue,.18*drive);
        signatureNode(c,p,reflected,.036,hue,.13*drive);
        signatureChannel(c,p,n,reflected,MO_GOLD,.10*freedom*drive,time-fi);
    }
    vec2 q=p*rot(.10*sin(time*.06));
    float r2=dot(q,q);
    float implicit=(r2*r2)-.32*(q.x*q.x-q.y*q.y)
        +.008*freedom*sin(q.y*9.+time*.12);
    float mirror=abs(implicit)/(.18+length(q))-.008;
    c+=MO_GOLD*(aaStroke(mirror,.006)+glow(mirror,.035)*.11)*drive;
}

void moPolarization(inout vec3 c,vec2 p,float time,float split,float drive){
    vec2 subject=vec2(-.46,0),object=vec2(.46,0);
    signatureNode(c,p,subject,.12,MO_CYAN,.34*drive);
    signatureNode(c,p,object,.12,MO_VIOLET,.34*drive);
    signatureChannel(c,p,subject,object,MO_GOLD,.34*drive,time);
    float enclosing=signatureBoundary(p,mix(.24,.72,split),.025,time*.08);
    c+=MO_WHITE*(aaStroke(enclosing,.006)+glow(enclosing,.04)*.08)*split;
}

void moOverflow(inout vec3 c,vec2 p,float time,float abundance,float drive){
    for(int i=0;i<12;i++){
        float fi=float(i),a=fi*TAU/12.+time*.01;
        vec2 origin=vec2(0,.70);
        vec2 target=vec2(.94*cos(a)*(.25+.75*abundance),-.55+.15*sin(a*3.));
        float beam=softBeam(p,origin,normalize(target-origin),.10+.012*fi,.85);
        c+=mix(MO_GOLD,MO_VIOLET,fi/11.)*beam*.15*drive;
    }
    c+=MO_GOLD*causticField((p-vec2(0,-.15))*.8,time)*.13*abundance;
}

void moDiminution(inout vec3 c,vec2 p,float time,float diminish,float drive){
    for(int i=0;i<9;i++){
        float fi=float(i),y=.80-fi*.20;
        float r=.12-.007*fi;
        float d=abs(length(p-vec2(.08*sin(fi+time*.03),y))-r)-.005;
        float energy=exp(-fi*.34*diminish);
        c+=mix(MO_GOLD,MO_VIOLET,fi/8.)*(aaStroke(d,.005)+glow(d,.025)*.08)*energy*drive;
    }
}

void moFreedomBranches(inout vec3 c,vec2 p,float time,float freedom,float drive){
    vec2 root=vec2(0,-.66);
    for(int i=0;i<13;i++){
        float fi=float(i),a=-PI*.78+fi*PI*1.56/12.;
        vec2 target=.78*vec2(cos(a),sin(a)) + vec2(0,.08);
        vec2 middle=mix(root,target,.5)+vec2(.15*sin(fi*2.3+time*.06),.12*cos(fi+time*.05))*freedom;
        signatureChannel(c,p,root,middle,MO_GOLD,.18*drive,time-fi);
        signatureChannel(c,p,middle,target,interferencePalette(fi/13.,.06),.17*freedom*drive,time+fi);
        signatureNode(c,p,target,.035,MO_CYAN,.14*drive);
    }
}

void moAscent(inout vec3 c,vec2 p,float time,float ascent,float drive){
    for(int i=0;i<7;i++){
        float fi=float(i),y=-.78+fi*.24;
        float r=.42-.045*fi;
        float gate=abs(length((p-vec2(0,y))*vec2(1,.42))-r)-.006;
        c+=mix(MO_VIOLET,MO_GOLD,fi/6.)
            *(aaStroke(gate,.006)+glow(gate,.028)*.08)*drive;
    }
    float traveller=sdCircle(p-vec2(.12*sin(time*.1),mix(-.72,.72,ascent)),.045);
    c+=MO_WHITE*aaFill(traveller)*drive;
}

void moBodyComparison(inout vec3 c,vec2 p,float time,float reveal,float drive){
    signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,drive);
    vec2 lp=p+vec2(.58,0),rp=p-vec2(.58,0);
    float weight=sdRoundBox(lp-vec2(0,-.20),vec2(.28,.34),.10);
    c+=MO_VIOLET*(aaStroke(weight,.007)+glow(weight,.04)*.10)*drive;
    float living=signatureBoundary(rp,.42,.075,time*.12);
    c+=MO_CYAN*(aaStroke(living,.007)+glow(living,.045)*.12)*drive;
    moMirrorField(c,rp*.78,time,reveal,drive);
}

void moWeave(inout vec3 c,vec2 p,float time,float balance,float drive){
    for(int i=-5;i<=5;i++){
        float fi=float(i),x=fi*.18;
        float a=abs(p.x-x-.08*sin(p.y*5.+time*.11+fi))-.005;
        float b=abs(p.y-x*.55-.08*sin(p.x*5.-time*.09-fi))-.005;
        c+=MO_VIOLET*aaStroke(a,.005)*drive*.55;
        c+=MO_CYAN*aaStroke(b,.005)*drive*.55;
    }
    float harmony=signatureBoundary(p,.58,.035,time*.07);
    c+=MO_GOLD*(aaStroke(harmony,.006)+glow(harmony,.035)*.10)*balance;
}

vec3 renderInfinityOptics(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    SignatureTiming s=signatureTiming(u,volume,beat);
    vec3 c=moField(p,time);
    float reveal=s.disclose,change=s.transform,resolve=s.resolve;

    if(mode==0){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        moProcession(c,p+vec2(.56,0),time,reveal,s.drive*.55);
        moMirrorField(c,p-vec2(.56,0),time,reveal,s.drive*.55);
    }else if(mode==1){
        moSource(c,p,time,reveal,s.drive);
        float beyond=abs(length(p)-mix(.35,1.16,reveal))-.006;
        c+=MO_WHITE*glow(beyond,.035)*.10;
    }else if(mode==2){
        moMirrorField(c,p,time,reveal,s.drive);
        float reflex=abs(length(p)-.68)-.006;
        c+=MO_CYAN*(aaStroke(reflex,.006)+glow(reflex,.04)*.11)*resolve;
    }else if(mode==3){
        moProcession(c,p,time,reveal,s.drive);
        float hierarchy=abs(p.x)-.006;
        c+=MO_WHITE*aaStroke(hierarchy,.006)*.32;
    }else if(mode==4){
        moPolarization(c,p,time,reveal,s.drive);
        moMirrorField(c,p*.65,time,reveal,s.drive*.38);
    }else if(mode==5){
        moOverflow(c,p,time,reveal,s.drive);
        moSource(c,p-vec2(0,.68),time,.8,s.drive*.42);
    }else if(mode==6){
        vec2 q=kaleido(projectiveWarp(p,.42*reveal,time*.025),8.,time*.018);
        moMirrorField(c,q,time,reveal,s.drive);
        c+=MO_CYAN*causticField(q*.8,time)*.10;
    }else if(mode==7){
        moDiminution(c,p,time,reveal,s.drive);
        c*=1.-.28*smoothstep(-.2,.9,-p.y)*reveal;
    }else if(mode==8){
        moFreedomBranches(c,p,time,reveal,s.drive);
        moSource(c,p-vec2(0,-.64),time,reveal,s.drive*.35);
    }else if(mode==9){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        moDiminution(c,(p+vec2(.56,0))*.86,time,reveal,s.drive*.65);
        moMirrorField(c,(p-vec2(.56,0))*.82,time,reveal,s.drive*.65);
    }else if(mode==10){
        float horizon=abs(p.y+.40)-.008;
        c+=MO_VIOLET*(aaStroke(horizon,.008)+glow(horizon,.045)*.10);
        float fragments=voronoi2((p+vec2(0,.55))*4.0).y-voronoi2((p+vec2(0,.55))*4.0).x;
        c+=MO_RED*signatureContour(fragments,7.,.024)*smoothstep(-.2,-.9,p.y)*.12*reveal;
        moSource(c,p-vec2(0,.52),time,reveal,s.drive*.35);
    }else if(mode==11){
        moMirrorField(c,p,time,.65,s.drive*.5);
        float aperture=signatureWindow(p,vec2(.74,.54),.18,1.-change);
        c+=MO_RED*(aaStroke(aperture,.008)+glow(aperture,.04)*.10);
        moPolarization(c,p*.72,time,resolve,s.drive*.55);
    }else if(mode==12){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        moAscent(c,(p+vec2(.56,0))*.82,time,reveal,s.drive*.58);
        moPolarization(c,(p-vec2(.56,0))*.82,time,reveal,s.drive*.58);
    }else if(mode==13){
        moAscent(c,p,time,reveal,s.drive);
        moSource(c,p-vec2(0,.72),time,resolve,s.drive*.38);
    }else if(mode==14){
        float frame=signatureWindow(p,vec2(.72,.52),.14,reveal);
        c+=MO_CYAN*(aaStroke(frame,.007)+glow(frame,.04)*.10);
        moMirrorField(c,projectiveWarp(p,-.34*reveal,time*.02),time,reveal,s.drive);
        c+=MO_WHITE*lensFlare(p,vec2(0))*.08*resolve;
    }else if(mode==15){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        moAscent(c,p+vec2(.58,0),time,reveal,s.drive*.55);
        moMirrorField(c,p-vec2(.58,0),-time,reveal,s.drive*.55);
        signatureChannel(c,p,vec2(-.18,.52),vec2(.18,.52),MO_GOLD,.24*resolve*s.drive,time);
    }else if(mode==16){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        vec2 lp=p+vec2(.58,0),rp=p-vec2(.58,0);
        float weight=sdRoundBox(lp-vec2(0,-.12),vec2(.28,.38),.10);
        c+=MO_VIOLET*(aaStroke(weight,.007)+glow(weight,.04)*.10)*s.drive;
        float living=signatureBoundary(rp,.43,.075,time*.12);
        c+=MO_CYAN*(aaStroke(living,.007)+glow(living,.045)*.12)*s.drive;
        moMirrorField(c,rp*.72,time,reveal,s.drive*.42);
    }else if(mode==17){
        for(int i=0;i<9;i++){
            float fi=float(i),r=.14+fi*.07;
            float wave=abs(length(p)-r-.025*sin(5.*atan(p.y,p.x)+time*.18+fi))-.005;
            c+=interferencePalette(fi/9.,.08)*(aaStroke(wave,.005)+glow(wave,.025)*.06)*s.drive;
        }
        moSource(c,p,time,resolve,s.drive*.42);
    }else if(mode==18){
        moWeave(c,p,time,reveal,s.drive);
        moPolarization(c,p*.74,time,resolve,s.drive*.38);
    }else if(mode==19){
        signatureSplitComparison(c,p,0.,MO_VIOLET,MO_CYAN,s.drive);
        moProcession(c,p+vec2(.58,0),time,reveal,s.drive*.58);
        moFreedomBranches(c,p-vec2(.58,0),time,reveal,s.drive*.48);
    }else if(mode==20){
        moProcession(c,p+vec2(.44,0),time,reveal,s.drive*.50);
        moMirrorField(c,p-vec2(.44,0),time,reveal,s.drive*.50);
        float caution=abs(sdRoundBox(p,vec2(.96,.64),.10))-.006;
        c+=MO_RED*(aaStroke(caution,.006)+glow(caution,.03)*.07)*s.drive;
    }else if(mode==21){
        moProcession(c,p,time,reveal,s.drive*.72);
        moMirrorField(c,p,time,reveal,s.drive*.72);
        float v=abs(p.x)-.006,h=abs(p.y)-.006;
        c+=MO_GOLD*(aaStroke(v,.006)+aaStroke(h,.006)+glow(min(v,h),.038)*.10)*resolve;
    }else{
        moSource(c,p,time,resolve,s.drive*.55);
        moProcession(c,p,time,reveal,s.drive*.60);
        moMirrorField(c,p,time,reveal,s.drive*.60);
        moWeave(c,p*.82,time,resolve,s.drive*.30);
        float outer=signatureBoundary(p,.82,.035,time*.06);
        c+=MO_WHITE*(aaStroke(outer,.006)+glow(outer,.04)*.12)*resolve;
    }
    c*=s.enter;
    return signatureFinish(c,uv,gl_FragCoord.xy,time,.95,.14+.08*s.drive);
}

#endif
