
## A Python Tutorial System
## Copyright (C) 2009,2010  Peter Robinson <pjr@itee.uq.edu.au>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.

## The frame in which the problem description is rendered as HTML
## The possible HTML tags are
## h1, h2, h3, h4, h5, it, tt, b, br, p, pre, ul, li, img
## and span as long as <span style='color:c'> where c is red, blue or green

from abc import ABCMeta, abstractmethod
from html.parser import HTMLParser
import os
import tkinter as tk
from tkinter import ttk

FONTS_INFO = [('h1', 8, 'bold'),
              ('h2', 6, 'bold'),
              ('h3', 4, 'bold'),
              ('h4', 2, 'bold'),
              ('h5', 0, 'bold'),
              ('it', 0, 'normal'),
              ('b', 0, 'bold'),
              ('tt', 1, 'normal')]

HEADERS = ['h1', 'h2', 'h3', 'h4', 'h5']
INDENT = ['indent0', 'indent1', 'indent2', 'indent3', 'indent4', 'indent5']
COLOURS = ['red', 'green', 'blue']

INTRO_TEXT = """
<p>
<p>
<h3>Welcome to MyPyTutor {version}</h3>

The Problems menu contains the
collection of problems to choose from.
"""

ONLINE_TEXT = """
<p>
Use the Online menu to interact with your online information.
</p>
"""


class TutorialHTMLParserDelegate(metaclass=ABCMeta):
    @abstractmethod
    def append_text(self, text, *args):
        pass

    @abstractmethod
    def append_image(self, image_name):
        pass


class TutorialFrame(ttk.Frame, TutorialHTMLParserDelegate):
    def __init__(self, master, fontinfo, textlen):
        super().__init__(master)

        font_name = fontinfo[0]
        font_size = int(fontinfo[1])

        self.text = tk.Text(self, height=textlen, wrap=tk.WORD)
        self.text.config(
            state=tk.DISABLED,
            font=(font_name, str(font_size), 'normal', 'roman')
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

        self.update_fonts(font_name, font_size)

        for i, tag in enumerate(INDENT):
            self.text.tag_config(tag, lmargin1=40*i, lmargin2=40*i + 14)

        for tag in COLOURS:
            self.text.tag_config(tag, foreground=tag)

        self.parser = TutorialHTMLParser(delegate=self)
        self.tut_directory = None

    # TutorialHTMLParserDelegate
    def append_text(self, text, *args):
        self.text.insert(tk.END, text, *args)

    def append_image(self, image_name):
        # TODO: img_obj used to be stored on self; check that changing that has
        # TODO: not introduced GC problems
        path = os.path.join(self.tutorial.tutorial_path, image_name)
        img_obj = tk.PhotoImage(file=path)

        img_label = ttk.Label(self.text, image=img_obj)
        self.text.window_create(tk.END, window=img_label)

    #
    def splash(self, online, version):
        text = INTRO_TEXT.format(version=version)

        if online:
            text += ONLINE_TEXT

        self.add_text(text)

    def update_text_length(self, lines):
        self.text.config(height=lines)

    def update_fonts(self, font_name, font_size):
        for name, font_delta, weight in FONTS_INFO:
            font = font_name
            style = 'roman'
            size = str(font_size + font_delta)

            if name == 'tt':
                font = 'courier'
            elif name == 'it':
                style = 'italic'

            self.text.tag_config(name, font=(font, size, 'normal', style))

        self.text.config(
            font=(font_name, str(font_size), 'normal', 'roman')
        )

    def set_directory(self, directory):
        # TODO: I'm not currently calling this
        self.tut_directory = directory

    def add_text(self, text):
        # TODO: this method name is bad - it doesn't add, it replaces
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)

        self.text.insert(tk.END, '\n')

        self.parser.reset()
        self.parser.feed(text)

        self.text.config(state=tk.DISABLED)

    def show_hint(self, text):
        self.text.config(state=tk.NORMAL)

        self.parser.reset()
        self.parser.feed(text)

        self.text.yview(tk.MOVETO, 1)

        self.text.config(state=tk.DISABLED)


class TutorialHTMLParser(HTMLParser):
    def __init__(self, delegate):
        super().__init__(self)

        self.delegate = delegate

        self.header = ''
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False

    def reset(self):
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        self.do_lstrip = False
        if tag == 'span':
            if len(attrs) == 1 and len(attrs[0]) == 2 \
                    and attrs[0][0] == 'style':
                style = attrs[0][1].split(':')
                if len(style) == 2 and style[0].strip() == 'color':
                    self.active_tags.append(style[1].strip())
                else:
                    self.active_tags.append(tag)
            else:
                self.active_tags.append(tag)
        elif tag == 'br':
            self.do_lstrip = True
            self.delegate.append_text('\n')
        elif tag == 'p':
            self.do_lstrip = True
            self.delegate.append_text('\n\n')
        elif tag == 'img':
            img_file = attrs[0][1]
            self.delegate.insert_image(img_file)
            self.active_tags.append(tag)
        else:
            if tag == 'ul':
                self.delegate.append_text('\n')
                self.indent += 1
                self.active_tags.append(tag)
            elif tag == 'li':
                self.active_tags.append(INDENT[self.indent])
                self.do_lstrip = True
                if not self.end_ul:
                    self.delegate.append_text('\n')
                self.delegate.append_text('* ', tuple(self.active_tags))
            else:
                self.active_tags.append(tag)
        self.end_ul = False

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.delegate.append_text('\n\n')
            self.indent -= 1
            self.do_lstrip = True
            self.end_ul = True
        elif tag == 'li':
            self.do_lstrip = True
        elif tag == 'p':
            self.do_lstrip = True
            return
        elif tag in HEADERS:
            self.delegate.append_text('\n\n')
            self.do_lstrip = True
        self.active_tags.pop(-1)

    def _compress_data(self, data):
        data = data.replace('\n', ' ')
        if len(data) > 1:
            first = data[0]
            last = data[-1]
        elif data == ' ':
            first = ' '
            last = ' '
        else:
            first = ''
            last = ''
        data = ' '.join(data.split())
        if self.do_lstrip:
            self.do_lstrip = False
            if data and last == ' ':
                data = data + last
        else:
            if first == ' ':
                data = first+data
            if data != ' ' and last == ' ':
                data = data + last
        return data

    def handle_data(self, data):
        if self.active_tags:
            tag = self.active_tags[-1]
            if tag == 'ul':
                return
            if tag == 'pre':
                self.delegate.append_text(data, ('tt',))
                return
            data = self._compress_data(data)
            # TODO: I'm not sure why it was necessary to give priority to
            # TODO: all non-indent tags; this seems to also reverse the order
            # TODO: of the active tags, which is a bit odd
            #for tag in self.active_tags:
            #    if 'indent' not in tag:
            #        self.textobj.tag_raise(tag)
            self.delegate.append_text(data, tuple(self.active_tags))
        else:
            data = self._compress_data(data)
            self.delegate.append_text(data)
