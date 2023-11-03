#!/usr/bin/python3

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from solver import *
from sudoku import *

button_txt_color    = (  0,   0,   0, 1)
button_click_color  = (127, 0, 0, 1)
button_bg_color     = (255, 255, 255, 1)

class root_layout(GridLayout):
    def __init__(self,**kwargs):
        super(root_layout, self).__init__(**kwargs)
        self.cols = 1
        self.input_value = None

        #self.padding = (10,10,10,10)

        # Add grid
        self.grid = grid_layout()
        self.add_widget(self.grid)

        # Add inputs
        self.inputs = inputs_layout()
        self.add_widget(self.inputs)

    def do_layout(self,*args):
        self.apply_ratio()
        super(root_layout, self).do_layout()

    def apply_ratio(self):
        # Get windows size
        x,y = Window.size

        self.grid.size_hint     = None,None
        self.inputs.size_hint   = None,None
        self.grid.pos_hint      = {"center_x": .5, "center_y": .5}
        self.inputs.pos_hint    = {"center_x": .5, "center_y": .5}

        # Resize elements
        if x > y:
            self.cols = 2
            self.grid.size   = y,y
            self.inputs.size = x-y,y
            self.inputs.cols = 1
            self.inputs.input_nums.cols = 2

        else:
            self.cols = 1
            self.grid.size   = x,x
            self.inputs.size = x,y-x
            self.inputs.cols = 2
            self.inputs.input_nums.cols = 5

        # Resize fonts
        for x in range(9):
            for y in range(9):
                self.grid.case_layout[x][y].font_size = self.grid.case_layout[x][y].width/2

        # for x in range(10):
        #     self.inputs.input_nums.nums_dict[x].size_hint = None,None
        #     self.inputs.input_nums.nums_dict[x].size      = self.grid.case_layout[0][0].size
        #     self.inputs.input_nums.nums_dict[x].font_size = self.grid.case_layout[0][0].width/3

        #for x in range(2):
            #self.inputs.input_acts.actions_dict[x].size_hint = None,None
            #self.inputs.input_acts.actions_dict[x].size      = self.grid.case_layout[0][0].size[0]*2,self.grid.case_layout[0][0].size[0]
            
            #self.inputs.input_acts.actions_dict[x].pos_hint  = {"center_x": .5, "center_y": .5}
            #self.inputs.input_acts.actions_dict[x].font_size = self.grid.case_layout[0][0].width/3

        # Set inputs
        # self.inputs.size_hint = None,None
        # self.inputs.pos_hint  = {"center_x": .5, "center_y": .5}

        # if x > y:
        #     self.inputs.size = y,y
        # else:
        #     self.inputs.size = x,x

class inputs_layout(GridLayout):
    def __init__(self,**kwargs):
        super(inputs_layout, self).__init__(**kwargs)
        self.cols = 2

        self.input_nums = input_numbers()
        self.add_widget( self.input_nums )

        self.input_acts = input_actions()
        self.add_widget( self.input_acts )

class input_actions(GridLayout):
    def __init__(self,**kwargs):
        super(input_actions, self).__init__(**kwargs)
        self.cols = 1
        self.padding = 3
        self.spacing = 2

        self.actions_dict = dict()
        for x in range(2):
            if x == 0:
                text_value = "Solve"
            else:
                text_value = "Clear"

            self.actions_dict[x] = Button(
                text=text_value,
                color=button_txt_color,
                background_color=button_bg_color,
                bold=False,
                font_size=self.width/3
                )
            self.actions_dict[x].value = text_value

            self.add_widget( self.actions_dict[x] )
            self.actions_dict[x].bind(on_press=self.button_pressed)
            self.actions_dict[x].bind(on_release=self.button_released)

    def button_pressed(self,instance):
        instance.background_color = button_click_color
        if instance.value == "Clear":
            for x in range(9):
                for y in range(9):
                    self.parent.parent.grid.case_layout[x][y].text = ""

        if instance.value == "Solve":
            # Create sudoku
            sudoku_obj = sudoku()
            for x in range(9):
                for y in range(9):
                    case_value = self.parent.parent.grid.case_layout[x][y].text
                    if case_value == "":
                        sudoku_obj.set_value(0,(x,y))
                    else:
                        sudoku_obj.set_value(int(case_value),(x,y))

            # Solve sudoku
            sudoku_solver(sudoku_obj,10,False)

            # Update Grid
            for x in range(9):
                for y in range(9):
                    self.parent.parent.grid.case_layout[x][y].text = str(sudoku_obj.get_value((x,y)))

    def button_released(self,instance):
        instance.background_color = button_bg_color

class input_numbers(GridLayout):
    def __init__(self,**kwargs):
        super(input_numbers, self).__init__(**kwargs)
        self.cols = 5
        self.padding = 3
        self.spacing = 2

        self.nums_dict = dict()
        for x in range(10):
            if x == 0: 
                text_value = ""
            else:
                text_value = str(x)

            self.nums_dict[x] = Button(
                text=text_value,
                color=button_txt_color,
                background_color=button_bg_color,
                bold=False,
                font_size=self.width/3
                )
            self.nums_dict[x].value = text_value
            self.nums_dict[x].bind(on_press=self.button_pressed)
            #self.nums_dict[x].bind(on_release=self.button_released)
            self.add_widget(self.nums_dict[x])

    def button_pressed(self,instance):
        # Clear button color            
        for x in range(10):
            self.nums_dict[x].background_color = button_bg_color
        
        if self.parent.parent.input_value != instance.value:
            self.parent.parent.input_value = instance.value
            # Color button
            instance.background_color = button_click_color
        else:
            self.parent.parent.input_value = None

    def button_released(self,instance):
        instance.background_color = button_bg_color

class grid_layout(GridLayout):
    def __init__(self,**kwargs):
        super(grid_layout, self).__init__(**kwargs)
        self.cols = 3
        #self.padding = 10

        # Create Block
        self.block_layout = dict()
        for line_block in range(3):
            self.block_layout[line_block] = dict()
            for row_block in range(3):
                self.block_layout[line_block][row_block] = GridLayout(cols=3,padding=3,spacing=2)
                self.add_widget(self.block_layout[line_block][row_block])

        # Create cases
        self.case_layout = dict()
        for line_case in range(9):
            self.case_layout[line_case] = dict()
            for row_case in range(9):
                self.case_layout[line_case][row_case] = Button(
                    text='',
                    color=button_txt_color,
                    background_color=button_bg_color,
                    bold=False,
                    font_size=self.width/3
                    )
                self.case_layout[line_case][row_case].position = (line_case,row_case)
                self.case_layout[line_case][row_case].pressed  = False
                self.case_layout[line_case][row_case].bind(on_press=self.button_pressed)
                self.case_layout[line_case][row_case].bind(on_release=self.button_released)

                # Add widget
                self.block_layout[int(line_case/3)][int(row_case/3)].add_widget(self.case_layout[line_case][row_case])

    def button_pressed(self,instance):
        instance.background_color = button_click_color
        x,y = instance.position
        if self.parent.input_value != None:
            self.case_layout[x][y].text = self.parent.input_value

    def button_released(self,instance):
        instance.background_color = button_bg_color

class SudokuSolverApp(App):
    def build(self):
        Window.clearcolor = (0.5, 0.5, 0.5, 1)
        self.root = root_layout()

        return self.root

if __name__ == '__main__':
    SudokuSolverApp().run()
