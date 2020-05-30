import json
import pathlib
import sqlite3
from googletrans import Translator
import xml.etree.ElementTree as ET
import time
import sys
import os


main_path = pathlib.Path().absolute()
available_languages = ["cs", "en", "et", "fr", "de", "it", "pl", "ru", "es", "tr", "uk"]

translator = Translator()

class file_method():
    def __init__(self):
        self.scan = 0


    def file_compatibility_check(path):
        with open(str(path), "r", encoding="utf-8") as selectedfile:
            selectedfile.seek(0)
            lines = selectedfile.readlines()
            table_count = 0
            table_end_count = 0
            row_count = 0
            row_end_count = 0
            cell_count = 0
            cell_end_count = 0
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

    def file_reorganization(path, file_name):
        with open(str(main_path) + r"\temp_" + str(file_name), "w", encoding="utf-8") as temp_file:
            pass
        with open(str(path), "r", encoding="utf-8") as original_file:
            lines = original_file.readlines()
            text = ""
            for i in lines:
                text = i
                text = text.replace('&lt;br/&gt;', '[H1]')
                text = text.replace('&lt;', '[H2]')
                text = text.replace("&gt;", "[H3]")
                text = text.replace("&amp;", "[H4]")
                text = text.replace("&nbsp;", "[H5]")
                text = text.replace("nbsp;", "[H6]")
                with open(str(main_path) + r"\temp_" + str(file_name), "a", encoding="utf-8") as temp_file:
                    temp_file.writelines(text)
        path = str(main_path) + r"\temp_" + str(file_name)
        tree = ET.parse(str(path))
        root = tree.getroot()
        list = []
        for row in root.iter(tag='Row'):
            count = 0
            for cell in row:
                list.append(cell.text)
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        query = "CREATE TABLE IF NOT EXISTS cells (row INT,cell TEXT,text TEXT)"
        cursor.execute(query)
        connection.commit()
        query = "DELETE FROM cells"
        cursor.execute(query)
        connection.commit()
        i = 0
        row_count = 1
        while i < len(list):
            query = "INSERT INTO cells VALUES(?,?,?)"
            cursor.execute(query, (row_count, "ID", str(list[i])))
            connection.commit()
            query = "INSERT INTO cells VALUES(?,?,?)"
            cursor.execute(query, (row_count, "ORIGINAL", str(list[i + 1])))
            connection.commit()
            query = "INSERT INTO cells VALUES(?,?,?)"
            cursor.execute(query, (row_count, "TRANSLATE", str(list[i + 2])))
            connection.commit()
            query = "INSERT INTO cells VALUES(?,?,?)"
            cursor.execute(query, (row_count, "NEW TRANSLATION", ""))
            connection.commit()
            row_count += 1
            sys.stdout.write("\r")
            sys.stdout.write("{} / {} Lines Transferred to Database!".format((i + 1)//3, (len(list)+1)//3))
            sys.stdout.flush()
            i += 3
        connection.close()
        os.remove(str(path)) #Deletes Temp XML File
        sys.stdout.write("\n")
        print("\nSTEP 2: Text Splitting and Transferring to Database Completed Successfully!")

    def prepare_for_translate(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        query = "SELECT text FROM cells WHERE cell='TRANSLATE'"
        cursor.execute(query)
        translate_list = cursor.fetchall()
        connection.close()

        self.list_of_will_translate = ""  # string
        self.bulk_of_will_translate = []  # list
        total_scan_length = 0
        self.bulk_counter = 0
        while self.scan < len(translate_list):
            if len(translate_list[self.scan][0]) > 10000:
                print("Lines too big (>10000) to handle!")
                raise SystemExit
            length_check = len(self.list_of_will_translate) + len(translate_list[self.scan][0])
            if length_check < 10000:
                self.list_of_will_translate = self.list_of_will_translate + '[' + str(self.scan) + ']' + translate_list[self.scan][0] + "\n"
                sys.stdout.write("\r")
                sys.stdout.write("{} / {} lines prepared.".format(self.scan + 1, len(translate_list)))
                sys.stdout.flush()
                self.scan += 1
            else:
                self.bulk_of_will_translate.append(self.list_of_will_translate)
                self.bulk_counter += 1
                total_scan_length = 0
                self.list_of_will_translate = ""
        self.list_of_will_translate = self.list_of_will_translate + '[' + str(self.scan) + ']'
        sys.stdout.write("\n")
        print("\nSTEP 3: Preparing For Translate Completed Successfully!")

    def translate_them_all(self, source, destination): #and in the darkness bind them.
        src_lang = source
        dest_lang = destination
        self.translated_text = "" #string
        self.translated_text_list = [] #list
        if self.bulk_counter > 0:
            print("-----Bulk Translation Will Be Done!-----")
            print("Estimated Translation Time Minimum= ", (self.bulk_counter*100)//60, " minutes!")
            m = 1
            while m <= self.bulk_counter:
                sys.stdout.write("\r")
                sys.stdout.flush()
                print(m, "/", self.bulk_counter + 1, "Bulk File Sending Google Server!")
                try:
                    self.translated_text_list.append(translator.translate(self.bulk_of_will_translate[m - 1], src=src_lang, dest=dest_lang))
                except json.decoder.JSONDecodeError:
                    print("ERROR: Possible Google Ban or Character Error.")
                    with open(str(main_path) + r"\error_log.txt", "w") as log:
                        log.writelines(self.bulk_of_will_translate[m - 1])
                    print("Error Log: ", str(main_path) + r"\error_log.txt")
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
                self.translated_text_list.append(translator.translate(self.list_of_will_translate, src=src_lang, dest=dest_lang))
                print(m, "/", self.bulk_counter + 1, "Translated Bulk File Retrieved!")
            else:
                pass
            print("\nSTEP 4: Translation Completed Successfully!")
        else:
            print("-----One List Translation Will Be Done!-----")
            self.translated_text = translator.translate(self.list_of_will_translate, src=src_lang, dest=dest_lang)
            print("\nSTEP 4: Translation Completed Successfully!")

    def to_database(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        if self.bulk_counter > 0:
            all_translated_text = ""
            for i in self.translated_text_list:
                all_translated_text = all_translated_text + i.text + "\n"
            i = 0
            while i <= self.scan:
                s_holder = '[' + str(i) + ']'
                e_holder = '[' + str(i + 1) + ']'
                start_point = all_translated_text.find(s_holder)
                end_point = all_translated_text.find(e_holder)
                if i <10:
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
                cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ", (text_for_database, str(i + 1)))
                connection.commit()
                sys.stdout.write("\r")
                sys.stdout.write("{} / {} Translated Lines Transferred to Database!".format(i, self.scan))
                sys.stdout.flush()
                i += 1
        else:
            i = 0
            while i < self.scan:
                s_holder = '[' + str(i) + ']'
                e_holder = '[' + str(i+1) + ']'
                start_point = str(self.translated_text.text).find(s_holder)
                end_point = str(self.translated_text.text).find(e_holder)
                text_for_database = str(self.translated_text.text)[start_point+4:end_point]
                cursor.execute("UPDATE cells SET text=? WHERE row=? AND cell='NEW TRANSLATION' ", (text_for_database, str(i+1)))
                connection.commit()
                i += 1
        connection.close()
        print("\nSTEP 5: Transferring Of Translated Lines To Database Completed Successfully!")

    def create_new_file(self, destination, file):
        dest_lang = destination
        file_name = file
        os.makedirs(str(main_path) + r"\Translated" + "\\" + str(dest_lang), exist_ok=True)
        with open(str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name), "w", encoding="utf-8") as new_file:
            new_file.writelines("<Table>\n")
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        i = 1
        while i <= self.scan:
            cursor.execute("SELECT text FROM cells WHERE row=? AND cell='ID'", (str(i),))
            cell_ID = cursor.fetchall()
            cursor.execute("SELECT text FROM cells WHERE row=? AND cell='ORIGINAL'", (str(i),))
            cell_ORIGINAL = cursor.fetchall()
            cursor.execute("SELECT text FROM cells WHERE row=? AND cell='NEW TRANSLATION'", (str(i),))
            cell_OLD_TRANSLATION = cursor.fetchall()
            cell_NEW_TRANSLATION = str(cell_OLD_TRANSLATION[0][0])[:-1] #removes \n from last of lines
            with open(str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name), "a", encoding="utf-8") as new_file:
                new_file.writelines("<Row><Cell>" + str(cell_ID[0][0]) + "</Cell><Cell>" + str(cell_ORIGINAL[0][0]) + "</Cell><Cell>" + str(cell_NEW_TRANSLATION) + "</Cell></Row>\n")
            sys.stdout.write("\r")
            sys.stdout.write("{} / {} Lines Written!".format(i, self.scan))
            sys.stdout.flush()
            i += 1
        with open(str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name), "a", encoding="utf-8") as new_file:
            new_file.writelines("</Table>")
        with open(str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name), "r", encoding="utf-8") as no_edit_file:
            read_lines = no_edit_file.readlines()
        text = ""
        text_list = []
        for line in read_lines:
            text = line
            text = text.replace("[H1]", '&lt;br/&gt;')
            text = text.replace("[H2]", '&lt;')
            text = text.replace("[H3]", "&gt;")
            text = text.replace("[H4]", "&amp;")
            text = text.replace("[H5]", "&nbsp;")
            text = text.replace("[H6]", "nbsp;")
            text_list.append(text)
        with open(str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name), "w", encoding="utf-8") as edit_file:
                edit_file.writelines(text_list)
        connection.close()
        os.remove(str(main_path) + r"\database.db")  # Deletes Database
        sys.stdout.write("\n")
        print("\nSTEP 6: New File Created!")
        print("Please Look For This File: " + str(main_path) + r"\Translated" + "\\" + str(dest_lang) + "\\" + str(file_name))
