from gi.repository import Gtk
import signal

from pprint import pprint
import pdb

class Paned(Gtk.Paned):
    """docstring for Paned"""

    loop = False

    def __init__(self, orientation, child1, child2, size, shadow=Gtk.ShadowType.IN):
        super(Paned, self).__init__(orientation=orientation)

        self.child1 = child1
        self.frame1 = Gtk.Frame(shadow_type=shadow)
        self.frame1.set_size_request(*size)
        self.pack1(self.frame1, resize=True, shrink=False)
        self.frame1.add(child1)

        self.child2 = child2
        self.frame2 = Gtk.Frame(shadow_type=shadow)
        self.frame2.set_size_request(*size)
        self.pack2(self.frame2, resize=True, shrink=False)
        self.frame2.add(child2)

    def on_notify(self, _, gparamspec):

        if not gparamspec.name == 'position':
            return

        if self.loop:
            self.loop^=True
            return

        self.loop^=True

        self.linked.props.position = self.props.position

    def bind_resize(self, linked):
        self.connect('notify', self.on_notify)
        self.linked = linked


