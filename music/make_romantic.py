"""Original, royalty-free Bollywood-style romantic loop: bansuri melody, sitar plucks, strings, keherwa tabla. 76 BPM, A minor / C. -> romantic.m4a"""
import numpy as np, wave, os, subprocess
SR=44100; BPM=76; Q=60/BPM; E=Q/2
BARS=16; LOOP=int(SR*Q*4*BARS); L=LOOP+SR*3
out=np.zeros((L,2)); rng=np.random.default_rng(3)
N={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def hz(n): return 440*2**((N[n[:-1]]+12*(int(n[-1])+1)-69)/12)
def add(s,t0,pan=0.,g=1.):
    i=int(t0*SR); s=s[:max(0,L-i)]; out[i:i+len(s),0]+=s*g*(1-pan); out[i:i+len(s),1]+=s*g*(1+pan)
def flute(f,d):
    t=np.arange(int(SR*d))/SR; vib=1+.006*np.sin(2*np.pi*5.2*t)*np.minimum(1,t/.35)
    ph=2*np.pi*np.cumsum(f*vib)/SR
    s=np.sin(ph)+.18*np.sin(2*ph)+.06*np.sin(3*ph)
    br=rng.standard_normal(len(t)); br=np.convolve(br,np.ones(30)/30,'same')*.25
    env=np.minimum(1,t/.09)*np.minimum(1,(d-t)/.12).clip(0); return (s+br*np.sin(ph))*env
def sitar(f,d=2.2):
    t=np.arange(int(SR*d))/SR; fm=f*(1+.004*np.exp(-t*6))
    ph=2*np.pi*np.cumsum(fm)/SR; s=sum((1/k)*np.sin(k*ph)*np.exp(-t*(2+k*.9)) for k in range(1,9))
    buzz=np.tanh(3*s)*.35; jor=.12*np.sin(2*np.pi*f*1.5*t)*np.exp(-t*1.5)
    return (s+buzz+jor)*np.minimum(1,t*600)
def strings(fs,d):
    t=np.arange(int(SR*d))/SR; s=0
    for f in fs:
        for det in (-.004,0,.004): s=s+np.sin(2*np.pi*f*(1+det)*t+rng.random()*6)
    return s/len(fs)/3*np.minimum(1,t/.8)*np.minimum(1,(d-t)/.8).clip(0)
def bayan(g=1):
    t=np.arange(int(SR*.6))/SR; f=70+45*np.exp(-t*9); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5)*g
def dayan(f=520,ring=1.,g=1):
    t=np.arange(int(SR*.5))/SR; s=np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2.01*t)+.3*np.sin(2*np.pi*f*3.02*t)
    n=rng.standard_normal(len(t))*np.exp(-t*90)*.6
    return (s*np.exp(-t*(6/ring))+n)*g
def ka(g=1):
    n=rng.standard_normal(int(SR*.08)); return np.diff(n,prepend=0)*np.exp(-np.arange(len(n))/SR*80)*g
# chords: Am F C G | Am F G Em  (vi IV I V romantic)
CH=[("A2","C3","E3"),("F2","A2","C3"),("C3","E3","G3"),("G2","B2","D3"),("A2","C3","E3"),("F2","A2","C3"),("G2","B2","D3"),("E2","G2","B2")]
# melody per bar: (note, beats)
M=[[("E5",1.5),("D5",.5),("C5",1),("D5",1)],[("E5",2),("A5",1),("G5",1)],[("G5",1.5),("E5",.5),("D5",1),("C5",1)],[("D5",3),("-",1)],
   [("C5",.5),("D5",.5),("E5",1),("G5",1),("A5",1)],[("A5",1.5),("G5",.5),("F5",1),("E5",1)],[("D5",1),("E5",1),("G5",1),("B4",1)],[("A4",3),("-",1)]]
MEL=M+[[(n,b) for n,b in bar] for bar in M]
for bar in range(BARS):
    tb=bar*4*Q; ch=CH[bar%8]; sec=bar//8
    add(strings([hz(n)*2 for n in ch],4*Q+.6),tb,g=.10 if sec==0 else .14)
    add(sitar(hz(ch[0])),tb,pan=-.1,g=.22)
    # sitar arpeggio on eighths
    arp=[ch[0],ch[1],ch[2],ch[1]]*2
    for k,n in enumerate(arp):
        if k==0: continue
        add(sitar(hz(n)*2,1.2),tb+k*E,pan=-.35,g=.07 if sec==0 else .09)
    # melody: bansuri (second half doubled octave-down by sitar)
    t=tb
    for n,b in MEL[bar]:
        if n!="-":
            add(flute(hz(n),b*Q*.97),t,pan=.15,g=.26)
            if sec==1: add(sitar(hz(n),1.4),t,pan=.4,g=.10)
        t+=b*Q
    # keherwa tabla: dha ge na ti | na ka dhi na  (eighths)
    if bar>=2 or sec==1:
        pat=["dha","ge","na","ti","na","ka","dhi","na"]
        for k,b in enumerate(pat):
            tt=tb+k*E
            if b in("dha","dhi","ge"): add(bayan(.5 if b!="ge" else .3),tt,pan=-.05,g=.55)
            if b in("dha","na"): add(dayan(520,1.2,.25),tt,pan=.1)
            if b in("dhi","ti"): add(dayan(780,.5,.15),tt,pan=.1)
            if b=="ka": add(ka(.15),tt,pan=.2)
        if bar%4==3: add(dayan(520,1,.18),tb+7.5*E,pan=.1)   # little fill
# room reverb-ish echo
for d,g in [(.11,.25),(.23,.18),(.37,.12),(.53,.07)]:
    s=int(d*SR); out[s:,0]+=out[:-s,1]*g; out[s:,1]+=out[:-s,0]*g
tail=out[LOOP:].copy(); out=out[:LOOP]; out[:len(tail)]+=tail
out/=np.abs(out).max()*1.12
d=os.path.dirname(os.path.abspath(__file__)); w=os.path.join(d,"romantic.wav")
with wave.open(w,"wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((out*32767).astype("<i2").tobytes())
subprocess.run(["afconvert","-f","m4af","-d","aac","-b","128000",w,os.path.join(d,"romantic.m4a")],check=True); os.remove(w)
print("ok",LOOP/SR,"s")
