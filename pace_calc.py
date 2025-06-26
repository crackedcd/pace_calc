from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView
)
from PySide6.QtGui import QIntValidator
import sys


class PaceCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("长跑配速计算器")
        self.init_ui()

    def init_ui(self):
        # 配速输入
        self.pace_input = QLineEdit()
        self.pace_input.setFixedSize(180, 30)
        self.pace_input.setPlaceholderText("配速（min/km）")
        self.pace_input.setValidator(QIntValidator(100, 9999))  # 限制输入范围
        pace_layout = QHBoxLayout()
        pace_layout.addWidget(QLabel("配速："))
        pace_layout.addWidget(self.pace_input)
        pace_layout.addWidget(QLabel("格式: 630, 500 ..."))
        pace_layout.addStretch()

        # 时速输入
        self.speed_input = QLineEdit()
        self.speed_input.setFixedSize(180, 30)
        self.speed_input.setPlaceholderText("时速（km/h）")
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("时速："))
        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(QLabel("格式: 12.3, 13 ..."))
        speed_layout.addStretch()

        # 最后一个被编辑过的输入框
        self.last_edited = None
        # 绑定 textEdited 信号，记录最近编辑的输入框
        self.pace_input.textEdited.connect(lambda _: self.set_last_edited(self.pace_input))
        self.speed_input.textEdited.connect(lambda _: self.set_last_edited(self.speed_input))

        # 提交和重置按钮
        self.submit_btn = QPushButton("提交")
        # self.reset_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.submit_btn.setFixedSize(90, 30)
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedSize(90, 30)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.reset_btn)

        self.submit_btn.clicked.connect(self.calculate)
        self.reset_btn.clicked.connect(self.reset_fields)

        # 表格一：距离 → 时间
        self.table_distance_to_time = QTableWidget()
        self.table_distance_to_time.setColumnCount(2)
        self.table_distance_to_time.setHorizontalHeaderLabels(["距离", "用时（时:分:秒）"])
        self.table_distance_to_time.verticalHeader().setVisible(False)
        self.table_distance_to_time.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 表格二：时间 → 距离
        self.table_time_to_distance = QTableWidget()
        self.table_time_to_distance.setColumnCount(2)
        self.table_time_to_distance.setHorizontalHeaderLabels(["时间", "可跑距离（km）"])
        self.table_time_to_distance.verticalHeader().setVisible(False)
        self.table_time_to_distance.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 两个输入横向布局
        input_layout = QVBoxLayout()
        input_layout.addLayout(pace_layout)
        input_layout.addLayout(speed_layout)

        # 两个表格横向布局
        tables_layout = QHBoxLayout()
        tables_layout.addWidget(self.table_distance_to_time)
        tables_layout.addWidget(self.table_time_to_distance)

        # 主布局纵向布局
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addLayout(btn_layout)
        layout.addLayout(tables_layout)
        self.setLayout(layout)

    def set_last_edited(self, input_edit):
        self.last_edited = input_edit

    def fill_pace_speed_input(self):
        if self.last_edited is self.pace_input:
            pace = str(int(self.pace_input.text()))
            if len(pace) == 3:
                minutes = int(pace[0])
                seconds = int(pace[1:3])
            elif len(pace) == 4:
                minutes = int(pace[:2])
                seconds = int(pace[2:4])
            else:
                raise ValueError("配速异于常人，请检查输入")
            if seconds >= 60:
                raise ValueError("秒数不能大于等于60")
            total_minutes = minutes + seconds / 60
            if total_minutes == 0:
                raise ValueError("配速不能为0")
            speed = 60 / total_minutes
            self.speed_input.setText(f"{speed:.1f}")
        elif self.last_edited is self.speed_input:
            speed = float(self.speed_input.text())
            if speed == 0:
                raise ValueError("时速不能为0")
            pace = 60 / speed
            minutes = int(pace)
            seconds = int(round((pace - minutes) * 60))
            if seconds == 60:
                minutes += 1
                seconds = 0
            self.pace_input.setText(f"{minutes}{seconds:02d}")

    def generate_tables(self, pace_min_per_km):
        def format_time(minutes_total):
            total_seconds = round(minutes_total * 60)
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        distances = [
            ("100m", 0.1), ("200m", 0.2), ("400m", 0.4), ("800m", 0.8), ("1KM", 1.0), 
            ("3KM", 3.0), ("5KM", 5.0), ("10KM", 10.0), ("半马", 21.0975), ("全马", 42.195)
        ]
        times = [
            ("1分", 1), ("5分", 5), ("10分", 10), ("15分", 15), ("20分", 20), ("30分", 30), 
            ("40分", 40), ("60分", 60), ("90分", 90), ("120分", 120)
        ]

        self.table_distance_to_time.setRowCount(len(distances))
        self.table_distance_to_time.setFixedHeight(340)
        for row, (label, km) in enumerate(distances):
            t = km * pace_min_per_km
            time_str = format_time(t)
            self.table_distance_to_time.setItem(row, 0, QTableWidgetItem(label))
            self.table_distance_to_time.setItem(row, 1, QTableWidgetItem(time_str))

        self.table_time_to_distance.setRowCount(len(times))
        self.table_time_to_distance.setFixedHeight(340)
        for row, (label, mins) in enumerate(times):
            km = mins / pace_min_per_km
            km_str = f"{km:.2f}"
            self.table_time_to_distance.setItem(row, 0, QTableWidgetItem(label))
            self.table_time_to_distance.setItem(row, 1, QTableWidgetItem(km_str))

    def calculate(self):
        try:
            self.fill_pace_speed_input()

            pace_text = self.pace_input.text().strip()
            speed_text = self.speed_input.text().strip()

            pace_min_per_km = None

            if pace_text:
                if not pace_text.isdigit() or len(pace_text) < 3:
                    raise ValueError("配速应为3~4位数字，例如500表示5分0秒，445表示4分45秒，1230表示12分30秒")
                seconds = int(pace_text[-2:])
                minutes = int(pace_text[:-2])
                if seconds >= 60:
                    raise ValueError("秒数应小于60")
                pace_min_per_km = minutes + seconds / 60
                if pace_min_per_km == 0:
                    raise ValueError("配速不能为0")
            elif speed_text:
                speed_kmh = float(speed_text)
                if speed_kmh == 0:
                    raise ValueError("时速不能为0")
                pace_min_per_km = 60 / speed_kmh
            else:
                raise ValueError("请输入配速或时速之一")

            self.generate_tables(pace_min_per_km)

        except Exception as e:
            QMessageBox.warning(self, "输入错误", str(e))

    def reset_fields(self):
        self.pace_input.clear()
        self.speed_input.clear()
        self.table_distance_to_time.clearContents()
        self.table_distance_to_time.setRowCount(0)
        self.table_time_to_distance.clearContents()
        self.table_time_to_distance.setRowCount(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaceCalculator()
    window.show()
    sys.exit(app.exec())
