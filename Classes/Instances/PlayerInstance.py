import copy


class PlayerInstance:
    """Spielerdaten. Alles liegt pro Instanz (vorher: Klassenattribute,
    dadurch teilten sich alle Spieler dieselben Listen)."""

    def __init__(self):
        # Main Player Stats
        self.accountID: list[int] = []
        self.accountToken: str | None = None
        self.sessionKey: str | None = None

        # Wird nicht gespeichert: True, sobald im aktuellen Kampf Eingaben ankamen
        self.inBattle: bool = False

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
        self.milestones: list[int] = []  # abgeholte Meilensteine im Weltenpfad

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
            "milestones": self.milestones,
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
        self.milestones = list(data.get("milestones", []))
        self.ensureBonusMembers()

    # ---- Belohnungen ----
    def addResource(self, resourceID: int, amount: int):
        """ID 0 = Diamanten (resources[0]), sonst die Resource mit dieser ID.
        Obergrenze: MaxCapacity aus resources.csv, sonst RewardConfig.RESOURCE_CAPS."""
        from Classes.Utilities import RewardConfig as R
        from Classes.Utilities import GameData
        if resourceID == 0:
            self.resources[0]["val"] = self.resources[0].get("val", 0) + amount
            return
        cap = GameData.resourceCap(resourceID)
        if cap is None:
            cap = R.RESOURCE_CAPS.get(resourceID)
        for res in self.resources[1:]:
            if res.get("id") == resourceID:
                value = res.get("val", 0) + amount
                res["val"] = min(value, cap) if cap is not None else value
                return
        value = amount if cap is None else min(amount, cap)
        self.resources.append({"id": resourceID, "val": value})

    def claimMilestone(self, milestoneID: int) -> bool:
        """Merkt sich den Meilenstein und schreibt die Belohnung gut. False = schon abgeholt."""
        from Classes.Utilities import GameData
        if milestoneID in self.milestones:
            return False
        reward = GameData.milestoneReward(milestoneID)
        if reward:
            if reward["resource"] and reward["amount"] > 0:
                rid = GameData.resourceIdByName(reward["resource"])
                if rid is not None:
                    self.addResource(rid, reward["amount"])
            if reward["character"]:
                cid = GameData.characterIdByName(reward["character"])
                if cid is not None and cid not in {m.get("id") for m in self.members}:
                    self.members.append({"id": cid})
        else:
            print(f"[PlayerInstance::] Keine Belohnung in den Spieldaten für Meilenstein {milestoneID}")
        self.milestones.append(milestoneID)
        return True

    def ensureBonusMembers(self):
        from Classes.Utilities import RewardConfig as R
        have = {m.get("id") for m in self.members}
        for cid in R.BONUS_MEMBER_IDS:
            if cid not in have:
                self.members.append({"id": cid})

    def applyBattleReward(self):
        from Classes.Utilities import RewardConfig as R
        self.expTokens += getattr(R, "EXP_PER_BATTLE", 0)
        self.addResource(0, R.GEMS_PER_BATTLE)
        self.addResource(R.COINS_RESOURCE_ID, R.COINS_PER_BATTLE)
        if R.ORBS_RESOURCE_ID is not None:
            self.addResource(R.ORBS_RESOURCE_ID, R.ORBS_PER_BATTLE)
        if getattr(R, "COSMETIC_PER_BATTLE", 0) > 0:
            self.addResource(R.COSMETIC_RESOURCE_ID, R.COSMETIC_PER_BATTLE)
