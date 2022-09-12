from __future__ import annotations
from re import L
import blessed
import random
import math

term = blessed.Terminal()

class Floor:
    HORIZONTAL = 0
    VERTICAL = 1
    ROOM_AT_LEAST: int = 5
    def __init__(self, x_size:int, y_size:int, room_exponent:int=3):
        self.x_size = x_size
        self.y_size = y_size
        self.room_exponent = room_exponent # room count = 2 ** room_exponent
        self.room_list:list[Room] = []
        self.hallway_list:list[Hallway] = []
        self.init_floor()

    def init_floor(self):
        def get_splitting_line(start:int, end:int, at_least:int):
            assert end > start
            assert (end - start + 1) >= at_least * 2
            return start + random.randint(at_least, (end - start + 1) - at_least)

        def get_tree_height(step):
            return math.floor(math.log(step + 1, 2))

        def get_orientation(step, start_orientation=Floor.HORIZONTAL):
            return (get_tree_height(step) + start_orientation) % 2

        # Step 1. Floor positions

        tree: list[tuple[tuple[int, int], tuple[int, int]]] = [((0, self.x_size - 1),(0, self.y_size - 1))]
        start_orientation = random.choice([Floor.HORIZONTAL, Floor.VERTICAL])
        for i in range(2 ** self.room_exponent - 1):
            step_at_least = round((self.room_exponent - get_tree_height(i)) / 2 + 0.1) * Floor.ROOM_AT_LEAST
            parent = tree[len(tree) // 2]
            if get_orientation(i, start_orientation) == Floor.HORIZONTAL:
                splitting_line = get_splitting_line(parent[1][0], parent[1][1], step_at_least)

                assert (splitting_line - 1) - parent[1][0] + 1 >= step_at_least
                assert parent[1][1] - splitting_line + 1>= step_at_least

                tree.append((parent[0], (parent[1][0], splitting_line - 1)))
                tree.append((parent[0], (splitting_line, parent[1][1])))
            else:
                splitting_line = get_splitting_line(parent[0][0], parent[0][1], step_at_least)

                assert (splitting_line - 1) - parent[0][0] + 1 >= step_at_least
                assert parent[0][1] - splitting_line + 1 >= step_at_least

                tree.append(((parent[0][0], splitting_line - 1), parent[1]))
                tree.append(((splitting_line, parent[0][1]), parent[1]))

        # Step 2. Put Rooms
        test = []
        for next_sector in tree[-(2 ** self.room_exponent):]:
            horizontal_size = next_sector[0][1] - next_sector[0][0] + 1
            vertical_size = next_sector[1][1] - next_sector[1][0] + 1
            assert horizontal_size >= Floor.ROOM_AT_LEAST
            assert vertical_size >= Floor.ROOM_AT_LEAST

            room_horizontal_size = random.randint(Floor.ROOM_AT_LEAST, horizontal_size)
            room_vertical_size = random.randint(Floor.ROOM_AT_LEAST, vertical_size)

            horizontal_span_tot = horizontal_size - room_horizontal_size
            vertical_span_tot = vertical_size - room_vertical_size

            horizontal_span_left = random.randint(0, horizontal_span_tot)
            vertical_span_top = random.randint(0, vertical_span_tot)

            room_x_axis = next_sector[0][0] + horizontal_span_left
            room_y_axis = next_sector[1][0] + vertical_span_top

            self.room_list.append(Room(room_x_axis, room_y_axis, room_horizontal_size, room_vertical_size))
            test.append((room_x_axis, room_y_axis, room_horizontal_size, room_vertical_size))

        for next_room in self.room_list:
            next_room.print_component()

        # Step 3. Put Hallways
        def join(node1, node2):
            pass

        for height in range(self.room_exponent - 1, -1, -1):
            for i in range(2 ** height - 1, 2 ** (height + 1)):
                tree[i * 2]
                tree[i * 2 + 1]




class Element:
    term_ = blessed.Terminal()
    def __init__(self, x:int, y:int):
        self.displayed_character: str = "."
        self.color_format: str = "white_on_black"
        self.x:int = x
        self.y:int = y

    @classmethod
    def from_elem_list(cls, x:int, y:int, i:int, j:int) -> Element:
        return cls(x + j, y + i)

    def printelem(self) -> None:
        with Element.term_.location(self.x, self.y):
            print(getattr(Element.term_, self.color_format) + self.displayed_character, end=Element.term_.normal)


class Wall(Element):
    def __init__(self, x:int, y:int):
        super().__init__(x, y)
        self.displayed_character = "#"

class Ground(Element):
    def __init__(self, x:int, y:int):
        super().__init__(x, y)
        self.displayed_character = "."

class Component:
    def __init__(self, x:int, y:int, x_size:int, y_size:int):
        self.x = x
        self.y = y
        self.x_size = x_size
        self.y_size = y_size
        self.type_list: list[list[type|None]] = [[None] * x_size for _ in range(y_size)]
        self.elem_list: list[list[Element|None]] = [[None] * x_size for _ in range(y_size)]
        self.init_component()
        self.init_component_elem()

    def init_component(self):
        pass

    def init_component_elem(self):
        for i in range(len(self.type_list)):
            for j in range(len(self.type_list[0])):
                if isinstance(self.type_list[i][j], type):
                    assert issubclass(self.type_list[i][j], Element)
                    elem_type: type[Element] = self.type_list[i][j]
                    self.elem_list[i][j] = elem_type.from_elem_list(self.x, self.y, i, j)
                    


    def print_component(self):
        for next_line in self.elem_list:
            for next_elem in next_line:
                if next_elem is not None:
                    next_elem.printelem()


class Room(Component):
    def init_component(self):
        for i in range(len(self.type_list)):
            for j in range(len(self.type_list[0])):
                if i == 0 or i == len(self.type_list) - 1 or j == 0 or j == len(self.type_list[0]) - 1:
                    self.type_list[i][j] = Wall
                else:
                    self.type_list[i][j] = Ground



class Hallway(Component):
    def __init__(self, start_point_x:int, start_point_y:int, end_point_x:int, end_point_y:int, width=3):
        x = min(start_point_x, end_point_x)
        y = min(start_point_y, end_point_y)
        x_size = abs(end_point_x - start_point_x) + 1
        y_size = abs(end_point_y - start_point_y) + 1
        self.start_x_relative = start_point_x - x
        self.start_y_relative = start_point_y - y
        self.end_x_relative = end_point_x - x
        self.end_y_relative = end_point_y - y
        #self.width = width
        super().__init__(x, y, x_size, y_size)

    def init_component(self):
        assert all(x in (0, self.x_size - 1)
                    for x in [self.start_x_relative,self.end_x_relative])
        assert all(y in (0, self.y_size - 1)
                    for y in [self.start_y_relative, self.end_y_relative])
        if self.start_x_relative == self.start_y_relative: # orientation: \
            for i in range(self.x_size):
                self.type_list[i][0] = Ground
            for i in range(self.y_size):
                self.type_list[-1][i] = Ground
        else: # orientation: /
            for i in range(self.x_size):
                self.type_list[i][-1] = Ground
            for i in range(self.y_size):
                self.type_list[0][i] = Ground

print(term.clear)

floor1 = Floor(80, 30, 4)

with term.cbreak(), term.hidden_cursor():
    term.inkey()
print(term.clear, end='')
