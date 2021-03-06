#-*- coding: utf-8 -*-

from model import HlList, HlListMembers
from pipobot.lib.modules import SyncModule, defaultcmd, answercmd
from pipobot.lib.known_users import KnownUser, minpermlvl


class HighLight(SyncModule):
    def __init__(self, bot):
        desc = _("hl <people>: Highligh <people> (whom can be registerd users, pseudos or list of people)")
        desc += _("\nhl <people> :<message>: Highligh <people>, and shows <message>")
        desc += _("\nhl show [<list>]: Shows list of people")
        desc += _("\nhl set|add <list> <people>: Add <people> to <list>")
        desc += _("\nhl rm|del <list> [<people>]: Remove <list>, or <people> from <list>")

        SyncModule.__init__(self,
                bot,
                desc=desc,
                name='hl')

    @answercmd(r'^show (?P<plist>\w+)')
    def aswer_show(self, sender, plist):
        hllist = self.bot.session.query(HlList).filter(HlList.name == plist).first()
        if not hllist:
            return _('I don\'t know that "%s" list' % plist)
        ret = _('list "%s"\'s members:' % plist)
        for user in hllist.members:
            ret += ' %s' % user.user
        return ret

    @answercmd(r'^show')
    def answer_showall(self, sender):
        hllists = self.bot.session.query(HlList).all()
        if not hllists:
            return _("%s: There is no HighLight List… Maybe you can create one, before trying that ?" % sender)
        ret = _("HighLight Lists:")
        for hllist in hllists:
            ret += "\n  %-31s" % hllist.name
            for user in hllist.members:
                ret += ' %s' % user.user
        return ret

    @answercmd(r'^(set|add) (?P<hllist>\w+) (?P<users>.*)')
    def answer_set(self, sender, hllist, users):
        ret = ''
        knownusers = []
        unknownusers = []
        users = users.split()

        for user in users:
            knownuser = KnownUser.get(user, self.bot, authviapseudo=True)
            if knownuser:
                knownusers.append(knownuser)
            else:
                unknownusers.append(user)

        if unknownusers:
            ret += _("\nunknown users: %s" % unknownusers)
        if not knownusers:
            ret += _("\n%s: You must provide at least one valid registered user" % sender)
            return ret.strip()

        hllistentry = self.bot.session.query(HlList).filter(HlList.name == hllist).first()
        if not hllistentry:
            hllistentry = HlList(hllist)
            self.bot.session.add(hllistentry)
            self.bot.session.commit()
            hllistentry = self.bot.session.query(HlList).filter(HlList.name == hllist).first()
            ret += _('\nlist "%s" added' % hllist)

        for user in knownusers:
            hllistmember = self.bot.session.query(HlListMembers).filter(HlListMembers.hlid == hllistentry.hlid).filter(HlListMembers.kuid == user.kuid).first()
            if hllistmember:
                ret += _('\n"%s" is already in list "%s"' % (user, hllistentry))
            else:
                hllistmember = HlListMembers(hllistentry.hlid, user.kuid)
                self.bot.session.add(hllistmember)
                ret += _('\n"%s" added in list "%s"' % (user, hllistentry))

        self.bot.session.commit()
        return ret.strip()

    @answercmd(r'^(rm|del) (?P<plist>\w+) (?P<users>.*)')
    @minpermlvl(2)
    def answer_rm_users(self, sender, plist, users):
        hllistname = plist
        hllist = self.bot.session.query(HlList).filter(HlList.name == hllistname).first()
        if not hllist:
            return _("%s: There is no such HighLight List" % sender)
        ret = ''

        users = users.split()
        if users:
            for user in users:
                knownuser = KnownUser.get(user, self.bot, authviapseudo=True)
                if not knownuser:
                    ret += _('user "%s" is not even registered…\n' % user)
                    continue
                hllistmember = self.bot.session.query(HlListMembers).filter(HlListMembers.hlid == hllist.hlid).filter(HlListMembers.kuid == knownuser.kuid).first()
                if not hllistmember:
                    ret += _('user "%s" is not a member of this list\n' % knownuser)
                    continue
                self.bot.session.delete(hllistmember)
                ret += _('user "%s" has been deleted from list "%s"\n' % (knownuser, hllistname))
        else:
            for member in hllist.members:
                self.bot.session.delete(member)
                ret += _('user "%s" has been deleted from list "%s"\n' % (member.user, hllistname))
            self.bot.session.delete(hllist)
            ret += _('list "%s" has been deleted' % hllistname)
        self.bot.session.commit()
        return ret.strip()

    @answercmd(r'^(rm|del) (?P<hllistname>\w+)')
    @minpermlvl(2)
    def answer_rm(self, sender, hllistname):
        hllist = self.bot.session.query(HlList).filter(HlList.name == hllistname).first()
        if not hllist:
            return _("%s: There is no such HighLight List" % sender)
        for hllistmember in self.bot.session.query(HlListMembers).filter(HlListMembers.hlid == hllist.hlid):
            self.bot.session.delete(hllistmember)
        self.bot.session.delete(hllist)
        self.bot.session.commit()
        return _("The list %s has been deleted, as well as all its subscribers" % hllistname)

    @defaultcmd
    def answer(self, sender, message):
        if not message:
            return self.desc
        knownusers = []
        unknownusers = []
        hllists = self.bot.session.query(HlList).all()
        hllistnames = [hllist.name for hllist in hllists]
        ret = 'HL:'
        for user in message.split(':')[0].split():
            if user in hllistnames:  # highliht a whole list
                for hllist in hllists:
                    if hllist.name == user:
                        for knownuser in hllist.members:
                            knownusers.append(knownuser.user)
                        break
            else:  # highlight one user
                knownuser = KnownUser.get(user, self.bot, authviapseudo=True, avoid_bot=False)
                if knownuser:
                    knownusers.append(knownuser)
                else:
                    unknownusers.append(user)
        for user in self.bot.occupants.users:
            if KnownUser.get(user, self.bot, avoid_bot=False) in knownusers:
                ret += ' %s' % user
        for user in unknownusers:
            ret += ' %s' % user
        if ':' in message:
            ret += ' => ' + message.split(':', 1)[1].strip()
        return ret
