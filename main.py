import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QGraphicsView, QGraphicsScene, QStatusBar, QScrollArea
)
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PyQt6.QtCore import Qt, QRectF, QLineF

# colors
COLOR_WALL = QColor(15, 60, 55)          
COLOR_CORRIDOR = QColor(255, 255, 255)   
COLOR_DOOR = QColor(255, 255, 255)       
COLOR_LABEL = QColor(70, 70, 70)         
COLOR_STAIRS = QColor(0, 0, 220)         

class DeckCanvas(QGraphicsScene):
    """Сцена для отрисовки векторной геометрии одной палубы."""
    def __init__(self, floor_level, cabins_count=26, deck_length=1400, deck_height=205):
        super().__init__()
        self.floor_level = floor_level
        self.deck_length = deck_length
        self.deck_height = deck_height
        self.cabins_count = cabins_count
        
        self.setSceneRect(0, 0, self.deck_length, self.deck_height)
        self.setBackgroundBrush(QBrush(COLOR_CORRIDOR))
        
        self.wall_pen = QPen(COLOR_WALL, 1.5, Qt.PenStyle.SolidLine)
        self.wall_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        self.generate_deck()

    # надписи
    def add_label(self, text, x, y, size=8):
        label = self.addText(text)
        label.setDefaultTextColor(COLOR_LABEL)
        label.setFont(QFont("Arial", size))
        label.setPos(x, y)

    def generate_deck(self):
        w, h = self.deck_length, self.deck_height
        
        if self.floor_level in [4, 5]:
            bow_taper = 80
            self.addLine(QLineF(10, 10, w - bow_taper, 10), self.wall_pen)
            self.addLine(QLineF(w - bow_taper, 10, w - 10, 40), self.wall_pen)
            self.addLine(QLineF(10, h - 10, w - 10, h - 10), self.wall_pen)
            self.addLine(QLineF(10, 10, 10, h - 10), self.wall_pen)
            self.addLine(QLineF(w - 10, 40, w - 10, h - 10), self.wall_pen)
            self.build_cabin_deck(w, h)
        elif self.floor_level == 6:
            self.addLine(QLineF(10, 10, w - 50, 10), self.wall_pen)
            self.addLine(QLineF(w - 50, 10, w - 10, 35), self.wall_pen)
            self.build_public_deck(w, h)

    def build_cabin_deck(self, w, h):
        corridor_y = h / 2
        cabin_depth = 55
        cabin_width = (w - 300) / self.cabins_count
        door_size = 12

        # стены коридора
        self.addLine(QLineF(20, corridor_y - 12, w - 80, corridor_y - 12), self.wall_pen)
        self.addLine(QLineF(20, corridor_y + 12, w - 80, corridor_y + 12), self.wall_pen)

        # ряды кают по верхнему и нижнему бортам
        start_x = 30
        for i in range(self.cabins_count):
            cx = start_x + i * cabin_width
            
            # --- верхний блок кают ---
            # вертикальная перегородка
            self.addLine(QLineF(cx, 10, cx, 10 + cabin_depth), self.wall_pen)
            # входная стена с разрывом под дверь
            self.addLine(QLineF(cx, 10 + cabin_depth, cx + cabin_width - door_size, 10 + cabin_depth), self.wall_pen)
            
            # --- нижний блок кают ---
            self.addLine(QLineF(cx, h - 10 - cabin_depth, cx, h - 10), self.wall_pen)
            self.addLine(QLineF(cx, h - 10 - cabin_depth, cx + cabin_width - door_size, h - 10 - cabin_depth), self.wall_pen)

        # лестничный узел
        stairs_rect = QRectF(start_x + (self.cabins_count // 2) * cabin_width - 15, corridor_y - 10, 20, 20)
        self.addRect(stairs_rect, QPen(Qt.PenStyle.NoPen), QBrush(COLOR_STAIRS))

        # общественная зона в носовой части палубы 5
        if self.floor_level == 5:
            self.add_label("restaurant", w - 240, 20)
            # столики / маркеры зон (квадратики)
            for row in range(3):
                for col in range(6):
                    self.addRect(QRectF(w - 220 + col * 25, 35 + row * 20, 8, 8), 
                                 self.wall_pen, QBrush(COLOR_WALL))

    def build_public_deck(self, w, h):
        # 1. блок ресторана на корме
        rest_w = 260
        rest_h = h - 20
        self.addLine(QLineF(40, 20, rest_w, 20), self.wall_pen)                  # верх
        self.addLine(QLineF(40, 20, 40, 70), self.wall_pen)                      # левая стена верх
        self.addLine(QLineF(40, 95, 40, rest_h - 40), self.wall_pen)             # левая стена низ
        self.addLine(QLineF(40, rest_h - 40, rest_w, rest_h - 40), self.wall_pen)# нижняя граница ресторана
        self.addLine(QLineF(rest_w, 20, rest_w, 60), self.wall_pen)              # правая стена верх
        self.addLine(QLineF(rest_w, 85, rest_w, rest_h - 40), self.wall_pen)     # правая стена низ

        self.add_label("restaurant", 45, 23)
        
        # столы в ресторане
        for col in range(5):
            self.addRect(QRectF(60 + col * 32, 35, 8, 14), self.wall_pen, QBrush(COLOR_WALL))
            self.addRect(QRectF(60 + col * 32, 65, 8, 8), self.wall_pen, QBrush(COLOR_WALL))

        # Leisure areas
        # верхняя правая комната
        rx_w = rest_w + 110
        self.addLine(QLineF(rest_w, 20, rx_w, 20), self.wall_pen)
        self.addLine(QLineF(rx_w, 20, rx_w, 80), self.wall_pen)
        self.addLine(QLineF(rest_w, 80, rx_w - 30, 80), self.wall_pen) # Стена с дверью
        self.add_label("leisure area", rest_w + 8, 30)

        # синий блок лифта/лестницы возле правой стены этой комнаты
        self.addRect(QRectF(rx_w - 18, 52, 18, 20), QPen(Qt.PenStyle.NoPen), QBrush(COLOR_STAIRS))
        self.addLine(QLineF(rx_w + 20, 20, rx_w + 20, 80), self.wall_pen) # Ограничитель коридора

        # две нижние изолированные комнаты отдыха под рестораном
        bot_y1 = rest_h - 40
        bot_y2 = rest_h
        mid_bot_x = 40 + (rest_w - 40) / 2
        # левая нижняя
        self.addLine(QLineF(40, bot_y1, 40, bot_y2), self.wall_pen)
        self.addLine(QLineF(40, bot_y2, mid_bot_x - 15, bot_y2), self.wall_pen)
        self.addLine(QLineF(mid_bot_x, bot_y1, mid_bot_x, bot_y2), self.wall_pen)
        self.add_label("leisure area", 43, bot_y1 + 4, size=7)
        # правая нижняя
        self.addLine(QLineF(mid_bot_x, bot_y2, rest_w - 15, bot_y2), self.wall_pen)
        self.addLine(QLineF(rest_w, bot_y1, rest_w, bot_y2), self.wall_pen)
        self.add_label("leisure area", mid_bot_x + 5, bot_y1 + 4, size=7)

        # 3. центральная круглая зона
        atrium_x = rx_w + 140
        atrium_y = 100
        circle_pen = QPen(COLOR_WALL, 1.3, Qt.PenStyle.DashLine)
        self.addEllipse(QRectF(atrium_x - 30, atrium_y - 30, 60, 60), circle_pen)
        self.add_label("leisure area", atrium_x - 35, 23)
        self.add_label("leisure area", atrium_x + 35, 45)

        arc_pen = QPen(COLOR_WALL, 1.2, Qt.PenStyle.DashLine)
        self.addPath(self._create_arc_path(atrium_x - 80, 20, atrium_x + 130, 20, atrium_x + 150, 70), arc_pen)
        self.addPath(self._create_arc_path(atrium_x + 150, 130, atrium_x + 130, 160, atrium_x - 60, 160), arc_pen)

        for angle_deg in [30, 70, 110, 150, 210, 250, 290, 330]:
            rad = np.radians(angle_deg)
            tx = atrium_x + 48 * np.cos(rad)
            ty = atrium_y + 48 * np.sin(rad)
            self.addRect(QRectF(tx - 3, ty - 3, 6, 6), self.wall_pen, QBrush(COLOR_WALL))

        # 4. правая открытая палуба
        deck_start_x = atrium_x + 170
        self.add_label("leisure area", deck_start_x + 20, 20)
        
        # сетка столиков на открытой палубе
        for r in range(4):
            for c in range(8):
                px = deck_start_x + c * 38
                py = 42 + r * 30
                if px < w - 40:
                    self.addRect(QRectF(px, py, 6, 6), self.wall_pen, QBrush(COLOR_WALL))
    
    def _create_arc_path(self, x1, y1, x2, y2, x3, y3):
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(x1, y1)
        path.quadTo(x2, y2, x3, y3)
        return path

class DeckView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFixedHeight(185)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cruise ship Simulation")
        self.resize(1200, 680)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        # создание трех палуб
        for floor_num in [6, 5, 4]:
            header = QLabel(f"  Floor {floor_num}")
            header.setFixedHeight(15)
            header.setStyleSheet("""
                background-color: #d8e4ea; 
                color: #2b4e5a; 
                font-weight: bold; 
                font-size: 9px;
                padding: 0px 2px; 
                border: 1px solid #b4c6cf;
            """)
            layout.addWidget(header)

            scene = DeckCanvas(floor_level=floor_num)
            view = DeckView(scene)
            layout.addWidget(view)

        self.setCentralWidget(main_widget)

        # статус-бар
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.setStyleSheet("background-color: #f0f0f0; border-top: 1px solid #ccc; font-size: 11px; color: #333;")
        
        status_bar.addWidget(QLabel("Time: 08:00:00   |   "))
        status_bar.addWidget(QLabel("Total passengers: 354   |   "))
        status_bar.addWidget(QLabel("Deck mode: Normal operations"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())