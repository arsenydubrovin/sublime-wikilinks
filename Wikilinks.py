import sublime
import sublime_plugin
import os
import re

SETTINGS_FILE = "Wikilinks.sublime-settings"


class FollowWikilinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Load settings
        settings = sublime.load_settings(SETTINGS_FILE)
        directory = settings.get("wiki_directory")
        if not directory:
            print('"wiki_directory" setting is empty')
            return
        directory = os.path.expanduser(directory)
        ext = settings.get("wiki_extension")

        # Get file name under the cursor
        link_text = self.get_link_text()
        if not link_text:
            return

        # Create file if it doesn't exist
        file = os.path.join(directory, link_text + ext)
        if not os.path.exists(file):
            open(file, "a").close()

        # Open file in a new window
        self.view.window().open_file(file)

    def get_link_text(self):
        region = self.view.sel()[0]

        # Return if the region is a selection
        if not region.empty():
            return ""

        # Get the line of text at the cursor position
        pos = region.a
        line_pos = self.view.line(pos)
        text = self.view.substr(line_pos)

        # Find the link under the cursor position
        for match in re.finditer(r"\[\[(.*?)\]\]", text):
            if match.start() <= (pos - line_pos.begin()) <= match.end():
                return match.group(1)

        return ""


class GetWikilinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Load settings
        settings = sublime.load_settings(SETTINGS_FILE)
        directory = settings.get("wiki_directory")
        if not directory:
            print('"wiki_directory" setting is empty')
            return
        directory = os.path.expanduser(directory)
        ext = settings.get("wiki_extension")

        # List all files in the directory without file extensions
        self.file_names = [f.replace(ext, "") for f in os.listdir(directory)]
        self.view.window().show_quick_panel(self.file_names, self.on_done)

    def on_done(self, selection):
        # If no selection was made, insert [[
        if selection == -1:
            self.view.run_command("insert_wikilink", {"args": {"text": "[["}})
        else:
            # Otherwise, insert the selected link
            link_text = "[[" + self.file_names[selection] + "]]"
            self.view.run_command("insert_wikilink", {"args": {"text": link_text}})


class InsertWikilinkCommand(sublime_plugin.TextCommand):
    def run(self, edit, args):
        # Insert given text at the current cursor position
        pos = self.view.sel()[0].begin()
        self.view.insert(edit, pos, args["text"])
