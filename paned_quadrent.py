#!/usr/bin/env python

from gi.repository import Gtk
import signal


class _LinkedPaned(Gtk.Paned):
    """
        Paned container with linked resize event.
    """

    loop = False

    def __init__(self):
        super(_LinkedPaned, self).__init__()

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


class PanedQuadrent(Gtk.Paned):
    """
        Nested Gtk.Paned containers to make a quadent with linked panes.
    """

    child1 = Gtk.Frame(shadow_type=Gtk.ShadowType.IN)
    child2 = Gtk.Frame(shadow_type=Gtk.ShadowType.IN)
    child3 = Gtk.Frame(shadow_type=Gtk.ShadowType.IN)
    child4 = Gtk.Frame(shadow_type=Gtk.ShadowType.IN)

    _linked1 = _LinkedPaned()
    _linked2 = _LinkedPaned()

    def __init__(self, orientation=Gtk.Orientation.VERTICAL):
        super(PanedQuadrent, self).__init__()

        self.orientation = orientation
        self._init_orientation()

        self._linked1.bind_resize(self._linked2)
        self._linked2.bind_resize(self._linked1)

        self._linked1.pack1(self.child1)
        self._linked1.pack2(self.child2)
        self._linked2.pack1(self.child3)
        self._linked2.pack2(self.child4)

        super(PanedQuadrent, self).pack1(self._linked1)
        super(PanedQuadrent, self).pack2(self._linked2)

    def _init_orientation(self):
        self.set_orientation(self.orientation)

        # Invert opientation
        self.sub_orientation = (
            Gtk.Orientation.HORIZONTAL
            if self.orientation is Gtk.Orientation.VERTICAL
            else Gtk.Orientation.VERTICAL
        )

        self._linked1.set_orientation(self.sub_orientation)
        self._linked2.set_orientation(self.sub_orientation)

    def pack1(self, widget):
        self.child1.add(widget)
    def pack2(self, widget):
        self.child2.add(widget)
    def pack3(self, widget):
        self.child3.add(widget)
    def pack4(self, widget):
        self.child4.add(widget)
