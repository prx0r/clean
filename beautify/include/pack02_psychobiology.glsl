// Pack 02: living stained-glass psychobiology.
#ifndef PACK02_PSYCHOBIOLOGY_GLSL
#define PACK02_PSYCHOBIOLOGY_GLSL

const vec3 BIO_VOID=vec3(0.022,0.009,0.040);
const vec3 BIO_WINE=vec3(0.250,0.026,0.155);
const vec3 BIO_VIOLET=vec3(0.345,0.120,0.610);
const vec3 BIO_CYAN=vec3(0.090,0.800,0.850);
const vec3 BIO_GOLD=vec3(1.000,0.650,0.195);
const vec3 BIO_GREEN=vec3(0.220,0.940,0.560);
const vec3 BIO_CRIMSON=vec3(0.950,0.110,0.260);
const vec3 BIO_PEARL=vec3(1.000,0.920,0.770);

vec3 bioBackground(vec2 uv, vec2 p, float time) {
    float warp=fbmWarp(p*1.15,time);
    float tissue=fbm(p*3.2+vec2(time*0.025,-time*0.018));
    float veins=pow(ridgedFbm(p*5.5+warp*1.4),4.0);
    vec3 col=mix(BIO_VOID,vec3(0.070,0.014,0.110),warp);
    col+=BIO_WINE*tissue*0.22;
    col+=BIO_VIOLET*veins*0.07;
    col*=0.55+0.45*vignette(uv);
    return col;
}

float bioMembrane(vec2 p, vec2 center, vec2 radii, float wobble, float time) {
    vec2 q=p-center;
    float a=atan(q.y,q.x);
    float n=sin(a*7.0+time*0.6)+0.5*sin(a*13.0-time*0.37);
    q/=radii*(1.0+wobble*n);
    return length(q)-1.0;
}

void bioCell(
    inout vec3 col, vec2 p, vec2 center, vec2 radii,
    vec3 membraneColor, float activation, float time
) {
    float d=bioMembrane(p,center,radii,0.018,time);
    float inner=aaFill(d);
    float edge=aaStroke(d,0.012);
    float halo=glow(d,0.075);
    float cytoplasm=fbmWarp((p-center)*10.0,time);
    col=mix(col,mix(BIO_WINE,membraneColor,0.28+0.22*cytoplasm),inner*0.48);
    col+=membraneColor*(edge*0.78+halo*(0.09+activation*0.13));
    float nucleus=sdCircle((p-center)/min(radii.x,radii.y),0.29+0.025*sin(time));
    col+=mix(BIO_GOLD,membraneColor,0.35)
        *(aaFill(nucleus)*0.22+glow(nucleus,0.18)*(0.18+0.25*activation));
}

void bioParticle(inout vec3 col, vec2 p, vec2 center, float size, vec3 color, float energy) {
    float d=length(p-center);
    col+=color*(exp(-(d*d)/(size*size))*energy);
    col+=BIO_PEARL*exp(-(d*d)/(size*size*0.08))*energy*0.8;
}

void bioFilament(inout vec3 col, vec2 p, vec2 a, vec2 b, vec3 color, float energy) {
    float d=sdSegment(p,a,b);
    col+=color*(exp(-(d*d)/0.00009)*0.28+exp(-(d*d)/0.0018)*0.07)*energy;
}

float bioRosette(vec2 p, float petals, float radius, float fold) {
    float a=atan(p.y,p.x);
    float r=length(p);
    float boundary=radius*(1.0+fold*cos(a*petals));
    return r-boundary;
}

void bioField(inout vec3 col, vec2 p, vec2 center, float radius, vec3 color, float energy, float time) {
    vec2 q=p-center;
    float e=length(q/vec2(1.0,0.62));
    float phase=e*42.0-time*1.1;
    float rings=pow(0.5+0.5*cos(phase),14.0);
    float envelope=exp(-e*e/(radius*radius));
    col+=color*rings*envelope*energy*0.42;
    col+=color*envelope*energy*0.055;
}

vec3 bioFinish(vec3 col, vec2 uv, vec2 fragCoord, float time) {
    col*=0.82+0.18*vignette(uv);
    col+=grain(fragCoord,time)*0.018;
    return filmic(col);
}

#endif
