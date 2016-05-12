# -*- coding: utf-8 -*-

import graphGithub as gph

user = 'AlexFabre'
org = 'twbs'
repo = 'bootlin'
p='Srp043k1'

rep=gph.Prepare(user,p,org,repo)


print rep
