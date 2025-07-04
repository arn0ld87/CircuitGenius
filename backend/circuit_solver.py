from typing import List, Dict, Any

def solve_series_circuit(resistors: List[float], total_voltage: float) -> Dict[str, Any]:
    """
    Solves a series circuit.

    Args:
        resistors: A list of resistor values.
        total_voltage: The total voltage applied to the circuit.

    Returns:
        A dictionary containing the results and a detailed solution path.
    """
    solution_steps = []
    
    # Calculate total resistance
    total_resistance = sum(resistors)
    step = f"1. Gesamtwiderstand (Rg) berechnen (Reihenschaltung):\n"
    step += f"   Rg = {' + '.join([f'R{i+1}' for i in range(len(resistors))])}\n"
    step += f"   Rg = {' + '.join([str(r) for r in resistors])} Ω\n"
    step += f"   Rg = {total_resistance:.2f} Ω"
    solution_steps.append(step)

    # Calculate total current
    total_current = total_voltage / total_resistance if total_resistance != 0 else 0
    step = f"2. Gesamtstrom (Ig) berechnen (Ohmsches Gesetz):\n"
    step += f"   Ig = Ug / Rg\n"
    step += f"   Ig = {total_voltage:.2f} V / {total_resistance:.2f} Ω\n"
    step += f"   Ig = {total_current:.4f} A"
    solution_steps.append(step)

    # Calculate total power
    total_power = total_voltage * total_current
    step = f"3. Gesamtleistung (Pg) berechnen:\n"
    step += f"   Pg = Ug * Ig\n"
    step += f"   Pg = {total_voltage:.2f} V * {total_current:.4f} A\n"
    step += f"   Pg = {total_power:.2f} W"
    solution_steps.append(step)

    # Calculate individual values
    individual_results = []
    individual_steps = ["4. Teilspannungen, Teilströme und Teilleistungen berechnen:"]
    for i, r in enumerate(resistors):
        current = total_current  # In series, current is the same
        voltage = current * r
        power = voltage * current
        
        res_name = f"R{i+1}"
        individual_results.append({
            "resistor": res_name,
            "resistance": r,
            "voltage": voltage,
            "current": current,
            "power": power
        })
        
        step = f"   Für Widerstand {res_name} ({r} Ω):\n"
        step += f"   - Strom (I{i+1}): In einer Reihenschaltung ist der Strom überall gleich.\n"
        step += f"     I{i+1} = Ig = {current:.4f} A\n"
        step += f"   - Spannung (U{i+1}): U = I * R\n"
        step += f"     U{i+1} = {current:.4f} A * {r} Ω = {voltage:.2f} V\n"
        step += f"   - Leistung (P{i+1}): P = U * I\n"
        step += f"     P{i+1} = {voltage:.2f} V * {current:.4f} A = {power:.2f} W"
        individual_steps.append(step)
        
    solution_steps.extend(individual_steps)

    return {
        "total_resistance": total_resistance,
        "total_current": total_current,
        "total_power": total_power,
        "individual_results": individual_results,
        "solution": "\n\n".join(solution_steps)
    }

def solve_parallel_circuit(resistors: List[float], total_voltage: float) -> Dict[str, Any]:
    """
    Solves a parallel circuit.

    Args:
        resistors: A list of resistor values.
        total_voltage: The total voltage applied to the circuit.

    Returns:
        A dictionary containing the results and a detailed solution path.
    """
    solution_steps = []

    # Calculate total resistance
    sum_of_inverses = sum(1/r for r in resistors if r != 0)
    total_resistance = 1 / sum_of_inverses if sum_of_inverses != 0 else 0
    
    step = f"1. Gesamtwiderstand (Rg) berechnen (Parallelschaltung):\n"
    step += f"   1/Rg = {' + '.join([f'1/R{i+1}' for i in range(len(resistors))])}\n"
    step += f"   1/Rg = {' + '.join([f'1/{r}' for r in resistors])}\n"
    step += f"   1/Rg = {sum_of_inverses:.4f} S (Siemens)\n"
    step += f"   Rg = 1 / {sum_of_inverses:.4f} S = {total_resistance:.2f} Ω"
    solution_steps.append(step)

    # Calculate total current
    total_current = total_voltage / total_resistance if total_resistance != 0 else 0
    step = f"2. Gesamtstrom (Ig) berechnen (Ohmsches Gesetz):\n"
    step += f"   Ig = Ug / Rg\n"
    step += f"   Ig = {total_voltage:.2f} V / {total_resistance:.2f} Ω\n"
    step += f"   Ig = {total_current:.4f} A"
    solution_steps.append(step)

    # Calculate total power
    total_power = total_voltage * total_current
    step = f"3. Gesamtleistung (Pg) berechnen:\n"
    step += f"   Pg = Ug * Ig\n"
    step += f"   Pg = {total_voltage:.2f} V * {total_current:.4f} A\n"
    step += f"   Pg = {total_power:.2f} W"
    solution_steps.append(step)

    # Calculate individual values
    individual_results = []
    individual_steps = ["4. Teilspannungen, Teilströme und Teilleistungen berechnen:"]
    for i, r in enumerate(resistors):
        voltage = total_voltage  # In parallel, voltage is the same
        current = voltage / r if r != 0 else 0
        power = voltage * current
        
        res_name = f"R{i+1}"
        individual_results.append({
            "resistor": res_name,
            "resistance": r,
            "voltage": voltage,
            "current": current,
            "power": power
        })

        step = f"   Für Widerstand {res_name} ({r} Ω):\n"
        step += f"   - Spannung (U{i+1}): In einer Parallelschaltung ist die Spannung an allen Bauteilen gleich.\n"
        step += f"     U{i+1} = Ug = {voltage:.2f} V\n"
        step += f"   - Strom (I{i+1}): I = U / R\n"
        step += f"     I{i+1} = {voltage:.2f} V / {r} Ω = {current:.4f} A\n"
        step += f"   - Leistung (P{i+1}): P = U * I\n"
        step += f"     P{i+1} = {voltage:.2f} V * {current:.4f} A = {power:.2f} W"
        individual_steps.append(step)

    solution_steps.extend(individual_steps)

    return {
        "total_resistance": total_resistance,
        "total_current": total_current,
        "total_power": total_power,
        "individual_results": individual_results,
        "solution": "\n\n".join(solution_steps)
    }

def solve_mixed_circuit(circuit: List[Any], total_voltage: float) -> Dict[str, Any]:
    next_resistor_id = 1

    def get_resistor_name():
        nonlocal next_resistor_id
        name = f"R{next_resistor_id}"
        next_resistor_id += 1
        return name

    def process_and_name_resistors(sub_circuit):
        processed = []
        for item in sub_circuit:
            if isinstance(item, (int, float)):
                processed.append({"name": get_resistor_name(), "value": float(item), "type": "resistor"})
            elif isinstance(item, dict) and 'type' in item:
                processed.append(item) # Already processed component
            else:
                # It's a nested list (sub-circuit)
                processed.append(process_and_name_resistors(item))
        return processed

    def calculate_equivalent_resistance(sub_circuit, steps_log):
        # Check if it's a series or parallel sub-circuit
        # A flat list of components is series
        is_series = all(isinstance(item, dict) for item in sub_circuit)

        if is_series:
            # --- SERIES CALCULATION ---
            total_r = sum(item['value'] for item in sub_circuit)
            
            # Logging
            names = [item['name'] for item in sub_circuit]
            values = [f"{item['value']:.2f}Ω" for item in sub_circuit]
            step_detail = f"Berechne Ersatzwiderstand für Reihenschaltung: [{ ', '.join(names) }].\n"
            step_detail += f"   R_eq = { ' + '.join(values) } = {total_r:.2f}Ω"
            steps_log.append(step_detail)
            
            return {"name": f"Eq({ ', '.join(names) })", "value": total_r, "type": "equivalent", "contains": sub_circuit}
        else:
            # --- PARALLEL CALCULATION ---
            # First, solve any nested parts recursively
            processed_parts = []
            for item in sub_circuit:
                if isinstance(item, list):
                    processed_parts.append(calculate_equivalent_resistance(item, steps_log))
                else:
                    processed_parts.append(item) # It's a resistor dict
            
            # Now, calculate the parallel resistance of the processed parts
            sum_of_inverses = sum(1 / part['value'] for part in processed_parts if part['value'] != 0)
            total_r = 1 / sum_of_inverses if sum_of_inverses != 0 else 0

            # Logging
            names = [part['name'] for part in processed_parts]
            inverses = [f"1/{part['name']} ({1/part['value']:.4f}S)" for part in processed_parts if part['value'] != 0]
            step_detail = f"Berechne Ersatzwiderstand für Parallelschaltung: [ { ', '.join(names) } ].\n"
            step_detail += f"   1/R_eq = { ' + '.join(inverses) } = {sum_of_inverses:.4f}S\n"
            step_detail += f"   R_eq = 1 / {sum_of_inverses:.4f}S = {total_r:.2f}Ω"
            steps_log.append(step_detail)

            return {"name": f"Eq({ ' || '.join(names) })", "value": total_r, "type": "equivalent", "contains": processed_parts}

    def calculate_individual_values(component, voltage, current):
        results = []
        component_type = component.get('type')

        if component_type == 'resistor':
            power = voltage * current
            results.append({
                "resistor": component['name'],
                "resistance": component['value'],
                "voltage": voltage,
                "current": current,
                "power": power
            })

        elif component_type == 'equivalent':
            # This is a simplified block, we need to break it down
            contained_parts = component.get('contains', [])
            
            # Check if the original connection was series or parallel
            # Heuristic: The name contains '||' for parallel
            is_parallel_group = '||' in component['name']

            if not is_parallel_group:
                # --- SERIES GROUP ---
                # Current is the same for all parts in series
                for part in contained_parts:
                    part_voltage = current * part['value']
                    results.extend(calculate_individual_values(part, part_voltage, current))
            else:
                # --- PARALLEL GROUP ---
                # Voltage is the same for all parts in parallel
                for part in contained_parts:
                    part_current = voltage / part['value'] if part['value'] != 0 else 0
                    results.extend(calculate_individual_values(part, voltage, part_current))
        return results

    # --- Main execution starts here ---
    solution_steps = ["Schritt 1: Vereinfachung der Schaltung zur Ermittlung des Gesamtwiderstands (Rg)"]
    
    # Give each raw resistor a unique name and structure
    named_circuit = process_and_name_resistors(circuit)

    # Recursively calculate the total equivalent resistance
    equivalent_circuit = calculate_equivalent_resistance(named_circuit, solution_steps)
    total_resistance = equivalent_circuit['value']
    solution_steps.append(f"\nDer Gesamtwiderstand der Schaltung beträgt: Rg = {total_resistance:.2f}Ω")

    # --- Calculate total values ---
    solution_steps.append("\nSchritt 2: Berechnung der Gesamtwerte der Schaltung")
    total_current = total_voltage / total_resistance if total_resistance != 0 else 0
    total_power = total_voltage * total_current
    solution_steps.append(f"Gesamtstrom (Ig) = Ug / Rg = {total_voltage:.2f}V / {total_resistance:.2f}Ω = {total_current:.4f}A")
    solution_steps.append(f"Gesamtleistung (Pg) = Ug * Ig = {total_voltage:.2f}V * {total_current:.4f}A = {total_power:.2f}W")

    # --- Calculate individual values by working backwards ---
    solution_steps.append("\nSchritt 3: Rückwärtsrechnung zur Ermittlung der Einzelwerte")
    individual_results = calculate_individual_values(equivalent_circuit, total_voltage, total_current)
    
    # Sort results by resistor name for consistency
    individual_results.sort(key=lambda x: x['resistor'])

    # Format the final solution steps for individual components
    for res in individual_results:
        solution_steps.append(
            f"Analyse für {res['resistor']} ({res['resistance']:.2f}Ω): Spannung={res['voltage']:.2f}V, Strom={res['current']:.4f}A, Leistung={res['power']:.2f}W"
        )

    return {
        "total_resistance": total_resistance,
        "total_current": total_current,
        "total_power": total_power,
        "individual_results": individual_results,
        "solution": "\n".join(solution_steps)
    }