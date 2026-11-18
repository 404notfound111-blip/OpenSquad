from Classes.Protocol.Commands.LogicCommand import LogicCommand

class LogicClaimMilestoneCommand(LogicCommand):
    """Command 517: Meilenstein im Weltenpfad abholen (ID = 4700000 + Zeile)."""

    def __init__(self, payload):
        super().__init__(payload)
        self.milestoneID: int = 0

    def decode(self, byteStream):
        raw = super().decode(byteStream)
        self.milestoneID = raw.reflectReflectablePointerBase("data", 0)
        print(f"claimed milestone: {self.milestoneID}")
        raw.destruct()

    def execute(self, receiver):
        player = receiver["Player"]
        if player.claimMilestone(self.milestoneID):
            receiver["ClientConnection"].db.savePlayer(player)

    def getCommandType(self):
        return 517
