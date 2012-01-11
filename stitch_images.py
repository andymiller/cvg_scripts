import Image
import os
from glob import glob

def half_and_half(im1, im2):
  im1 = Image.open(im1);
  im2 = Image.open(im2);
  assert(im1.size == im2.size)

  ni,nj = im1.size
  halfI = int(ni/2)
  lbox = (0, 0, halfI, nj)
  left = im1.crop(lbox)

  rbox = (halfI,0, ni,nj)
  right = im2.crop(rbox)

  #new image
  stitched = Image.new("RGB", im1.size)
  stitched.paste(left, lbox)
  stitched.paste(right, rbox)
  return stitched

#run on two dirs
outdir = "/home/acm/data/galactica/fused/half"
imgs1 = glob("/home/acm/data/galactica/dense_eo/spiral1/*.png")
imgs2 = glob("/home/acm/data/galactica/dense_orbit/xspiral/*.png")
imgs1.sort(); imgs2.sort()
assert len(imgs1) == len(imgs2)
for idx in range(len(imgs1)):
  stitched = half_and_half(imgs1[idx], imgs2[idx])
  fname = outdir + "/stitched_%04d.png"%(idx)
  stitched.save(fname)


