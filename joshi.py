# coding:utf-8
from TWordclass import TWordclass

TW = TWordclass()
unify_particle = lambda x: TW.Particle_to.get(x,x)
print unify_particle(u"で")
# tripleFrame[u"助詞"] = tripleFrame[u"助詞"].map(unify_particle)
