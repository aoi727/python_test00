from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QStyledItemDelegate, QComboBox, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt, QAbstractTableModel


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, data_table, parent=None):
        """
        data_table: [[value, display], [value, display], ...]
        """
        super().__init__(parent)
        self.data_table = data_table

    def createEditor(self, parent, option, index):
        # コンボボックスをエディタとして作成
        combo = QComboBox(parent)

        # データテーブルから値と表示文字列をセット
        for value, display in self.data_table:
            combo.addItem(display, value)

        return combo

    def setEditorData(self, editor, index):
        # モデルの値を取得してコンボボックスで選択
        if isinstance(editor, QComboBox):
            current_value = index.model().data(index, Qt.EditRole)
            combo_index = editor.findData(current_value)
            if combo_index != -1:
                editor.setCurrentIndex(combo_index)

    def setModelData(self, editor, model, index):
        # コンボボックスの選択値をモデルに設定
        if isinstance(editor, QComboBox):
            selected_value = editor.currentData()
            model.setData(index, selected_value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        # エディタの表示位置を設定
        editor.setGeometry(option.rect)


class TableModel(QAbstractTableModel):
    def __init__(self, data, headers, combo_data, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers

        # コンボボックスデータからマッピングを動的に生成
        self._mapping = {value: display for value, display in combo_data}

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])

    def data(self, index, role):
        if not index.isValid():
            return None

        value = self._data[index.row()][index.column()]

        if role == Qt.DisplayRole:
            # 特定の列（例: 2列目）で値を文字列に変換して表示
            if index.column() == 1:  # 2列目
                return self._mapping.get(value, "不明")
            return value

        if role == Qt.EditRole:
            # 編集時には元の値を返す
            return value

        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        # 編集可能にする
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            else:
                return section + 1
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # データとヘッダー
        data = [
            [1, 101, 3],
            [2, 201, 1],
            [3, 311, 2]
        ]
        headers = ["列1", "列2（口座）", "列3"]

        # コンボボックス用のデータテーブル
        combo_data = [
            [101, "現金"],
            [201, "普通預金"],
            [311, "未払金"]
        ]

        # モデルとビューの設定
        model = TableModel(data, headers, combo_data)
        table_view = QTableView()
        table_view.setModel(model)

        # 2列目をコンボボックスにする
        combo_delegate = ComboBoxDelegate(combo_data)
        table_view.setItemDelegateForColumn(1, combo_delegate)

        # レイアウト設定
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(table_view)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
