#-*- coding: utf-8 -*-

from datetime import datetime
from locale import setlocale, LC_ALL
from pytz import timezone, UnknownTimeZoneError

from pipobot.lib.modules import SyncModule, defaultcmd, answercmd
from pipobot.lib.module_test import ModuleTest
from pipobot.lib.known_users import KnownUser

from .model import KnownUserTimeZone as KUTZ


class CmdDateTimeZone(SyncModule):
    _config = (("dateformat", str, '%a %d %b %Y, %X'), ("locale", str, 'fr_FR.UTF-8'),)

    def __init__(self, bot):
        desc = _("date : show the actual date and time for all registered users\n")
        desc += _("date set <timezone> : set your actual timezone (see http://pastebin.com/XbLSvZhY)\n")
        desc += _("date <user> : show the actual date and time for <user>")
        SyncModule.__init__(self,
                            bot,
                            desc=desc,
                            name="date")

    @answercmd(r'^help')
    def answer_help(self, sender):
        return self.desc

    @answercmd(r'^set (?P<tz>.*)')
    def answer_set(self, sender, tz):
        try:
            timezone(tz)
        except UnknownTimeZoneError:
            return _("I don't know this timezone")
        knownuser = KnownUser.get(sender, self.bot)
        if not knownuser:
            return _("I don't know you, %s, please try '!user register'." % sender)

        kutz = self.bot.session.query(KUTZ).filter(KUTZ.kuid == knownuser.kuid).first()
        if kutz is None:
            kutz = KUTZ(kuid=knownuser.kuid)
        kutz.timezone = tz
        self.bot.session.add(kutz)
        self.bot.session.commit()
        return _("Current timezone of %s set to %s" % (sender, tz))

    @answercmd(r'^(?P<user>\w+)')
    def answer_user(self, sender, user):
        knownuser = KnownUser.get(user, self.bot, authviapseudo=True)
        if not knownuser:
            return _("I don't know that %s, he has to try '!user register'." % user)
        kutz = self.bot.session.query(KUTZ).filter(KUTZ.kuid == knownuser.kuid).first()
        if kutz is None:
            return _("I don't know %s's timezone, he has to '!date set <timezone>'" % user)
        setlocale(LC_ALL, self.locale)
        return kutz.timezone + ': ' + datetime.now(timezone(kutz.timezone)).strftime('%A %d %B %Y, %X')

    @defaultcmd
    def answer(self, sender, message):
        session = self.bot.session
        setlocale(LC_ALL, self.locale)
        ret = _("It is:\n")
        timezones = [tz[0] for tz in session.query(KUTZ.timezone).distinct().all()]
        timezones_users = [(timezone(tz), ", ".join([k.user.pseudo for k in session.query(KUTZ).filter(KUTZ.timezone == tz).all()])) for tz in timezones]
        timezones_users = sorted(timezones_users, key=lambda tz: datetime.now(tz[0]).timetuple())
        ret += '\n'.join(['%s (%s): %s' % (datetime.now(tz).strftime(self.dateformat), tz.zone, users) for tz, users in timezones_users])
        return ret
