import pygame, os

def secondsToFormat(s):
    t = {"h":3600, "m":60, "s":1}
    for i in t:
        f = s//t[i]
        s -=  f * t[i]
        t[i] = f
    return "{}:{}:{}".format(*list(["0"+str(i) if len(str(i)) < 2 else i for i in t.values()]))

def factoredScaling(Surface, factor):
    return pygame.transform.scale(Surface, (Surface.get_width() * factor, Surface.get_height() * factor))

def loadConvFacScaledImg(pathTuple, scaleFactor=1, preserveAlpha=True):
    img = pygame.image.load(os.path.join(*pathTuple)).convert_alpha() if preserveAlpha else pygame.image.load(os.path.join(*pathTuple)).convert()
    return img if scaleFactor == 1 else  factoredScaling(img, scaleFactor)

def loadConvScaledImg(pathTuple, newDimensions=None, preserveAlpha=True):
    img = pygame.image.load(os.path.join(*pathTuple)).convert_alpha() if preserveAlpha else pygame.image.load(os.path.join(*pathTuple)).convert()
    return img if newDimensions == None else pygame.transform.scale(img, newDimensions)