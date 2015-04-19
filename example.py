#!/usr/bin/env python2

import signal
from gi.repository import Gtk
from paned_quadrent import PanedQuadrent

class ExampleWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Example Quadrent")
        self.connect("delete-event", Gtk.main_quit)

        self.quad = PanedQuadrent()
        self.add(self.quad)

        self.label1 = Gtk.Label('Top Left')
        self.quad.pack1(self.label1)

        self.label2 = Gtk.Label('Top Right')
        self.quad.pack2(self.label2)

        self.label3 = Gtk.Label('Bottom Left')
        self.quad.pack3(self.label3)

        self.label4 = Gtk.Label('Bottom Right')
        self.quad.pack4(self.label4)

    def main(self):
        self.set_default_size(400, 300)
        self.show_all()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

def main():
    ExampleWindow().main()

if __name__ == '__main__':
    main()
