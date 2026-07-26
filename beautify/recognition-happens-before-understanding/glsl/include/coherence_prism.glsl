#ifndef BEAUTIFY_COHERENCE_PRISM_GLSL
#define BEAUTIFY_COHERENCE_PRISM_GLSL

const vec3 RHU_BLACK=vec3(0.008,0.013,0.028);
const vec3 RHU_BLUE=vec3(0.035,0.34,1.08);
const vec3 RHU_CYAN=vec3(0.02,0.94,1.05);
const vec3 RHU_GOLD=vec3(1.35,0.62,0.08);
const vec3 RHU_CORAL=vec3(1.18,0.08,0.20);
const vec3 RHU_VIOLET=vec3(0.54,0.18,1.12);
const vec3 RHU_WHITE=vec3(0.92,0.97,1.06);

vec3 rhuField(vec2 p,float time){
    vec3 c=signatureNightField(p,time,vec3(.08,.12,.31));
    float interference=waveInterference(p*.62,time*.18);
    c+=mix(RHU_BLUE,RHU_VIOLET,.5+.5*interference)*.025;
    return c;
}

float rhuInvariant(vec2 p,float phase,float clarity){
    vec2 q=projectiveWarp(p,.22*(1.-clarity),phase*.04);
    float a=atan(q.y,q.x),r=length(q);
    float body=r-(.46+.055*sin(5.*a+phase)+.025*sin(11.*a-phase*.7));
    float inner=abs(length(q)-(.22+.025*sin(3.*a-phase)))-.012;
    float axis=abs(q.x+.05*sin(q.y*7.+phase))-.009;
    return min(body,min(inner+.035*(1.-clarity),axis+.08));
}

void rhuWhole(inout vec3 c,vec2 p,float time,float clarity,float drive){
    float d=rhuInvariant(p,time*.14,clarity);
    float phase=fbmWarp(p*1.7,time*.12);
    float inside=aaFill(d);
    c+=mix(RHU_BLUE,RHU_GOLD,clarity)
        *(aaStroke(d,.007)+glow(d,.045)*(.10+.14*clarity))*drive;
    c+=interferencePalette(phase+clarity*.12,.05)
        *signatureContour(phase,11.,.024)*inside*(.07+.08*clarity);
    for(int i=0;i<11;i++){
        float fi=float(i),a=fi*2.399+time*.025;
        vec2 n=(.10+.031*fi)*vec2(cos(a),sin(a));
        signatureNode(c,p,n,.026,mix(RHU_CYAN,RHU_WHITE,clarity),.16*drive);
    }
}

void rhuPrism(inout vec3 c,vec2 p,float time,float separation,float drive){
    for(int i=0;i<7;i++){
        float fi=float(i),x=-.78+fi*.26;
        vec2 q=p-vec2(x,.10*sin(fi*1.7+time*.08));
        float shard=sdRegularPolygon(q*rot(fi*.31),.12+.025*mod(fi,3.),3.+mod(fi,4.),fi*.2);
        vec3 hue=interferencePalette(fi/7.+time*.005,.04);
        c+=hue*(aaStroke(shard,.006)+glow(shard,.027)*.10)*drive;
        if(i<6){
            vec2 a=vec2(x+.10,.02*sin(fi+time*.08));
            vec2 b=vec2(x+.16,.02*sin(fi+1.+time*.08));
            signatureChannel(c,p,a,b,RHU_WHITE,.13*(1.-separation)*drive,time-fi);
        }
    }
}

void rhuAnalysisPanels(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int i=0;i<8;i++){
        float fi=float(i),a=fi*TAU/8.;
        vec2 n=mix(vec2(0),(.54+.05*mod(fi,2.))*vec2(cos(a),sin(a)),reveal);
        vec2 q=(p-n)*rot(-a*.5);
        float panel=sdRoundBox(q,vec2(.13,.10),.025);
        float metric=abs(q.y-.035*sin(q.x*24.+time*.3+fi))-.005;
        vec3 hue=interferencePalette(fi/8.,.08);
        c+=hue*(aaStroke(panel,.006)+aaStroke(metric,.004)+glow(panel,.025)*.06)*drive;
        signatureChannel(c,p,n*.72,n,RHU_WHITE,.10*reveal*drive,time+fi);
    }
}

void rhuLivingWave(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int i=0;i<7;i++){
        float fi=float(i);
        float x=-1.08+fi*.36;
        float y=.20*sin(fi*.84+time*.18);
        vec2 n=vec2(x,y);
        signatureNode(c,p,n,.045,mix(RHU_CYAN,RHU_GOLD,reveal),.27*drive);
        if(i>0){
            float px=-1.08+(fi-1.)*.36;
            float py=.20*sin((fi-1.)*.84+time*.18);
            signatureChannel(c,p,vec2(px,py),n,RHU_CYAN,.30*drive,time*1.2-fi);
        }
    }
    float whole=signatureRibbon(p,time*.18,.008,.18);
    c+=RHU_GOLD*(aaStroke(whole,.006)+glow(whole,.032)*.11)*reveal*drive;
}

void rhuAtmosphere(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int i=0;i<6;i++){
        float fi=float(i),a=fi*TAU/6.+time*.012;
        vec2 source=.52*vec2(cos(a),sin(a));
        float beam=softBeam(p,source,-source,.24+.06*fi,.62);
        vec3 hue=interferencePalette(fi/6.,.11);
        c+=hue*beam*.16*drive;
    }
    float atmosphere=fbmWarp(p*1.05,time*.18);
    c+=mix(RHU_VIOLET,RHU_GOLD,reveal)*signatureContour(atmosphere,9.,.026)*.08*reveal;
}

void rhuCompletion(inout vec3 c,vec2 p,float time,float correction,float drive){
    float a=atan(p.y,p.x),r=length(p);
    float missing=smoothstep(.26,.42,abs(a-PI*.35));
    float ring=abs(r-.48-.035*sin(7.*a+time*.12))-.007;
    c+=RHU_CYAN*aaStroke(ring,.007)*(1.-missing);
    c+=RHU_GOLD*(aaStroke(ring,.007)+glow(ring,.04)*.18)
        *missing*correction*drive;
    for(int i=0;i<8;i++){
        float fi=float(i),ang=fi*TAU/8.;
        vec2 n=.48*vec2(cos(ang),sin(ang));
        signatureNode(c,p,n,.035,mix(RHU_BLUE,RHU_WHITE,correction),.18*drive);
    }
}

void rhuLanguage(inout vec3 c,vec2 p,float time,float capture,float drive){
    float whole=signatureRibbon(p,time*.15,.008,.26);
    c+=RHU_CYAN*(aaStroke(whole,.006)+glow(whole,.03)*.14)*(1.-capture)*drive;
    for(int i=0;i<9;i++){
        float fi=float(i),x=-1.02+fi*.255;
        vec2 q=p-vec2(x,.02*sin(fi+time*.1));
        float token=sdRegularPolygon(q,.075,3.+mod(fi,5.),fi*.37);
        c+=mix(RHU_VIOLET,RHU_GOLD,fi/8.)
            *(aaStroke(token,.005)+glow(token,.021)*.07)*capture*drive;
    }
}

void rhuCorrection(inout vec3 c,vec2 p,float time,float correction,float drive){
    vec2 top=vec2(0,.74),bottom=vec2(0,-.74);
    for(int i=0;i<9;i++){
        float fi=float(i),x=-.84+fi*.21;
        vec2 evidence=vec2(x,-.42+.12*sin(fi*1.8+time*.16));
        vec2 expectation=vec2(x*.74,.40+.08*cos(fi+time*.11));
        signatureChannel(c,p,top,expectation,RHU_GOLD,.18*drive,time-fi);
        signatureChannel(c,p,bottom,evidence,RHU_CYAN,.18*drive,-time+fi);
        vec2 fit=mix(expectation,evidence,.5+.5*correction);
        signatureNode(c,p,fit,.038,mix(RHU_CORAL,RHU_WHITE,correction),.20*drive);
    }
    float seam=abs(p.y)-.006;
    c+=mix(RHU_CORAL,RHU_WHITE,correction)*aaStroke(seam,.006)*.48;
}

vec3 renderCoherencePrism(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    SignatureTiming s=signatureTiming(u,volume,beat);
    vec3 c=rhuField(p,time);
    float reveal=s.disclose,change=s.transform,resolve=s.resolve;

    if(mode==0){
        vec2 q=(p-vec2(.48,-.08))*.88+.05*vec2(sin(time*.15),cos(time*.11));
        rhuWhole(c,q,time,reveal*.45,s.drive);
        float haze=fbmWarp(q*.8,time*.2);
        c=mix(c,c+RHU_WHITE*.12*haze,.55*(1.-reveal));
    }else if(mode==1){
        for(int side=-1;side<=1;side+=2){
            float eye=sdVesica(p-vec2(float(side)*.18,.09),.13,.08);
            c+=RHU_CYAN*(aaStroke(eye,.006)+glow(eye,.036)*.15)*s.drive;
        }
        float shell=abs(sdEllipse(p,vec2(.35,.49)))-.008;
        float axis=abs(p.x+.025*sin(p.y*8.+time*.18))-.006;
        c+=RHU_GOLD*(aaStroke(shell,.008)+glow(shell,.07)*.22)*reveal*s.drive;
        c+=RHU_VIOLET*aaStroke(axis,.006)*reveal*.55;
        c+=RHU_WHITE*lensFlare(p,vec2(0,.04))*.10*(.3+.7*s.beat);
    }else if(mode==2){
        signatureAgents(c,p,time,reveal,vec2(0),RHU_BLUE,RHU_GOLD,s.drive);
        float whole=rhuInvariant(p,time*.1,reveal);
        c+=RHU_WHITE*aaStroke(whole,.006)*reveal;
    }else if(mode==3){
        rhuWhole(c,p,time,.30,s.drive*(1.-.55*change));
        rhuAnalysisPanels(c,p,time,change,s.drive);
    }else if(mode==4){
        float wave=abs(length(p)-mix(.04,1.18,reveal))-.012;
        c+=RHU_GOLD*(aaStroke(wave,.010)+glow(wave,.07)*.26)*s.drive;
        rhuWhole(c,p*.72,time,reveal,s.drive);
        c+=RHU_WHITE*lensFlare(p,vec2(0))*.14*(.35+.65*s.beat);
    }else if(mode==5){
        vec2 left=p+vec2(.52,0),right=p-vec2(.52,0);
        rhuWhole(c,left*.88,time,.35,s.drive*.55);
        rhuWhole(c,right*.88,time+9.,reveal,s.drive*.55);
        signatureChannel(c,p,vec2(-.30,0),vec2(.30,0),RHU_GOLD,.42*reveal*s.drive,time);
    }else if(mode==6){
        rhuLivingWave(c,p,time,reveal,s.drive);
    }else if(mode==7){
        rhuAtmosphere(c,p,time,reveal,s.drive);
        rhuWhole(c,p*.82,time,reveal*.6,s.drive*.46);
    }else if(mode==8){
        for(int lane=-1;lane<=1;lane++){
            float fy=float(lane)*.42;
            for(int i=0;i<6;i++){
                float fi=float(i),x=-.95+fi*.38;
                vec2 n=vec2(x,fy+.06*sin(fi*1.7+time*.1+float(lane)));
                signatureNode(c,p,n,.032,mix(RHU_BLUE,RHU_GOLD,reveal),.18*s.drive);
                if(i>0) signatureChannel(c,p,vec2(x-.38,fy),n,RHU_CYAN,.14*reveal*s.drive,time-fi);
            }
        }
        float insight=sdRegularPolygon(p-vec2(.82,.42),.11,5.,time*.04);
        c+=RHU_WHITE*(aaStroke(insight,.006)+glow(insight,.04)*.18)*reveal;
    }else if(mode==9){
        rhuCompletion(c,p,time,reveal,s.drive);
    }else if(mode==10){
        rhuWhole(c,p+vec2(.16,0),time,.74,s.drive*.72);
        rhuWhole(c,p-vec2(.16,0),time+2.7,.38,s.drive*.58);
        float mismatch=abs(p.x)-.008;
        c+=RHU_CORAL*(aaStroke(mismatch,.008)+glow(mismatch,.04)*.18)*change;
    }else if(mode==11){
        float lens=signatureLens(p,vec2(.26,-.04),.39,-.42*change);
        c+=RHU_GOLD*(aaStroke(lens,.007)+glow(lens,.045)*.13);
        signatureAgents(c,p,time,.16,vec2(.26,-.04),RHU_BLUE,RHU_CORAL,s.drive);
        float forced=rhuInvariant((p-vec2(.26,-.04))*.85,time*.1,1.);
        c+=RHU_CORAL*aaStroke(forced,.006)*change;
    }else if(mode==12){
        rhuCorrection(c,p,time,reveal,s.drive);
        rhuWhole(c,p*.67,time,resolve,s.drive*.42);
    }else if(mode==13){
        rhuLanguage(c,p,time,reveal,s.drive);
        float remainder=rhuInvariant(p*.78,time*.1,.7);
        c+=RHU_WHITE*glow(remainder,.055)*.08;
    }else if(mode==14){
        for(int i=0;i<8;i++){
            float fi=float(i),x=-.95+fi*.27;
            float activation=smoothstep(fi/9.,fi/9.+.18,reveal);
            signatureNode(c,p,vec2(x,.24*sin(fi*.74)),.045,RHU_CYAN,.23*activation*s.drive);
            if(i>0)signatureChannel(c,p,vec2(x-.27,.24*sin((fi-1.)*.74)),vec2(x,.24*sin(fi*.74)),RHU_BLUE,.17*activation*s.drive,time-fi);
        }
        float burst=abs(length(p)-.55)-.009;
        c+=RHU_GOLD*(aaStroke(burst,.008)+glow(burst,.065)*.18)*resolve*s.drive;
    }else if(mode==15){
        rhuWhole(c,p,time,.85,s.drive*(1.-.7*change));
        rhuPrism(c,p,time,change,s.drive);
        for(int i=-4;i<=4;i++){
            float x=float(i)*.22+.04*sin(time*.1+float(i));
            float cut=abs(p.x-x)-.004;
            c+=RHU_CORAL*aaStroke(cut,.004)*change*.55;
        }
    }else if(mode==16){
        rhuAnalysisPanels(c,p,time,1.-change,s.drive*.5);
        rhuWhole(c,p,time,change,s.drive);
        float scar=abs(signatureRibbon(p*rot(.7),time*.11,.004,.08));
        c+=RHU_CORAL*aaStroke(scar,.004)*resolve*.55;
    }else if(mode==17){
        signatureSplitComparison(c,p,0.,RHU_BLUE,RHU_GOLD,s.drive);
        for(int i=0;i<6;i++){
            float fi=float(i),y=-.60+fi*.24;
            float bin=sdRoundBox(p-vec2(-.55,y),vec2(.24,.07),.018);
            c+=RHU_BLUE*aaStroke(bin,.005);
        }
        rhuWhole(c,(p-vec2(.55,0))*.86,time,reveal,s.drive*.62);
        float boundary=abs(p.x)-.006;
        c+=RHU_WHITE*aaStroke(boundary,.006)*resolve;
    }else if(mode==18){
        float aperture=signatureWindow(p,vec2(.58,.43),.12,reveal);
        c+=RHU_WHITE*(aaStroke(aperture,.007)+glow(aperture,.04)*.10);
        rhuWhole(c,p,time,reveal,s.drive);
        rhuAnalysisPanels(c,p*.92,time,resolve*.45,s.drive*.34);
    }else{
        signatureAgents(c,p,time,reveal,vec2(0),RHU_BLUE,RHU_GOLD,s.drive*.58);
        rhuWhole(c,p,time,resolve,s.drive);
        rhuPrism(c,p,time,1.-resolve,s.drive*.32);
        float outer=signatureBoundary(p,.72,.025,time*.08);
        c+=RHU_WHITE*(aaStroke(outer,.006)+glow(outer,.04)*.13)*resolve;
        float pulse=abs(length(p)-mix(.18,.88,fract(time*.12)))-.006;
        c+=RHU_CYAN*glow(pulse,.025)*.07*(.4+.6*s.beat);
    }
    c*=s.enter;
    return signatureFinish(c,uv,gl_FragCoord.xy,time,.95,.15+.10*s.drive);
}

#endif
