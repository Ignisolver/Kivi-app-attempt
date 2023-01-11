import numpy as np
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
import pandas as pd
from kivymd.uix.textfield import MDTextField
import os
import shutil
from datetime import datetime

from gdrive_connector import GDriveConnector

from screens import *


class PAPApp(MDApp):
    data = {
        "Dodaj": "database-plus",
        "Usuń": "database-minus"
    }
    current_database = "None"
    dialog = None
    current_table = None
    saved = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_action = None
        self.to_edit = None
        self.parent_ = None
        self.menu_items = None
        self.menu = None
        self.cloud = None
        self.set_up_theme()

        self.manager = Builder.load_file("mdtestkivy.kv")
        self.set_up_database_menu()

        self.set_up_dataframe_view()

    def login(self):
        self.cloud = GDriveConnector()

    def set_up_theme(self, style="Dark", primary_palette="Teal", primary_hue="A700"):
        self.theme_cls.theme_style = style
        self.theme_cls.primary_palette = primary_palette
        self.theme_cls.primary_hue = primary_hue

    def download_databases(self, *kw):
        try:
            folder_id = self.cloud.get_id("database")
            self.cloud.backup_folder(folder_id, "database")

            new_name = f"database-{datetime.now().strftime('%Y-%m-%d;%H.%M.%S')}"
            os.rename('database', new_name)
            shutil.move(new_name, 'previous_databases')
            os.mkdir('database')
            for file in os.listdir(f"./previous_databases/{new_name}"):
                file_id = self.cloud.get_id(file)
                self.cloud.download_xlsx_file(file_id=file_id, dest_file=f"./database/{file}")
            self.saved = True
            self.set_up_dataframe_view()
        except:
            self.show_dialog("Coś poszło nie tak, spróbuj ponownie później")

    def cloud_upload(self, *kw):
        if not self.saved:
            self.show_dialog("Wprowadzone zmiany nie zostały zapisane")
        else:
            try:
                database_list = os.listdir('database')
                folder_id = self.cloud.get_id("database")
                self.cloud.backup_folder(folder_id, "database")
                for file in database_list:
                    print(file)
                    file_id = self.cloud.get_id(file)
                    print(file_id)
                    print(self.cloud.update_file(file_id, f"database/{file}", '/database'))
            except:
                self.show_dialog("Coś poszło nie tak, spróbuj ponownie później")

    def save_locally(self, *kw):
        try:
            table = self.current_table
            column_data = [table.column_data[i][0] for i in range(len(table.column_data))]
            row_data = np.array(table.row_data)
            df = pd.DataFrame(data=row_data, columns=column_data)
            df.to_excel(f"database/{self.current_database}.xlsx", index=False)
            self.saved = True
        except:
            self.show_dialog("Coś poszło nie tak, spróbuj ponownie później")

    def set_up_database_menu(self, directory="database"):
        database_list = os.listdir(directory)
        self.menu_items = [
            {
                "text": f"{database_list[i][:-5]}",
                "icon_": "database",
                "viewclass": "MenuItem",
                "height": dp(54),
                "on_release": lambda x=i: self.menu_callback(x),
            }
            for i in range(len(database_list))
        ]

        self.current_database = self.menu_items[0]["text"]
        self.manager.get_screen('MainAppScreen').ids.button.text = self.current_database

        self.menu = MDDropdownMenu(
            caller=self.manager.get_screen('MainAppScreen').ids.button,
            items=self.menu_items,
            width_mult=4,
        )
        self.menu.bind(on_release=self.menu_callback)

    def set_up_dataframe_view(self, directory="database"):
        dataframe = pd.read_excel(f"{directory}/{self.current_database}.xlsx")
        self.create_datatable(dataframe)

    @staticmethod
    def get_data_table(dataframe):
        column_data = list(dataframe.columns)
        row_data = dataframe.to_records(index=False)
        return column_data, row_data

    def menu_callback(self, i):
        self.current_database = self.menu_items[i]["text"]
        self.manager.get_screen('MainAppScreen').ids.button.text = self.current_database

        self.set_up_dataframe_view()

    def change_to_parent(self, *kw):
        """ Powrót do poprzedniego ekranu"""
        self.manager.current = self.parent_

    def set_up_EditScreen(self):
        """ Konfiguracja EditScreen"""
        self.manager.get_screen('EditScreen').ids.container.clear_widgets()
        for col in self.current_table.column_data:
            widget = MDTextField(hint_text=f"{col[0]}:", mode="rectangle", pos_hint={"left": 0.9, "right": 0.9})
            self.manager.get_screen('EditScreen').ids.container.add_widget(widget)
            self.manager.get_screen('EditScreen').ids[f"{col[0]}"] = widget

    def edit_row(self):
        """Edit row of database"""
        self.to_edit = True
        row = self.current_table.get_row_checks()
        if len(row) == 0:
            self.show_dialog("Zaznacz element do edycji")
        elif len(row) > 1:
            self.show_dialog("Do edycji zaznaczony musi być dokładnie jeden element.")
        else:
            row = row[0]
            self.manager.get_screen('EditScreen').ids.container.clear_widgets()
            for col_num in range(len(self.current_table.column_data)):
                col = self.current_table.column_data[col_num]
                widget = MDTextField(hint_text=f"{col[0]}:", mode="rectangle", pos_hint={"left": 0.9, "right": 0.9})
                widget.text = row[col_num]
                widget.symbol = row[col_num]
                self.manager.get_screen('EditScreen').ids.container.add_widget(widget)
                self.manager.get_screen('EditScreen').ids[f"{col[0]}"] = widget

            self.parent_ = self.manager.current
            self.manager.current = "EditScreen"

    def add_row(self):
        """Add row to database"""
        self.to_edit = False
        self.manager.get_screen('EditScreen').ids.container.clear_widgets()
        for col_num in range(len(self.current_table.column_data)):
            col = self.current_table.column_data[col_num]
            widget = MDTextField(hint_text=f"{col[0]}:", mode="rectangle", pos_hint={"left": 0.9, "right": 0.9})
            self.manager.get_screen('EditScreen').ids.container.add_widget(widget)
            self.manager.get_screen('EditScreen').ids[f"{col[0]}"] = widget

        self.parent_ = self.manager.current
        self.manager.current = "EditScreen"

    def save_row_Edit(self, *kw):
        row = self.manager.get_screen('EditScreen').ids.container.children
        row.reverse()
        row = [item.text for item in row]

        table = self.current_table
        column_data = [table.column_data[i][0] for i in range(len(table.column_data))]
        row_data = np.array(table.row_data)
        df = pd.DataFrame(data=row_data, columns=column_data)

        if self.to_edit:
            old_row = tuple(self.current_table.get_row_checks()[0])
            bool_list = [
                [str(self.current_table.row_data[i][j]) == str(old_row[j]) for j in range(len(old_row))] == [True for i
                                                                                                             in range(
                        len(old_row))] for i in range(len(self.current_table.row_data))]
            index = bool_list.index(True)
            for j in range(len(row)):
                row_data[index][j] = row[j]
            df = pd.DataFrame(data=row_data, columns=column_data)
        else:
            df_row = pd.DataFrame(data=row, columns=column_data)
            df = pd.concat([df, df_row], ignore_index=True)

        self.create_datatable(df)

    def create_datatable(self, df):
        column_data, row_data = self.get_data_table(df)
        column_data = [(x, dp(42)) for x in column_data]

        self.current_table = MDDataTable(  # update_row_data() after changes
            use_pagination=True,
            rows_num=10000,
            column_data=column_data,
            row_data=row_data,
            check=True,
            pos_hint={'top': 0.95},
            size_hint=(0.7, 0.95)
        )
        self.manager.get_screen("MainAppScreen").ids['datalabel'].clear_widgets()
        self.manager.get_screen("MainAppScreen").ids['datalabel'].add_widget(self.current_table, index=3)
        self.manager.get_screen("MainAppScreen").ids['table'] = self.current_table
        self.change_to_parent()

    def show_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog
                    )
                ],
            )
        self.dialog.open()
        self.dialog.on_pre_dismiss = self.remove_dialog

    def remove_dialog(self, *kw):
        self.dialog = None

    def close_dialog(self, *kw):
        self.dialog.dismiss(force=True)
        self.dialog = None

    def set_up_AddRemoveScreen(self):
        """ Konfiguracja AddRemoveScreen"""
        self.manager.get_screen('AddRemoveScreen').ids.container.clear_widgets()
        self.manager.get_screen('AddRemoveScreen').ids.borrowlayout.clear_widgets()

        # for col in self.current_table.column_data:
        #     widget = MDTextField(hint_text=f"{col[0]}:", mode="rectangle", pos_hint={"left": 0.9, "right": 0.9})
        #     self.manager.get_screen('AddRemoveScreen').ids.container.add_widget(widget)
        #     self.manager.get_screen('AddRemoveScreen').ids[f"{col[0]}"] = widget
        #     # kolumny powinny być kod|nazwa|ilość do dodania

        for col in ['Kod', 'Nazwa', 'Ilość']:
            widget = MDTextField(hint_text=f"{col}:", mode="rectangle", pos_hint={"left": 0.9, "right": 0.9})
            self.manager.get_screen('AddRemoveScreen').ids.container.add_widget(widget)
            self.manager.get_screen('AddRemoveScreen').ids[f"{col}"] = widget

        widget = MDLabel(text='Wypożyczenie:')
        self.manager.get_screen('AddRemoveScreen').ids.borrowlayout.add_widget(widget)
        self.manager.get_screen('AddRemoveScreen').ids["borrowtext"] = widget
        widget = MDCheckbox()
        self.manager.get_screen('AddRemoveScreen').ids.borrowlayout.add_widget(widget)
        self.manager.get_screen('AddRemoveScreen').ids["borrow"] = widget

    def save_row_AddRemove(self, *kw):
        count, name, code = self.manager.get_screen('AddRemoveScreen').ids.container.children
        count, name, code = int(count.text), name.text, code.text

        table = self.current_table
        column_data = [table.column_data[i][0] for i in range(len(table.column_data))]
        row_data = np.array(table.row_data)
        df = pd.DataFrame(data=row_data, columns=column_data)

        try:
            row_idx = self.get_row_idx_by_code(code)
            if not self.add_action:
                count = -count
            print(row_data[row_idx])
            df["Stan magazynu"][row_idx] += count
            if not self.manager.get_screen('AddRemoveScreen').ids.borrow.active:
                df["Stan ogólny"][row_idx] += count

        except Exception as e:
            row = [[code, name, count, count]]
            df_row = pd.DataFrame(data=row, columns=column_data)
            df = pd.concat([df, df_row], ignore_index=True)

        self.create_datatable(df)

    def floating_callback(self, instance):
        """Określenie akcji oraz konfiguracja EditScreen"""
        if instance.icon == "database-plus":
            self.add_action = True
        elif instance.icon == "database-minus":
            self.add_action = False

        self.set_up_EditScreen()
        self.set_up_AddRemoveScreen()
        self.parent_ = self.manager.current
        self.manager.current = "ZbarcamScreen"

    def show_code(self):
        """Wyświetlenie kodu w AddRemoveScreen"""
        code = self.manager.get_screen('AddRemoveScreen').ids['endtextplace'].symbol
        self.manager.get_screen('AddRemoveScreen').ids["Kod"].text = code
        try:
            row_idx = self.get_row_idx_by_code(code)
            name_idx = self.get_col_idx_by_col_name("Nazwa produktu")
            self.manager.get_screen('AddRemoveScreen').ids["Nazwa"].text = self.current_table.row_data[row_idx][
                name_idx]
        except Exception as e:
            print(e)

    def get_col_idx_by_col_name(self, name):
        idx = [col[0] == name for col in self.current_table.column_data].index(True)
        return idx

    def get_row_idx_by_code(self, code):
        idx = self.get_col_idx_by_col_name("Kod")
        row_idx = [str(row[idx]) == str(code) for row in self.current_table.row_data].index(True)
        return row_idx

    def on_stop(self):
        exit(0)  # dobrze zamyka kamerę

    def build(self):
        return self.manager


# Problemy todo:
# 1. dodanie wiersza(save_row_Edit) o takim samym kodzie doda kolejny wpis - kod pojawi się dwa razy
# 2. Można mieć ujemne wartości w bazie.
#