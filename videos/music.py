import numpy as np, wave
sr=44100; dur=30.0; bpm=96; beat=60/bpm
t=np.arange(int(sr*dur))/sr; out=np.zeros_like(t)
def n2f(n): return 440*2**((n-69)/12)
def note(start,length,midi,amp,kind='keys'):
    i0=int(start*sr); n=int(length*sr); 
    if i0>=len(out): return
    n=min(n,len(out)-i0); tt=np.arange(n)/sr; f=n2f(midi)
    if kind=='keys':
        w=np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*3)+.12*np.sin(2*np.pi*3*f*tt)*np.exp(-tt*5)
        env=np.exp(-tt*1.6)*(1-np.exp(-tt*200))
    elif kind=='pad':
        w=sum(np.sin(2*np.pi*f*(1+d)*tt) for d in (-.003,0,.003))/3
        env=np.minimum(tt/.6,1)*np.minimum((length-tt)/.6,1)
    elif kind=='pluck':
        w=np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*8)
        env=np.exp(-tt*6)*(1-np.exp(-tt*300))
    elif kind=='bass':
        w=np.sin(2*np.pi*f*tt)+.2*np.sin(2*np.pi*2*f*tt)
        env=np.exp(-tt*2.2)*(1-np.exp(-tt*120))
    out[i0:i0+n]+=amp*w*env
# Fmaj7 - Am7 - Dm7 - Bbmaj7 (2 mesures chacun... 1 mesure = 4 temps)
chords=[[53,57,60,64],[57,60,64,67],[50,53,57,60],[46,50,53,57]]
bass=[41,45,38,46]
bar=4*beat; nb=int(dur/bar)+1
rng=np.random.default_rng(3)
for b in range(nb):
    ch=chords[b%4]; s=b*bar
    for m in ch: note(s,bar,m+12,.05,'pad')
    note(s,beat*1.5,bass[b%4]-12,.22,'bass'); note(s+beat*2.5,beat*1.5,bass[b%4]-12,.16,'bass')
    for k in range(4):  # accords piano légers sur les temps 2 et 4
        if k in (1,3):
            for m in ch: note(s+k*beat,beat,m+12,.045,'keys')
    if b>=1:  # arpège à la croche, après l'accroche
        arp=[ch[0]+24,ch[2]+24,ch[1]+24,ch[3]+24,ch[2]+24,ch[1]+24,ch[3]+24,ch[2]+24]
        for k,m in enumerate(arp): note(s+k*beat/2,beat/2,m,.05 if k%2==0 else .035,'pluck')
    if b>=1:  # petit shaker doux
        for k in range(8):
            i0=int((s+k*beat/2)*sr); n=int(.06*sr)
            if i0+n<len(out):
                nz=rng.standard_normal(n); nz=np.diff(np.concatenate([[0],nz]))
                out[i0:i0+n]+=(.018 if k%2 else .010)*nz*np.exp(-np.arange(n)/sr*60)
# fondu final
fade=np.ones_like(t); fe=t>dur-3; fade[fe]=np.linspace(1,0,fe.sum()); fade[t<.3]=t[t<.3]/.3
out*=fade; out/=np.abs(out).max()*1.12
st=np.stack([out,np.roll(out,int(.012*sr))*.95],1)
with wave.open('music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype(np.int16).tobytes())
