import copy


class PlayerInstance:
    """Spielerdaten. Alles liegt jetzt pro Instanz (vorher: Klassenattribute,
    dadurch teilten sich alle Spieler dieselben Listen)."""

    def __init__(self):
        # Main Player Stats
        self.accountID: list[int] = []
        self.accountToken: str | None = None
        self.sessionKey: str | None = None

        # Main Player Items
        self.name: str | None = None
        self.registrationState: int = -1
        self.expTokens: int = 0
        self.trophies: int = 0
        self.resources: list[dict[str, int]] = [
            {"val": 10},
            {"id": 1, "val": 10000},
        ]
        self.members: list[dict[str, int]] = [
            {"id": 0},
            {"id": 2},
            {"id": 4},
        ]
        self.skins: list = []
        self.emotes: list[dict[str, int]] = [
            {"id": 0, "idx": 0},
            {"id": 1, "idx": 1},
            {"id": 2, "idx": 2},
            {"id": 2, "idx": 2},
        ]
        self.quests: list[dict[str, int]] = [{"id": 94, "progress": 4}]

    def toDict(self) -> dict:
        """Kompletter Spielstand, so wie er in die DB geschrieben wird."""
        return {
            "id": self.accountID,
            "token": self.accountToken,
            "name": self.name,
            "regState": self.registrationState,
            "expTokens": self.expTokens,
            "trophies": self.trophies,
            "resources": self.resources,
            "members": self.members,
            "skins": self.skins,
            "emotes": self.emotes,
            "quests": self.quests,
        }

    # Alter Name bleibt erhalten, damit bestehender Code weiter funktioniert
    def createDataEntry(self) -> dict:
        return self.toDict()

    def loadInstance(self, data: dict):
        self.accountID = data["id"]
        self.name = data.get("name", None)
        self.registrationState = data.get("regState", -1)
        self.expTokens = data.get("expTokens", 0)
        self.trophies = data.get("trophies", 0)
        self.resources = copy.deepcopy(data.get("resources", self.resources))
        self.members = copy.deepcopy(data.get("members", self.members))
        self.skins = copy.deepcopy(data.get("skins", self.skins))
        self.emotes = copy.deepcopy(data.get("emotes", self.emotes))
        self.quests = copy.deepcopy(data.get("quests", self.quests))
