#!/usr/bin/env python3
import gi
import requests
import threading
import time

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib

# Replace 'YOUR_OPENAI_API_KEY' with your actual API key
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
API_ENDPOINT = 'https://api.openai.com/v1/chat/completions'

class ChatApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ChatGPT Chat Box")
        self.set_default_size(400, 300)

        # Create a vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.chat_view)

        vbox.pack_start(scrolled_window, True, True, 0)

        self.chat_entry = Gtk.Entry()
        self.chat_entry.connect("activate", self.send_message)
        vbox.pack_start(self.chat_entry, False, False, 0)

        self.messages = []

    def center_text(self):
        buffer = self.chat_view.get_buffer()
        tag = buffer.create_tag("center", justification=Gtk.Justification.CENTER)
        buffer.get_tag_table().add(tag)
        buffer.apply_tag(tag, buffer.get_start_iter(), buffer.get_end_iter())



    def send_message(self, entry):
        message = entry.get_text()
        entry.set_text("")  # Clear the entry

        # Display user's message
        self.display_message(f"You: {message}", is_user=True)

        # Request response from ChatGPT
        response = self.request_gpt_response(message)

        # Display ChatGPT's response
        self.display_message(f"ChatGPT: {response}", is_user=False)

    def request_gpt_response(self, message):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}',
        }

        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'},
                         {'role': 'user', 'content': message}],
        }

        response = requests.post(API_ENDPOINT, json=data, headers=headers)
        response_data = response.json()
        return response_data['choices'][0]['message']['content']

    def display_message(self, message, is_user=True):
        buffer = self.chat_view.get_buffer()

        # Get the end iterator of the buffer
        end_iter = buffer.get_end_iter()

        # Create a text mark at the end of the buffer
        mark = buffer.create_mark(None, end_iter, left_gravity=True)

        # If not user, apply bold styling
        if not is_user:
            buffer.insert_with_tags(end_iter, f"\n{message}\n", "bold", "center")
        else:
            buffer.insert(end_iter, f"\n{message}\n")

        # Scroll to the mark to keep the latest message visible
        self.chat_view.scroll_mark_onscreen(mark)
        buffer.delete_mark(mark)

def main():
    Gtk.main()

if __name__ == "__main__":
    chat_app = ChatApp()
    chat_app.connect("destroy", Gtk.main_quit)
    chat_app.show_all()

    # Start a thread for the GTK main loop
    GLib.idle_add(main)

    # Periodically update the GTK main loop
    while True:
        time.sleep(0.1)
        while Gtk.events_pending():
            Gtk.main_iteration()
