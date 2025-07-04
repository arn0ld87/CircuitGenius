import React, { useState, useCallback } from 'react';
import { ReactFlowProvider } from 'reactflow';
import CircuitVisualizer from './CircuitVisualizer';
import './App.css';

function CircuitCalculator() {
    const [circuitType, setCircuitType] = useState('series');
    const [resistors, setResistors] = useState(['']);
    const [mixedCircuit, setMixedCircuit] = useState('[]');
    const [totalVoltage, setTotalVoltage] = useState('12');
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');
    const [highlightedNode, setHighlightedNode] = useState(null);

    const handleResistorChange = (index, value) => {
        const newResistors = [...resistors];
        newResistors[index] = value;
        setResistors(newResistors);
    };

    const addResistor = () => {
        setResistors([...resistors, '']);
    };

    const removeResistor = (index) => {
        const newResistors = resistors.filter((_, i) => i !== index);
        setResistors(newResistors);
    };

    const handleCalculate = async () => {
        setError('');
        setResults(null);

        let payload = {
            circuit_type: circuitType,
            total_voltage: parseFloat(totalVoltage)
        };

        if (circuitType === 'mixed') {
            try {
                payload.resistors = JSON.parse(mixedCircuit);
            } catch (e) {
                setError('Ungültiges JSON-Format. Bitte korrigieren Sie die Schaltungsdefinition.');
                return;
            }
        } else {
            const numericResistors = resistors.map(r => parseFloat(r)).filter(r => !isNaN(r) && r > 0);
            if (numericResistors.length === 0) {
                setError('Bitte geben Sie mindestens einen gültigen Widerstandswert ein.');
                return;
            }
            payload.resistors = numericResistors;
        }

        if (isNaN(payload.total_voltage) || payload.total_voltage <= 0) {
            setError('Bitte geben Sie eine gültige, positive Gesamtspannung ein.');
            return;
        }

        try {
            const response = await fetch('https://circuitgenius.onrender.com', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) throw new Error('Netzwerkfehler oder Serverproblem.');

            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                setResults(data);
            }
        } catch (err) {
            setError(err.message);
        }
    };
    
    const handleReset = () => {
        setCircuitType('series');
        setResistors(['']);
        setMixedCircuit('[]');
        setTotalVoltage('12');
        setResults(null);
        setError('');
        setHighlightedNode(null);
    };

    return (
        <div className="container-fluid my-4">
            <div className="row g-4">
                {/* --- LEFT COLUMN: INPUTS --- */}
                <div className="col-lg-6">
                    <div className="card shadow-sm">
                        <div className="card-body">
                            <h1 className="card-title text-center mb-2">CircuitGenius</h1>
                <p className="text-center text-muted mb-4">Entwickelt von Alexander Schneider (Fi-S 25/2)</p>
                            
                            {/* Voltage Input */}
                            <div className="mb-3">
                                <label htmlFor="totalVoltage" className="form-label"><strong>Gesamtspannung (Ug) in Volt:</strong></label>
                                <input
                                    type="number"
                                    className="form-control"
                                    id="totalVoltage"
                                    value={totalVoltage}
                                    onChange={(e) => setTotalVoltage(e.target.value)}
                                    placeholder="z.B. 12"
                                />
                            </div>

                            {/* Circuit Type Selection */}
                            <div className="mb-4">
                                <label className="form-label"><strong>Schaltungstyp:</strong></label>
                                <div>
                                    <button className={`btn ${circuitType === 'series' ? 'btn-primary' : 'btn-outline-primary'} me-2`} onClick={() => setCircuitType('series')}>Reihe</button>
                                    <button className={`btn ${circuitType === 'parallel' ? 'btn-primary' : 'btn-outline-primary'} me-2`} onClick={() => setCircuitType('parallel')}>Parallel</button>
                                    <button className={`btn ${circuitType === 'mixed' ? 'btn-primary' : 'btn-outline-primary'}`} onClick={() => setCircuitType('mixed')}>Gemischt</button>
                                </div>
                            </div>

                            {/* Input Area */}
                            {circuitType === 'mixed' ? (
                                <div className="p-3 border rounded">
                                    <label htmlFor="mixedCircuitInput" className="form-label"><strong>Gemischte Schaltung (JSON-Format):</strong></label>
                                    <textarea 
                                        id="mixedCircuitInput"
                                        className="form-control font-monospace"
                                        rows="5"
                                        value={mixedCircuit}
                                        onChange={(e) => setMixedCircuit(e.target.value)}
                                        placeholder='z.B. [[100, [100, 100]], 50]'
                                    ></textarea>
                                    <div className="form-text">
                                        Stellen Sie Reihenschaltungen als flache Liste <code>[R1, R2, ...]</code> und Parallelschaltungen als verschachtelte Liste <code>[[R1, R2], ...]</code> dar.
                                        <br/>Beispiel: <code>[100, [200, 300], 400]</code> bedeutet 100Ω in Reihe mit einer Parallelschaltung von 200Ω und 300Ω, gefolgt von 400Ω in Reihe.
                                        <br/>Beispiel für eine reine Parallelschaltung: <code>[[100, 200, 300]]</code>
                                    </div>
                                </div>
                            ) : (
                                <div className="p-3 border rounded">
                                    <label className="form-label"><strong>Widerstände (R) in Ohm:</strong></label>
                                    {resistors.map((resistor, index) => (
                                        <div key={index} className="input-group mb-2">
                                            <span className="input-group-text">R{index + 1}</span>
                                            <input
                                                type="number"
                                                className="form-control"
                                                value={resistor}
                                                onChange={(e) => handleResistorChange(index, e.target.value)}
                                                placeholder={`Wert für R${index + 1}`}
                                            />
                                            <button className="btn btn-outline-danger" type="button" onClick={() => removeResistor(index)}>X</button>
                                        </div>
                                    ))}
                                    <button className="btn btn-outline-success mt-2 btn-sm" onClick={addResistor}>+ Hinzufügen</button>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="mt-4 d-grid gap-2">
                                <button className="btn btn-success btn-lg" onClick={handleCalculate}>Berechnen</button>
                                <button className="btn btn-secondary" onClick={handleReset}>Alles zurücksetzen</button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- RIGHT COLUMN: RESULTS --- */}
                <div className="col-lg-6">
                    <div className="card shadow-sm">
                        <div className="card-body">
                            <h3 className="card-title mb-4">2. Ergebnisse</h3>
                            {error && <div className="alert alert-danger">{error}</div>}
                            {!results && !error && <div className="alert alert-info">Bitte definieren Sie eine Schaltung und klicken Sie auf 'Berechnen'.</div>}
                            {results && (
                                <>
                                    <div className="card bg-light p-3 mb-4">
                                        <h4>Gesamtwerte</h4>
                                        <p className="mb-1"><strong>Gesamtwiderstand (Rg):</strong> {results.total_resistance.toFixed(2)} Ω</p>
                                        <p className="mb-1"><strong>Gesamtstrom (Ig):</strong> {results.total_current.toFixed(4)} A</p>
                                        <p className="mb-0"><strong>Gesamtleistung (Pg):</strong> {results.total_power.toFixed(2)} W</p>
                                    </div>

                                    <h4>Einzelwerte der Widerstände</h4>
                                    <div className="table-responsive">
                                        <table className="table table-striped table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Bauteil</th>
                                                    <th>Widerstand (Ω)</th>
                                                    <th>Spannung (V)</th>
                                                    <th>Strom (A)</th>
                                                    <th>Leistung (W)</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {results.individual_results.map((res, index) => (
                                                    <tr 
                                                        key={index} 
                                                        onMouseEnter={() => setHighlightedNode(res.resistor)}
                                                        onMouseLeave={() => setHighlightedNode(null)}
                                                    >
                                                        <td><strong>{res.resistor}</strong></td>
                                                        <td>{res.resistance.toFixed(2)}</td>
                                                        <td>{res.voltage.toFixed(2)}</td>
                                                        <td>{res.current.toFixed(4)}</td>
                                                        <td>{res.power.toFixed(2)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    
                                    <div className="mt-4">
                                        <h4>Detaillierter Lösungsweg</h4>
                                        <pre className="bg-dark text-white p-3 rounded"><code>{results.solution}</code></pre>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CircuitCalculator;
