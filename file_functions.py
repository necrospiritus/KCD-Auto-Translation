import json
import pathlib
import sqlite3
from googletrans import Translator
import xml.etree.ElementTree as ET
import time
import sys
import os
import re


class file_method:
    def __init__(self, source, destination, file_name, file_path):
        self.source = source
        self.destination = destination
        self.file_name = file_name
        self.file_path = file_path

        # in-function variables
        self.translator = Translator()
        self.main_path = pathlib.Path().absolute()  # Location of this file
        self.placeholder_storage = []  # Storage array for placeholders
        self.scan = 0
        self.bulk_counter = 0
        self.cell_list = []
        self.list_of_will_translate = ""  # string variable for <10K size of un-translated texts
        self.bulk_of_will_translate = []  # list variable for >10K size of un-translated texts
        self.translated_text = ""  # string variable for <10K size of translated texts
        self.translated_text_list = []  # list variable for >10K size of translated texts

        # For Database
        self.database = database_function()

    def file_compatibility_check(self):
        with open(str(self.file_path), "r", encoding="utf-8") as selected_file:
            selected_file.seek(0)
            lines = selected_file.readlines()
            table_count = table_end_count = row_count = row_end_count = cell_count = cell_end_count = 0
            for i in lines:
                table_count = table_count + i.count("<Table>")
                table_end_count = table_end_count + i.count("</Table>")
                row_count = row_count + i.count("<Row>")
                row_end_count = row_end_count + i.count("</Row>")
                cell_count = cell_count + i.count("<Cell>")
                cell_end_count = cell_end_count + i.count("</Cell>")
                count_error = 0
            if table_count != table_end_count:
                print("<Table> count= " + str(table_count) + "\n" + "</Table> count= " + str(table_end_count))
                print("They should be equal! Please check the file.")
                count_error = 1
            else:
                pass
            if row_count != row_end_count:
                print("<Row> count= " + str(row_count) + "\n" + "</Row> count= " + str(row_end_count))
                print("They should be equal! Please check the file.")
                count_error = 1
            else:
                pass
            if cell_count != cell_end_count:
                print("<Cell> count= " + str(cell_count) + "\n" + "</Cell> count= " + str(cell_end_count))
                print("They should be equal! Please check the file.")
                count_error = 1
            else:
                pass
        if count_error == 1:
            raise SystemExit
        else:
            print("\nSTEP 1: File Compatibility Check Completed Successfully!")

    def add_placeholders(self):
        with open(str(self.main_path) + r"\temp_" + str(self.file_name), "w", encoding="utf-8") as temp_file:
            pass
        with open(str(self.file_path), "r", encoding="utf-8") as original_file:
            lines = original_file.readlines()
            for i in lines:
                # Creating placeholders for every unique code in a line
                text = i
                text = text.replace('&amp;nbsp;', '[H]')

                find_result = re.findall("&amp;lt;.*?&amp;gt;", text)
                if find_result:
                    for j in find_result:
                        if j not in self.placeholder_storage:
                            self.placeholder_storage.append(j)
                find_result = re.findall("&lt;[^;]+&gt;", text)
                if find_result:
                    for j in find_result:
                        if j not in self.placeholder_storage:
                            self.placeholder_storage.append(j)
                find_result = re.findall(r"\$[^;]+;", text)
                if find_result:
                    for j in find_result:
                        if j not in self.placeholder_storage:
                            self.placeholder_storage.append(j)
                # Importing placeholders to line
                k = 0
                while k < len(self.placeholder_storage):
                    text = text.replace(self.placeholder_storage[k], "[H" + str(k) + "]")
                    k += 1
                with open(str(self.main_path) + r"\temp_" + str(self.file_name), "a", encoding="utf-8") as temp_file:
                    temp_file.writelines(text)
        self.file_path = str(self.main_path) + r"\temp_" + str(self.file_name)
        sys.stdout.write("\n")
        print("\nAdding Placeholders Completed Successfully!")

    def xml_parsing(self):
        tree = ET.parse(str(self.file_path))
        root = tree.getroot()
        for row in root.iter(tag='Row'):
            for cell in row:
                self.cell_list.append(cell.text)

    def xml_to_database(self):
        self.database.connect_database()
        self.database.create_database()
        i = 0
        row_count = 1
        while i < len(self.cell_list):
            self.database.cursor.execute("INSERT INTO cells VALUES(?,?,?)",
                                         (row_count, "ID", str(self.cell_list[i])))
            self.database.connection.commit()
            self.database.cursor.execute("INSERT INTO cells VALUES(?,?,?)",
                                         (row_count, "ORIGINAL", str(self.cell_list[i + 1])))
            self.database.connection.commit()
            self.database.cursor.execute("INSERT INTO cells VALUES(?,?,?)",
                                         (row_count, "TRANSLATE", str(self.cell_list[i + 2])))
            self.database.connection.commit()
            self.database.cursor.execute("INSERT INTO cells VALUES(?,?,?)",
                                         (row_count, "NEW TRANSLATION", ""))
            self.database.connection.commit()
            row_count += 1
            sys.stdout.write("\r")
            sys.stdout.write(
                "{} / {} Lines Transferred to Database!".format((i + 1) // 3, (len(self.cell_list) + 1) // 3))
            sys.stdout.flush()
            i += 3
        self.database.close_database()
        os.remove(str(self.file_path))  # Deletes Temp XML File
        sys.stdout.write("\n")
        print("\nSTEP 2: Text Splitting and Transferring to Database Completed Successfully!")

    def prepare_for_translate(self):
        self.database.connect_database()
        translate_list = self.database.select_for_translate()
        original_list = self.database.select_for_original()
        self.database.close_database()

        translate_list_cleaned = []
        for x, y in zip(translate_list, original_list):
            if x == y:
                translate_list_cleaned.append(x[0])
            else:
                translate_list_cleaned.append("")

        while self.scan < len(translate_list_cleaned):
            if len(translate_list_cleaned[self.scan]) > 10000:
                print("Lines too big (>10000) to handle!")
                raise SystemExit
            length_check = len(self.list_of_will_translate) + len(translate_list_cleaned[self.scan])
            if length_check < 10000:
                self.list_of_will_translate = self.list_of_will_translate + '[' + str(self.scan) + ']' + \
                                              translate_list_cleaned[self.scan] + "\n"
                sys.stdout.write("\r")
                sys.stdout.write("{} / {} lines prepared.".format(self.scan + 1, len(translate_list_cleaned)))
                sys.stdout.flush()
                self.scan += 1
            else:
                self.bulk_of_will_translate.append(self.list_of_will_translate)
                self.bulk_counter += 1
                self.list_of_will_translate = ""
        self.list_of_will_translate = self.list_of_will_translate + '[' + str(self.scan) + ']'
        sys.stdout.write("\n")
        print("\nSTEP 3: Preparing For Translate Completed Successfully!")

    def translate_them_all(self):  # and in the darkness bind them.
        if self.bulk_counter > 0:
            print("-----Bulk Translation Will Be Done!-----")
            print("Estimated Translation Time Minimum= ", (self.bulk_counter * 100) // 60, " minutes!")
            m = 1
            while m <= self.bulk_counter:
                sys.stdout.write("\r")
                sys.stdout.flush()
                print(m, "/", self.bulk_counter + 1, "Bulk File Sending Google Server!")
                try:
                    self.translated_text_list.append(
                        self.translator.translate(self.bulk_of_will_translate[m - 1],
                                                  src=self.source,
                                                  dest=self.destination))
                except json.decoder.JSONDecodeError:
                    print("ERROR: Possible Google IP Ban or Character Error.")
                    print()
                    with open(str(self.main_path) + r"\error_text.txt", "w") as log:
                        log.writelines(self.bulk_of_will_translate[m - 1])
                    print("Texts which have been sending to Google: ", str(self.main_path) + r"\error_text.txt")
                    print(json.decoder.JSONDecodeError)
                    raise SystemExit
                print(m, "/", self.bulk_counter + 1, "Translated Bulk File Retrieved From Google Server!")
                print("Waiting For Cooldown.")
                for remaining in range(100, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                    sys.stdout.flush()
                    time.sleep(1)
                m += 1
            if self.list_of_will_translate != "":
                print(m, "/", self.bulk_counter + 1, "Bulk File Sending Servers!")
                self.translated_text_list.append(
                    self.translator.translate(self.list_of_will_translate,
                                              src=self.source,
                                              dest=self.destination))
                print(m, "/", self.bulk_counter + 1, "Translated Bulk File Retrieved!")
            else:
                pass
            print("\nSTEP 4: Translation Completed Successfully!")
        else:
            print("-----One List Translation Will Be Done!-----")
            try:
                self.translated_text = self.translator.translate(self.list_of_will_translate,
                                                                 src=self.source,
                                                                 dest=self.destination)
            except json.decoder.JSONDecodeError:
                print("ERROR: Possible Google IP Ban or Character Error.")
                print()
                with open(str(self.main_path) + r"\error_text.txt", "w") as log:
                    log.writelines(self.list_of_will_translate)
                print("Texts which have been sending to Google: ", str(self.main_path) + r"\error_text.txt")
                raise SystemExit
            print("\nSTEP 4: Translation Completed Successfully!")

    def to_database(self):
        self.database.connect_database()
        if self.bulk_counter > 0:
            all_translated_text = ""
            for i in self.translated_text_list:
                all_translated_text = all_translated_text + i.text + "\n"
            i = 0
            while i <= self.scan - 1:
                s_holder = '[' + str(i) + ']'
                e_holder = '[' + str(i + 1) + ']'
                start_point = all_translated_text.find(s_holder)
                end_point = all_translated_text.find(e_holder)
                text_for_database = ""
                if i < 10:
                    text_for_database = all_translated_text[start_point + 4:end_point]
                elif i < 100:
                    text_for_database = all_translated_text[start_point + 5:end_point]
                elif i < 1000:
                    text_for_database = all_translated_text[start_point + 6:end_point]
                elif i < 10000:
                    text_for_database = all_translated_text[start_point + 7:end_point]
                elif i < 100000:
                    text_for_database = all_translated_text[start_point + 8:end_point]
                elif i < 1000000:
                    text_for_database = all_translated_text[start_point + 9:end_point]
                elif i < 10000000:
                    text_for_database = all_translated_text[start_point + 10:end_point]

                if text_for_database == "":
                    self.database.cursor.execute("SELECT text FROM cells WHERE row=? AND cell='TRANSLATE' ",
                                                 (str(i + 1),))
                    already_translated = self.database.cursor.fetchall()
                    self.database.cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ",
                                                 (str(already_translated[0][0]), str(i + 1)))
                    self.database.connection.commit()
                else:
                    self.database.cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ",
                                                 (text_for_database, str(i + 1)))
                    self.database.connection.commit()
                sys.stdout.write("\r")
                sys.stdout.write("{} / {} Translated Lines Transferred to Database!".format(i, self.scan))
                sys.stdout.flush()
                i += 1
        else:
            i = 0
            while i < self.scan:
                s_holder = '[' + str(i) + ']'
                e_holder = '[' + str(i + 1) + ']'
                start_point = str(self.translated_text.text).find(s_holder)
                end_point = str(self.translated_text.text).find(e_holder)
                text_for_database = str(self.translated_text.text)[start_point + 4:end_point]

                if text_for_database == "":
                    self.database.cursor.execute("SELECT text FROM cells WHERE row=? AND cell='TRANSLATE' ",
                                                 (str(i + 1),))
                    already_translated = self.database.cursor.fetchall()
                    self.database.cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ",
                                                 (str(already_translated[0][0]), str(i + 1)))
                    self.database.connection.commit()
                else:
                    self.database.cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ",
                                                 (text_for_database, str(i + 1)))
                    self.database.connection.commit()
                i += 1
        self.database.close_database()
        print("\nSTEP 5: Transferring Of Translated Lines To Database Completed Successfully!")

    def create_new_file(self):
        self.database.connect_database()
        os.makedirs(str(self.main_path) + r"\Translated" + "\\" + str(self.destination), exist_ok=True)
        with open(str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name),
                  "w", encoding="utf-8") as new_file:
            new_file.writelines("<Table>\n")
        i = 1
        while i <= self.scan:
            self.database.cursor.execute("SELECT text FROM cells WHERE row=? AND cell='ID'", (str(i),))
            cell_id = self.database.cursor.fetchall()
            self.database.cursor.execute("SELECT text FROM cells WHERE row=? AND cell='ORIGINAL'", (str(i),))
            cell_original = self.database.cursor.fetchall()
            self.database.cursor.execute("SELECT text FROM cells WHERE row=? AND cell='NEW TRANSLATION'", (str(i),))
            cell_old_translation = self.database.cursor.fetchall()
            cell_new_translation = str(cell_old_translation[0][0])[:-1]  # removes \n from last of lines
            with open(str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name),
                      "a", encoding="utf-8") as new_file:
                new_file.writelines("<Row><Cell>" + str(cell_id[0][0]) + "</Cell><Cell>" + str(
                    cell_original[0][0]) + "</Cell><Cell>" + str(cell_new_translation) + "</Cell></Row>\n")
            sys.stdout.write("\r")
            sys.stdout.write("{} / {} Lines Written!".format(i, self.scan))
            sys.stdout.flush()
            i += 1
        with open(str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name),
                  "a", encoding="utf-8") as new_file:
            new_file.writelines("</Table>")
        self.database.close_database()
        os.remove(str(self.main_path) + r"\database.db")  # Deletes Database

    def remove_placeholders(self):
        with open(str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name),
                  "r", encoding="utf-8") as no_edit_file:
            read_lines = no_edit_file.readlines()
        text_list = []
        for line in read_lines:
            text = line
            text = text.replace('[H]', '&amp;nbsp;')
            i = 0
            while i < len(self.placeholder_storage):
                text = text.replace("[H" + str(i) + "]", str(self.placeholder_storage[i]))
                i += 1
            text_list.append(text)
        with open(str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name),
                  "w", encoding="utf-8") as edit_file:
            edit_file.writelines(text_list)
        sys.stdout.write("\n")
        print("\nSTEP 6: New File Created!")
        print("Please Look For This File: " +
              str(self.main_path) + r"\Translated" + "\\" + str(self.destination) + "\\" + str(self.file_name))


class database_function:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def connect_database(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def create_database(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS cells (row INT,cell TEXT,text TEXT)")
        self.connection.commit()
        self.cursor.execute("DELETE FROM cells")
        self.connection.commit()

    def close_database(self):
        self.connection.close()

    def select_for_translate(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT text FROM cells WHERE cell='TRANSLATE'")
        translate_list = self.cursor.fetchall()
        return translate_list

    def select_for_original(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT text FROM cells WHERE cell='ORIGINAL'")
        original_list = self.cursor.fetchall()
        return original_list
