import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDesktopWidget, QGridLayout, QDialog, QInputDialog, QHBoxLayout, QLineEdit
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtGui import QPalette, QColor, QIntValidator
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QObject, pyqtSignal

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Введите IP-адрес и порт")
        self.setGeometry(0, 0, 300, 150)
        self.setFixedSize(self.size())

        layout = QVBoxLayout()

        label_info = QLabel("Введите IP-адрес и порт в формате 'IP:порт'", self)
        self.edit_ip_port = QLineEdit(self)
        self.edit_ip_port.setPlaceholderText("Пример: 127.0.0.1:1234")

        layout.addWidget(label_info)
        layout.addWidget(self.edit_ip_port)

        button_layout = QHBoxLayout()

        self.btn_connect = QPushButton("Подключиться", self)
        self.btn_connect.clicked.connect(self.accept_connection)
        button_layout.addWidget(self.btn_connect)

        self.btn_cancel = QPushButton("Отмена", self)
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.move_to_center()

    def move_to_center(self):
        screen_center = QDesktopWidget().screenGeometry().center()
        self.move(screen_center - self.rect().center())

    def accept_connection(self):
        ip_port_text = self.edit_ip_port.text()

        if ":" not in ip_port_text:
            print("Введите IP-адрес и порт в формате 'IP:порт'")
            return

        ip, port = ip_port_text.split(":", 1)

        if not ip or not port.isdigit():
            print("Введите корректный IP-адрес и порт.")
            return

        self.accept()

    def get_connection_info(self):
        ip_port_text = self.edit_ip_port.text()
        ip, port = ip_port_text.split(":", 1)
        return ip, int(port) if port.isdigit() else 0

class NetworkServer(QTcpServer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_connection = None

    def incomingConnection(self, socket_descriptor):
        if self.new_connection:
            self.new_connection(socket_descriptor)

    def listen(self, address, port):
        return super().listen(QHostAddress(address), port)

    def closeServer(self):
        if self.isListening():
            self.close()


class NetworkClient(QTcpSocket):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ready_read = self.readyRead


class GameWindow(QWidget):
    def __init__(self, mode, network=None):
        super().__init__()

        self.setWindowTitle("Игра Крестики-нолики")
        self.setGeometry(0, 0, 400, 300)

        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

        self.mode = mode
        self.network = network
        self.current_player = "X"
        self.board = [""] * 9

        self.label_turn = QLabel(f"Ход игрока {self.current_player}", self)
        self.label_local_player = QLabel("", self) 
        self.winner_label = QLabel("", self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_turn)
        self.layout.addWidget(self.winner_label)
        self.layout.addWidget(self.label_local_player)

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
        if not button.text() and (self.network is None or (hasattr(self.network, 'role') and self.current_player == self.network.role)):
            button.setText(self.current_player)
            self.check_winner()
            self.switch_player()

            if self.network:
                self.network.send_move(row, col)

    def make_ai_move(self):
        available_moves = [i for i, val in enumerate(self.board) if not val.text()]
        if available_moves:
            move = self.minimax(self.board, 3, False)
            self.board[move].setText("O")
            self.check_winner()
            self.switch_player()

    def minimax(self, board, depth, is_maximizing_player):
        scores = {"X": -1, "O": 1, "": 0}

        if self.check_winner(board):
            return scores[board[0].text()]

        if depth == 0:
            return scores[""]

        if is_maximizing_player:
            max_eval = -float("inf")
            for move in range(9):
                if not board[move].text():
                    board[move].setText("O")
                    eval = self.minimax(board, depth - 1, False)
                    board[move].setText("")
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float("inf")
            for move in range(9):
                if not board[move].text():
                    board[move].setText("X")
                    eval = self.minimax(board, depth - 1, True)
                    board[move].setText("")
                    min_eval = min(min_eval, eval)
            return min_eval

    def check_winner(self, board=None):
        win_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Горизонтальные
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Вертикальные
            (0, 4, 8), (2, 4, 6)              # Диагональные
        ]

        if board is None:
            board = self.board

        for combo in win_combinations:
            if (
                board[combo[0]].text() == board[combo[1]].text() == board[combo[2]].text()
                and board[combo[0]].text() != ""
            ):
                self.show_winner(self.current_player if self.network is None else self.network.role)
                return True

        return False

    def set_local_player_label(self, role):
        self.label_local_player.setText(f"Вы играете за {role}")

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

        if self.network and self.current_player == "O":
            self.make_ai_move()


class WaitingDialog(QDialog):
    def __init__(self, parent=None, server_info=None):
        super().__init__(parent)

        ip_address, port = server_info if server_info else ("", 0)

        self.setWindowTitle("Ожидание соперника")
        self.setGeometry(0, 0, 400, 150)
        self.setFixedSize(self.size())

        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        layout = QVBoxLayout()

        label_waiting = QLabel("Ожидание подключения соперника...", self)

        ip_port_layout = QHBoxLayout()

        self.ip_port_line_edit = QLineEdit(self)
        self.ip_port_line_edit.setText(f"{ip_address}:{port}")
        self.ip_port_line_edit.setReadOnly(True)
        
        self.ip_port_line_edit.setFrame(False)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor(255, 255, 255, 0)) 
        self.ip_port_line_edit.setPalette(palette)

        ip_port_layout.addWidget(self.ip_port_line_edit)

        self.btn_copy = QPushButton("Скопировать", self)
        self.btn_copy.clicked.connect(self.copy_ip_port)
        ip_port_layout.addWidget(self.btn_copy)

        layout.addWidget(label_waiting)
        layout.addLayout(ip_port_layout)

        button_layout = QHBoxLayout()

        self.btn_exit = QPushButton("Выйти", self)
        self.btn_exit.clicked.connect(self.exit_to_menu)
        button_layout.addWidget(self.btn_exit)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def exit_to_menu(self):
        self.close()
        if self.parent():
            self.parent().return_to_menu()

    def copy_ip_port(self):
        clipboard = QApplication.clipboard()
        ip_port_text = self.ip_port_line_edit.text()

        colon_index = ip_port_text.find(':')

        if colon_index != -1:
            cleaned_ip_port = ip_port_text[colon_index + 1:]
        else:
            cleaned_ip_port = ip_port_text

        clipboard.setText(cleaned_ip_port)


...

class NetworkManager(QObject):
    connection_established = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.server = None
        self.client = None
        self.role = None
        self.local_role = None 

        self.init_ui()

    def init_ui(self):
        self.main_menu = self.parent

        layout = QVBoxLayout()
        btn_host = QPushButton("Host Game", self.parent)
        btn_join = QPushButton("Join Game", self.parent)

        btn_host.clicked.connect(self.host_game)
        btn_join.clicked.connect(self.join_game)

        layout.addWidget(btn_host)
        layout.addWidget(btn_join)

        self.dialog = QDialog(self.parent)
        self.dialog.setWindowTitle("Network Setup")
        self.dialog.setLayout(layout)

    def set_role(self, role):
        self.role = role
        if self.parent.game_window:
            self.parent.game_window.set_local_player_label(role) 

    def set_local_role(self, local_role):
        self.local_role = local_role
        if self.parent.game_window:
            self.parent.game_window.set_local_player_label(local_role) 

    def host_game(self):
        self.server = NetworkServer(self.parent)
        self.server.new_connection = self.handle_new_connection
        port = 1234
        if self.server.listen(QHostAddress.Any, port):
            print("Server listening on port", port)
            self.show_waiting_dialog(port)
        else:
            print("Server could not start")

    def join_game(self):
        connection_dialog = ConnectionDialog(self.parent)
        if connection_dialog.exec_() == QDialog.Accepted:
            ip, port = connection_dialog.get_connection_info()
            self.client = NetworkClient(self.parent)
            self.client.connectToHost(ip, port)
            if self.client.waitForConnected(1000):
                print("Connected to server")
                self.connection_established.emit()
            else:
                print("Connection failed")

    def show_waiting_dialog(self, port):
        ip_address = "127.0.0.1"  
        self.waiting_dialog = WaitingDialog(self.parent, (ip_address, port))
        self.waiting_dialog.show()

    def handle_new_connection(self, socket_descriptor):
        self.client = NetworkClient(self.parent)
        self.client.setSocketDescriptor(socket_descriptor)
        self.client.ready_read.connect(self.handle_ready_read)

        self.set_role("O" if self.parent.game_window.current_player == "X" else "X")

        self.set_local_role("O" if self.parent.game_window.current_player == "X" else "X")

        self.connection_established.emit()

        if self.waiting_dialog:
            self.waiting_dialog.close()

    def handle_ready_read(self):
        data = self.client.readAll()
        stream = QDataStream(data, QIODevice.ReadOnly)
        row, col = None, None
        stream >> row >> col

        if row is not None and col is not None:
            self.parent.game_window.make_move(row, col)

    def send_move(self, row, col):
        if self.client:
            data = QByteArray()
            stream = QDataStream(data, QIODevice.WriteOnly)
            stream << row << col
            self.client.write(data)

    def disconnect(self):
        if self.server:
            self.server.close()
        elif self.client:
            self.client.disconnectFromHost()


class NetworkSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Настройки сети")
        self.setGeometry(0, 0, 300, 150)  
        self.setFixedSize(self.size())  

        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)  

        layout = QVBoxLayout()

        btn_host = QPushButton("Стать сервером", self)
        btn_join = QPushButton("Присоединиться", self)

        btn_host.clicked.connect(self.accept_host)
        btn_join.clicked.connect(self.accept_join)

        layout.addWidget(btn_host)
        layout.addWidget(btn_join)

        self.setLayout(layout)

    def accept_host(self):
        self.accept()

    def accept_join(self):
        self.accept()


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Крестики-нолики: Главное меню")
        self.setGeometry(0, 0, 400, 300)

        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        btn_start = QPushButton("Начать игру", self)
        btn_network = QPushButton("Сетевая игра", self)

        btn_start.clicked.connect(self.start_game)
        btn_network.clicked.connect(self.setup_network)

        layout.addWidget(btn_start)
        layout.addWidget(btn_network)

        self.setLayout(layout)

    def start_game(self):
        game_window = GameWindow("single")
        game_window.show()

    def setup_network(self):
        dialog = NetworkSetupDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            network_manager = NetworkManager(self)
            if dialog.result() == QDialog.Accepted:
                network_manager.dialog.exec_()
                network_manager.dialog.accepted.connect(self.show_game_window)
            else:
                network_manager.show_waiting_dialog(1234)
                network_manager.connection_established.connect(self.show_game_window)

    def show_game_window(self):
        network_manager = self.sender()
        game_window = GameWindow("network", network_manager)
        network_manager.parent.game_window = game_window
        network_manager.parent.hide()
        game_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())
