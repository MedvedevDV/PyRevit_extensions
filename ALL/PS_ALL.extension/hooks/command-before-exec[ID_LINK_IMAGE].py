# -*- coding: utf-8 -*-
#⬇️ Imports
import clr
import datetime
clr.AddReference('System.Windows.Forms')  # Явно добавляем ссылку на библиотеку Windows Forms
clr.AddReference('System.Drawing')  # Для работы с координатами и графическими объектами

from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult, FormStartPosition, FormBorderStyle
import System.Drawing  # Для работы с координатами и точками
from pyrevit import revit, EXEC_PARAMS
from Autodesk.Revit.UI import TaskDialog

# Функция для генерации пароля на основе текущей даты
def generate_password():
    today = datetime.datetime.now()
    day = today.day
    month = today.month

    # Получаем цифры для пароля
    day_str = str(day).zfill(2)  # Преобразуем день в строку и добавляем ведущий ноль, если необходимо
    month_str = str(month).zfill(2)  # То же самое для месяца

    # Формируем пароль: первая цифра дня, первая цифра месяца, вторая цифра дня, вторая цифра месяца
    password = day_str[0] + month_str[0] + day_str[1] + month_str[1]
    return password

# Класс для формы с вводом пароля
class PasswordForm(Form):
    def __init__(self, x, y):
        self.Text = 'Действие запрещено!'
        self.Width = 255  # Фиксированная ширина формы
        self.Height = 150  # Фиксированная высота формы
        self.StartPosition = FormStartPosition.Manual  # Устанавливаем позицию вручную
        self.Location = System.Drawing.Point(x, y)  # Устанавливаем позицию формы
        
        # Запрет изменения размеров окна
        self.FormBorderStyle = FormBorderStyle.FixedDialog  # Фиксированный стиль рамки
        self.MaximizeBox = False  # Убираем кнопку максимизации
        self.MinimizeBox = False  # Убираем кнопку минимизации

        # Добавляем метку
        label = Label()
        label.Text = 'Введите пароль для продолжения:'
        label.Top = 20
        label.Left = 20
        label.Width = 260  # Ширина метки
        label.AutoSize = False  # Отключаем автоматическую подстройку под размер
        self.Controls.Add(label)

        # Поле для ввода пароля
        self.password_box = TextBox()
        self.password_box.Left = 20
        self.password_box.Top = 50
        self.password_box.Width = 200
        self.password_box.UseSystemPasswordChar = True  # Маскирует вводимые символы
        self.Controls.Add(self.password_box)

        # Кнопка OK
        button_ok = Button()
        button_ok.Text = 'OK'
        button_ok.Left = 20
        button_ok.Top = 80
        button_ok.DialogResult = DialogResult.OK
        self.Controls.Add(button_ok)

        # Кнопка Отмена
        button_cancel = Button()
        button_cancel.Text = 'Отмена'
        button_cancel.Top = 80
        button_cancel.Left = 145  # Устанавливаем позицию кнопки "Отмена" к правому краю
        button_cancel.DialogResult = DialogResult.Cancel
        self.Controls.Add(button_cancel)

        self.AcceptButton = button_ok  # Устанавливаем кнопку OK как кнопку по умолчанию
        self.CancelButton = button_cancel  # Устанавливаем кнопку отмены как кнопку отмены по умолчанию

#📦 Variables
sender = __eventsender__  # UIApplication
args = __eventargs__      # Autodesk.Revit.UI.Events.BeforeExecutedEventArgs

doc = revit.doc

# Получаем имя текущего пользователя через doc.Application.Username
current_user = doc.Application.Username

# Список разрешенных пользователей, для которых не нужно вводить пароль
allowed_users = ["legostaev", "chernova.a", "medvedev"]

# Если текущий пользователь не в списке разрешенных, показываем окно с паролем
if current_user not in allowed_users:
    # Генерируем пароль
    calculated_password = generate_password()  # Пароль на основе текущей даты

    # Получаем координаты курсора
    cursor_position = System.Windows.Forms.Cursor.Position  # Получаем текущие координаты курсора

    #🎯 MAIN
    # Пропускаем окно предупреждения и сразу показываем ввод пароля
    form = PasswordForm(cursor_position.X-130, cursor_position.Y-80)
    result = form.ShowDialog()

    # Проверяем, была ли нажата кнопка "Отмена"
    if result == DialogResult.Cancel:
        args.Cancel = True  # Отмена действия, если нажали на кнопку "Отмена"
    else:  # Если нажата кнопка "OK"
        user_input = form.password_box.Text  # Получаем введенный пароль

        # ❌ Stop Execution if password is incorrect
        if user_input != calculated_password:
            args.Cancel = True
