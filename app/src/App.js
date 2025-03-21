import React, { useState, useEffect } from "react";
import GraphVisualizer from "./GraphVisualizer";
import TiktokPanel from "./TiktokPanel";
import { Typography, Box, fabClasses } from "@mui/material";


function App() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [showVideo, setShowVideo] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [nodeDegrees, setNodeDegrees] = useState({});

  const [showAuthModal, setShowAuthModal] = useState(true);

  const handleAuthModalClose = () => {
    setShowAuthModal(false);
  };

  useEffect(() => {
    // In a real app, you'd fetch this from an API
    // For now, we'll simulate with the data structure you provided

    const graphData = require('./graph_data.json');
    const degrees = {};
    graphData.links.forEach(({ source, target }) => {
      const sourceId = typeof source === 'object' ? source.id : source;
      const targetId = typeof target === 'object' ? target.id : target;
      degrees[sourceId] = (degrees[sourceId] || 0) + 1;
      degrees[targetId] = (degrees[targetId] || 0) + 1;
    });
    setNodeDegrees(degrees);
    setGraphData(graphData);
  }, []);

  const closePanel = () => {
    setShowVideo(false);
    setHighlightLinks(new Set());
    setHighlightNodes(new Set());
  };



  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };


  if (!graphData) {
    return <div>Loading...</div>;
  }


  return (
    <div style={{ height: "100vh", background: "#000000" }}>
      {/* <WelcomeModal
        open={showAuthModal}
        onClose={handleAuthModalClose}
      /> */}
      <Box sx={{ position: 'fixed', top: 10, left: 10, zIndex: 1000 }}>
        <Typography sx={{ fontSize: 12, fontWeight: 'bold', color: '#ffffff', }}>Doom or Boom</Typography>
        <Typography sx={{ fontSize: 10, fontWeight: 'medium', color: '#ffffff', }}>created by talbert and max</Typography>
        <Typography sx={{ fontSize: 10, fontWeight: 'medium', color: '#ffffff', }}>Graph Data: {graphData.nodes.length} nodes, {graphData.links.length} links</Typography>
        <Typography sx={{ fontSize: 10, fontWeight: 'medium', color: '#ffffff', }}>Selected Node: {selectedNode ? selectedNode.id : 'None'}</Typography>
      </Box>
      <TiktokPanel open={showVideo} selectedNode={selectedNode} isExpanded={isExpanded} toggleExpand={toggleExpand} closePanel={closePanel} highlightNodes={highlightNodes} />
      <GraphVisualizer graphData={graphData} nodeDegrees={nodeDegrees} selectedNode={selectedNode} setSelectedNode={setSelectedNode} setShowVideo={setShowVideo} highlightLinks={highlightLinks} setHighlightLinks={setHighlightLinks} highlightNodes={highlightNodes} setHighlightNodes={setHighlightNodes} />
    
    </div>
  );
}

export default App;