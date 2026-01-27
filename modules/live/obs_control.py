"""
OBS Control - Optional OBS WebSocket control
"""

import logging
from typing import Optional
try:
    from obswebsocket import obsws, requests
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False


class OBSControl:
    """Controls OBS via WebSocket for automated streaming/recording"""
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        """
        Initialize OBS WebSocket connection
        
        Args:
            host: OBS WebSocket host
            port: OBS WebSocket port (default 4455 for obs-websocket 5.x)
            password: WebSocket password
        """
        if not OBS_AVAILABLE:
            raise ImportError("obs-websocket-py not installed. Install with: pip install obs-websocket-py")
        
        self.host = host
        self.port = port
        self.password = password
        self.ws: Optional[obsws] = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("OBSControl")
        logger.setLevel(logging.INFO)
        return logger
    
    def connect(self) -> bool:
        """Connect to OBS WebSocket"""
        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.logger.info(f"Connected to OBS at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket"""
        if self.ws:
            self.ws.disconnect()
            self.logger.info("Disconnected from OBS")
    
    def start_recording(self) -> bool:
        """Start recording in OBS"""
        if not self.ws:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.ws.call(requests.StartRecord())
            self.logger.info("Recording started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording in OBS"""
        if not self.ws:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.ws.call(requests.StopRecord())
            self.logger.info("Recording stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def start_streaming(self) -> bool:
        """Start streaming in OBS"""
        if not self.ws:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.ws.call(requests.StartStream())
            self.logger.info("Streaming started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self) -> bool:
        """Stop streaming in OBS"""
        if not self.ws:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.ws.call(requests.StopStream())
            self.logger.info("Streaming stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop streaming: {e}")
            return False
    
    def set_scene(self, scene_name: str) -> bool:
        """
        Switch to a specific scene
        
        Args:
            scene_name: Name of the scene to switch to
        """
        if not self.ws:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
            self.logger.info(f"Switched to scene: {scene_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch scene: {e}")
            return False
    
    def get_recording_status(self) -> dict:
        """Get current recording status"""
        if not self.ws:
            return {"error": "Not connected"}
        
        try:
            response = self.ws.call(requests.GetRecordStatus())
            return {
                "is_recording": response.getOutputActive(),
                "recording_paused": response.getOutputPaused() if hasattr(response, 'getOutputPaused') else False
            }
        except Exception as e:
            self.logger.error(f"Failed to get recording status: {e}")
            return {"error": str(e)}


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OBS WebSocket Control')
    parser.add_argument('command', choices=['start-recording', 'stop-recording', 'start-streaming', 'stop-streaming', 'scene', 'status'])
    parser.add_argument('--host', default='localhost', help='OBS host')
    parser.add_argument('--port', type=int, default=4455, help='OBS WebSocket port')
    parser.add_argument('--password', default='', help='WebSocket password')
    parser.add_argument('--scene', help='Scene name (for scene command)')
    
    args = parser.parse_args()
    
    obs = OBSControl(args.host, args.port, args.password)
    
    if not obs.connect():
        print("Failed to connect to OBS")
        return
    
    try:
        if args.command == 'start-recording':
            obs.start_recording()
        elif args.command == 'stop-recording':
            obs.stop_recording()
        elif args.command == 'start-streaming':
            obs.start_streaming()
        elif args.command == 'stop-streaming':
            obs.stop_streaming()
        elif args.command == 'scene':
            if not args.scene:
                print("Error: --scene required")
            else:
                obs.set_scene(args.scene)
        elif args.command == 'status':
            status = obs.get_recording_status()
            print(f"Recording status: {status}")
    finally:
        obs.disconnect()


if __name__ == '__main__':
    main()
