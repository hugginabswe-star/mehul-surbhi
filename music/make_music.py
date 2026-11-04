"""Original, royalty-free cheerful loop for the invite (music box + santoor-ish pluck, D major). Writes bg.wav -> bg.m4a"""
import numpy as np, wave, os, subprocess
SR=44100; BPM=100; E=60/BPM/2          # eighth-note seconds
BARS=16; L=int(SR*E*8*BARS)+SR*2
out=np.zeros((L,2))
N={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def hz(n): name,o=n[:-1],int(n[-1]); return 440*2**((N[name]+12*(o+1)-69)/12)
def add(sig,t0,pan=0.0,g=1.0):
    i=int(t0*SR); s=sig[:max(0,L-i)]
    out[i:i+len(s),0]+=s*g*(1-pan)/1.0; out[i:i+len(s),1]+=s*g*(1+pan)/1.0
def pluck(f,d=1.6,bright=1.0):
    t=np.arange(int(SR*d))/SR
    s=(np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*2*f*t)*np.exp(-t*4)+.25*bright*np.sin(2*np.pi*3*f*t)*np.exp(-t*7)
       +.18*bright*np.sin(2*np.pi*2.76*f*t)*np.exp(-t*9)+.3*np.sin(2*np.pi*f*1.003*t))
    env=np.exp(-t*3.2)*np.minimum(1,t*400); return s*env
def pad(fs,d):
    t=np.arange(int(SR*d))/SR; s=sum(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t) for f in fs)/len(fs)
    env=np.minimum(1,t/0.6)*np.minimum(1,(d-t)/0.6); return s*env
def kick():
    t=np.arange(int(SR*.22))/SR; f=50+90*np.exp(-t*25); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)
rng=np.random.default_rng(7)
def shaker(g=1):
    n=int(SR*.06); x=rng.standard_normal(n); x=np.diff(x,prepend=0); return x*np.exp(-np.arange(n)/SR*70)*g
A=["F#5 A5 B5 A5 F#5 - E5 D5","E5 F#5 A5 - F#5 E5 D5 -","D5 E5 F#5 A5 B5 - A5 F#5","E5 - F#5 E5 D5 - . ."]
B=["A5 - B5 D6 B5 A5 F#5 -","F#5 E5 F#5 A5 F#5 - E5 -","D5 E5 F#5 - A5 B5 A5 F#5","E5 F#5 E5 - D5 - . ."]
mel=A+B+A+B
CH=[("D3","F#3","A3"),("B2","D3","F#3"),("G2","B2","D3"),("A2","C#3","E3")]
for bar,line in enumerate(mel):
    tb=bar*8*E; sec=bar//8
    for k,tok in enumerate(line.split()):
        if tok in "-.": continue
        f=hz(tok)*(2 if (sec==1 and bar%8>=4) else 1)
        add(pluck(f),tb+k*E,pan=-.15,g=.30)
        if sec==1: add(pluck(f*2,1.0,1.4),tb+k*E+.004,pan=.3,g=.08)   # music-box sparkle 2nd time
    ch=CH[bar%4]
    add(pad([hz(n)*2 for n in ch],8*E+.3),tb,g=.07)
    add(pluck(hz(ch[0]),1.2,.3),tb,g=.22); add(pluck(hz(ch[0]),1.0,.3),tb+4*E,g=.16)
    # light arpeggio on offbeats
    for k,n in zip([1,3,5,7],[ch[1],ch[2],ch[1],ch[2]]): add(pluck(hz(n)*2,.7,.6),tb+k*E,pan=.35,g=.06)
    if bar>=1:
        add(kick(),tb,g=.35); add(kick(),tb+5*E,g=.22)
        for k in range(8): add(shaker(.06 if k%2 else .03),tb+k*E,pan=.5)
# simple stereo echo for space
for d,g in [(.19,.22),(.31,.15),(.47,.08)]:
    s=int(d*SR); out[s:,0]+=out[:-s,1]*g; out[s:,1]+=out[:-s,0]*g
loop=int(SR*E*8*BARS); tail=out[loop:loop+SR*2].copy(); out=out[:loop]; out[:len(tail)]+=tail   # wrap tail -> seamless loop
out/=np.abs(out).max()*1.12
d=os.path.dirname(os.path.abspath(__file__)); w=os.path.join(d,"bg.wav")
with wave.open(w,"wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((out*32767).astype("<i2").tobytes())
subprocess.run(["afconvert","-f","m4af","-d","aac","-b","128000",w,os.path.join(d,"bg.m4a")],check=True); os.remove(w)
print("ok", loop/SR, "s")
