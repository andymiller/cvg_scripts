import numpy as np
import pylab as pl

def features(eoPixels, irPixels):
  #gbDiff = green_blue_difference(eoPixels, irPixels)
  irDiff = ir_difference(eoPixels, irPixels)
  rRatio = pixelRatio(eoPixels, irPixels, "red")
  gRatio = pixelRatio(eoPixels, irPixels, "green")
  #bRatio = pixelRatio(eoPixels, irPixels, "blue")
  #return np.column_stack( (gbDiff, irDiff, rRatio, bRatio, gRatio) )
  return np.column_stack( (gRatio, rRatio) )

def ir_difference(eoPixels, irPixels):
  irdiff = irPixels[:,0] - eoPixels[:,2]
  intensity = np.sum(eoPixels[:,:3]) + irPixels[:,0]
  return irdiff/intensity

def green_blue_difference(eoPixels, irPixels):
  """Assuming eo and ir pixes are passed in, returns array of green blue diff"""
  assert eoPixels.shape[0] == irPixels.shape[0]
  gbdiff = eoPixels[:,1] - eoPixels[:,2]
  intensity = np.sum(eoPixels[:,:3]) + irPixels[:,0]
  return gbdiff / intensity

def pixelRatio(eoPixels, irPixels, pixel_type="red"):
  """Green / (Green + Red + Blue + IR)"""
  assert eoPixels.shape[0] == irPixels.shape[0] 
  
  if pixel_type=="red":
    num = eoPixels[:,0]
  if pixel_type=="green":
    num = eoPixels[:,1]
  if pixel_type=="blue":
    num = eoPixels[:,2]
  if pixel_type=="ir":
    num = irPixels[:,0]

  denom = np.sum(eoPixels[:,:3]) + irPixels[:,0]
  return num / denom



