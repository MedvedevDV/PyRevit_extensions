# -*- coding: utf-8 -*-
import clr
import datetime
import os
import xml.etree.ElementTree as ET
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult, FormStartPosition, FormBorderStyle
import System.Drawing
from pyrevit import revit, EXEC_PARAMS
from Autodesk.Revit.DB import Category
from Autodesk.Revit.UI import TaskDialog
from xml.dom import minidom

# Функция для генерации пароля на основе текущей даты
def generate_password():
    today = datetime.datetime.now()
    day = today.day
    month = today.month

    day_str = str(day).zfill(2)
    month_str = str(month).zfill(2)

    password = day_str[0] + month_str[0] + day_str[1] + month_str[1]
    return password

# Функция для записи отформатированного XML
def write_pretty_xml(filepath, root):
    # Преобразуем дерево XML в строку
    xml_string = ET.tostring(root, encoding='utf-8')
    
    # Используем minidom для форматирования
    formatted_xml = minidom.parseString(xml_string)
    
    # Преобразуем в читаемый формат, убирая лишние отступы
    pretty_xml_as_string = '\n'.join([line for line in formatted_xml.toprettyxml(indent="    ").splitlines() if line.strip()])

    # Открываем файл для записи
    with open(filepath, 'wb') as f:
        f.write(pretty_xml_as_string.encode('utf-8'))

# Функция для записи данных в XML файл
def log_user_data(user_name):
    # Определяем путь к файлу XML (рядом со скриптом)
    xml_file = os.path.join(os.path.dirname(__file__), "password_hide_elements_user_log.xml")
    
    # Проверяем, существует ли файл
    if os.path.exists(xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
    else:
        # Если файл не существует, создаем корневой элемент
        root = ET.Element("UserLog")
        tree = ET.ElementTree(root)

    # Создаем элемент записи
    log_entry = ET.Element("LogEntry")
    user_element = ET.SubElement(log_entry, "User")
    user_element.text = user_name
    time_element = ET.SubElement(log_entry, "Time")
    time_element.text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Добавляем запись в корень
    root.append(log_entry)

    # Сохраняем XML с форматированием
    write_pretty_xml(xml_file, root)


# Класс для формы с вводом пароля
class PasswordForm(Form):
    def __init__(self, x, y):
        self.Text = 'Действие запрещено!'
        self.Width = 255
        self.Height = 150
        self.StartPosition = FormStartPosition.Manual
        self.Location = System.Drawing.Point(x, y)

        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.MaximizeBox = False
        self.MinimizeBox = False

        label = Label()
        label.Text = 'Введите пароль для продолжения:'
        label.Top = 20
        label.Left = 20
        label.Width = 260
        label.AutoSize = False
        self.Controls.Add(label)

        self.password_box = TextBox()
        self.password_box.Left = 20
        self.password_box.Top = 50
        self.password_box.Width = 200
        self.password_box.UseSystemPasswordChar = True
        self.Controls.Add(self.password_box)

        button_ok = Button()
        button_ok.Text = 'OK'
        button_ok.Left = 20
        button_ok.Top = 80
        button_ok.DialogResult = DialogResult.OK
        self.Controls.Add(button_ok)

        button_cancel = Button()
        button_cancel.Text = 'Отмена'
        button_cancel.Top = 80
        button_cancel.Left = 145
        button_cancel.DialogResult = DialogResult.Cancel
        self.Controls.Add(button_cancel)

        self.AcceptButton = button_ok
        self.CancelButton = button_cancel

try:
    #📦 Variables
    sender = __eventsender__
    args = __eventargs__

    doc = revit.doc
    uidoc = revit.uidoc

    # Получаем имя текущего пользователя через doc.Application.Username
    current_user = doc.Application.Username

    # Список разрешенных пользователей, для которых не нужно вводить пароль
    allowed_users = ["legostaev", "chernova.a", "medvedev", "strelbitskaya","shahtarin", "sulzhenko", "VashchenkoAnton", "turusheva"]

    # Если текущий пользователь в списке разрешенных, окно с паролем не показываем
    if current_user in allowed_users:
        pass  # Пропускаем ввод пароля для разрешенных пользователей

    else:
        # Получаем выбранные элементы
        selected_ids = uidoc.Selection.GetElementIds()
        selected_elements = [doc.GetElement(id) for id in selected_ids]

        # Категории, при которых окно не нужно показывать
        excluded_categories = ["Оси", "Уровни","Несущая арматура","Армирование по площади несущей конструкции","Армирование по траектории несущей конструкции","Формы"]

        # Проверяем, есть ли в выбранных элементах категории, отличные от "Оси" и "Уровни"
        show_password_prompt = False
        for element in selected_elements:
            if element.Category and element.Category.Name not in excluded_categories:
                show_password_prompt = True
                break

        # Если есть элементы других категорий, показываем окно с паролем
        if show_password_prompt:
            calculated_password = generate_password()
            cursor_position = System.Windows.Forms.Cursor.Position

            form = PasswordForm(cursor_position.X - 130, cursor_position.Y - 80)
            result = form.ShowDialog()

            if result == DialogResult.Cancel:
                args.Cancel = True
            else:
                user_input = form.password_box.Text
                if user_input != calculated_password:
                    args.Cancel = True
                else:
                    # Логируем данные пользователя при успешном вводе пароля
                    log_user_data(current_user)

except Exception as e:
    # Показываем сообщение с ошибкой в диалоговом окне Revit
    TaskDialog.Show("Ошибка", str(e))
