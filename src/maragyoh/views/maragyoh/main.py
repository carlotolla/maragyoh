#! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa Marayho
# Copyright 2014-2017 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://j.mp/GNU_GPL3>`__.
#
# Marayho é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>

"""Recursiv Item List.

.. moduleauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

try:
    from browser import document, html, window
    from connector import Connect
    NODOM = html.DIV()
except ImportError:
    from maragyoh.views.browser import document, html, window, NODOM
    from maragyoh.views.connector import Connect
"""
from . import log, document, html, window, NODOM
from .connector import Connect


from random import randint

SIZE = (50, 50)
GRAY = (50, 50, 50)


"""*##########################################*.

"""


class Item:
    """ An Item in the outline.

    :param node_id: Id for remote connection
    :param rgb: Color for the item
    :param size: Size for the item
    :param parent: Parent for the Item
    """
    conn = None
    item = {}
    prefix = "S_N_O_D_E_%03x" % randint(0x111, 0xfff) + "-%02d"

    def __init__(self, node_id, rgb, size=SIZE, parent=NODOM, text="-enter text-"):
        self.container = []
        self.capacity = self.item_count = self.rows = self.cols = 1
        self.base = self.content = NODOM
        self.parent, self.node_id, self.rgb, self.size, self.text = self.init_(node_id, rgb, size, parent, text)
        self.parent = parent

    def init_(self, node_id, rgb, size, parent, text):
        """
        >>> print(item.init_(2, (0, 0, 0), (15, 15), NODOM)[1:])
        (2, (0, 0, 0), (15, 15))

        :param text:
        :param node_id: Id for remote connection
        :param rgb: Color for the item
        :param size: Size for the item
        :param parent: the node from wich this stems
        :return: parent, node_id, rgb, size
        """
        # print("XXXXXXX>>>> _init", ">%s<" % [node_id, rgb, size])
        height, width = size
        brgb = tuple([max(0, k-randint(30, 100)) for k in rgb])
        self.base = base = html.DIV(style={
            "background-color": "rgb(%d, %d, %d)" % rgb, "border": "4px solid rgb(%d, %d, %d)" % brgb, "padding": "4px",
            "margin": "4px", "border-width": "medium", "border-radius": "15px",
            "height": "%dpx" % height, "width": "%dpx" % width, "float": "left"})
        self.content = content = html.SPAN(text, style={"position": "relative", "float": "left", "width": "75%"})
        adder = html.SPAN("➕", style={"position": "relative", "float": "left", "left": "-4px", "top": "-4px"})
        fixer = html.SPAN("❌", style={"position": "relative", "float": "right", "top": "-4px"})
        self.base <= adder
        self.base <= content
        self.base <= fixer
        fixer.onclick = self.fix_item
        adder.onclick = self.add_item
        content.onclick = self.edit_item
        # parent = Item.item[tuple(node_id[:-1])]
        parent <= self
        return parent, node_id, rgb, size, text

    def create(self, rgb=None, node_id=None, size=None):
        """Create an Item instance.

        :param node_id: Id for remote connection
        :param rgb: Color for the item
        :param size: Size for the item
        :return: An instance of Item
        """
        nodeid = node_id if node_id else self.node_id + (len(self.container),)
        rgb = rgb or (randint(240, 255), randint(240, 255), randint(240, 255))
        size = size if size else self.compute_grid()
        item = Item(node_id=nodeid, rgb=rgb, size=size, parent=self)
        Item.item[nodeid] = item
        size = self.compute_grid()
        [it.resize(size) for it in self.container]
        return item

    def compute_grid(self):
        height, width = self.size
        while len(self.container) > self.capacity:
            if height / (self.rows + 1) >= width / (self.cols + 1):
                self.rows = self.rows + 1
            else:
                self.cols = self.cols + 1
            self.capacity = self.rows * self.cols
        # size = height / self.rows-10, width / self.cols-10
        size = (height-1*(self.rows+1))/self.rows, (width-1*(self.cols+1))/self.cols
        # self.resize(size)
        return size

    def resize(self, size):
        height, width = self.size = size
        height, width = height-8*(self.rows+1), width-8*(self.cols+1)
        self.base.style.width = "%dpx" % width
        self.base.style.height = "%dpx" % height
        self.size = height, width
        [item.resize((height/self.rows, width/self.cols)) for item in self.container]

    def __le__(self, square):
        self.container.append(square)
        self.base <= square.base

    @staticmethod
    def fix_item(ev=None):
        ev.stopPropagation()
        ev.target.contentEditable = False

    @staticmethod
    def edit_item(ev=None):
        ev.stopPropagation()
        ev.target.contentEditable = True
        # self.create().send()

    def add_item(self, ev=None):
        ev.stopPropagation()
        log.debug("XXXXXXX>>>> Item.add_item(ev) = >%s<", [list(self.node_id), list(self.rgb), list(self.size)])
        self.create().send()
        # Item(self, self.compute_grid())

    def send(self):
        data = [list(self.node_id), list(self.rgb), list(self.size)]
        Item.conn.send(data)


"""*##########################################*.

"""


class Base(Item):
    """ The Base Item of the outline.

    :param node_id: Id for remote connection
    :param rgb: Color for the item
    :param last: index for the item
    """
    def __init__(self, last, node_id, rgb=GRAY):
        self.base = canvas = document["pydiv"]

        def _add_item(data):
            log.debug("XXXXXXX>>>> Base._add_item(data) = >%s<", data)
            _node_id, _rgb, _size = tuple(data[0]), tuple(data[1]), tuple(data[2])
            log.debug("XXXXXXX>>>> Base.Item.item = >%s<", Item.item.keys())
            log.debug("XXXXXXX>>>> type(_node_id) = >%s<, _node_id = >%s<", type(_node_id), _node_id)
            Item.item[_node_id[:-1]].create(_rgb, _node_id, _size)

        class NoItem:
            def __init__(self):
                self.container = []

            def __le__(self, square):
                canvas <= square.base

        Item.prefix = node_id
        self.no_item = NoItem()
        height,  width = window.innerHeight - 40, window.innerWidth - 100
        size = height,  width
        Item.item[()], Item.item[(0,)] = self.no_item, self
        Item.__init__(self, (0,), rgb, size, self.no_item)
        Item.conn = Connect(last, node_id, _add_item)
        self.base.style.left = 40
        self.base.style.top = 10
        self.base.style.position = "absolute"


"""*##########################################*.

"""


def main(last, nodeid):
    Base(last, nodeid)


if __name__ == "__main__":
    import doctest

    doctest.testmod(globs=dict(
        item=Item(12, GRAY),
        NODOM=NODOM
    ))

    doctest.testmod(globs=dict(item=Item(12, GRAY), NODOM=NODOM))