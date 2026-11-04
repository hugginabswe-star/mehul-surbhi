"""Cut art from the v3 GPT cards (source/v3) into transparent PNGs for the web invite."""
from PIL import Image, ImageFilter, ImageChops
import numpy as np, os, sys
SRC = os.path.expanduser("~/Documents/Wedding-Kankotri/source/v3")
OUT = os.path.expanduser("~/Documents/Wedding-Kankotri/web/img3")
# name: (file, box x0,y0,x1,y1, feather px, key-strength)
CUTS = {
 "ganesha":  ("prewedding.png", (335, 42, 690, 234), 10),
 "bell":     ("prewedding.png", (212, 92, 290, 300), 6),
 "corner":   ("vows.png", (0, 0, 330, 280), 16),
 "cornerb":  ("prewedding.png", (0, 1235, 290, 1455), 16),
 "kalash":   ("prewedding.png", (305, 675, 432, 768), 8),
 "dandiya":  ("prewedding.png", (292, 855, 425, 955), 8),
 "haldi":    ("prewedding.png", (438, 996, 542, 1068), 8),
 "kumbh":    ("prewedding.png", (436, 1082, 548, 1198), 8),
 "chhatri":  ("village.png", (280, 30, 745, 280), 14),
 "fork":     ("village.png", (72, 688, 222, 855), 6),
 "horse":    ("village.png", (72, 898, 222, 1060), 6),
 "village":  ("village.png", (34, 1060, 990, 1488), 28),
 "rings":    ("vows.png", (385, 62, 625, 222), 10),
 "trees":    ("vows.png", (34, 1205, 990, 1488), 28),
 "peacock":  ("tahuko.png", (158, 985, 312, 1110), 8),
}
KILL = {"ganesha":[(0,0,110,40),(260,0,355,40)], "cornerb":[(250,0,290,80)], "chhatri":[(0,0,130,80),(335,0,465,80)]}
def paper(im):
    a = np.asarray(im.convert("RGB")).reshape(-1,3).astype(float)
    lum = a.sum(1); top = a[lum > np.percentile(lum, 70)]
    return np.median(top, 0)
for name,(f,box,fe) in CUTS.items():
    im = Image.open(os.path.join(SRC,f)).convert("RGB").crop(box)
    p = paper(im); a = np.asarray(im).astype(float)
    d = np.sqrt(((a-p)**2).sum(2))
    alpha = np.clip((d-16)/26, 0, 1)
    if name.startswith('corner'):   # drop the GPT gold frame lines, keep leaves/flowers
        r,g,b = a[...,0],a[...,1],a[...,2]
        gold = (r>g+12)&(g>b+25)&(r>150)
        alpha[gold] = 0            # paper -> transparent, soft ramp
    for (x0,y0,x1,y1) in KILL.get(name,[]): alpha[y0:y1,x0:x1]=0
    al = Image.fromarray((alpha*255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))
    # feather crop edges
    w,h = im.size; m = Image.new("L",(w,h),0)
    inner = Image.new("L",(max(1,w-2*fe),max(1,h-2*fe)),255); m.paste(inner,(fe,fe))
    m = m.filter(ImageFilter.GaussianBlur(fe/2))
    al = ImageChops.multiply(al, m)
    out = im.copy(); out.putalpha(al)
    # sharper on retina phones: 3x Lanczos upscale + unsharp mask
    W3,H3 = out.width*3, out.height*3
    rgb = out.convert('RGB').resize((W3,H3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=140, threshold=2))
    a3 = out.getchannel('A').resize((W3,H3), Image.LANCZOS)
    out = rgb; out.putalpha(a3)
    out.save(os.path.join(OUT, name+".webp"), quality=88, method=6)
    print(name, out.size)
