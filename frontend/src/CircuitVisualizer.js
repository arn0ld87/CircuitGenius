import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, { addEdge, applyEdgeChanges, applyNodeChanges, MiniMap, Controls, Background, useReactFlow, ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';

let id = 1;
const getId = () => `R${id++}`;

// Custom Resistor Node Component
const ResistorNode = ({ data }) => {
    return (
        <div style={{ 
            border: '2px solid #333', 
            borderRadius: '5px', 
            padding: '5px 15px', 
            background: '#fff', 
            textAlign: 'center' 
        }}>
            <div style={{ fontSize: '12px' }}>{data.label}</div>
            <div style={{ 
                fontFamily: 'monospace',
                fontSize: '16px',
                fontWeight: 'bold'
            }}>
                {data.value}Ω
            </div>
            <input 
                type="range" 
                min="1" 
                max="1000" 
                defaultValue={data.value}
                onChange={data.onChange}
                className="nodrag"
                style={{ width: '100px', marginTop: '5px' }}
            />
        </div>
    );
};

const nodeTypes = { resistor: ResistorNode };

const initialNodes = [
  { id: 'start', type: 'input', data: { label: 'Spannungsquelle' }, position: { x: 50, y: 200 }, deletable: false, draggable: false },
  { id: 'end', type: 'output', data: { label: 'Masse' }, position: { x: 650, y: 200 }, deletable: false, draggable: false },
];

const CircuitVisualizer = ({ setCircuitDefinition, highlightedNode }) => {
    const reactFlowWrapper = useRef(null);
    const { project } = useReactFlow();
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState([]);

    const onNodesChange = useCallback(
        (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
        [setNodes]
    );
    const onEdgesChange = useCallback(
        (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        [setEdges]
    );
    const onConnect = useCallback(
        (connection) => setEdges((eds) => addEdge({ ...connection, type: 'step', markerEnd: { type: 'arrowclosed' } }, eds)),
        [setEdges]
    );

    const handleResistorValueChange = (id, value) => {
        setNodes((nds) =>
            nds.map((node) => {
                if (node.id === id) {
                    node.data = { ...node.data, value: parseFloat(value) };
                }
                return node;
            })
        );
    };

    const onAddResistor = useCallback(() => {
        const newId = getId();
        const newNode = {
            id: newId,
            type: 'resistor',
            position: project({ x: 250, y: 150 }),
            data: { 
                label: newId,
                value: 100, 
                onChange: (e) => handleResistorValueChange(newId, e.target.value) 
            },
        };
        setNodes((nds) => nds.concat(newNode));
    }, [project, setNodes]);

    const onClear = () => {
        setNodes(initialNodes);
        setEdges([]);
        id = 1; // Reset resistor count
    };

    // This effect will run every time the highlightedNode changes
    useEffect(() => {
        setNodes((nds) =>
            nds.map((node) => {
                if (node.type === 'resistor') {
                    // check if node is highlighted
                    const isHighlighted = node.id === highlightedNode;
                    node.style = { 
                        ...node.style, 
                        border: isHighlighted ? '3px solid #ff0072' : '2px solid #333',
                        boxShadow: isHighlighted ? '0 0 15px #ff0072' : 'none'
                    };
                }
                return node;
            })
        );
    }, [highlightedNode, setNodes]);

    // Effect to build circuit definition whenever nodes or edges change
    useEffect(() => {
        const buildCircuitDefinition = () => {
            if (nodes.length <= 2 && edges.length === 0) {
                setCircuitDefinition('[]');
                return;
            }

            const adj = new Map(); // Adjacency list: nodeId -> [targetNodeId, ...]
            const reverseAdj = new Map(); // Reverse adjacency list: nodeId -> [sourceNodeId, ...]
            const resistorValues = new Map(); // Resistor values: resistorId -> value

            nodes.forEach(node => {
                adj.set(node.id, []);
                reverseAdj.set(node.id, []);
                if (node.type === 'resistor') {
                    resistorValues.set(node.id, node.data.value);
                }
            });

            edges.forEach(edge => {
                adj.get(edge.source).push(edge.target);
                reverseAdj.get(edge.target).push(edge.source);
            });

            // Recursive DFS to parse the circuit structure
            function parseGraph(currentNodeId, visited = new Set()) {
                if (visited.has(currentNodeId)) {
                    return null; // Avoid cycles
                }
                visited.add(currentNodeId);

                const outgoing = adj.get(currentNodeId) || [];
                const incoming = reverseAdj.get(currentNodeId) || [];

                // If it's a resistor node, add its value
                if (resistorValues.has(currentNodeId)) {
                    return resistorValues.get(currentNodeId);
                }

                // If it's the end node, we're done with this path
                if (currentNodeId === 'end') {
                    return null; // Signifies end of a branch/circuit
                }

                // Determine if it's a series or parallel connection
                if (outgoing.length === 1 && incoming.length <= 1) {
                    // Series connection (or start of a new segment)
                    const nextNodeId = outgoing[0];
                    const nextComponent = parseGraph(nextNodeId, visited);
                    if (nextComponent !== null) {
                        return nextComponent;
                    }
                } else if (outgoing.length > 1) {
                    // Parallel connection
                    const branches = [];
                    const branchVisited = new Set(visited); // Fork visited set for parallel branches

                    for (const nextNodeId of outgoing) {
                        const branchResult = parseGraph(nextNodeId, branchVisited);
                        if (branchResult !== null) {
                            branches.push(branchResult);
                        }
                    }
                    if (branches.length > 0) {
                        return branches.length === 1 ? branches[0] : branches; // If only one branch, it's not truly parallel
                    }
                }
                
                return null; // Should not happen for a well-formed circuit
            }

            // Start parsing from the 'start' node
            const result = parseGraph('start');
            
            // The result from parseGraph('start') will be the main circuit structure.
            // We need to handle the case where the top-level is a single resistor or a single parallel block.
            let finalDefinition = [];
            if (result !== null) {
                if (Array.isArray(result) && result.every(item => Array.isArray(item))) {
                    // If it's an array of arrays, it's a parallel block at the top level
                    finalDefinition = result;
                } else if (Array.isArray(result)) {
                    // If it's a flat array, it's a series at the top level
                    finalDefinition = result;
                } else {
                    // If it's a single value, it's a single resistor
                    finalDefinition = [result];
                }
            }

            setCircuitDefinition(JSON.stringify(finalDefinition, null, 2));
        };

        buildCircuitDefinition();
    }, [nodes, edges, setCircuitDefinition]);

    return (
        <div style={{ height: '500px', border: '1px solid #ccc', borderRadius: '8px' }} ref={reactFlowWrapper}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
            >
                <Controls />
                <MiniMap />
                <Background variant="dots" gap={12} size={1} />
                <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 4 }}>
                    <button onClick={onAddResistor} className="btn btn-primary btn-sm">+ Widerstand</button>
                    <button onClick={onClear} className="btn btn-danger btn-sm ms-2">Löschen</button>
                </div>
            </ReactFlow>
        </div>
    );
};

const CircuitVisualizerWrapper = (props) => {
    return (
        <ReactFlowProvider>
            <CircuitVisualizer {...props} />
        </ReactFlowProvider>
    );
}

export default CircuitVisualizerWrapper;