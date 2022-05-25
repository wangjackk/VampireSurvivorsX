import os
import sys
import time
import string
from copy import deepcopy
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QScrollArea, QGroupBox, QLabel, QLineEdit, QMessageBox, \
    QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QFont, QPen
from PyQt5.QtCore import QSize, Qt, QRect, pyqtSignal
from PyQt5.Qt import QIntValidator, QDoubleValidator


def get_bundle(bundle_path):
    with open(bundle_path, encoding='utf-8') as f:
        text = f.readlines()
        text = ''.join(text)
        text = text.strip('\n')
    return text


def find(txt: str, sig='name'):
    records = []
    pos = 0
    length = len(sig)
    while True:
        num = txt.find(sig)
        if num == -1:
            break
        else:
            pos += num
        records.append(pos)
        txt = txt[num + length:]
        pos += length
    return records


def get_attribute(line: str, attr='charName', attr_is_sig=False):
    sig = attr
    if not attr_is_sig:
        sig = "'" + attr + "':"
    pos = line.find(sig)
    if pos > -1:
        line = line[pos:]
        length = line.find(',')
        if length < 0:
            length = len(line)
        return line[len(sig):length], pos + len(sig), length - len(sig)
    else:
        return ''


def get_hero_dic_from_line_with_pos(line_with_pos, attr_is_sig=False):
    line, pos, length = line_with_pos
    _hero_dic = {'js_pos_and_length': (pos, length)}
    for attr in ATTRIBUTES:
        _hero_dic[attr] = get_attribute(line, attr=attr, attr_is_sig=attr_is_sig)
    return _hero_dic


def get_hero_dic_from_line(line, attr_is_sig=False):
    _hero_dic = {}
    for attr in ATTRIBUTES:
        _hero_dic[attr] = get_attribute(line, attr=attr, attr_is_sig=attr_is_sig)
    return _hero_dic


def get_heroes_dic_with_pos_from_line_with_pos(lines_with_pos, attr_is_sig=False):
    dic = []
    for line in lines_with_pos:
        hero_dic = get_hero_dic_from_line_with_pos(line, attr_is_sig=attr_is_sig)
        dic.append(hero_dic)
    return dic


def hero_dic_with_pos_to_hero_dic(hero_dic_with_pos):
    _hero_dic = {}
    for attr in ATTRIBUTES:
        v = hero_dic_with_pos[attr]
        _hero_dic[attr] = v[0] if v else ''
    return _hero_dic


def get_heroes_line_with_pos(text: str, clip_length=600, sig="'charName':"):
    pos_all = find(text, sig=sig)
    _heroes_line = []
    for i in range(len(pos_all) - 1):
        s = pos_all[i]
        t = text[s:s + clip_length]
        line = (t, s, clip_length)
        _heroes_line.append(line)
    return _heroes_line


def dic_to_str(dic: dict):
    text = ''
    for key, value in dic.items():
        if key != 'js_pos_and_length':
            line = key + ':' + str(value) + ','
            text += line
    return text


def has_letter(strings):
    letters = string.ascii_letters
    for i in strings:
        if i in letters:
            return True
    return False


def generate_hero_txt_from_original_txt(bundle_path, save_dic_path=''):
    bundle = get_bundle(bundle_path)

    pos_data = [('top', 0)]
    heroes_dic = get_heroes_dic_with_pos(bundle_path=bundle_path)
    for hero in heroes_dic:
        pos = hero['js_pos_and_length'][0]
        name = hero['charName'][0].strip("'")
        if 'LATO' not in name:
            last_name = pos_data[-1][0]
            start = pos_data[-1][1]
            end = pos
            pos_data[-1] = (last_name, (start, end))
            pos_data.append((name, end))
        else:
            last_name = pos_data[-1][0]
            start = pos_data[-1][1]
            end = pos
            pos_data[-1] = (last_name, (start, end))

            start = end
            end = len(bundle)
            pos_data.append(('end', (start, end)))
            break
    heroes_names = []
    for data in pos_data:
        name, pos = data
        s, e = pos
        text = bundle[s:e]
        name = name if has_letter(name) else 'hero_' + str(pos)
        name = name.replace('\\', '')
        name = name.replace("'", '')
        name = name.replace(' ', '')
        heroes_names.append(name)
        name = os.path.join(save_dic_path, name.strip("'") + '.txt')
        with open(name, 'w', encoding='utf-8') as f:
            f.write(text)
    return heroes_names


def get_heroes_dic_with_pos(bundle_path):
    bundle = get_bundle(bundle_path=bundle_path)
    lines = get_heroes_line_with_pos(text=bundle)
    return get_heroes_dic_with_pos_from_line_with_pos(lines_with_pos=lines)


def get_heroes_dic_(bundle_path):
    bundle = get_bundle(bundle_path=bundle_path)
    lines = get_heroes_line_with_pos(text=bundle)
    heroes_dic_with_pos = get_heroes_dic_with_pos_from_line_with_pos(lines_with_pos=lines)
    heroes_dic = []
    for hero_dic in heroes_dic_with_pos:
        dic = hero_dic_with_pos_to_hero_dic(hero_dic)
        heroes_dic.append(dic)
    return heroes_dic


def get_heroes_dic(bundle_path):
    heroes_dic = get_heroes_dic_(bundle_path=bundle_path)
    heroes = {}
    for i in heroes_dic:
        name = i.pop('charName').strip("'")
        heroes[name] = i
    return heroes


def alter_hero_attributes_by_txt(hero_txt_path, attributes_dic):
    """
    :param hero_txt_path: txt_path
    :param attributes_dic: {'maxHp': '0x64', 'power': '0x66'}
    """
    line = get_bundle(hero_txt_path)
    for attr, v in attributes_dic.items():
        if attr in line:
            _, pos, length = get_attribute(line=line, attr=attr)
            line = line[:pos] + attributes_dic[attr] + line[pos + length:]
    with open(hero_txt_path, 'w', encoding='utf-8') as f:
        f.write(line)


def alter_hero_attributes_by_name(hero_name, attributes_dic, hero_txt_dic_path):
    path = os.path.join(hero_txt_dic_path, hero_name + '.txt')
    alter_hero_attributes_by_txt(hero_txt_path=path, attributes_dic=attributes_dic)


def alter_heroes_attributes_by_name(new_heroes_attrs, hero_txt_dic_path):
    for hero_name, attrs in new_heroes_attrs.items():
        alter_hero_attributes_by_name(hero_name=hero_name, attributes_dic=attrs, hero_txt_dic_path=hero_txt_dic_path)


def merge_heroes_txt(txt_dic, top_heroes_end, save_path=''):
    text = ''
    for name in top_heroes_end:
        name += '.txt'
        txt_path = os.path.join(txt_dic, name)
        bundle = get_bundle(txt_path)
        text += bundle
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(text)


def copy_original_bundle(bundle_path, save_path):
    from shutil import copyfile
    copyfile(bundle_path, save_path)


def get_real_heroes_dic(bundle_path):
    heroes_dic = get_heroes_dic(bundle_path=bundle_path)
    dic = {}
    for name, attrs in heroes_dic.items():
        if 'LATO' not in name:
            name = name.replace('\\', '')
            name = name.replace(' ', '')
            name = name.replace("'", '')
            if has_letter(name):
                dic[name] = attrs
    return dic


class HeroesData:
    def __init__(self, old_js_path, now_js_path):
        self.old_txt_path = old_js_path
        self.now_txt_path = now_js_path
        self.old_heroes_dict = get_real_heroes_dic(bundle_path=old_js_path)
        self.now_heroes_dict = get_real_heroes_dic(bundle_path=ChangedBundlePath)
        self.trans_to_int()
        self.add_powerUp()
        self.heroes = list(self.old_heroes_dict.keys())

    def getHeroAttribute(self, name, attribute, kind='now'):
        hero = self.getHero(name=name, kind=kind)
        return hero[attribute]

    def setHeroAttribute(self, name, attribute, value):
        self.now_heroes_dict[name][attribute] = value

    def getHero(self, name, kind='now'):
        dic = self.now_heroes_dict
        if kind == 'old':
            dic = self.old_heroes_dict
        elif kind == 'now':
            dic = self.now_heroes_dict
        return dic[name]

    def trans_to_int(self):
        self.old_heroes_dict = heroes_attrs_hex_to_int(heroes_dict=self.old_heroes_dict)
        self.now_heroes_dict = heroes_attrs_hex_to_int(heroes_dict=self.now_heroes_dict)

    def add_powerUp(self):
        self.old_heroes_dict = heroes_addPowerUp(self.old_heroes_dict)
        self.now_heroes_dict = heroes_addPowerUp(self.now_heroes_dict)

    def save_bundle(self):
        save_dict = heroes_deletePowerUp(self.now_heroes_dict)
        save_dict = heroes_attrs_int_to_hex(heroes_dict=save_dict)
        hero_names = generate_hero_txt_from_original_txt(bundle_path=BundlePath, save_dic_path=HeroTxtPath)
        alter_heroes_attributes_by_name(new_heroes_attrs=save_dict, hero_txt_dic_path=HeroTxtPath)
        merge_heroes_txt(txt_dic=HeroTxtPath, top_heroes_end=hero_names, save_path=ChangedBundlePath)

    def startGame(self):
        self.save_bundle()
        # #  copy
        copy_original_bundle(bundle_path=BundlePath, save_path=BundleCopyPath)
        #  started altered
        copy_original_bundle(bundle_path=os.path.join(HeroTxtPath, 'main.bundle.js'), save_path=BundlePath)
        os.startfile(EXEPath)
        time.sleep(3)

        # #  recover main.bundle.js
        copy_original_bundle(bundle_path=BundleCopyPath, save_path=BundlePath)


def attr_hex_to_int(attr_str):
    if attr_str:
        return eval(attr_str)
    else:
        return 0


def attr_int_to_hex(attr_int):
    if type(attr_int) == int:
        attr_int = hex(attr_int)
    elif type(attr_int) == float:
        if attr_int == round(attr_int):
            attr_int = round(attr_int)
            attr_int = hex(attr_int)

        attr_int = str(attr_int)
    return attr_int


def hero_attrs_hex_to_int(hero_dict: dict):
    new_dict = {}
    for attr_name, attr_str in hero_dict.items():
        new_dict[attr_name] = attr_hex_to_int(attr_str)
    return new_dict


def hero_attrs_int_to_hex(hero_dict: dict):
    new_dict = {}
    for attr_name, attr_str in hero_dict.items():
        new_dict[attr_name] = attr_int_to_hex(attr_str)
    return new_dict


def heroes_attrs_hex_to_int(heroes_dict: dict):
    new_dict = {}
    for name, hero_dict in heroes_dict.items():
        new_dict[name] = hero_attrs_hex_to_int(hero_dict=hero_dict)

    return new_dict


def heroes_attrs_int_to_hex(heroes_dict: dict):
    new_dict = {}
    for name, hero_dict in heroes_dict.items():
        new_dict[name] = hero_attrs_int_to_hex(hero_dict=hero_dict)

    return new_dict


def addPowerUp(attr_name, base_attr_value):
    value = 0
    power_up = PowerUp[attr_name]
    if attr_name == 'maxHp':
        value = round(base_attr_value * (1 + power_up))
    elif attr_name == 'armor':
        value = base_attr_value - power_up
    elif attr_name in ['moveSpeed', 'area', 'speed', 'power', 'cooldown', 'duration', 'luck', 'growth', 'greed',
                       'curse']:
        value = round(base_attr_value + power_up - 1, 2)
    elif attr_name in ['magnet', 'regen', 'amount', 'revivals', 'rerolls', 'skips', 'banish']:
        value = base_attr_value + power_up
    return value


def deletePowerUp(attr_name, attr_value):
    base_attr_value = 0
    power_up = PowerUp[attr_name]
    if attr_name == 'maxHp':
        base_attr_value = round(attr_value / (1 + power_up))
    elif attr_name == 'armor':
        base_attr_value = attr_value + power_up
    elif attr_name in ['moveSpeed', 'area', 'speed', 'power', 'cooldown', 'duration', 'luck', 'growth', 'greed',
                       'curse']:
        base_attr_value = round(attr_value - power_up + 1, 2)
    elif attr_name in ['magnet', 'regen', 'amount', 'revivals', 'rerolls', 'skips', 'banish']:
        base_attr_value = round(attr_value - power_up, 2)
    return base_attr_value


def hero_addPowerUp(hero_attrs_dict: dict):
    new_dict = {}
    for attr_name, value in hero_attrs_dict.items():
        new_dict[attr_name] = addPowerUp(attr_name=attr_name, base_attr_value=value)
    return new_dict


def hero_deletePowerUp(hero_attrs_dict: dict):
    new_dict = {}
    for attr_name, value in hero_attrs_dict.items():
        new_dict[attr_name] = deletePowerUp(attr_name=attr_name, attr_value=value)
    return new_dict


def heroes_addPowerUp(heroes_dict):
    new_dict = {}
    for name, attrs_dict in heroes_dict.items():
        new_dict[name] = hero_addPowerUp(hero_attrs_dict=attrs_dict)
    return new_dict


def heroes_deletePowerUp(heroes_dict):
    new_dict = {}
    for name, attrs_dict in heroes_dict.items():
        new_dict[name] = hero_deletePowerUp(hero_attrs_dict=attrs_dict)
    return new_dict


def get_row_col(max_cols=4, num=5):
    row = num // max_cols
    col = num % 4
    if col == 0:
        col = 4
    else:
        row += 1
    return row, col


def get_rect(w, h, width_scale=16, height_scale=10):
    if w > h * width_scale / height_scale:
        w_ = h * width_scale / height_scale
        h_ = h

        x = (w - w_) / 2
        y = 0
    else:
        w_ = w
        h_ = w / width_scale * height_scale
        x = 0
        y = (h - h_) / 2

    return QRect(round(x), round(y), round(w_), round(h_))


def attr_value_to_percent(attr_name, attr_value):
    if attr_name in ['maxHp', 'revivals', 'rerolls', 'banish', 'amount', 'skips', 'armor']:
        attr_value = round(attr_value)
    elif attr_name == 'regen':
        attr_value = round(attr_value, 1)
    else:
        attr_value = round(attr_value * 100)
    return attr_value


def percent_value_to_normal(attr_name, attr_value):
    if attr_name in ['maxHp', 'revivals', 'rerolls', 'banish', 'amount', 'skips', 'armor']:
        attr_value = round(attr_value)
    elif attr_name == 'regen':
        attr_value = round(attr_value, 1)
    else:
        attr_value = round(attr_value / 100, 2)
    return attr_value


class PowerUpItem:
    def __init__(self, attr, level, max_level, change_size):
        self.attr = attr
        self.level = level
        self.max_level = max_level
        self.change_size = change_size
        self.value = round(level * change_size, 2)

    def levelUp(self):
        self.level = min(self.level + 1, self.max_level)
        self.value = round(self.level * self.change_size, 2)

    def levelDown(self):
        self.level = max(self.level - 1, 0)
        self.value = round(self.level * self.change_size, 2)

    def setLevel(self, level):
        self.level = min(level, self.max_level)
        self.level = max(level, 0)
        self.value = round(self.level * self.change_size, 2)


class PowerUpData:
    def __init__(self, power_up_txt_path=''):
        self.power_up = {}
        self.power_up_ = {'power': (0.05, 5), 'armor': (-1, 3), 'maxHp': (0.1, 3), 'regen': (0.1, 5),
                          'cooldown': (-0.025, 2), 'area': (0.05, 2), 'speed': (0.1, 2), 'duration': (0.15, 2),
                          'amount': (1, 1), 'moveSpeed': (0.05, 2), 'magnet': (0.25, 2), 'luck': (0.1, 3),
                          'growth': (0.03, 5), 'greed': (0.1, 5), 'curse': (0.1, 5), 'revivals': (1, 1),
                          'rerolls': (1, 3), 'skips': (2, 2), 'banish': (1, 2)}
        self.initData()
        if power_up_txt_path:
            self.loadPowerUpTxt(power_up_txt_path)

    def initData(self):
        for attr, data in self.power_up_.items():
            change_size, max_level = data
            item = PowerUpItem(attr=attr, level=max_level, max_level=max_level, change_size=change_size)
            self.power_up[attr] = item

    def levelUp(self, attr):
        self.power_up[attr].levelUp()

    def levelDown(self, attr):
        self.power_up[attr].levelDown()

    def get_max_level(self, attr):
        return self.power_up[attr].max_level

    def get_level(self, attr):
        return self.power_up[attr].level

    def set_level(self, attr, level):
        self.power_up[attr].setLevel(level=level)

    def get_value(self, attr):
        return self.power_up[attr].value

    def toPowerUp(self):
        power_up = {}
        for attr in self.power_up.keys():
            power_up[attr] = self.get_value(attr)
        return power_up

    def toPowerUpTxt(self, save_txt_path):
        with open(save_txt_path, 'w', encoding='utf-8') as f:
            lines = []
            for attr, power_up_item in self.power_up.items():
                level = power_up_item.level
                line = attr + ',' + str(level) + '\n'
                lines.append(line)
            f.writelines(lines)

    def loadPowerUpTxt(self, load_txt_path):
        with open(load_txt_path, encoding='utf-8') as f:
            lines = f.read().splitlines()
        for line in lines:
            attr, level = line.split(',')
            self.set_level(attr=attr, level=eval(level))


class HeroButton(QPushButton):
    def __init__(self, parent, num, hero_name, max_cols=4):
        super().__init__(parent=parent)
        self.parent = parent
        self.name = hero_name
        self.num = num
        self.max_cols = max_cols

        self.btn_width = 0
        self.space = 0
        self.cell_width = 0
        self.row_col = (0, 0)

        self.start_xy = (0, 0)
        self.row_col = get_row_col(max_cols=4, num=self.num)

        self.initUI()

    def initUI(self):
        self.update_btn_width_and_space(self.parent.width())
        self.setStyleSheet(HeroButtonStyleSheet.replace('FONTSIZE', str(round(self.btn_width / 5))))
        self.resize(self.btn_width, self.btn_width)
        self.change_geometry()

        self.clicked.connect(lambda: self.parent.change_selected_signal((self.geometry(), self.num, self.name)))

    def Update(self, parent_window_width):
        self.update_btn_width_and_space(parent_window_width=parent_window_width)
        self.setStyleSheet(HeroButtonStyleSheet.replace('FONTSIZE', str(round(self.btn_width / 8))))
        self.change_geometry()
        self.load_icon()

    def change_geometry(self):
        start_x, start_y = self.start_xy
        r, c = self.row_col
        cell_x = (c - 1) * self.cell_width + start_x
        cell_y = (r - 1) * self.cell_width + start_y
        btn_x = round(cell_x + self.space / 2)
        btn_y = round(cell_y + self.space / 2)
        self.setGeometry(btn_x, btn_y, self.btn_width, self.btn_width)

    def load_icon(self):
        icon_path = os.path.join(HeroImgPath, self.name + '.png')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setIcon(icon)
            self.setIconSize(QSize(self.btn_width, self.btn_width))
        else:
            self.setText(self.name)

    def update_btn_width_and_space(self, parent_window_width):
        p_width = parent_window_width
        self.cell_width = p_width / 4
        self.btn_width = round(self.cell_width * 0.885)
        self.space = round(self.cell_width - self.btn_width)

    def resizeEvent(self, event):
        selected_hero_num = self.parent.selected_hero_info[-1]
        if selected_hero_num == self.num:
            self.parent.change_selected_signal((self.geometry(), self.num, ''))


class Window(QWidget):
    windowWidthChangedSignal = pyqtSignal(int)
    selectedHeroNameChangedSignal = pyqtSignal(str)

    def __init__(self, heroes):
        super(Window, self).__init__()
        self.selectedName = None
        self.resize(500, 500)
        self.heroes = heroes
        self.hero_buttons = []
        self.selected_hero_info = (0, 0, 0, 0, 0)  # rect, num
        self.initUI()

    def initUI(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMinimumSize(200, 500)
        self.setMaximumSize(1000, 1500)
        self.setStyleSheet('QWidget{background:rgb(75, 79, 116)}')
        self.init_hero_buttons()

    def change_selected_signal(self, hero_info):
        geometry, num, name = hero_info
        if name:
            self.selectedName = name
            self.selectedHeroNameChangedSignal.emit(name)
        x = geometry.x()
        y = geometry.y()
        w = geometry.width()
        h = geometry.height()
        self.selected_hero_info = (x, y, w, h, num)
        self.update()

    def getSelectedSignalRect(self):
        x, y, w, h = self.selected_hero_info[:4]
        selected_w = round(w * 250 / 227)
        selected_h = selected_w
        dx = (selected_w - w) / 2
        x -= dx
        dy = (selected_h - h) / 2
        y -= dy
        return QRect(round(x), round(y), selected_w, selected_h)

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        pixmap = QPixmap(SelectedSignalImgPath)
        p.drawPixmap(self.getSelectedSignalRect(), pixmap)
        p.end()

    def init_hero_buttons(self):
        names = self.heroes
        names = [i for i in names if has_letter(i)]
        for num, name in enumerate(names):
            btn = HeroButton(self, num + 1, name)
            self.windowWidthChangedSignal.connect(btn.Update)
            self.hero_buttons.append(btn)

    def resizeEvent(self, event):
        self.resize(self.parent().width(), round(self.hero_buttons[-1].y() + 2.5 * self.hero_buttons[-1].btn_width))
        self.windowWidthChangedSignal.emit(self.width())


class HeroScrollArea(QScrollArea):
    def __init__(self, parent, heroes):
        super(HeroScrollArea, self).__init__(parent=parent)
        self.widget = Window(heroes=heroes)
        self.setWidget(self.widget)
        self.initUI()

    def initUI(self):
        self.setMaximumSize(1000, 1000)
        self.setStyleSheet(ScrollAreaStyleSheet)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        self.widget.resizeEvent(0)  # 通知子控件

        self.verticalScrollBar().setMaximumHeight(round(self.height() * 0.8))

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()
        y = round(0.094 * h)
        self.setGeometry(0, y, w, h)


class AttributeLineEdit(QLineEdit):
    def __init__(self, parent):
        super(AttributeLineEdit, self).__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.updateGeometry()
        self.setStyleSheet("""
                            * {
                                outline: none;
                            }

                            QDialog {
                                background: #D6DBE9;
                            }

                            QLineEdit {
                                border: 1px solid #A0A0A0; /* 边框宽度为1px，颜色为#A0A0A0 */
                                border-radius: 3px; /* 边框圆角 */
                                padding-left: 5px; /* 文本距离左边界有5px */
                                background-color: #F2F2F2; /* 背景颜色 */
                                color: #A0A0A0; /* 文本颜色 */
                                selection-background-color: #A0A0A0; /* 选中文本的背景颜色 */
                                selection-color: #F2F2F2; /* 选中文本的颜色 */
                                font-family: "Microsoft YaHei"; /* 文本字体族 */
                                font-size: 10pt; /* 文本字体大小 */
                            }

                            QLineEdit:hover { /* 鼠标悬浮在QLineEdit时的状态 */
                                border: 1px solid #298DFF;
                                border-radius: 3px;
                                background-color: #F2F2F2;
                                color: #298DFF;
                                selection-background-color: #298DFF;
                                selection-color: #F2F2F2;
                            }

                            QLineEdit[echoMode="2"] { /* QLineEdit有输入掩码时的状态 */
                                lineedit-password-character: 9679;
                                lineedit-password-mask-delay: 2000;
                            }

                            QLineEdit:disabled { /* QLineEdit在禁用时的状态 */
                                border: 1px solid #CDCDCD;
                                background-color: #CDCDCD;
                                color: #B4B4B4;
                            }

                            QLineEdit:read-only { /* QLineEdit在只读时的状态 */
                                background-color: #CDCDCD;
                                color: #F2F2F2;
                            }
                            """)

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()
        x = round((w - self.width()) / 2)
        y = round(h * 1 / 3 - self.height() / 2)
        nw = round(0.3 * w)
        nh = round(0.2 * h)

        self.setGeometry(x, y, nw, nh)

    def readyShow(self, hero_name, attr_name):
        if attr_name == 'regen':
            self.setValidator(QDoubleValidator(-999999999.0, 999999999.0, 1))
        else:
            self.setValidator(QIntValidator())
        attr_value = HeroesInfo.getHeroAttribute(name=hero_name, attribute=attr_name)
        attr_value = attr_value_to_percent(attr_name=attr_name, attr_value=attr_value)
        self.setText(str(attr_value))
        self.show()


class OkButton(QPushButton):
    def __init__(self, parent):
        super(OkButton, self).__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.setText('OK')
        self.updateGeometry()
        self.setStyleSheet("""QPushButton{background:yellow;}""")

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()
        x = round((w - self.width()) / 2)
        y = round(h * 2 / 3 - self.height() / 2)
        nw = round(0.3 * w)
        nh = round(0.2 * h)
        self.setGeometry(x, y, nw, nh)


class SignLabel(QLabel):
    def __init__(self, parent):
        super(SignLabel, self).__init__(parent=parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel{background:transparent;font: 14pt Arial;}")


class ChangeAttributeValueWindow(QWidget):
    def __init__(self):
        super(ChangeAttributeValueWindow, self).__init__()
        self.hero_name = None
        self.attr_name = None
        self.resize(300, 150)
        self.input = AttributeLineEdit(parent=self)

        self.signLabel = SignLabel(self)

        self.okButton = OkButton(parent=self)
        self.initUI()

    def initUI(self):
        self.signLabel.setGeometry(200, 35, 30, 30)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.okButton.clicked.connect(self.close)
        self.okButton.clicked.connect(self.changeValue)

    def resizeEvent(self, event):
        self.input.updateGeometry()
        self.okButton.updateGeometry()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.close()
            self.changeValue()

    def changeValue(self):
        value = eval(self.input.text())
        value = percent_value_to_normal(attr_name=self.attr_name, attr_value=value)
        HeroesInfo.setHeroAttribute(name=self.hero_name, attribute=self.attr_name, value=value)

    def readyShow(self, hero_name, attr_name, geometry):
        self.hero_name = hero_name
        self.attr_name = attr_name
        self.resetUI()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        x0 = round(x+w/2-self.width()/2)
        y0 = round(y+h/2-self.height()/2)
        self.setGeometry(x0, y0, self.width(), self.height())
        if not (hero_name == 'Antonio' and attr_name in ['rerolls', 'skips', 'banish']):
            self.show()

    def resetUI(self):
        if self.attr_name in ['moveSpeed', 'power', 'cooldown', 'area', 'speed', 'duration', 'luck', 'growth', 'greed',
                              'curse', 'magnet']:
            self.signLabel.setText('%')
        self.input.readyShow(self.hero_name, self.attr_name)


class AttributeButton(QPushButton):
    def __init__(self, parent, name, geometry):
        super(AttributeButton, self).__init__(parent=parent)
        self.name = name
        self.relative_geometry = geometry
        self.changeValueWindow = ChangeAttributeValueWindow()
        self.initUI()

    def initUI(self):
        self.clicked.connect(self.onChangeValueWindow)
        self.setStyleSheet('''QPushButton{background:rgba(0, 0, 0, 0);}
                              QPushButton::hover{background:rgba(0,255,0,0.4);}''')

    def update_geometry(self, window_size):
        w, h = window_size
        rx, ry, rw, rh = self.relative_geometry
        self.setGeometry(round(w * rx), round(h * ry), round(rw * w), round(rh * h))

    def onChangeValueWindow(self):
        hero_name = self.parent().name
        geometry = self.parent().parent().geometry()
        self.changeValueWindow.readyShow(hero_name=hero_name, attr_name=self.name, geometry=geometry)


class AttributeWindow(QGroupBox):
    windowWidthChangedSignal = pyqtSignal(tuple)

    def __init__(self, parent):
        super(AttributeWindow, self).__init__(parent=parent)
        self.name = None
        self.heroAttrDict = None
        self.attribute_buttons = []
        self.initAttributeButtons()

        self.bg = QPixmap(AttributesBarImgPath)
        self.getAttributeYH()
        self.setEnabled(False)

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        self.showHeroInfo(p)
        p.end()

    def updateCurrentHeroInfo(self, name):
        self.setEnabled(True)
        self.name = name
        self.heroAttrDict = HeroesInfo.getHero(name=name)
        self.update()

    def getAttributeYH(self):
        ry, rh = self.getAttributeRYH()
        y = {}
        for attr, ry_ in ry.items():
            y[attr] = round(ry_ * self.height())
        h = rh * self.height()
        return y, round(h)

    @staticmethod
    def getAttributeRYH():
        attr_list = ['maxHp', 'regen', 'armor', 'moveSpeed', 'power', 'area', 'speed', 'duration', 'amount', 'cooldown',
                     'luck', 'growth', 'greed', 'curse', 'magnet', 'revivals', 'rerolls', 'skips', 'banish']
        dy = 0.04325
        h = 0.054

        attrs_layout = [4, 6, 5, 4]
        r_y_data = [8 / 430, 101 / 430, 232 / 430, 344 / 430]

        def get_space(start_y, space, num):
            y = []
            for i in range(num):
                y.append(start_y + i * space)
            return y

        def get_all_y(layout=(4, 6, 5, 4)):
            y = []
            for n, i in enumerate(layout):
                y.extend(get_space(r_y_data[n], dy, i))
            return y

        y = get_all_y(layout=attrs_layout)
        y = dict(zip(attr_list, y))
        return y, h

    def showHeroInfo(self, p: QPainter):

        def decimal_to_percentage(decimal):
            if decimal > 0:
                return f'+{round(decimal * 100)}%'
            elif decimal < 0:
                return f'-{round(decimal * 100)}%'

        def attr_value_show(attr_name, attr_value):
            if attr_name in ['moveSpeed', 'power', 'cooldown', 'area', 'speed', 'duration', 'luck', 'growth', 'greed',
                             'curse', 'magnet']:
                attr_value = decimal_to_percentage(attr_value)
            elif attr_name not in ['maxHp', 'regen']:
                if attr_value > 0:
                    attr_value = f'+{attr_value}'
                elif attr_value < 0:
                    attr_value = f'-{attr_value}'
            return attr_value

        pen = QPen(Qt.yellow)
        p.setPen(pen)
        font_size = round(0.027 * self.height())
        font = QFont('Times New Roman', font_size)
        font.setBold(True)
        p.setFont(font)
        if self.heroAttrDict:
            p.drawPixmap(self.rect(), self.bg)
            y, h = self.getAttributeYH()
            for attr, y0 in y.items():
                value = self.heroAttrDict[attr]
                value = attr_value_show(attr, value)
                w = round(0.5 * self.width())
                x0 = round(0.922 * self.width() - w)
                p.drawText(QRect(x0, y0, w, h), Qt.AlignRight, str(value))

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()

        rect = get_rect(w, h)
        x0 = rect.x()
        y0 = rect.y()
        w = rect.width()
        h = rect.height()

        x = round(w * 0.0486)
        y = round(0.23 * h)
        w_ = round(0.183 * w)
        h_ = round(w_ * 763 / 415)
        self.setGeometry(x + x0, y + y0, w_, h_)

    def initAttributeButtons(self):
        ry, rh = self.getAttributeRYH()
        for attr, ry0 in ry.items():
            btn = AttributeButton(self, name=attr, geometry=(0.0223, ry0, 0.955, rh))
            self.windowWidthChangedSignal.connect(btn.update_geometry)
            self.attribute_buttons.append(btn)

    def resizeEvent(self, event):
        self.windowWidthChangedSignal.emit((self.width(), self.height()))


class TitleLabel(QLabel):
    def __init__(self, parent):
        super(TitleLabel, self).__init__(parent=parent)
        self.wordsPng = QPixmap(WordsImgPath)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("QLabel{background:rgb(75, 79, 116);border:none;}")

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()
        h = round(h * 0.096)
        self.setGeometry(0, 0, w, h)

    def drawWords(self, p: QPainter):
        x = round(0.138 * self.width())
        y = round(0.35 * self.height())
        w = round(0.72 * self.width())
        h = round(w / 759 * 46)
        p.drawPixmap(QRect(x, y, w, h), self.wordsPng)

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        self.drawWords(p)
        p.end()


class CentralGroupBox(QGroupBox):
    def __init__(self, parent, heroes):
        super(CentralGroupBox, self).__init__(parent=parent)

        self.scrollArea = HeroScrollArea(self, heroes=heroes)
        self.button = Button(parent=self, text='Confirm', geometry=(0.02, 0.89, 0.2, 0.1),
                             bg_path=GreenButton)
        self.resetButton = Button(parent=self, text='Reset', geometry=(0.78, 0.89, 0.2, 0.1),
                                  bg_path=GreenButton)
        self.titleLabel = TitleLabel(self)
        self.initUI()

    def initUI(self):
        self.setStyleSheet(GroupBoxStyleSheet)

        self.button.clicked.connect(self.startGame)
        self.resetButton.clicked.connect(self.reset)

    @staticmethod
    def startGame():
        HeroesInfo.startGame()

    @staticmethod
    def reset():
        HeroesInfo.now_heroes_dict = deepcopy(HeroesInfo.old_heroes_dict)

    def updateGeometry(self):
        w = self.parent().width()
        h = self.parent().height()

        rect = get_rect(w, h)
        x0 = rect.x()
        y0 = rect.y()
        w = rect.width()
        h = rect.height()

        x = round(0.268 * w)
        y = round(0.0935 * h)
        w_ = round(w - 2 * x)
        self.setGeometry(x + x0, y + y0, w_, h - y - 5)
        self.resize(w_, h - y - 5)

    def resizeEvent(self, event):
        self.scrollArea.updateGeometry()  # 通知子控件
        self.titleLabel.updateGeometry()
        self.button.updateGeometry()
        self.resetButton.updateGeometry()


class Button(QPushButton):
    def __init__(self, parent, text, geometry, bg_path='', style_sheet=''):
        super(Button, self).__init__(parent=parent, text=text)
        self.r_geometry = self.getRGeometry(geometry)
        self.bg_path = bg_path
        self.style_sheet = style_sheet
        self.initUI()

    def initUI(self):
        self.updateStylesheet()

    def getRGeometry(self, geometry):
        x, y, w, h = geometry
        if x == 0 or x > 1:
            self.setGeometry(x, y, w, h)
            pw = self.parent().width()
            ph = self.parent().height()
            return x / pw, y / ph, w / pw, h / pw
        else:
            return x, y, w, h

    def updateStylesheet(self):
        font = round(self.width() / 8)
        font = f'font:{font}pt Arial;color:white;'
        if self.bg_path:
            img = f'border-image: url({self.bg_path});'
            style_sheet = 'QPushButton{background:transparent;' + img + font + '}'
        else:
            style_sheet = self.style_sheet
        self.setStyleSheet(style_sheet)

    def updateGeometry(self):
        rx, ry, rw, rh = self.r_geometry
        pw = self.parent().width()
        ph = self.parent().height()
        x = round(rx * pw)
        y = round(ry * ph)
        w = round(rw * pw)
        h = round(rh * ph)
        self.setGeometry(x, y, w, h)
        self.updateStylesheet()


class WindowButton(Button):
    def __init__(self, parent, text, geometry, bg_path=''):
        super().__init__(parent=parent, text=text, geometry=geometry, bg_path=bg_path)

    def updateGeometry(self):
        rx, ry, rw, rh = self.r_geometry
        pw = self.parent().width()
        ph = self.parent().height()
        rect = get_rect(pw, ph)
        x0 = rect.x()
        y0 = rect.y()
        w = rect.width()
        h = rect.height()
        x = round(rx * w) + x0
        y = round(ry * h) + y0
        w = round(rw * w)
        h = round(rh * h)
        self.setGeometry(x, y, w, h)
        self.updateStylesheet()


class MainWindow(QWidget):
    def __init__(self, heroes):
        super(MainWindow, self).__init__()
        self.resize(1280, 800)

        self.setOptionButton = WindowButton(parent=self, text='OPTIONS', geometry=(600, 10, 90, 80),
                                            bg_path=ResourcePath + '/imgs/blue_btn.png')
        self.setOptionWindow = SetOptionWindow()

        self.groupBox = CentralGroupBox(self, heroes=heroes)
        self.attributeBar = AttributeWindow(self)
        self.bg = QPixmap(WindowBackgroundImgPath)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('VampireSurvivorsX')
        self.setStyleSheet("QWidget{background:black;}")

        #  signal-slot
        signal = self.groupBox.scrollArea.widget.selectedHeroNameChangedSignal
        slot = self.attributeBar.updateCurrentHeroInfo
        signal.connect(slot)

        self.setOptionButton.clicked.connect(self.setOptionWindow.show)
        self.setOptionWindow.finishButton.clicked.connect(self.close)

        self.groupBox.resetButton.clicked.connect(
            lambda: self.attributeBar.updateCurrentHeroInfo(self.groupBox.scrollArea.widget.selectedName))

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        p.drawPixmap(get_rect(self.width(), self.height()), self.bg)
        p.end()

    def resizeEvent(self, event):
        self.groupBox.updateGeometry()  # 通知子控件
        self.attributeBar.updateGeometry()
        self.setOptionButton.updateGeometry()


class ChangePowerUpWindow(QWidget):
    def __init__(self, parent, name, attribute, geometry):
        super().__init__(parent=parent)
        self.name = name
        self.attribute = attribute
        self.label = QLabel(name + ': ', self)
        self.addButton = QPushButton('+', self)
        self.reduceButton = QPushButton('-', self)
        self.geometry_ = geometry
        self.initUI()

    def initUI(self):
        x, y, w, h = self.geometry_
        self.setGeometry(x, y, w, h)
        self.label.setGeometry(0, 0, 130, 30)
        self.label.setStyleSheet('QLabel{font: 15px;}')
        self.label.setText(self.name + ': ' + str(PowerUpInfo.get_level(attr=self.attribute)))
        button_style_sheet = "{font:20px}"

        self.addButton.setStyleSheet(button_style_sheet)
        self.addButton.clicked.connect(lambda: self.changeLevel(1))
        self.reduceButton.setStyleSheet(button_style_sheet)
        self.reduceButton.clicked.connect(lambda: self.changeLevel(-1))
        self.addButton.setGeometry(150, 0, 30, 30)
        self.reduceButton.setGeometry(180, 0, 30, 30)

    def changeLevel(self, num=0):
        if num == 1:
            PowerUpInfo.levelUp(self.attribute)
        elif num == -1:
            PowerUpInfo.levelDown(self.attribute)
        self.label.setText(self.name + ': ' + str(PowerUpInfo.get_level(attr=self.attribute)))


class SetOptionWindow(QWidget):
    def __init__(self):
        super(SetOptionWindow, self).__init__()
        if GamePath:
            self.path = GamePath
        else:
            self.path = r'E:\SteamLibrary\steamapps\common\Vampire Survivors'
        self.gamePathLabel = QLabel(self)
        self.powerUpWidgets = []
        self.setGamePathButton = QPushButton('...', self)
        self.finishButton = QPushButton('设置完成,请手动重启', self)
        self.powerUp = {'Might': 'power', 'Armor': 'armor', 'Max Health': 'maxHp', 'Recovery': 'regen',
                        'Cooldown': 'cooldown', 'Area': 'area', 'Speed': 'speed', 'Duration': 'duration',
                        'Amount': 'amount', 'MoveSpeed': 'moveSpeed', 'Magnet': 'magnet', 'Luck': 'luck',
                        'Growth': 'growth', 'Greed': 'greed', 'Curse': 'curse', 'Revival': 'revivals',
                        'Reroll': 'rerolls', 'Skip': 'skips', 'Banish': 'banish'}

        self.initUI()

    def initUI(self):
        self.resize(600, 600)
        self.setWindowModality(Qt.ApplicationModal)
        self.gamePathLabel.setStyleSheet("QLabel{font:15px;background:yellow;}")
        self.gamePathLabel.setGeometry(50, 50, len('游戏目录：' + self.path) * 10, 30)
        self.gamePathLabel.setText('游戏目录：' + self.path)
        self.setGamePathButton.setGeometry(10, 50, 30, 30)
        self.setGamePathButton.clicked.connect(self.setGamePath)
        self.finishButton.clicked.connect(self.close)
        self.finishButton.clicked.connect(self.savePowerUp)

        x = 10
        y = 90
        w = 250
        h = 30
        dy = 10 + h
        n = 0
        for name, attribute in self.powerUp.items():
            window_ = ChangePowerUpWindow(self, name=name, attribute=attribute, geometry=(x, y, w, h))
            self.powerUpWidgets.append(window_)
            y += dy
            n += 1
            if n == 10:
                x += w
                y = 90

    def setGamePath(self):
        global GamePath
        path = QFileDialog.getExistingDirectory(self, 'SetGamePath')
        if path:
            GamePath = path
            self.gamePathLabel.setText(f'游戏目录：{GamePath}')
            path = os.path.join(ResourcePath, 'config\\pathlist.txt')
            with open(path, 'w', encoding='utf-8') as f:
                text = f'GamePath={GamePath}'
                f.write(text)

    @staticmethod
    def savePowerUp():
        PowerUpInfo.toPowerUpTxt(os.path.join(ResourcePath, 'config\\powerUp.txt'))

    def resizeEvent(self, event):
        self.setGamePathButton.updateGeometry()


def getGamePath():
    txt_path = os.path.join(ResourcePath, 'config\\pathlist.txt')
    if os.path.exists(txt_path):
        with open(txt_path, encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            name, path = line.split('=')
            if name == 'GamePath':
                return path
    return None


if __name__ == '__main__':
    # game fp
    # GamePath = r'E:\SteamLibrary\steamapps\common\Vampire Survivors'
    # your fp
    ResourcePath = os.path.dirname(sys.argv[0])
    PowerUpPath = os.path.join(ResourcePath, 'config\\powerUp.txt')
    PowerUpInfo = PowerUpData(PowerUpPath)
    GamePath = getGamePath()
    if not GamePath:
        app = QApplication(sys.argv)
        window = SetOptionWindow()
        window.show()
        sys.exit(app.exec_())
    EXEPath = os.path.join(GamePath, 'VampireSurvivors.exe')
    BundlePath = os.path.join(GamePath, 'resources\\app\\.webpack\\renderer\\main.bundle.js')

    BundleCopyPath = os.path.join(ResourcePath, 'originalBundle\\main.bundle.js')
    ChangedBundlePath = os.path.join(ResourcePath, 'heroes\\main.bundle.js')
    HeroTxtPath = os.path.join(ResourcePath, 'heroes')
    HeroImgPath = os.path.join(ResourcePath, 'imgs')
    SelectedSignalImgPath = os.path.join(HeroImgPath, 'selected.png')
    WindowBackgroundImgPath = os.path.join(HeroImgPath, 'bg.png')
    WordsImgPath = os.path.join(HeroImgPath, 'words.png')
    AttributesBarImgPath = os.path.join(HeroImgPath, 'attrs_bar.png')
    GreenButton = ResourcePath + '/imgs/green_btn.png'

    PowerUp = PowerUpInfo.toPowerUp()
    ATTRIBUTES = ['charName', 'maxHp', 'armor', 'regen', 'moveSpeed', 'power', 'cooldown', 'area',
                  'speed', 'duration', 'amount', 'luck', 'growth', 'greed', 'curse', 'magnet', 'revivals', 'rerolls',
                  'skips', 'banish']

    HeroButtonStyleSheet = '''QPushButton{color:gray;
                                  background-color:rgb(75, 79, 116);
                                  font: FONTSIZEpt "Adobe 楷体 Std R";
                                  border:yellow;}
                               '''
    ScrollAreaStyleSheet = '''
        QScrollArea{background:rgb(75, 79, 116)}
        QScrollBar:vertical {
        background-color: rgb(44, 48, 85);
        width:10px;
        padding: 1px;
        border-radius: 5px;
        }

        /* 中部滑动块 */
        QScrollBar::handle:vertical {
        border: none;
        border-radius: 4px;
        background-color: rgba(255, 255, 0, 128);
        }

        /* 向上滑动按钮 */
        QScrollBar::sub-line:vertical {
        border: none;
        }

        /* 向下滑动按钮 */
        QScrollBar::add-line:vertical {
        border: none;
        }

        /* 滑动块上方空白区域 */
        QScrollBar::add-page:vertical {
        background: rgba(0, 0, 0, 0);
        }

        /* 滑动块下方空白区域 */
        QScrollBar::sub-page:vertical {
        background: rgba(0, 0, 0, 0);
        }

                             '''
    GroupBoxStyleSheet = '''
        QGroupBox{background-color:rgb(75, 79, 116);
        }
        '''
    if not os.path.exists(ChangedBundlePath):
        copy_original_bundle(bundle_path=BundlePath, save_path=ChangedBundlePath)
    HeroesInfo = HeroesData(old_js_path=BundlePath, now_js_path=ChangedBundlePath)
    heroes = HeroesInfo.heroes
    app = QApplication(sys.argv)
    wd = MainWindow(heroes=heroes)
    wd.show()
    sys.exit(app.exec_())
