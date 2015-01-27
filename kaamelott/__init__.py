#-*- coding: utf-8 -*-
import os
import random

from pipobot.lib.modules import MultiSyncModule, defaultcmd
from pipobot.lib.utils import ListConfigParser


class Kaamelott(MultiSyncModule):
    def __init__(self, bot):
        names = self.readconf()
        MultiSyncModule.__init__(self,
                                 bot,
                                 names=names)

    def readconf(self):
        config_file = os.path.join(os.path.dirname(__file__), 'kaamelott.cfg')
        names = {}
        self.dico = {}
        config = ListConfigParser()
        config.read(config_file)
        self.genericCmd = config.sections()
        for c in self.genericCmd:
            self.dico[c] = {}
            self.dico[c]['desc'] = config.get(c, 'desc')
            quote = config.get(c, 'citation')
            self.dico[c]['citation'] = quote if type(quote) is list else [config.get(c, 'citation')]
            names[c] = self.dico[c]['desc']
        return names

    @defaultcmd
    def answer(self, cmd, sender, message):
        if cmd == '':
            return "Il faut mettre une personne parmi la liste que tu peux aller voir tout seul dans le help !"
        elif message == '':
            return random.choice(self.dico[cmd]["citation"])
        else:
            return "Pourquoi un argument ?"
