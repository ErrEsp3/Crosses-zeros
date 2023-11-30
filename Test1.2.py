from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDesktopWidget, QGridLayout, QDialog

class GameWindow(QWidget):
    def __init__(self, mode):
        super().__init__()

        self.setWindowTitle("Игра Крестики-нолики")
        self.setGeometry(0, 0, 400, 300)


        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

        self.mode = mode
        self.current_player = "X"
        self.board = [""] * 9  

        self.label_turn = QLabel(f"Ход игрока {self.current_player}", self)
        self.winner_label = QLabel("", self) 

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_turn)
        self.layout.addWidget(self.winner_label)

        self.setup_board()
        self.setup_buttons()

        self.setLayout(self.layout)

    def setup_board(self):

        self.board_widget = QWidget(self)
        self.board_layout = QGridLayout(self.board_widget)

        for row in range(3):
            for col in range(3):
                button = QPushButton("", self)
                button.clicked.connect(lambda _, r=row, c=col: self.make_move(r, c))
                self.board_layout.addWidget(button, row, col)
                self.board[row * 3 + col] = button 

        self.layout.addWidget(self.board_widget)

    def setup_buttons(self):

        self.btn_menu = QPushButton("В меню", self)
        self.btn_menu.clicked.connect(self.return_to_menu)

        self.btn_new_game = QPushButton("Новая игра", self)
        self.btn_new_game.clicked.connect(self.new_game)

        self.layout.addWidget(self.btn_menu)
        self.layout.addWidget(self.btn_new_game)

    def make_move(self, row, col):
        button = self.board[row * 3 + col]
        if not button.text():
            button.setText(self.current_player)
            self.check_winner()
            self.switch_player()

    def check_winner(self):

        win_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Горизонтальные
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Вертикальные
            (0, 4, 8), (2, 4, 6)              # Диагональные
        ]

        for combo in win_combinations:
            if (self.board[combo[0]].text() == self.board[combo[1]].text() == self.board[combo[2]].text() and
                    self.board[combo[0]].text() != ""):
                self.show_winner(self.current_player)
                return

    def show_winner(self, winner):
        self.winner_label.setText(f"Игрок {winner} победил!")
        self.winner_label.setStyleSheet("font-size: 18px; color: green; font-weight: bold;")

        self.disable_buttons()

    def disable_buttons(self):
        for button in self.board:
            button.setEnabled(False)

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.label_turn.setText(f"Ход игрока {self.current_player}")

    def return_to_menu(self):
        self.close()

    def new_game(self):
        for button in self.board:
            button.setText("")
            button.setEnabled(True)

        self.winner_label.clear()

class MainMenu(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Крестики-нолики")
        self.setGeometry(0, 0, 300, 200)  


        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

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


        self.game_window = None

    def start_player_vs_player(self):
        self.start_game("player_vs_player")

    def start_local_multiplayer(self):
        self.start_game("local_multiplayer")

    def start_player_vs_ai(self):
        self.start_game("player_vs_ai")

    def start_game(self, mode):

        self.game_window = GameWindow(mode)
        self.game_window.show()

if __name__ == "__main__":
    app = QApplication([])

    main_menu = MainMenu()
    main_menu.show()

    app.exec_()
