import numpy as np
import pygame, os
from timeit import default_timer
from math import pi
from PygameCollection.math import Vector2D, Matrix2D
from PygameCollection.gameObjects import MovableSprite

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


# class linearVectorArt:
#     pass

# todo: implement correctly -> generalize drawing arrows (see LinearVecArt2D-class)
def showVector(screen, vector: Vector2D, x, y, length=100, lineWidth=7, headLength=20, headWidth=14, scale=True):
    pos = Vector2D(x, y)
    vectors = list()
    points = list()

    #todo: refine this
    if scale:
        length *= vector.magnitude()

    vectors.append([Vector2D(0, length)])
    vectors.append([Vector2D(-headWidth//2, -headLength)])
    vectors.append([Vector2D(headWidth//2-lineWidth//2, 0)])
    vectors.append([Vector2D(0, headLength-length)])
    vectors.append([Vector2D(lineWidth, 0)])
    vectors.append([Vector2D(0, length-headLength)])
    vectors.append([Vector2D(headWidth//2-lineWidth//2, 0)])
    vectors.append([Vector2D(-headWidth//2, headLength)])

    offset = pi / 2  # based on the fact, that the arrow is drawn facing "downwards"
    m = Matrix2D.fromRotation(offset - vector.toRadiant())  # todo: why is this argument correct??? why not vector.toRadiant()-offset
    for i, v in enumerate(vectors):
        vectors[i] = [Vector2D.fromMatrixVecMul(vectors[i][0], m)]

    for i, v in enumerate(vectors):
        if i == 0:
            vectors[i].append(pos)
        else:
            vectors[i].append(vectors[i-1][1]+vectors[i-1][0])

        points.append(v[1].toTuple())
    del points[0]

    pygame.draw.polygon(screen, (255, 0, 0), points)

def showVecDirSprite(sprite: MovableSprite, *args, **kwargs):
    showVector(sprite.screen, sprite.dir, *sprite.pos.toTuple(), *args, **kwargs)

def printRuntime(callable):
    def __inner(*args, **kwargs):
        start = default_timer()
        r = callable(*args, **kwargs)
        print(default_timer()-start)
        return r
    return __inner
