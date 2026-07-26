#ifndef BEAUTIFY_COUNTERFACTUAL_ANATOMY_GLSL
#define BEAUTIFY_COUNTERFACTUAL_ANATOMY_GLSL

const vec3 CBA_INK=vec3(.30,.42,.41);
const vec3 CBA_CYAN=vec3(.00,.57,.69);
const vec3 CBA_DEEP=vec3(.02,.19,.31);
const vec3 CBA_GOLD=vec3(1.08,.56,.07);
const vec3 CBA_GREEN=vec3(.03,.55,.33);
const vec3 CBA_RED=vec3(.80,.06,.12);
const vec3 CBA_WHITE=vec3(.98,.99,1.0);

vec3 cbaField(vec2 p,float time){
    float wash=fbmWarp(p*.65+vec2(time*.003,0),time*.05);
    vec3 c=vec3(.010,.024,.025)+vec3(.025,.090,.075)*wash;
    float fiber=signatureContour(fbm(p*8.0+17.0),15.,.020);
    c+=vec3(.018,.030,.026)*fiber;
    c+=vec3(.025,.045,.040)*exp(-dot(p,p)*.55);
    return c;
}

float cbaBody(vec2 p,float twoHead,float phase){
    vec2 q=p;
    q.y+=.055*sin(q.x*4.2+phase);
    float trunk=sdRoundBox(q,vec2(.58,.15),.14);
    float left=sdCircle(q-vec2(-.58,0),.19);
    float right=sdCircle(q-vec2(.58,0),mix(.10,.19,twoHead));
    float form=smoothUnion(trunk,left,.14);
    form=smoothUnion(form,right,.12);
    float taper=abs(q.x)-.72;
    return max(form,taper-.08);
}

float cbaTarget(vec2 p,float phase){
    vec2 q=p;
    q.y+=.045*sin(q.x*4.8+phase);
    float shell=cbaBody(q,1.,phase);
    float lobes=min(sdCircle(q-vec2(-.66,.08),.13),sdCircle(q-vec2(.66,-.08),.13));
    return smoothUnion(shell,lobes,.08);
}

void cbaGlassBody(inout vec3 c,vec2 p,float time,float targetReveal,float drive){
    float present=cbaBody(p,0.,time*.12);
    float future=cbaTarget(p,time*.12);
    float tissue=fbmWarp(p*2.2,time*.16);
    float inside=aaFill(present);
    c=mix(c,mix(c,vec3(.72,.92,.94),.35+.18*tissue),inside*.52);
    c+=CBA_CYAN*(aaStroke(present,.008)+glow(present,.045)*.10)*drive;
    c+=CBA_DEEP*signatureContour(tissue,12.,.022)*inside*.10;
    c+=CBA_GOLD*(aaStroke(future,.006)+glow(future,.038)*.13)
        *targetReveal*drive;
}

void cbaNetwork(inout vec3 c,vec2 p,float time,float memory,float drive){
    vec2 previous=vec2(-.86,0);
    for(int i=0;i<17;i++){
        float fi=float(i),x=-.86+fi*.1075;
        vec2 n=vec2(x,.11*sin(fi*1.7+time*.13)+.035*sin(fi*4.1));
        signatureNode(c,p,n,.026,mix(CBA_CYAN,CBA_GOLD,memory),.18*drive);
        if(i>0)signatureChannel(c,p,previous,n,mix(CBA_GREEN,CBA_GOLD,memory),.18*drive,time-fi*.4);
        if(mod(fi,3.)<.5){
            vec2 branch=n+vec2(0,.18*cos(fi+time*.08));
            signatureChannel(c,p,n,branch,CBA_GREEN,.11*drive,time+fi);
            signatureNode(c,p,branch,.022,CBA_GREEN,.12*drive);
        }
        previous=n;
    }
}

void cbaVectorRule(inout vec3 c,vec2 p,float time,float targetState,float drive){
    for(int y=-4;y<=4;y++)for(int x=-7;x<=7;x++){
        vec2 id=vec2(float(x),float(y));
        vec2 n=id*vec2(.17,.16);
        vec2 toCenter=-normalize(n+vec2(.001));
        vec2 toPoles=normalize(vec2(sign(n.x)*.72,0)-n+vec2(.001));
        vec2 dir=normalize(mix(toCenter,toPoles,targetState));
        vec2 curl=.16*vec2(-dir.y,dir.x)*sin(time*.12+hash21(id)*TAU);
        vec2 end=n+(dir+curl)*.065;
        signatureChannel(c,p,n,end,mix(CBA_CYAN,CBA_GOLD,targetState),.19*drive,time-hash21(id)*TAU);
    }
}

void cbaAttractors(inout vec3 c,vec2 p,float time,float selection,float drive){
    vec2 a=vec2(-.52,-.12),b=vec2(.52,.12);
    for(int i=0;i<12;i++){
        float fi=float(i),x=-1.12+fi*.20;
        float potential=.32*cos(x*2.7)-.18*cos(x*5.4+time*.04);
        vec2 point=vec2(x,potential);
        if(i>0){
            float px=x-.20;
            float py=.32*cos(px*2.7)-.18*cos(px*5.4+time*.04);
            signatureChannel(c,p,vec2(px,py),point,CBA_DEEP,.16*drive,time-fi);
        }
    }
    signatureNode(c,p,a,.12,mix(CBA_CYAN,CBA_GOLD,1.-selection),.30*drive);
    signatureNode(c,p,b,.12,mix(CBA_GOLD,CBA_CYAN,1.-selection),.30*drive);
    float chooser=sdCircle(p-mix(a,b,selection),.045);
    c+=CBA_WHITE*aaFill(chooser)*drive;
}

void cbaCellField(inout vec3 c,vec2 p,float time,float replace,float drive){
    for(int y=-4;y<=4;y++)for(int x=-8;x<=8;x++){
        vec2 id=vec2(float(x),float(y));
        vec2 n=id*vec2(.15,.15)+(hash22(id+floor(time*.15)*replace)-.5)*.055;
        float generation=hash21(id+floor(time*.15)*replace);
        float d=length(p-n)-(.033+.012*generation);
        vec3 hue=mix(CBA_CYAN,CBA_GREEN,generation);
        c+=hue*(aaStroke(d,.004)+glow(d,.017)*.05)*drive;
    }
}

void cbaLayers(inout vec3 c,vec2 p,float time,float reveal,float drive){
    for(int i=0;i<5;i++){
        float fi=float(i),y=-.52+fi*.26;
        vec2 q=p-vec2(.05*sin(fi+time*.04),y);
        float slab=sdRoundBox(q,vec2(.82,.08),.035);
        vec3 hue=mix(CBA_DEEP,CBA_GOLD,fi/4.);
        c+=hue*(aaStroke(slab,.006)+glow(slab,.026)*.07)*drive;
        float phase=fbm(q*vec2(4.,18.)+fi*7.);
        c+=hue*signatureContour(phase,8.,.026)*aaFill(slab)*.10*reveal;
        if(i>0)signatureChannel(c,p,vec2(-.62,y-.16),vec2(.62,y),hue,.10*reveal*drive,time+fi);
    }
}

vec3 renderCounterfactualAnatomy(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    SignatureTiming s=signatureTiming(u,volume,beat);
    vec3 c=cbaField(p,time);
    float reveal=s.disclose,change=s.transform,resolve=s.resolve;

    if(mode==0){
        cbaGlassBody(c,p-vec2(-.16,.05),time,reveal,s.drive);
        float shadow=cbaTarget(p-vec2(.30,-.20),time*.12);
        c+=CBA_GOLD*glow(shadow,.065)*.10*reveal;
    }else if(mode==1){
        cbaGlassBody(c,p,time,.22+reveal*.78,s.drive);
        float plane=abs(p.x+.12*sin(time*.05))-.009;
        c+=CBA_RED*(aaStroke(plane,.009)+glow(plane,.045)*.14)*s.drive;
        for(int i=0;i<7;i++){
            float fi=float(i),a=-.9+fi*.3;
            signatureChannel(c,p,vec2(0),.72*vec2(cos(a),sin(a)),CBA_GOLD,.16*reveal*s.drive,time-fi);
        }
    }else if(mode==2){
        cbaGlassBody(c,p,time,.35*reveal,s.drive*.55);
        cbaNetwork(c,p,time,reveal,s.drive);
    }else if(mode==3){
        cbaAttractors(c,p,time,reveal,s.drive);
        float pulse=abs(p.x-mix(-.52,.52,reveal))-.007;
        c+=CBA_RED*aaStroke(pulse,.007)*.42;
    }else if(mode==4){
        cbaVectorRule(c,p,time,reveal,s.drive);
        float picture=cbaTarget(p*.82,time*.1);
        c+=CBA_GOLD*glow(picture,.055)*.06*(1.-reveal);
        float response=cbaTarget(p*.82,time*.1);
        c+=CBA_GOLD*aaStroke(response,.006)*resolve;
    }else if(mode==5){
        vec2 left=p+vec2(.62,0),right=p-vec2(.62,0);
        cbaGlassBody(c,left*.82,time,0.,s.drive*.62);
        cbaGlassBody(c,right*.82,time+2.,reveal,s.drive*.62);
        signatureChannel(c,p,vec2(-.30,0),vec2(.30,0),CBA_GOLD,.30*reveal*s.drive,time);
    }else if(mode==6){
        cbaCellField(c,p,time,0.,s.drive*.72);
        cbaNetwork(c,p,time,reveal,s.drive);
        float whole=cbaTarget(p*.72,time*.1);
        c+=CBA_GOLD*(aaStroke(whole,.006)+glow(whole,.04)*.10)*reveal;
    }else if(mode==7){
        for(int ring=0;ring<4;ring++){
            float fr=float(ring),radius=.20+fr*.18;
            float boundary=abs(length(p)-radius)-.006;
            c+=mix(CBA_GREEN,CBA_GOLD,fr/3.)*aaStroke(boundary,.006)*s.drive;
        }
        for(int i=0;i<12;i++){
            float fi=float(i),a=fi*TAU/12.+time*.02;
            vec2 n=mix(.58*vec2(cos(a),sin(a)),.22*vec2(cos(a),sin(a)),reveal);
            signatureChannel(c,p,n,vec2(0),CBA_GOLD,.16*reveal*s.drive,time-fi);
            signatureNode(c,p,n,.026,CBA_CYAN,.12*s.drive);
        }
    }else if(mode==8){
        cbaCellField(c,p,time,change,s.drive);
        float persistentForm=cbaTarget(p*.80,time*.08);
        c+=CBA_GOLD*(aaStroke(persistentForm,.006)+glow(persistentForm,.035)*.08)*s.drive;
        signatureEchoes(c,p,vec2(.58,0),vec2(.16,0),.42,.035,CBA_GREEN,.24*change);
    }else if(mode==9){
        cbaAttractors(c,p,time,reveal,s.drive);
        float sweep=abs(p.x-mix(-1.1,1.1,change))-.012;
        c+=CBA_RED*(aaStroke(sweep,.010)+glow(sweep,.045)*.10)*s.drive;
        float restored=cbaBody(p*.62,0.,time*.1);
        c+=CBA_CYAN*aaStroke(restored,.006)*resolve;
    }else if(mode==10){
        cbaGlassBody(c,p,time,reveal,s.drive);
        float control=signatureRibbon((p-vec2(0,.52))*vec2(1,.7),time*.18,.006,.12);
        c+=CBA_RED*(aaStroke(control,.006)+glow(control,.026)*.10);
        for(int i=0;i<9;i++){
            float fi=float(i),x=-.76+fi*.19;
            signatureChannel(c,p,vec2(x,.48),vec2(x*.72,.13*sin(fi)),CBA_GREEN,.13*reveal*s.drive,time-fi);
        }
    }else if(mode==11){
        cbaLayers(c,p,time,reveal,s.drive);
        float bracket=sdRoundBox(p,vec2(.95,.66),.08);
        c+=CBA_INK*aaStroke(bracket,.006)*.55;
    }else if(mode==12){
        cbaGlassBody(c,p,time,.38*reveal,s.drive*.62);
        float window=signatureWindow(p-vec2(.38,0),vec2(.40,.48),.06,reveal);
        c+=CBA_INK*(aaStroke(window,.007)+glow(window,.035)*.05);
        float beyond=cbaTarget(p-vec2(.48,0),time*.1);
        c+=CBA_GOLD*aaStroke(beyond,.006)*aaFill(window)*reveal;
        c*=1.-.15*aaFill(-window);
    }else if(mode==13){
        signatureSplitComparison(c,p,0.,CBA_GREEN,CBA_GOLD,s.drive);
        cbaNetwork(c,(p+vec2(.58,0))*.72,time,reveal,s.drive*.55);
        signatureConstellation(c,(p-vec2(.58,0))*.78,time,reveal,CBA_DEEP,.45*s.drive);
        float caution=abs(p.x)-.006;
        c+=CBA_RED*aaStroke(caution,.006)*.45;
    }else{
        cbaCellField(c,p,time,.35*change,s.drive*.35);
        cbaGlassBody(c,p-vec2(.18,0),time,resolve,s.drive);
        float future=cbaTarget(p-vec2(.42,-.16),time*.1);
        c+=CBA_GOLD*(aaStroke(future,.006)+glow(future,.045)*.11)*resolve;
        cbaNetwork(c,p*.88,time,resolve,s.drive*.55);
        float horizon=abs(p.y+.52)-.007;
        c+=CBA_INK*aaStroke(horizon,.007)*.38;
    }
    c=mix(signatureIvoryField(p,time,.64),c,s.enter);
    return signatureFinish(c,uv,gl_FragCoord.xy,time,1.04,.08+.07*s.drive);
}

#endif
