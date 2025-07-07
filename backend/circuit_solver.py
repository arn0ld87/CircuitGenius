from typing import List, Dict, Any, Union

# This is the internal representation for any component in the circuit tree.
# It can be a single resistor or a group (series/parallel) of other components.
class Component:
    def __init__(self, name: str, value: float, comp_type: str = "resistor"):
        self.name = name
        self.value = value          # Ohmic value
        self.type = comp_type       # "resistor", "series", "parallel"
        self.voltage = 0.0
        self.current = 0.0
        self.power = 0.0
        self.children: List['Component'] = []

    def to_dict(self):
        return {
            "resistor": self.name,
            "resistance": self.value,
            "voltage": self.voltage,
            "current": self.current,
            "power": self.power,
        }

class MixedCircuitSolver:
    """
    A class-based solver for mixed circuits to provide better state management
    and a clearer structure for the recursive two-pass calculation.
    """
    def __init__(self):
        self.resistor_id_counter = 1
        self.solution_steps = []

    def _build_component_tree(self, structure: Union[Dict, float, int]) -> Component:
        """
        Pass 1 (Part 1): Recursively builds the component tree from the input JSON.
        """
        if isinstance(structure, (int, float)):
            name = f"R{self.resistor_id_counter}"
            self.resistor_id_counter += 1
            return Component(name, float(structure))

        if isinstance(structure, dict):
            comp_type = structure.get("type")
            if comp_type not in ["series", "parallel"]:
                raise ValueError(f"Invalid component type: {comp_type}")

            children_structures = structure.get("components", [])
            children = [self._build_component_tree(c) for c in children_structures]
            
            child_names = [c.name for c in children]
            name_symbol = '+' if comp_type == "series" else '||'
            name = f"({name_symbol.join(child_names)})"
            
            node = Component(name, 0, comp_type) # Value is a placeholder for now
            node.children = children
            return node
        
        raise ValueError(f"Invalid circuit structure provided: {structure}")

    def _calculate_equivalent_resistance(self, node: Component):
        """
        Pass 1 (Part 2): Recursively calculates the equivalent resistance for each node
        in the tree, starting from the leaves.
        """
        if not node.children:
            return # It's a base resistor, its value is already set.

        # Recursively solve for children first
        for child in node.children:
            self._calculate_equivalent_resistance(child)

        child_values = [child.value for child in node.children]
        
        if node.type == "parallel":
            sum_of_inverses = sum(1/v for v in child_values if v != 0)
            node.value = 1 / sum_of_inverses if sum_of_inverses != 0 else 0
            
            step = f"Berechne Ersatzwiderstand für Parallelschaltung: {node.name}\n"
            step += f"   1/R_eq = {' + '.join([f'1/{v:.2f}' for v in child_values])} = {sum_of_inverses:.4f} S\n"
            step += f"   R_eq = {node.value:.2f} Ω"
            self.solution_steps.append(step)
        
        elif node.type == "series":
            node.value = sum(child_values)
            step = f"Berechne Ersatzwiderstand für Reihenschaltung: {node.name}\n"
            step += f"   R_eq = {' + '.join([f'{v:.2f}' for v in child_values])} Ω = {node.value:.2f} Ω"
            self.solution_steps.append(step)

    def _distribute_values(self, node: Component, voltage: float, current: float):
        """
        Pass 2: Distributes voltage and current down the tree from the root.
        """
        node.voltage = voltage
        node.current = current
        node.power = voltage * current

        if not node.children:
            return

        if node.type == "parallel":
            # Voltage is the same for all children in a parallel group
            for child in node.children:
                child_current = voltage / child.value if child.value != 0 else 0
                self._distribute_values(child, voltage, child_current)
        
        elif node.type == "series":
            # Current is the same for all children in a series group
            for child in node.children:
                child_voltage = current * child.value
                self._distribute_values(child, child_voltage, current)

    def _get_flat_resistor_list(self, node: Component) -> List[Component]:
        """
        Flattens the tree to get a simple list of all base resistors for the final output.
        """
        if not node.children:
            return [node]
        flat_list = []
        for child in node.children:
            flat_list.extend(self._get_flat_resistor_list(child))
        return flat_list

    def solve(self, circuit_structure: Dict[str, Any], total_voltage: float) -> Dict[str, Any]:
        """
        The main public method to solve the circuit.
        """
        # Pass 1: Build tree and calculate total resistance
        self.solution_steps.append("Schritt 1: Vereinfachung der Schaltung (Ersatzwiderstände)")
        root_node = self._build_component_tree(circuit_structure)
        self._calculate_equivalent_resistance(root_node)
        total_resistance = root_node.value
        self.solution_steps.append(f"\nGesamtwiderstand der Schaltung: Rg = {total_resistance:.2f} Ω")

        # Calculate total circuit values
        self.solution_steps.append("\nSchritt 2: Berechnung der Gesamtwerte")
        total_current = total_voltage / total_resistance if total_resistance != 0 else 0
        total_power = total_voltage * total_current
        self.solution_steps.append(f"Gesamtstrom (Ig) = Ug / Rg = {total_voltage:.2f}V / {total_resistance:.2f}Ω = {total_current:.4f}A")
        self.solution_steps.append(f"Gesamtleistung (Pg) = Ug * Ig = {total_voltage:.2f}V * {total_current:.4f}A = {total_power:.2f}W")

        # Pass 2: Distribute voltage/current back down the tree
        self.solution_steps.append("\nSchritt 3: Berechnung der Einzelwerte (Spannungen, Ströme, Leistungen)")
        self._distribute_values(root_node, total_voltage, total_current)

        # Get the final list of individual resistor results
        individual_results_components = self._get_flat_resistor_list(root_node)
        individual_results_components.sort(key=lambda c: int(c.name.replace("R", "")))
        
        individual_results_dicts = [comp.to_dict() for comp in individual_results_components]

        for res in individual_results_dicts:
            step = f"   Für Widerstand {res['resistor']} ({res['resistance']:.2f} Ω):\n"
            step += f"   - Spannung (U): {res['voltage']:.2f} V\n"
            step += f"   - Strom (I): {res['current']:.4f} A\n"
            step += f"   - Leistung (P): {res['power']:.2f} W"
            self.solution_steps.append(step)

        return {
            "total_resistance": total_resistance,
            "total_current": total_current,
            "total_power": total_power,
            "individual_results": individual_results_dicts,
            "solution": "\n\n".join(self.solution_steps)
        }

# Wrapper function to be called by the API
def solve_mixed_circuit(circuit_structure: Dict[str, Any], total_voltage: float) -> Dict[str, Any]:
    solver = MixedCircuitSolver()
    return solver.solve(circuit_structure, total_voltage)


# --- The simple series and parallel functions remain unchanged ---

def solve_series_circuit(resistors: List[float], total_voltage: float) -> Dict[str, Any]:
    solution_steps = []
    total_resistance = sum(resistors)
    step = f"1. Gesamtwiderstand (Rg) berechnen (Reihenschaltung):\n"
    step += f"   Rg = {' + '.join([f'R{i+1}' for i in range(len(resistors))])}\n"
    step += f"   Rg = {' + '.join([str(r) for r in resistors])} Ω\n"
    step += f"   Rg = {total_resistance:.2f} Ω"
    solution_steps.append(step)
    total_current = total_voltage / total_resistance if total_resistance != 0 else 0
    step = f"2. Gesamtstrom (Ig) berechnen (Ohmsches Gesetz):\n"
    step += f"   Ig = Ug / Rg\n"
    step += f"   Ig = {total_voltage:.2f} V / {total_resistance:.2f} Ω\n"
    step += f"   Ig = {total_current:.4f} A"
    solution_steps.append(step)
    total_power = total_voltage * total_current
    step = f"3. Gesamtleistung (Pg) berechnen:\n"
    step += f"   Pg = Ug * Ig\n"
    step += f"   Pg = {total_voltage:.2f} V * {total_current:.4f} A\n"
    step += f"   Pg = {total_power:.2f} W"
    solution_steps.append(step)
    individual_results = []
    individual_steps = ["4. Teilspannungen, Teilströme und Teilleistungen berechnen:"]
    for i, r in enumerate(resistors):
        current = total_current
        voltage = current * r
        power = voltage * current
        res_name = f"R{i+1}"
        individual_results.append({"resistor": res_name, "resistance": r, "voltage": voltage, "current": current, "power": power})
        step = f"   Für Widerstand {res_name} ({r} Ω):\n"
        step += f"   - Strom (I{i+1}): In einer Reihenschaltung ist der Strom überall gleich.\n"
        step += f"     I{i+1} = Ig = {current:.4f} A\n"
        step += f"   - Spannung (U{i+1}): U = I * R\n"
        step += f"     U{i+1} = {current:.4f} A * {r} Ω = {voltage:.2f} V\n"
        step += f"   - Leistung (P{i+1}): P = U * I\n"
        step += f"     P{i+1} = {voltage:.2f} V * {current:.4f} A = {power:.2f} W"
        individual_steps.append(step)
    solution_steps.extend(individual_steps)
    return {"total_resistance": total_resistance, "total_current": total_current, "total_power": total_power, "individual_results": individual_results, "solution": "\n\n".join(solution_steps)}

def solve_parallel_circuit(resistors: List[float], total_voltage: float) -> Dict[str, Any]:
    solution_steps = []
    sum_of_inverses = sum(1/r for r in resistors if r != 0)
    total_resistance = 1 / sum_of_inverses if sum_of_inverses != 0 else 0
    step = f"1. Gesamtwiderstand (Rg) berechnen (Parallelschaltung):\n"
    step += f"   1/Rg = {' + '.join([f'1/R{i+1}' for i in range(len(resistors))])}\n"
    step += f"   1/Rg = {' + '.join([f'1/{r}' for r in resistors])}\n"
    step += f"   1/Rg = {sum_of_inverses:.4f} S (Siemens)\n"
    step += f"   Rg = 1 / {sum_of_inverses:.4f} S = {total_resistance:.2f} Ω"
    solution_steps.append(step)
    total_current = total_voltage / total_resistance if total_resistance != 0 else 0
    step = f"2. Gesamtstrom (Ig) berechnen (Ohmsches Gesetz):\n"
    step += f"   Ig = Ug / Rg\n"
    step += f"   Ig = {total_voltage:.2f} V / {total_resistance:.2f} Ω\n"
    step += f"   Ig = {total_current:.4f} A"
    solution_steps.append(step)
    total_power = total_voltage * total_current
    step = f"3. Gesamtleistung (Pg) berechnen:\n"
    step += f"   Pg = Ug * Ig\n"
    step += f"   Pg = {total_voltage:.2f} V * {total_current:.4f} A\n"
    step += f"   Pg = {total_power:.2f} W"
    solution_steps.append(step)
    individual_results = []
    individual_steps = ["4. Teilspannungen, Teilströme und Teilleistungen berechnen:"]
    for i, r in enumerate(resistors):
        voltage = total_voltage
        current = voltage / r if r != 0 else 0
        power = voltage * current
        res_name = f"R{i+1}"
        individual_results.append({"resistor": res_name, "resistance": r, "voltage": voltage, "current": current, "power": power})
        step = f"   Für Widerstand {res_name} ({r} Ω):\n"
        step += f"   - Spannung (U{i+1}): In einer Parallelschaltung ist die Spannung an allen Bauteilen gleich.\n"
        step += f"     U{i+1} = Ug = {voltage:.2f} V\n"
        step += f"   - Strom (I{i+1}): I = U / R\n"
        step += f"     I{i+1} = {voltage:.2f} V / {r} Ω = {current:.4f} A\n"
        step += f"   - Leistung (P{i+1}): P = U * I\n"
        step += f"     P{i+1} = {voltage:.2f} V * {current:.4f} A = {power:.2f} W"
        individual_steps.append(step)
    solution_steps.extend(individual_steps)
    return {"total_resistance": total_resistance, "total_current": total_current, "total_power": total_power, "individual_results": individual_results, "solution": "\n\n".join(solution_steps)}