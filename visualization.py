# visualization.py

import tkinter as tk
from circuit_logic import CircuitElement, Resistor, SeriesCircuit, ParallelCircuit

class CircuitVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.resistor_elements = [] # To store canvas IDs and resistor data
        self.tooltip = None

    def draw(self, circuit_type, num_resistors, resistor_details=None, root_element=None):
        self.canvas.delete("all")
        self.resistor_elements = [] # Reset for new drawing

        if circuit_type == "Reihenschaltung":
            self.draw_series_circuit(num_resistors, resistor_details)
        elif circuit_type == "Parallelschaltung":
            self.draw_parallel_circuit(num_resistors, resistor_details)
        elif circuit_type == "Mischschaltung" and root_element:
            self.draw_mixed_circuit(root_element)

    def draw_series_circuit(self, num_resistors, resistor_details):
        start_x, start_y = 50, self.canvas.winfo_height() / 2
        self.draw_voltage_source(start_x, start_y)
        x, y = start_x + 40, start_y

        for i in range(num_resistors):
            resistor_data = resistor_details[i] if resistor_details else None
            self.draw_resistor(x, y, f"R{i+1}", resistor_data)
            x += 80
            self.draw_line(x - 40, y, x, y)

        self.draw_line(start_x, start_y, start_x, start_y + 50)
        self.draw_line(start_x, start_y + 50, x, start_y + 50)
        self.draw_line(x, y, x, start_y + 50)

    def draw_parallel_circuit(self, num_resistors, resistor_details):
        start_x, start_y = 50, self.canvas.winfo_height() / 2
        self.draw_voltage_source(start_x, start_y)
        x, y = start_x + 60, start_y - (num_resistors // 2 * 60)

        self.draw_line(start_x, start_y, x, start_y)

        for i in range(num_resistors):
            resistor_data = resistor_details[i] if resistor_details else None
            self.draw_line(x, start_y, x, y)
            self.draw_resistor(x, y, f"R{i+1}", resistor_data)
            self.draw_line(x + 40, y, x + 80, y)
            self.draw_line(x + 80, start_y, x + 80, y)
            y += 60

        self.draw_line(x, start_y, x + 80, start_y)

    def draw_resistor(self, x, y, label, data=None):
        rect_id = self.canvas.create_rectangle(x, y - 10, x + 40, y + 10, fill="white", outline="black")
        text_id = self.canvas.create_text(x + 20, y, text=label)
        
        self.resistor_elements.append({
            'rect_id': rect_id,
            'text_id': text_id,
            'data': data
        })

        self.canvas.tag_bind(rect_id, "<Enter>", lambda event, d=data: self.show_tooltip(event, d))
        self.canvas.tag_bind(rect_id, "<Leave>", self.hide_tooltip)
        self.canvas.tag_bind(text_id, "<Enter>", lambda event, d=data: self.show_tooltip(event, d))
        self.canvas.tag_bind(text_id, "<Leave>", self.hide_tooltip)

    def draw_mixed_circuit(self, root_element):
        start_x, start_y = 50, self.canvas.winfo_height() / 2
        self.draw_voltage_source(start_x, start_y)
        
        # Recursively draw the circuit elements
        self._draw_element(root_element, start_x + 60, start_y, 'horizontal')

    def _draw_element(self, element, x, y, orientation, level=0):
        if isinstance(element, Resistor):
            self.draw_resistor(x, y, element.name, {
                'resistance': element.resistance,
                'voltage': element.voltage,
                'current': element.current,
                'power': element.power
            })
            return x + 80, y # Return end position
        
        elif isinstance(element, SeriesCircuit):
            current_x = x
            current_y = y
            for i, child in enumerate(element.children):
                if i > 0:
                    self.draw_line(current_x - 40, current_y, current_x, current_y) # Connect previous element
                current_x, current_y = self._draw_element(child, current_x, current_y, orientation, level + 1)
            return current_x, current_y

        elif isinstance(element, ParallelCircuit):
            # Draw parallel lines
            branch_start_x = x
            branch_end_x = x + 120 # Arbitrary width for parallel branches
            
            # Draw entry line to parallel block
            self.draw_line(x, y, branch_start_x, y)

            # Calculate vertical spacing for parallel branches
            total_height = len(element.children) * 60
            current_y = y - (total_height / 2) + 30 # Center branches around y

            child_end_x = branch_end_x
            for i, child in enumerate(element.children):
                # Draw line to branch start
                self.draw_line(branch_start_x, y, branch_start_x, current_y)
                
                # Draw child element
                child_x, child_y = self._draw_element(child, branch_start_x + 20, current_y, 'horizontal', level + 1)
                
                # Draw line from child end to parallel end
                self.draw_line(child_x, current_y, branch_end_x, current_y)
                self.draw_line(branch_end_x, current_y, branch_end_x, y)
                
                current_y += 60
            
            # Draw exit line from parallel block
            self.draw_line(branch_end_x, y, branch_end_x + 40, y)
            return branch_end_x + 40, y
        return x, y

    def draw_voltage_source(self, x, y):
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="white", outline="black")
        self.canvas.create_text(x, y, text="Ug")

    def draw_line(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2)

    def show_tooltip(self, event, data):
        if data:
            tooltip_text = f"U: {data['voltage']:.2f} V\nI: {data['current']:.2f} A\nP: {data['power']:.2f} W"
            x, y = event.x, event.y
            self.tooltip = self.canvas.create_text(x + 10, y + 10, text=tooltip_text, anchor=tk.NW, 
                                                    bbox=(x + 5, y + 5, x + 100, y + 60), fill="black",
                                                    font=("Inter", 10), background="lightyellow", relief=tk.SOLID, borderwidth=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.canvas.delete(self.tooltip)
            self.tooltip = None
