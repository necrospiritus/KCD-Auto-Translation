import pathlib
import os
import googletrans
from CODES import *
main_path = pathlib.Path().absolute()
available_languages = ["cs", "en", "et", "fr", "de", "it", "pl", "ru", "es", "tr", "uk"]

print("""***********************************

Kingdom Come Deliverance

Auto-Translation

Programming by Burak Karabey

Press 'q' for quit.
***********************************""")
print("""
What is your purpose?

1-I want to auto-translate missing translation in available languages.
2-I want to auto-translate to new language.
""")
while True:
    key = input("What is your answer?: ")

    if (key == "q"):
        print("Program closing.....")
        break
    elif (key == "1"):
        print("""
---------AVAILABLE LANGUAGES---------
cs-Czech    en-English  et-Estonian
fr-French   de-German   it-Italian
pl-Polish   ru-Russian  es-Spanish
tr-Turkish  uk-Ukrainian
-------------------------------------
        """)
        destination_language = input("Please enter the code of language which you want choose as source language: ")
        source_language = "en"
        if destination_language in available_languages:
            pass
        else:
            print("Error: Selected Language is not available!")
            print("Programme closing.....")
            break
        file_list = []
        for path, subdirs, files in os.walk(str(main_path) + r"\Source Languages\\" + destination_language):
            file_list = files
        counter_key = 0
        for i in file_list:
            print(counter_key, " - ", i)
            counter_key += 1
        selected_file = input("Please enter the number of file which you want auto-translate: ")
        selected_file_path = str(main_path) + r"\Source Languages\\" + destination_language + r"\\" + file_list[int(selected_file)]
        sys.stdout.write("\n")
        print("Selected file is", file_list[int(selected_file)])
        print("Translation will be from ", destination_language, " to ", destination_language)
        file_method.file_compatibility_check(selected_file_path)
        file_method.file_reorganization(selected_file_path, file_list[int(selected_file)])
        object1 = file_method()
        object1.prepare_for_translate()
        object1.translate_them_all(source_language, destination_language)
        object1.to_database()
        object1.create_new_file(destination_language, file_list[int(selected_file)])

    elif (key == "2"):
        google_language_list = googletrans.LANGUAGES
        print("""
---------TRANSLATABLE LANGUAGES---------
        """)
        for x, y in google_language_list.items():
            print(x + " - " + y)
        print("""
--------------------------------------
        """)
        destination_language = input("Please enter the code of language which you want use as destination language: ")
        if destination_language in google_language_list.keys():
            pass
        else:
            print("Error: Selected Language is not available!")
            print("Programme closing.....")
            break
        os.system('cls' if os.name == 'nt' else 'clear')
        answer = input("en-English will be used as source language as default. Do you want to change it? (Y/N): ")
        if answer == "N" or answer == "n":
            source_language = "en"
        elif answer == "Y" or answer == "y":
            print("""
---------AVAILABLE LANGUAGES---------
cs-Czech    en-English  et-Estonian
fr-French   de-German   it-Italian
pl-Polish   ru-Russian  es-Spanish
tr-Turkish  uk-Ukrainian
-------------------------------------
            """)
            source_language = input("Please enter the code of language which you want choose as source language: ")
            if source_language in available_languages:
                pass
            else:
                print("Error: Selected Language is not available!")
                print("Programme closing.....")
                break
        else:
            print("Invalid Answer...")
            print("Programme closing.....")
            break
        if destination_language == source_language:
            print("Destination Language: " + destination_language + "\n" + "Source Language: " + source_language + "\n" + "They can not be same!!! Program closing...")
            break
        else:
            pass

        file_list = []
        for path, subdirs, files in os.walk(str(main_path) + r"\Source Languages\\" + source_language):
            file_list = files
        counter_key = 0
        for i in file_list:
            print(counter_key, " - ", i)
            counter_key += 1
        selected_file = input("Please enter the number of file which you want auto-translate: ")
        sys.stdout.write("\n")
        print("Selected file is", file_list[int(selected_file)])
        print("Translation will be from ", source_language, " to ", destination_language)
        selected_file_path = str(main_path) + r"\Source Languages\\" + source_language + r"\\" + file_list[int(selected_file)]
        file_method.file_compatibility_check(selected_file_path)
        file_method.file_reorganization(selected_file_path, file_list[int(selected_file)])
        object1 = file_method()
        object1.prepare_for_translate()
        object1.translate_them_all(source_language, destination_language)
        object1.to_database()
        object1.create_new_file(destination_language, file_list[int(selected_file)])

    else:
        print("Invalid Operation...")