from Classes.Protocol.Commands.LogicCommand import LogicCommand

class LogicSimpleCommand(LogicCommand):
    """Commands mit genau einem Zahlenwert:
       505 = Charakter-Upgrade (Charakter-Nr.)      517 = Weltenpfad abholen (4700000 + Zeile)
       535 = Skin gekauft (5500000 + Index)         536 = Pin freigeschaltet (4200000 + Index)
       540 = Quest abgeschlossen (Quest-Nr.)"""

    def __init__(self, payload, commandID: int = 0):
        super().__init__(payload)
        self.commandID: int = commandID
        self.value: int = 0

    def decode(self, byteStream):
        raw = super().decode(byteStream)
        self.value = raw.reflectReflectablePointerBase("data", 0)
        raw.destruct()
        print(f"[Command {self.commandID}] value: {self.value}")

    def execute(self, receiver):
        player = receiver["Player"]
        changed = False
        if self.commandID == 505:
            changed = player.upgradeCharacter(self.value)
        elif self.commandID == 517:
            changed = player.claimMilestone(self.value)
        elif self.commandID == 535:
            changed = player.buySkin(self.value)
        elif self.commandID == 536:
            changed = player.claimPin(self.value)
        elif self.commandID == 540:
            changed = player.finishQuest(self.value)
        if changed:
            receiver["ClientConnection"].db.savePlayer(player)

    def getCommandType(self):
        return self.commandID
