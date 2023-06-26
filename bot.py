from pathlib import Path
from classes import Record, AddressBook, Name, Email, Birthday, Phone, Notebook, RecordNote, Hashtag
# from classes_for_notebook import Notebook, RecordNote, Hashtag
import sort_dir


phonebook = AddressBook()
notebook = Notebook()
cashe = ""


def input_error(func):
    def inner(*args, **kwargs):
        global cashe
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError:
            print(find_matching_lines(cashe))
            return "There is no such name"
        except ValueError as error:
            print(find_matching_lines(cashe))
            return str(error)
        except IndexError:
            print(find_matching_lines(cashe))
            return "Enter user name"
        except TypeError:
            print(find_matching_lines(cashe))
            return "Incorrect values"

    return inner


@input_error
def greeting():
    return "How can I help you?"


def unknown_command():
    return "Enter a new command"


def change_command(user_input):
    while True:
        print(find_matching_lines(user_input))
        choice = input(
            "Unknown command. Do you want to change the command? \n(Y/N): "
        )

        if choice.lower() == "y":
            words = user_input.split(" ")
            new_user_input = input("Repeat the command: ")
            if len(words) == 1:
                user_input = new_user_input + user_input[len(new_user_input) + 1 :]
            elif len(words) >= 2:
                user_input = " ".join([new_user_input] + words[1:])
            print(user_input)
            return user_input
        elif choice.lower() == "n":
            return None
        else:
            print('Please enter your choice "Y" or "N".')


@input_error
def exit():
    return None


def help():
    return (
        "add name 0*********/example@email.com/dd.mm.yyyy - add a phone/email/birthday to a contact\n"
        "note note_#hashtag_note - create a note with the specified hashtag(can be specified now or later)\n"
        "change name new_phone index - change the phone number at the specified index (if not specified, the first one will be changed)\n"
        "modify hashtag index new_note - modify the note with the specified hashtag and index\n"
        "search criteria - search for criteria among emails, phones, and names\n"
        "show all - show all contacts\n"
        "show notes - show all notes\n"
        "phone name - show all phone numbers for the specified name\n"
        "email name - show all emails for the specified name\n"
        "hashtag hashtag - displays all notes for the specified hashtag\n"
        "birthday name - show the birthday date with the number of days remaining\n"
        "birthdays - displays a list of contacts whose birthday is a specified number of days from the current date(standard 7 days)\n"
        "page page_number number_of_contacts_per_page - show all contacts divided into pages, default is the first page with 3 contacts\n"
        "notes page_number number_of_hashtags - show all notes divided into pages, default is the first page with all notes of one hashtag\n"
        "delete name/#hashtag - clears a contact/hashtag by the specified name/hashtag\n"
        "exit/good bye/close - shutdown/end program"
    )


def find_matching_lines(user_input):
    matching_lines = []
    help_text = help()

    if user_input.strip():
        words = user_input.split()
        first_word = words[0]
        second_word = words[1] if len(words) > 1 else None

        for line in help_text.split("\n"):
            if first_word.lower() in line.lower() and len(first_word) >= 3:
                line = line.strip()
                if line:
                    matching_lines.append(line)

        if not matching_lines and second_word:
            for line in help_text.split("\n"):
                if second_word.lower() in line.lower() and len(second_word) >= 3:
                    line = line.strip()
                    if line:
                        matching_lines.append(line)

        if matching_lines:
            matching_lines.insert(0, "Commands in this context:")

    return "\n".join(matching_lines) + "\n"


@input_error
def add_user(name, contact_details):
    record = phonebook.get_records(name)
    if record:
        return update_user(record, contact_details)
    else:
        if "@" in contact_details:
            record = Record(Name(name), email=Email(contact_details))
        elif "." in contact_details:
            record = Record(Name(name), birthday=Birthday(contact_details))
        else:
            phone = Phone(contact_details)
            record = Record(Name(name), phone=phone)
        phonebook.add_record(record)
        return "Contact successfully added"


@input_error
def add_note(note):
    hashtags = extract_hashtags(note)

    if not hashtags:
        user_input = input("Please enter hashtags for the note: ")
        user_input = user_input.strip()
        if not user_input:
            hashtags = ["#untagged"]
        else:
            hashtags = extract_hashtags(user_input)
            if not hashtags:
                hashtags = [user_input]

    cleaned_note = remove_hashtags_from_note(note)

    for hashtag in hashtags:
        record = notebook.get_records(hashtag)
        if record:
            record.add_note(cleaned_note)
        else:
            record = RecordNote(Hashtag(hashtag), note=cleaned_note)
            notebook.add_record(record)

    return "Note added successfully"


def extract_hashtags(text):
    hashtags = []
    words = text.split()
    for word in words:
        if word.startswith("#"):
            hashtags.append(word)
    return hashtags


def remove_hashtags_from_note(note):
    cleaned_note = note
    hashtags = extract_hashtags(note)
    for hashtag in hashtags:
        cleaned_note = cleaned_note.replace(hashtag, "")
    cleaned_note = cleaned_note.strip()
    return cleaned_note


def update_user(record, contact_details):
    if "@" in contact_details:
        record.add_email(Email(contact_details))
    elif "." in contact_details:
        record.add_birthday(Birthday(contact_details))
    else:
        phone = Phone(contact_details)
        record.add_phone(phone)
    return "Contact details added successfully"


@input_error
def del_record(key: str):
    if "#" in key:
        notebook.data.pop(key)
        return f"Record for hashtag {key} was deleted from notebook."
    phonebook.data.pop(key)
    return f"Record for user {key} was deleted from addressbook."


@input_error
def change_phone(name, new_phone, index=0):
    record = phonebook.get_records(name)
    if record:
        if record.phones and "0" <= str(index) < str(len(record.phones)):
            record.edit_phone(
                old_phone=record.phones[int(index)].value, new_phone=new_phone
            )
            return "Phone number updated successfully"
        else:
            return "Invalid phone number index"
    else:
        return "There is no such name"


def change_note(hashtag, index, new_note):
    record = notebook.get_records(hashtag)
    if record:
        if record.notes and "0" <= str(index) < str(len(record.notes)):
            record.edit_note(old_note=record.notes[int(index)].value, new_note=new_note)
            return "Note updated successfully"
        else:
            return "Invalid note number index"
    else:
        return "There is no such hashtag"


@input_error
def show_all():
    if not phonebook.data:
        return "The phonebook is empty"
    result = ""
    for name in phonebook.data:
        result += phonebook.show_record(name) + "\n"
    return result.rstrip()


@input_error
def find_user_adressbook(name: str, flag=None):
    if not phonebook.data:
        return "The phonebook is empty"
    result = ""
    if flag is None:
        return phonebook.show_record(name)
    else:
        name = name.lower()
        for user in phonebook.data:
            if name == user.lower():
                result += phonebook.show_record(user) + "\n"
        return result.rstrip()


@input_error
def show_notes(criteria=None):
    if not notebook.data:
        return "The notebook is empty"
    if not criteria:
        return str(notebook)

    records = notebook.search(criteria)
    if not records:
        return "No note records found for " + criteria

    result = ""
    for record in records:
        result += str(record) + "\n"
    return result


@input_error
def get_note(hashtag):
    if hashtag[0] != "#":
        hashtag = "#" + hashtag
    record = notebook.get_records(hashtag)
    if record:
        notes = [f"{note}\n----------------------\n" for note in record.notes]
        if notes:
            notes_str = "".join(notes)
            return f"{hashtag}:\n{notes_str}"
        else:
            return f"No notes found for {hashtag}"
    else:
        return "There is no such hashtag"


@input_error
def get_birthday(name):
    record = phonebook.get_records(name)
    if record:
        if record.birthday:
            return f"{record.name.value}: {record.birthday.value}, Days to birthday: {record.days_to_birthday()}"
        else:
            return "No birthday found for that name"
    else:
        return "There is no such name"


def remaining_days(days=7):
    upcoming_birthdays = []
    result = ""
    for record in phonebook.data.values():
        name = record.get_name()
        birthday = record.get_birthday()

        if birthday is not None:
            days_left = record.days_to_birthday()
            if days_left is not None and days_left <= int(days):
                upcoming_birthdays.append((name, birthday.value, days_left))

    if len(upcoming_birthdays) == 0:
        result = "No upcoming birthdays in the next few days."
    else:
        for name, birthday, days_left in upcoming_birthdays:
            result += f"{name}: birthday: {birthday} days to birthday: {days_left}\n"

    return result.rstrip()


@input_error
def get_phone_number(name):
    record = phonebook.get_records(name)
    if record:
        if record.phones:
            phones = [f"{record.get_name()}: {phone}" for phone in record.phones]
            result = "\n".join(phones)
            return result
        else:
            return "No phone number found for that name"
    else:
        return "There is no such name"


@input_error
def get_email(name):
    record = phonebook.get_records(name)
    if record:
        if record.emails:
            emails = [f"{record.get_name()}: {email}" for email in record.emails]
            result = "\n".join(emails)
            return result

        else:
            return "No email found for that name"

    else:
        return "There is no such name"


@input_error
def search_by_criteria(criteria: str, flag=None):
    if criteria:
        result = []
        result_str = ""
        for user in phonebook.data:
            record_str = phonebook.show_record(user)
            if flag is not None:
                criteria = criteria.lower()
                record_str = record_str.lower()
            if record_str.find(criteria) >= 0:
                result.append(phonebook.show_record(user))
        for el in result:
            result_str += el + "\n"
        if result == []:
            return f"No records found for that criteria"
        return result_str.rstrip()


@input_error
def iteration_note(page=1, count_hashtag=1):
    if not notebook.data:
        return "The notebook is empty"

    page = int(page)
    count_hashtag = int(count_hashtag)
    start_index = (page - 1) * count_hashtag
    end_index = start_index + count_hashtag

    records = list(notebook)
    total_pages = (len(records) + count_hashtag - 1) // count_hashtag

    if page < 1 or page > total_pages:
        return f"Invalid page number. Please enter a page number between 1 and {total_pages}"

    result = ""
    for record in records[start_index:end_index]:
        result += f"{record.hashtag}:\n"
        if record.notes:
            notes = "\n".join(
                [f"{note.value}\n---------------------" for note in record.notes]
            )
            result += f"\n{notes}\n"

    result += f"Page {page}/{total_pages}"

    return result.rstrip()


@input_error
def iteration(page=1, page_size=3):
    if not phonebook.data:
        return "The phonebook is empty"

    page = int(page)
    page_size = int(page_size)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    records = list(phonebook)
    total_pages = (len(records) + page_size - 1) // page_size

    if page < 1 or page > total_pages:
        return f"Invalid page number. Please enter a page number between 1 and {total_pages}"

    result = ""
    for record in records[start_index:end_index]:
        result += f"{record}\n"

    result += f"Page {page}/{total_pages}"

    return result.rstrip()


def sorting_directory(folder):
    return sort_dir(Path(folder).resolve())


commands = {
    "hello": greeting,
    "help": help,
    "add": add_user,
    "note": add_note,
    "change": change_phone,
    "show all": show_all,
    "show notes": show_notes,
    "phone": get_phone_number,
    "exit": exit,
    "good bye": exit,
    "close": exit,
    "email": get_email,
    "birthday": get_birthday,
    "birthdays": remaining_days,
    "search": search_by_criteria,
    "page": iteration,
    "notes": iteration_note,
    "modify": change_note,
    "find": find_user_adressbook,
    "delete": del_record,
    "hashtag": get_note,
    "sort": sorting_directory,
}

filename1 = "address_book.bin"
filename2 = "note_book.bin"


def command_parser(user_input):
    command, *args = user_input.strip().split(" ")
    if not command.strip():
        return unknown_command, args
    try:
        handler = commands[command.lower()]

    except KeyError:
        if args:
            command_part2, *args = args[0].strip().split(" ", 1)
            command = command + " " + command_part2
        handler = commands.get(command.lower())
        if handler is None:
            user_input = change_command(user_input)
            if user_input is None:
                return unknown_command, args
            return command_parser(user_input)
    if command.lower() == "modify":
        args = [args[0], args[1], " ".join(args[2:])]
    elif command.lower() == "note":
        try:
            args = [" ".join(args)]
        except IndexError:
            pass
    return handler, args


def main():
    phonebook.load_address_book(filename1)
    notebook.load_notes(filename2)

    while True:
        user_input = input(">>> ")

        global cashe
        cashe = user_input

        handler, args = command_parser(user_input)
        result = handler(*args)

        if not result:
            print("Goodbye!")
            phonebook.save_address_book(filename1)
            notebook.save_notes(filename2)
            break
        print(result)


if __name__ == "__main__":
    main()
