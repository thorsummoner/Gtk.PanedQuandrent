# pylint: disable=too-many-arguments
#
# Gtk.PanedQuadrant Synchronized Nested Gtk.Paned Widgets
# Copyright (C) 2014  Dylan Scott Grafmyre <thorsummoner@live.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
    Gtk.PanedQuadrant Synchronized Nested Gtk.Paned Widgets
"""

from gi.repository import Gtk

class PanedQuadrant(Gtk.Bin):
    """ Linked Panes is a set of three paned widgets, one top level one
        and two nested ones that keep in sync with eachother.

        Args:
            tl (Gtk.Widget): Top left widget
            tr (Gtk.Widget): Top right widget
            bl (Gtk.Widget): Bottom left widget
            br (Gtk.Widget): Bottom right widget
    """
    def __init__(self,
                 tl, tr, bl, br,
                 pane_width=-1, pane_height=-1,
                 width=-1, height=-1,
                 *args, **kwargs
                ):
        super(PanedQuadrant, self).__init__()
        self.connect('realize', self.on_realize)

        self.tl_pane = tl
        self.tr_pane = tr
        self.bl_pane = bl
        self.br_pane = br

        # linked-pane
        self.link1 = LinkedPane(
            Gtk.Orientation.HORIZONTAL,
            self.tl_pane, self.tr_pane,
            width=pane_width, height=pane_height,
        )
        self.link2 = LinkedPane(
            Gtk.Orientation.HORIZONTAL,
            self.bl_pane, self.br_pane,
            width=pane_width, height=pane_height,
        )
        self.link1.bind_resize(self.link2)
        self.link2.bind_resize(self.link1)

        # primary-pane
        self.pane = Pane(
            Gtk.Orientation.VERTICAL,
            self.link1, self.link2,
            Gtk.ShadowType.NONE,
            *args, **kwargs
        )
        self.pane.set_size_request(width, height)
        self.add(self.pane)

    def reset(self):
        """ Reset panes to equal position
        """
        self.pane.set_position(self.pane.get_allocated_height() / float(2) - 1)
        vposition = self.link1.get_allocated_width() / float(2) - 1
        self.link1.set_position(vposition)
        self.link2.set_position(vposition)


    def get_hsize(self):
        return self.link1.get_allocated_width()

    def set_hposition(self, position):
        """ Adjust Linked Horizontal Position
        """
        self.link1.set_position(position)
        self.link2.set_position(position)

    def get_vsize(self):
        return self.pane.get_allocated_height()

    def set_vposition(self, position):
        """ Adjust Linked Vertical Position
        """
        self.pane.set_position(position)

    def on_realize(self, _):
        """ Make minimum sizes homogeneous.
        """
        tl_min = self.tl_pane.get_preferred_size()[0]
        tr_min = self.tr_pane.get_preferred_size()[0]
        bl_min = self.bl_pane.get_preferred_size()[0]
        br_min = self.br_pane.get_preferred_size()[0]

        min_width = max([tl_min.width, tr_min.width, bl_min.width, br_min.width])
        min_height = max([tl_min.height, tr_min.height, bl_min.height, br_min.height])

        self.tl_pane.set_size_request(min_width, min_height)
        self.tr_pane.set_size_request(min_width, min_height)
        self.bl_pane.set_size_request(min_width, min_height)
        self.br_pane.set_size_request(min_width, min_height)

class Pane(Gtk.Paned):
    """ Gtk.Paned wrapper for easier building.

        Args:
            orientation (Gtk.Orientation): Horizontal or vertical orientation.
            child1 (Gtk.Widget): First widget to pack
            child2 (Gtk.Widget): Second widget to pack
            size (tuple): Pixel width-and-height-packed tuple.
            shadow (Gtk.ShadowType, optional): Shadow type, assumed "in" for best visual ease.
    """

    def __init__(self,
                 orientation, child1, child2,
                 width=-1, height=-1,
                 shadow=Gtk.ShadowType.IN,
                 *args, **kwargs
                ):
        super(Pane, self).__init__(orientation=orientation, *args, **kwargs)

        self.child1 = child1
        self.frame1 = Gtk.Frame(shadow_type=shadow)
        self.frame1.set_size_request(width, height)
        self.pack1(self.frame1, resize=True, shrink=False)
        self.frame1.add(child1)

        self.child2 = child2
        self.frame2 = Gtk.Frame(shadow_type=shadow)
        self.frame2.set_size_request(width, height)
        self.pack2(self.frame2, resize=True, shrink=False)
        self.frame2.add(child2)


class LinkedPane(Pane):
    """ Pane wrapper with methods for position synchronizing.

        Args:
            *args (tuple): Passed to :py:class:`Paned`
    """

    _lp_user_activated = False
    linked = None

    def __init__(self, *args, **kwargs):
        super(LinkedPane, self).__init__(*args, **kwargs)
        self.connect('notify::position', self.on_position)
        self.connect('button-press-event', self.on_button_press)
        self.connect('button-release-event', self.on_button_release)

    def on_position(self, *_):
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
