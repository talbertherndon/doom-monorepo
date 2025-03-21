import React, { useRef, useState, useEffect } from "react";
import { ForceGraph3D } from "react-force-graph";
import * as THREE from "three";

const GraphVisualizer = ({ graphData, nodeDegrees, setSelectedNode, selectedNode, setShowVideo, highlightLinks, setHighlightLinks, highlightNodes, setHighlightNodes }) => {
    const fgRef = useRef();
    const [autoRotate, setAutoRotate] = useState(true);
    const [isHovering, setIsHovering] = useState(false);

    const rotationRef = useRef(null);
    const hoverTimeoutRef = useRef(null);

    const getNodeColor = (node) => {
        if (highlightNodes.has(node.id)) {
            return "#ffffff"; // Highlight color
        }

        // Color based on degree (number of connections)
        const degree = nodeDegrees[node.id] || 0;

        // Color scale based on connection count
        if (degree >= 4) return "#ff4f4f";      // Red for highly connected
        if (degree === 3) return "#ffaf4f";     // Orange
        if (degree === 2) return "#4fff9f";     // Green
        if (degree === 1) return "#4fc3ff";     // Blue
        return "#af4fff";                       // Purple for isolated nodes
    };
    const getLinkColor = (link) => {
        return highlightLinks.has(link) ? "#ffffff" : "#666666";
    };

    const getNodeSize = (node) => {
        const degree = nodeDegrees[node.id] || 1;
        const baseSize = Math.min(5 + degree * 0.5, 15);

        return highlightNodes.has(node.id) ? baseSize * 1.5 : baseSize;
    };

    const handleNodeClick = (node) => {
        console.log("Node clicked:", node);

        if (node.id == selectedNode?.id) {
            setAutoRotate(false)
            setSelectedNode(null)
            setShowVideo(false)
            return
        } else {
            setAutoRotate(true)
        }

        setSelectedNode(node);
        setShowVideo(true);

        // Highlight connected nodes and links
        const connectedLinks = graphData.links.filter(
            link => link.source.id === node.id || link.target.id === node.id
        );

        const connectedNodes = new Set();
        connectedLinks.forEach(link => {
            connectedNodes.add(link.source.id);
            connectedNodes.add(link.target.id);
        });

        setHighlightLinks(new Set(connectedLinks));
        setHighlightNodes(connectedNodes);

        // Move camera to focus on the node
        const distance = 50;
        const offsetX = 50; // Adjust this value to shift more to the left

        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

        if (fgRef.current) {
            fgRef.current.cameraPosition(
                { x: (node.x * distRatio) + offsetX, y: node.y * distRatio, z: node.z * distRatio },
                node,
                5000
            );
        }
    };

    const handleNodeHover = (node) => {
        // Update cursor style
        document.body.style.cursor = node ? 'pointer' : 'default';
        
        // // Clear any existing timeout when hover state changes
        // if (hoverTimeoutRef.current) {
        //     clearTimeout(hoverTimeoutRef.current);
        //     hoverTimeoutRef.current = null;
        // }
        
        // if (node) {
        //     // Node is being hovered - stop rotation immediately
        //     setIsHovering(true);
        // } else {
        //     // Node hover ended - set timeout to restart rotation
        //     hoverTimeoutRef.current = setTimeout(() => {
        //         setIsHovering(false);
        //     }, 3000); // 3 second delay
        // }
    };


    // Create text sprite for node labels
    const createTextSprite = (text, color) => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        canvas.width = 256;
        canvas.height = 64;
        context.fillStyle = "rgba(0, 0, 0, 0)";
        context.fillRect(0, 0, canvas.width, canvas.height);

        context.font = "Bold 24px Inter, system-ui, sans-serif";
        context.fillStyle = color;
        context.textAlign = "center";
        context.fillText(text, canvas.width / 2, canvas.height / 2);

        return canvas;
    };




    return (
        <div className="w-full h-screen relative bg-black overflow-hidden">
            {/* Main Graph Visualization */}
            <div className="w-full h-full">
                <ForceGraph3D
                    ref={fgRef}
                    graphData={graphData}
                    backgroundColor="#000000"
                    linkColor={getLinkColor}
                    linkWidth={link => highlightLinks.has(link) ? 2 : 1}
                    linkOpacity={0.6}
                    linkDirectionalParticles={2}
                    linkDirectionalParticleWidth={link => highlightLinks.has(link) ? 3 : 1}
                    linkDirectionalParticleSpeed={() => 0.005}
                    nodeRelSize={6}
                    onNodeClick={handleNodeClick}
                    onNodeHover={handleNodeHover}
                    onEngineStop={() => {
                        console.log("Engine stopped");
                        // Set a timeout to consider the simulation idle after a short delay
                        setTimeout(() => {
                            // setIsSimulationActive(false);
                        }, 1000);
                    }}
                    cooldownTicks={100}
                    nodeThreeObject={(node) => {
                        const material = new THREE.MeshBasicMaterial({
                            color: getNodeColor(node),
                            transparent: true,
                            opacity: 0.9,
                        });

                        const sphere = new THREE.Mesh(
                            new THREE.SphereGeometry(getNodeSize(node)),
                            material
                        );

                        // Add text label
                        const spriteMaterial = new THREE.SpriteMaterial({
                            map: new THREE.CanvasTexture(
                                createTextSprite(node.id, getNodeColor(node))
                            ),
                            depthTest: false,
                        });

                        const sprite = new THREE.Sprite(spriteMaterial);
                        sprite.scale.set(20, 10, 1);
                        sprite.position.set(0, 10, 0);
                        sphere.add(sprite);

                        // Add subtle glow effect
                        if (highlightNodes.has(node.id)) {
                            const glowMaterial = new THREE.MeshBasicMaterial({
                                color: "#ffffff",
                                transparent: true,
                                opacity: 0.15,
                            });
                            const glow = new THREE.Mesh(
                                new THREE.SphereGeometry(getNodeSize(node) * 1.5),
                                glowMaterial
                            );
                            sphere.add(glow);
                        }

                        return sphere;
                    }}
                />
            </div>
        </div>
    );
};

export default GraphVisualizer;