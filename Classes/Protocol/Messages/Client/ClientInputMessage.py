from Classes.Protocol.PiranhaMessage import PiranhaMessage

class ClientInputMessage(PiranhaMessage):
    def __init__(self, payload):
        super().__init__(payload)

    def decode(self, receiver):
        # Werte werden nur gelesen (vorher: je Paket 3 print-Zeilen, im Kampf über 2000x)
        self.readInt()
        self.readInt()
        self.readVInt()

    def execute(self, receiver):
        # Merkt sich, dass gerade ein Kampf läuft
        receiver["Player"].inBattle = True

    def getMessageType(self):
        return 18856
