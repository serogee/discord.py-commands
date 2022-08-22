import discord
import os
import re

EMPTYLIST = list()

class ContextStatic:

    def __init__(self, message, prefix, trigger, command) -> None:
        self.message = message
        self.prefix = prefix
        self.trigger = trigger
        self.command = command

    async def reply(self, content=None, embed=None, mention_author=False):
        await self.message.reply(content, embed=embed, mention_author=mention_author)

    async def get_reference(self):
        return await self.message.channel.fetch_message(self.message.reference.message_id)

class Flags(tuple):

    def __new__(cls, flags_list, flags_raw) -> Flags:
        return super(Flags, cls).__new__(cls, tuple(flags_list))

    def __init__(self, flags_list, flags_raw) -> None:
        self.raw = flags_raw

    def __str__(self) -> str:
        return self.raw
    
    def __repr__(self) -> str:
        return f"<flags_raw: {self.raw}, activated_flags: {super().__str__()}>"

class ContextFlagged(ContextStatic):

    def __init__(self, message, prefix, trigger, command, flags) -> None:
        super().__init__(message, prefix, trigger, command)
        self.flags = Flags(command.valid_flags, flags)

def anycase(match):
    group = match.group(1)
    return f"[{group.lower()}{group.upper()}]"

class Command:

    def __init__(self, traceback, parent, aliases: list=EMPTYLIST, mention_as_prefix=False, case_sensitive=False) -> None:
        self._traceback = traceback
        self.cluster = parent
        self.aliases = aliases
        self.mention_as_prefix = mention_as_prefix
        self.case_sensitive = case_sensitive
        self.name = traceback.__name__
        self.description = traceback.__doc__
        self.triggers = [self.name, *aliases]
        if case_sensitive:
            regex = [re.escape(trigger) for trigger in self.triggers]
        else:
            regex = [re.sub(r"([a-zA-Z])", anycase, re.escape(trigger)) for trigger in self.triggers]
        self.regex = fr"{'|'.join(regex)}"
        
class CommandStatic(Command):

    def __init__(self, traceback, parent, aliases: list=EMPTYLIST, mention_as_prefix=False, case_sensitive=False) -> None:
        super().__init__(traceback, parent, aliases, mention_as_prefix, case_sensitive)
        self.search