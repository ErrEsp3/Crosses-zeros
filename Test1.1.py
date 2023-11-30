from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QLabel

class MainMenu(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Крестики-нолики")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        btn_player_vs_player = QPushButton("Игра против друга", self)
        btn_local_multiplayer = QPushButton("Игра по локальной сети", self)
        btn_player_vs_ai = QPushButton("Игра против компьютера", self)

        btn_player_vs_player.clicked.connect(self.start_player_vs_player)
        btn_local_multiplayer.clicked.connect(self.start_local_multiplayer)
        btn_player_vs_ai.clicked.connect(self.start_player_vs_ai)

        layout.addWidget(btn_player_vs_player)
        layout.addWidget(btn_local_multiplayer)
        layout.addWidget(btn_player_vs_ai)

        self.setLayout(layout)

    def start_player_vs_player(self):
        self.start_game("player_vs_player")

    def start_local_multiplayer(self):
        self.start_game("local_multiplayer")

    def start_player_vs_ai(self):
        self.start_game("player_vs_ai")

    def start_game(self, mode):

        print(f"Выбран режим: {mode}")
        self.close()

if __name__ == "__main__":
    app = QApplication([])

    main_menu = MainMenu()
    main_menu.show()

    app.exec_()