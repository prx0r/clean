#ifndef BEAUTIFY_TEMPORAL_EXPOSURE_GLSL
#define BEAUTIFY_TEMPORAL_EXPOSURE_GLSL

const vec3 TPF_BLACK=vec3(.004,.008,.022);
const vec3 TPF_BLUE=vec3(.025,.24,1.08);
const vec3 TPF_CYAN=vec3(.00,.92,1.05);
const vec3 TPF_GOLD=vec3(1.38,.58,.07);
const vec3 TPF_MAGENTA=vec3(1.05,.04,.38);
const vec3 TPF_GREEN=vec3(.02,.78,.48);
const vec3 TPF_WHITE=vec3(.94,.98,1.08);

vec3 tpfField(vec2 p,float time){
    vec3 c=signatureNightField(p,time,vec3(.06,.12,.34));
    float strata=waveInterference(p*.38,time*.08);
    c+=mix(TPF_BLUE,TPF_GOLD,.5+.5*strata)*.020;
    float dust=pow(noise21(gl_FragCoord.xy*.33+floor(time*3.)),22.);
    c+=TPF_WHITE*dust*.12;
    return c;
}

void tpfSimultaneity(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int layer=0;layer<9;layer++){
        float fl=float(layer),z=(fl-4.)*.13;
        vec2 q=p*rot(.08*fl+time*.006*(fl-4.));
        float path=signatureRibbon(q-vec2(z*.55,z*.22),time*.07+fl,.006,.14);
        vec3 hue=interferencePalette(fl/9.,.07);
        c+=hue*(aaStroke(path,.005)+glow(path,.025)*.07)*drive*(.45+.55*reveal);
    }
}

void tpfTimeline(inout vec3 c,vec2 p,float time,float sequence,float drive){
    float rail=abs(p.y)-.006;
    c+=TPF_CYAN*(aaStroke(rail,.006)+glow(rail,.028)*.10)*drive;
    for(int i=0;i<13;i++){
        float fi=float(i),x=-1.08+fi*.18;
        float activation=smoothstep(fi/14.,fi/14.+.12,sequence);
        vec2 n=vec2(x,.055*sin(fi*1.7+time*.10));
        signatureNode(c,p,n,.033,mix(TPF_BLUE,TPF_GOLD,activation),.18*drive);
        if(i>0)signatureChannel(c,p,vec2(x-.18,0),n,TPF_CYAN,.12*activation*drive,time-fi);
    }
}

void tpfShutter(inout vec3 c,vec2 p,float time,float narrow,float drive){
    float position=.55*sin(time*.045);
    float width=mix(.88,.055,narrow);
    float mask=signatureShutter(p,position,width,.025);
    c*=.20+.80*mask;
    float left=abs(p.x-position+width)-.006;
    float right=abs(p.x-position-width)-.006;
    c+=TPF_CYAN*(aaStroke(left,.006)+aaStroke(right,.006)+glow(min(left,right),.035)*.10)*drive;
}

void tpfPast(inout vec3 c,vec2 p,float time,float memory,float drive){
    vec2 current=vec2(.70,.12*sin(time*.12));
    signatureEchoes(c,p,current,vec2(.22,.04),.42,.052,TPF_GOLD,.58*drive);
    signatureNode(c,p,current,.065,TPF_CYAN,.38*drive);
    for(int i=0;i<8;i++){
        float fi=float(i),x=.48-fi*.23;
        float uncertain=memory*.035*fi*sin(fi*2.1+time*.08);
        signatureNode(c,p,vec2(x,uncertain),.025,mix(TPF_BLUE,TPF_GOLD,memory),.15*drive*exp(-fi*.22));
    }
}

void tpfFuture(inout vec3 c,vec2 p,float time,float choice,float drive){
    vec2 root=vec2(-.82,0);
    for(int i=0;i<15;i++){
        float fi=float(i),a=-1.0+fi*2./14.;
        vec2 target=vec2(.88,.62*sin(a*1.8)+.10*sin(fi*3.));
        vec2 middle=vec2(.05,.30*sin(a)+.12*cos(fi+time*.04));
        signatureChannel(c,p,root,middle,TPF_CYAN,.12*drive,time-fi);
        signatureChannel(c,p,middle,target,mix(TPF_BLUE,TPF_GOLD,choice),.12*drive*(.4+.6*choice),time+fi);
    }
    signatureNode(c,p,root,.065,TPF_WHITE,.28*drive);
}

void tpfElasticTime(inout vec3 c,vec2 p,float time,float dilation,float drive){
    float phase=p.x*mix(16.,3.2,dilation)+time*.25;
    float curve=abs(p.y-.24*sin(phase)-.08*sin(phase*2.7))-.007;
    c+=mix(TPF_CYAN,TPF_MAGENTA,dilation)
        *(aaStroke(curve,.007)+glow(curve,.032)*.12)*drive;
    for(int i=0;i<11;i++){
        float fi=float(i),x=-1.+fi*.2;
        float spacing=mix(x,sign(x)*pow(abs(x),.55),dilation);
        signatureNode(c,p,vec2(spacing,.24*sin(spacing*mix(16.,3.2,dilation)+time*.25)),.030,TPF_GOLD,.15*drive);
    }
}

void tpfMemoryBraid(inout vec3 c,vec2 p,float time,float bind,float drive){
    for(int strand=0;strand<4;strand++){
        float fs=float(strand);
        vec2 previous=vec2(-1.,.18*sin(-3.+fs*1.4));
        for(int i=1;i<28;i++){
            float fi=float(i)/27.,x=-1.+fi*2.;
            float y=.20*sin(x*3.+fs*1.45+time*.08)+.07*sin(x*9.-time*.05+fs);
            vec2 next=vec2(x,y);
            signatureChannel(c,p,previous,next,interferencePalette(fs/4.,.05),.12*drive,time-fi*9.);
            previous=next;
        }
    }
    float owner=signatureBoundary(p,.62,.035,time*.07);
    c+=TPF_GOLD*(aaStroke(owner,.006)+glow(owner,.035)*.09)*bind;
}

void tpfTenses(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int lane=-1;lane<=1;lane++){
        float fl=float(lane),y=fl*.38;
        float hueIndex=(fl+1.)*.5;
        vec3 hue=mix(TPF_BLUE,TPF_GOLD,hueIndex);
        for(int i=0;i<8;i++){
            float fi=float(i),x=-.90+fi*.26;
            float token=sdRegularPolygon(p-vec2(x,y),.055,3.+mod(fi+fl+5.,5.),fi*.3);
            c+=hue*(aaStroke(token,.005)+glow(token,.020)*.06)*drive;
            if(i>0)signatureChannel(c,p,vec2(x-.26,y),vec2(x,y),hue,.10*reveal*drive,time-fi);
        }
    }
}

void tpfGapField(inout vec3 c,vec2 p,float time,float gap,float drive){
    for(int i=-9;i<=9;i++){
        float fi=float(i),x=fi*.12;
        float pulse=exp(-pow((p.x-x)*28.,2.))*exp(-p.y*p.y*14.);
        float silence=1.-smoothstep(.12,.45,gap)*exp(-fi*fi*.12);
        c+=mix(TPF_BLUE,TPF_WHITE,gap)*pulse*silence*.34*drive;
    }
    float open=abs(p.x)-mix(.006,.24,gap);
    c+=TPF_GOLD*glow(open,.035)*.10*gap;
}

vec3 renderTemporalExposure(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    SignatureTiming s=signatureTiming(u,volume,beat);
    vec3 c=tpfField(p,time);
    float reveal=s.disclose,change=s.transform,resolve=s.resolve;

    if(mode==0){
        tpfSimultaneity(c,p,time,reveal,s.drive);
        float whole=signatureBoundary(p,.82,.025,time*.05);
        c+=TPF_GOLD*aaStroke(whole,.006)*resolve;
    }else if(mode==1){
        tpfSimultaneity(c,p,time,.6,s.drive);
        tpfShutter(c,p,time,reveal,s.drive);
    }else if(mode==2){
        tpfSimultaneity(c,p,time,.5,s.drive*(1.-.65*change));
        tpfTimeline(c,p,time,reveal,s.drive);
        tpfShutter(c,p,time,change,s.drive*.65);
    }else if(mode==3){
        tpfTimeline(c,p,time,.72,s.drive*.45);
        float position=.62*sin(time*.045);
        float slice=abs(p.x-position)-.012;
        c+=TPF_WHITE*(aaStroke(slice,.010)+glow(slice,.065)*.26)*s.drive;
        c*=.30+.70*signatureShutter(p,position,mix(.42,.04,reveal),.035);
    }else if(mode==4){
        tpfPast(c,p,time,reveal,s.drive);
        float boundary=abs(p.x-.70)-.006;
        c+=TPF_WHITE*aaStroke(boundary,.006)*.45;
    }else if(mode==5){
        tpfFuture(c,p,time,reveal,s.drive);
        float open=abs(p.x-.82)-.006;
        c+=TPF_GOLD*glow(open,.05)*.08*reveal;
    }else if(mode==6){
        tpfElasticTime(c,p,time,reveal,s.drive);
        float attractor=glowPoint(p,vec2(.82,.32),.20);
        c+=TPF_MAGENTA*attractor*.24*reveal*s.drive;
    }else if(mode==7){
        tpfFuture(c,p,time,.25,s.drive*.55);
        vec2 threat=vec2(.72,.24);
        signatureNode(c,p,threat,.20,TPF_MAGENTA,.42*reveal*s.drive);
        for(int i=0;i<9;i++){
            float fi=float(i),a=fi*TAU/9.;
            signatureChannel(c,p,.82*vec2(cos(a),sin(a)),threat,TPF_MAGENTA,.13*reveal*s.drive,time-fi);
        }
    }else if(mode==8){
        tpfElasticTime(c,p,time,1.,s.drive*.55);
        for(int i=0;i<5;i++){
            float fi=float(i),x=-.82+fi*.41;
            float slab=sdRoundBox(p-vec2(x,0),vec2(.12,.36),.06);
            c+=TPF_BLUE*aaStroke(slab,.006)*.35;
        }
        c*=.65+.35*(1.-reveal);
    }else if(mode==9){
        tpfElasticTime(c,p,time,0.,s.drive);
        float tunnel=softBeam(p,vec2(-1.,0),vec2(1,0),.11,.22);
        c+=TPF_GREEN*tunnel*.24*reveal*s.drive;
    }else if(mode==10){
        tpfMemoryBraid(c,p,time,reveal,s.drive);
        tpfPast(c,p*.78,time,reveal,s.drive*.28);
    }else if(mode==11){
        tpfTenses(c,p,time,reveal,s.drive);
        float seam=abs(p.x)-.006;
        c+=TPF_WHITE*aaStroke(seam,.006)*resolve;
    }else if(mode==12){
        signatureSplitComparison(c,p,0.,TPF_BLUE,TPF_GOLD,s.drive);
        vec2 gridPoint=(p+vec2(.58,0))*.82;
        vec2 gridCell=abs(fract(gridPoint*5.)-.5);
        float grid=1.-smoothstep(.025,.045,min(gridCell.x,gridCell.y));
        c+=TPF_BLUE*grid*.16;
        tpfElasticTime(c,(p-vec2(.58,0))*.82,time,reveal,s.drive*.62);
    }else if(mode==13){
        tpfSimultaneity(c,p,time,.6,s.drive*.42);
        float window=signatureWindow(p,vec2(.84,.56),.16,1.-change);
        c*=.22+.78*aaFill(window);
        c+=TPF_MAGENTA*(aaStroke(window,.008)+glow(window,.04)*.10);
        tpfTimeline(c,p*.72,time,reveal,s.drive*.55);
    }else if(mode==14){
        tpfTimeline(c,p,time,reveal,s.drive);
        for(int i=0;i<7;i++){
            float fi=float(i),x=-.72+fi*.24;
            float gate=abs(p.x-x)-.005;
            c+=TPF_GOLD*aaStroke(gate,.005)*smoothstep(fi/8.,fi/8.+.12,reveal)*.42;
        }
    }else if(mode==15){
        tpfSimultaneity(c,p,time,reveal,s.drive);
        float timeline=abs(p.y)-.006;
        c+=TPF_CYAN*aaStroke(timeline,.006)*(1.-reveal);
        float outer=signatureBoundary(p,.78,.03,time*.06);
        c+=TPF_WHITE*aaStroke(outer,.006)*resolve;
    }else if(mode==16){
        tpfSimultaneity(c,p,time,.45,s.drive*.45);
        float wave=abs(length(p)-mix(.03,1.10,reveal))-.010;
        c+=TPF_GOLD*(aaStroke(wave,.009)+glow(wave,.065)*.24)*s.drive;
        c+=TPF_WHITE*lensFlare(p,vec2(0))*.10*(.35+.65*s.beat);
    }else if(mode==17){
        for(int voice=0;voice<5;voice++){
            float fv=float(voice),y=(fv-2.)*.17;
            float phrase=signatureRibbon(p-vec2(0,y),time*.16+fv,.005,.10);
            c+=interferencePalette(fv/5.,.06)*(aaStroke(phrase,.005)+glow(phrase,.025)*.07)*s.drive;
        }
        float chord=abs(p.x-mix(-.82,.82,reveal))-.008;
        c+=TPF_GOLD*glow(chord,.04)*.16*resolve;
    }else if(mode==18){
        tpfTimeline(c,p,time,reveal,s.drive*.62);
        float terminal=abs(p.x-.72)-.010;
        c+=TPF_WHITE*(aaStroke(terminal,.009)+glow(terminal,.055)*.16)*s.drive;
        c*=1.-.55*smoothstep(.72,1.05,p.x)*reveal;
    }else if(mode==19){
        tpfGapField(c,p,time,reveal,s.drive);
        float observer=signatureBoundary(p,.72,.02,time*.04);
        c+=TPF_CYAN*aaStroke(observer,.006)*resolve;
    }else if(mode==20){
        tpfShutter(c,p,time,1.-reveal,s.drive*.65);
        tpfSimultaneity(c,p,time,reveal,s.drive);
        float lens=signatureLens(p,vec2(0),mix(.18,.82,reveal),-.22*reveal);
        c+=TPF_GOLD*(aaStroke(lens,.006)+glow(lens,.04)*.11)*resolve;
    }else if(mode==21){
        signatureSplitComparison(c,p,0.,TPF_BLUE,TPF_GREEN,s.drive);
        tpfTimeline(c,(p+vec2(.58,0))*.80,time,reveal,s.drive*.58);
        tpfMemoryBraid(c,(p-vec2(.58,0))*.78,time,reveal,s.drive*.45);
    }else if(mode==22){
        tpfTimeline(c,p,time,.72,s.drive*.52);
        float frame=sdRoundBox(p,vec2(.92,.62),.10);
        c+=TPF_MAGENTA*(aaStroke(frame,.006)+glow(frame,.03)*.06);
        tpfSimultaneity(c,p,time,.35,s.drive*.28);
    }else{
        tpfSimultaneity(c,p,time,reveal,s.drive*.72);
        tpfTimeline(c,p,time,1.-reveal*.45,s.drive*.55);
        tpfPast(c,p*.78,time,resolve,s.drive*.32);
        float outer=signatureBoundary(p,.84,.025,time*.05);
        c+=TPF_GOLD*(aaStroke(outer,.006)+glow(outer,.04)*.12)*resolve;
        float slit=abs(p.x-.52*sin(time*.045))-.007;
        c+=TPF_CYAN*aaStroke(slit,.007)*(1.-resolve)*.55;
    }
    c*=s.enter;
    return signatureFinish(c,uv,gl_FragCoord.xy,time,.95,.13+.08*s.drive);
}

#endif
