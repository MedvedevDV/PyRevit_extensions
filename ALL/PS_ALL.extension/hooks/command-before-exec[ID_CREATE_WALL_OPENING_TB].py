# -*- coding: utf-8 -*-
#⬇️ Imports
import clr
import datetime
clr.AddReference('System.Windows.Forms')  # Явно добавляем ссылку на библиотеку Windows Forms
clr.AddReference('System.Drawing')  # Для работы с координатами и графическими объектами

from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult, FormStartPosition, FormBorderStyle
import System.Drawing 
from pyrevit import revit, EXEC_PARAMS
from Autodesk.Revit.UI import TaskDialog

def generate_password():
    today = datetime.datetime.now()
    day = today.day
    month = today.month

    day_str = str(day).zfill(2) 
    month_str = str(month).zfill(2)

    password = day_str[0] + month_str[0] + day_str[1] + month_str[1]
    return password


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
#📦 Variables
sender = __eventsender__  # UIApplication
args = __eventargs__      # Autodesk.Revit.UI.Events.BeforeExecutedEventArgs

doc = revit.doc

current_user = doc.Application.Username

allowed_users = ["legostaev", "chernova.a", "medvedev"]


if current_user not in allowed_users:
    calculated_password = generate_password()
    cursor_position = System.Windows.Forms.Cursor.Position

    #🎯 MAIN
    form = PasswordForm(cursor_position.X-130, cursor_position.Y-80)
    result = form.ShowDialog()

    if result == DialogResult.Cancel:
        args.Cancel = True 
    else:
        user_input = form.password_box.Text
        if user_input != calculated_password:
            args.Cancel = True
