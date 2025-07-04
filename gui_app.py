# gui_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from visualization import CircuitVisualizer
from circuit_logic import Circuit

class App(ttkb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("CircuitPro - Schaltungsanalyse")
        self.geometry("1200x700")

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Paned window for resizable sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Input Frame (Left) ---
        input_frame = ttk.Frame(paned_window, padding="10", relief="solid", borderwidth=1)
        paned_window.add(input_frame, weight=1)

        # --- Visualization Frame (Center) ---
        vis_frame = ttk.Frame(paned_window, padding="10", relief="solid", borderwidth=1)
        paned_window.add(vis_frame, weight=3)

        # --- Results Frame (Right) ---
        results_frame = ttk.Frame(paned_window, padding="10", relief="solid", borderwidth=1)
        paned_window.add(results_frame, weight=1)

        # --- Widgets for Input Frame ---
        # Title
        ttk.Label(input_frame, text="Parameter", font=("Inter", 16, "bold")).pack(pady=10)

        # Voltage Input
        voltage_frame = ttk.Frame(input_frame)
        voltage_frame.pack(fill=tk.X, pady=10)
        ttk.Label(voltage_frame, text="Gesamtspannung (Ug):").pack(side=tk.LEFT, padx=5)
        self.voltage_entry = ttk.Entry(voltage_frame, width=10)
        self.voltage_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Label(voltage_frame, text="V").pack(side=tk.LEFT)

        # Circuit Type Selection
        circuit_type_frame = ttk.Frame(input_frame)
        circuit_type_frame.pack(fill=tk.X, pady=10)
        ttk.Label(circuit_type_frame, text="Schaltungsart:").pack(side=tk.LEFT, padx=5)
        self.circuit_type = ttk.Combobox(circuit_type_frame, values=["Reihenschaltung", "Parallelschaltung", "Mischschaltung"])
        self.circuit_type.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.circuit_type.current(0)

        # Mixed Circuit Input Frame (defined early to avoid AttributeError)
        self.mixed_circuit_frame = ttk.LabelFrame(input_frame, text="Mischschaltung Definition", padding=10)
        self.mixed_circuit_label = ttk.Label(self.mixed_circuit_frame, text="Definieren Sie die Schaltung (z.B. R1 + (R2 || R3)):", wraplength=250)
        self.mixed_circuit_text = tk.Text(self.mixed_circuit_frame, height=5, width=30)
        # Initially hide mixed circuit input
        self.mixed_circuit_frame.pack_forget()
        self.mixed_circuit_label.pack_forget()
        self.mixed_circuit_text.pack_forget()

        # Resistors Frame (for Series/Parallel)
        self.resistors_frame = ttk.LabelFrame(input_frame, text="Widerstände", padding=10)
        self.resistors_frame.pack(fill=tk.BOTH, expand=True, pady=10) # Initially packed
        
        # Buttons for Series/Parallel (defined before add_resistor_entry to avoid AttributeError)
        self.button_frame = ttk.Frame(input_frame)
        self.button_frame.pack(fill=tk.X, pady=10) # Initially packed
        ttk.Button(self.button_frame, text="+ Widerstand", command=lambda: self.add_resistor_entry(self.resistors_frame)).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(self.button_frame, text="- Widerstand", command=self.remove_resistor_entry).pack(side=tk.LEFT, expand=True, padx=5)

        # Buttons for Series/Parallel (defined before add_resistor_entry to avoid AttributeError)
        self.button_frame = ttk.Frame(input_frame)
        self.button_frame.pack(fill=tk.X, pady=10) # Initially packed
        ttk.Button(self.button_frame, text="+ Widerstand", command=lambda: self.add_resistor_entry(self.resistors_frame)).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(self.button_frame, text="- Widerstand", command=self.remove_resistor_entry).pack(side=tk.LEFT, expand=True, padx=5)

        # Buttons for Series/Parallel (defined before add_resistor_entry to avoid AttributeError)
        self.button_frame = ttk.Frame(input_frame)
        self.button_frame.pack(fill=tk.X, pady=10) # Initially packed
        ttk.Button(self.button_frame, text="+ Widerstand", command=lambda: self.add_resistor_entry(self.resistors_frame)).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(self.button_frame, text="- Widerstand", command=self.remove_resistor_entry).pack(side=tk.LEFT, expand=True, padx=5)

        self.resistor_entries = []
        self.add_resistor_entry(self.resistors_frame) # Add first resistor

        # Action Buttons
        action_button_frame = ttk.Frame(input_frame)
        action_button_frame.pack(fill=tk.X, pady=20, side=tk.BOTTOM)
        ttk.Button(action_button_frame, text="Berechnen", style="success.TButton", command=self.calculate_and_display).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(action_button_frame, text="Zurücksetzen", style="danger.TButton", command=self.reset_all).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)


        # --- Widgets for Visualization Frame ---
        self.canvas = tk.Canvas(vis_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.visualizer = CircuitVisualizer(self.canvas)

        # Bind events to update visualization
        self.circuit_type.bind("<<ComboboxSelected>>", self.update_visualization)
        self.update_visualization() # Initial draw

        # --- Widgets for Results Frame ---
        self.results_frame = results_frame # Store reference
        ttk.Label(results_frame, text="Ergebnisse", font=("Inter", 16, "bold")).pack(pady=10)

    def add_resistor_entry(self, parent_frame):
        resistor_id = len(self.resistor_entries) + 1
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, pady=5)
        
        label = ttk.Label(frame, text=f"R{resistor_id}:")
        label.pack(side=tk.LEFT, padx=5)
        
        entry = ttk.Entry(frame, width=10)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        unit_label = ttk.Label(frame, text="Ω")
        unit_label.pack(side=tk.LEFT)
        
        self.resistor_entries.append((frame, entry))
        self.update_visualization()

    def remove_resistor_entry(self):
        if len(self.resistor_entries) > 1:
            frame, entry = self.resistor_entries.pop()
            frame.destroy()
            self.update_visualization()

    def update_visualization(self, event=None):
        circuit_type = self.circuit_type.get()
        num_resistors = len(self.resistor_entries)

        if circuit_type == "Mischschaltung":
            self.resistors_frame.pack_forget()
            self.button_frame.pack_forget()
            self.mixed_circuit_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            self.mixed_circuit_label.pack(pady=5)
            self.mixed_circuit_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.mixed_circuit_frame.pack_forget()
            self.mixed_circuit_label.pack_forget()
            self.mixed_circuit_text.pack_forget()
            self.resistors_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            self.button_frame.pack(fill=tk.X, pady=10)

        root_element = getattr(self, '_last_calculated_root_element', None) if circuit_type == "Mischschaltung" else None
        self.after(50, lambda: self.visualizer.draw(circuit_type, num_resistors, resistor_details=getattr(self, '_last_calculated_resistor_details', None), root_element=root_element)) # Delay to allow canvas to resize

    def calculate_and_display(self):
        try:
            voltage = float(self.voltage_entry.get())
            if voltage <= 0:
                messagebox.showerror("Fehler", "Die Gesamtspannung muss positiv sein.")
                return
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Zahl für die Gesamtspannung ein.")
            return

        resistor_values = []
        for frame, entry in self.resistor_entries:
            try:
                resistor_val = float(entry.get())
                if resistor_val <= 0:
                    messagebox.showerror("Fehler", "Alle Widerstandswerte müssen positiv sein.")
                    return
                resistor_values.append(resistor_val)
            except ValueError:
                messagebox.showerror("Fehler", f"Bitte geben Sie eine gültige Zahl für Widerstand R{len(resistor_values) + 1} ein.")
                return
        
        if not resistor_values:
            messagebox.showerror("Fehler", "Bitte fügen Sie mindestens einen Widerstand hinzu.")
            return

        circuit_type = self.circuit_type.get()
        mixed_circuit_definition = None
        if circuit_type == "Mischschaltung":
            mixed_circuit_definition = self.mixed_circuit_text.get("1.0", tk.END).strip()
            if not mixed_circuit_definition:
                messagebox.showerror("Fehler", "Bitte geben Sie eine Definition für die Mischschaltung ein.")
                return

        circuit = Circuit(voltage, resistor_values, circuit_type, mixed_circuit_definition=mixed_circuit_definition)
        results = circuit.calculate()

        self.display_results(results)
        self._last_calculated_resistor_details = results['resistor_details']
        self._last_calculated_resistor_details = results['resistor_details']
        self._last_calculated_root_element = circuit.root_element # Store the root element
        self.update_visualization() # Redraw visualization with calculated details

    def display_results(self, results):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            if widget.winfo_class() != "TLabel" or widget.cget("text") != "Ergebnisse": # Keep the title label
                widget.destroy()

        # Display total values
        ttk.Label(self.results_frame, text=f"Gesamtwiderstand (Rg): {results['total_resistance']:.2f} Ω", font=("Inter", 12)).pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(self.results_frame, text=f"Gesamtstrom (Ig): {results['total_current']:.2f} A", font=("Inter", 12)).pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(self.results_frame, text=f"Gesamtleistung (Pg): {results['total_power']:.2f} W", font=("Inter", 12)).pack(anchor=tk.W, padx=10, pady=2)

        ttk.Separator(self.results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10, padx=5)

        # Display individual resistor details
        ttk.Label(self.results_frame, text="Widerstandsdetails:", font=("Inter", 14, "bold")).pack(anchor=tk.W, padx=10, pady=5)

        for i, detail in enumerate(results['resistor_details']):
            ttk.Label(self.results_frame, text=f"R{i+1} ({detail['resistance']:.2f} Ω):", font=("Inter", 12, "bold")).pack(anchor=tk.W, padx=15, pady=2)
            ttk.Label(self.results_frame, text=f"  Spannung (U): {detail['voltage']:.2f} V").pack(anchor=tk.W, padx=25)
            ttk.Label(self.results_frame, text=f"  Strom (I): {detail['current']:.2f} A").pack(anchor=tk.W, padx=25)
            ttk.Label(self.results_frame, text=f"  Leistung (P): {detail['power']:.2f} W").pack(anchor=tk.W, padx=25)

    def reset_all(self):
        self.voltage_entry.delete(0, tk.END)
        self.voltage_entry.insert(0, "")
        self.circuit_type.current(0)

        # Remove all but one resistor entry
        while len(self.resistor_entries) > 1:
            frame, entry = self.resistor_entries.pop()
            frame.destroy()
        self.resistor_entries[0][1].delete(0, tk.END) # Clear the remaining resistor entry
        self.resistor_entries[0][1].insert(0, "")

        # Clear results display
        for widget in self.results_frame.winfo_children():
            if widget.winfo_class() != "TLabel" or widget.cget("text") != "Ergebnisse":
                widget.destroy()
        
        self.mixed_circuit_text.delete("1.0", tk.END)
        
        self.update_visualization() # Redraw empty circuit
