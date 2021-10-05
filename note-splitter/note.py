import os
from typing import List


class Note:
    def __init__(self, path: str, folder_path: str, name: str):
        self.path = path
        self.folder_path = folder_path
        self.name = name


def get_chosen_notes(settings: dict) -> List[Note]:
    """Gets the notes that the user chose to split."""
    chosen_notes = []
    all_notes = get_all_notes(settings)
    for note in all_notes:
        with open(note.path, 'r', encoding='utf8') as file:
            contents = file.read()
        if settings['split keyword'] in contents:
            chosen_notes.append()
    return chosen_notes


def get_all_notes(settings: dict) -> List[Note]:
    """Gets all the notes in the user's chosen folder."""
    notes = []
    folder_path = settings['source folder path']
    folder_list = os.listdir(folder_path)
    for file_name in folder_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file_name)
            if file_ext in settings['note types']:
                notes.append(Note(file_path, folder_path, file_name))

    return notes
