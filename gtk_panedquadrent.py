""" Gtk Widget for linked 2x2 panes
"""

from gi.repository import Gtk

class LinkedPanes(Gtk.Bin):
    """ Linked Panes is a set of three paned widgets, one top level one
        and two nested ones that keep in sync with eachother.

        Args:
            tl (Gtk.Widget): Top left widget
            tr (Gtk.Widget): Top right widget
            bl (Gtk.Widget): Bottom left widget
            br (Gtk.Widget): Bottom right widget
    """
    def __init__(self, tl, tr, bl, br):
        super(LinkedPanes, self).__init__()

        if 'linked-pane':
            link1 = LinkedPane(
                Gtk.Orientation.HORIZONTAL,
                tl, tr,
                (160, 90)
            )
            link2 = LinkedPane(
                Gtk.Orientation.HORIZONTAL,
                bl, br,
                (160, 90)
            )
            link1.bind_resize(link2)
            link2.bind_resize(link1)

        if 'primary-pane':
            self.add(
                Pane(
                    Gtk.Orientation.VERTICAL,
                    link1, link2,
                    (160, 90),
                    Gtk.ShadowType.NONE
                )
            )

class Pane(Gtk.Paned):
    """ Gtk.Paned wrapper for easier building.

        Args:
            orientation (Gtk.Orientation): Horizontal or vertical orientation.
            child1 (Gtk.Widget): First widget to pack
            child2 (Gtk.Widget): Second widget to pack
            size (tuple): Pixel width-and-height-packed tuple.
            shadow (Gtk.ShadowType, optional): Shadow type, assumed "in" for best visual ease.
    """

    def __init__(self, orientation, child1, child2, size, shadow=Gtk.ShadowType.IN):
        super(Pane, self).__init__(orientation=orientation)

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

class LinkedPane(Pane):
    """ Pane wrapper with methods for position synchronizing.

        Args:
            *args (tuple): Passed to :py:class:`Paned`
    """

    _lp_user_activated = False

    def __init__(self, *args):
        super(LinkedPane, self).__init__(*args)
        self.connect('notify::position', self.on_position)
        self.connect('button-press-event', self.on_button_press)
        self.connect('button-release-event', self.on_button_release)

    def on_position(self, _, gparamspec):
        """ `notify::position` handler
            Updates sibling pane with new position.
        """
        if self._lp_user_activated:
            self.linked.child_on_position(self.props.position)

    def child_on_position(self, position):
        """ Sibling `notify::position` handler.
            This responds to sibling position updates.
        """
        self.set_position(position)

    def on_button_press(self, *_):
        """ Record when event happened directly to this widget (by a user
            mouse input) vs when it happens on another widget (eg the
            window is resized).
            We only wish to resize on user events as the window resize
            cascades its own resize events correctly already.
        """
        self._lp_user_activated = True

    def on_button_release(self, *_):
        """
            Correct real-time positioning mistakes.
            http://stackoverflow.com/a/7892056/1695680
        """
        self._lp_user_activated = False
        self.linked.set_position(self.props.position)

    def bind_resize(self, linked):
        """ Realize the sibling link.
        """
        self.linked = linked
