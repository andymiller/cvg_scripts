import Image
import os, sys
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


if __name__ == "__main__":
  if len(sys.argv) < 4:
    print "usage: stitch_images.py <dir1> <dir2> <outdir>"
    sys.exit(-1)

  #stitch two dirs of images together
  outdir = sys.argv[3];
  if not os.path.exists(outdir):
    os.mkdir(outdir)

  #make sure they are the same size
  imgs1 = glob(sys.argv[1] + "/*.png")
  imgs2 = glob(sys.argv[2] + "/*.png")
  imgs1.sort(); imgs2.sort()
  assert len(imgs1) == len(imgs2)
  for idx in range(len(imgs1)):
    stitched = half_and_half(imgs1[idx], imgs2[idx])
    fname = outdir + "/stitched_%04d.png"%(idx)
    stitched.save(fname)


