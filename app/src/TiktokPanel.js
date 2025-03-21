import React from 'react';
import { 
  Box, 
  Modal,
  Paper, 
  Typography, 
  IconButton, 
  Stack,
  Fade
} from '@mui/material';
import { Close, Fullscreen, FullscreenExit, Videocam } from '@mui/icons-material';

export default function TiktokPanel({
  selectedNode,
  isExpanded,
  toggleExpand,
  closePanel,
  open
}) {

  if (!open) return null;

  return (
    <Modal
      open={open}
      onClose={closePanel}
      closeAfterTransition
      hideBackdrop={true}
      disableAutoFocus={true}
      disableEnforceFocus={true}
      disablePortal={false}
      disableScrollLock={true}
      sx={{ pointerEvents: 'none' }}
    >
      <Fade in={open}>
        <Paper
          elevation={0}
          sx={{
            position: 'absolute',
            top: '50%',
            right: 40,
            transform: 'translateY(-50%)',
            width: isExpanded ? '400px' : '330px',
            height: '650px',
            bgcolor: 'transparent',
            transition: 'width 0.3s ease-in-out',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 10,
            borderRadius: 0,
            outline: 'none',
            pointerEvents: 'auto',
            overflow: 'hidden'
          }}
        >
          {/* Minimal header with controls only */}
          <Box
            sx={{
              p: 1,
              display: 'flex',
              justifyContent: 'flex-end',
              position: 'absolute',
              top: 0,
              right: 0,
              zIndex: 20,
              width: '100%',
            }}
          >
            <Stack direction="row" spacing={1}>
              {/* <IconButton
                size="small"
                onClick={toggleExpand}
                sx={{ 
                  color: 'white', 
                  bgcolor: 'rgba(0,0,0,0.3)',
                  '&:hover': { 
                    bgcolor: 'rgba(0,0,0,0.5)', 
                    color: 'white' 
                  } 
                }}
              >
                {isExpanded ? <FullscreenExit fontSize="small" /> : <Fullscreen fontSize="small" />}
              </IconButton> */}
              <IconButton
                size="small"
                onClick={closePanel}
                sx={{ 
                  color: 'white', 
                  bgcolor: 'rgba(0,0,0,0.3)',
                  '&:hover': { 
                    bgcolor: 'rgba(0,0,0,0.5)', 
                    color: 'white' 
                  } 
                }}
              >
                <Close fontSize="small" />
              </IconButton>
            </Stack>
          </Box>

          {/* TikTok video embed with perfect fit */}
          <Box
            sx={{
              width: '100%',
              height: '100%',
              overflow: 'hidden',
              borderRadius: 2,
              position: 'relative',
            }}
          >
            {selectedNode.metadata?.url ? (
              <Box
                component="iframe"
                src={selectedNode.metadata.url.replace('tiktokv.com/share/video', 'tiktok.com/embed')}
                sx={{
                  width: '100%',
                  height: '100%',
                  border: 0,
                  bgcolor: 'transparent',
                  
                }}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : (
              <Box
                sx={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'rgba(0,0,0,0.2)',
                  borderRadius: 2
                }}
              >
                <Videocam sx={{ fontSize: 40, color: 'white' }} />
                <Typography sx={{ color: 'white', ml: 1, fontWeight: 'medium' }}>
                  No video available
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      </Fade>
    </Modal>
  );
}