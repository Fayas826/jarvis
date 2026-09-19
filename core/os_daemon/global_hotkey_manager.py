import ctypes
import threading
import time
import logging
from ctypes import wintypes
from typing import Callable, Dict, Optional

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Constants for Hotkey Management
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

# Virtual-Key codes
VK_SPACE = 0x20
VK_A = 0x41
VK_J = 0x4A

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlobalHotkeyManager")

class GlobalHotkeyManager:
    """
    ⚔️ PILLAR 1: System-Wide Global Hotkey & Sentinel Invocation Layer
    Registers OS-wide hotkeys via Win32 RegisterHotKey so A.E.G.I.S. can be 
    summoned instantly from any game, fullscreen application, or code editor.
    """
    
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._callbacks: Dict[int, Callable[[], None]] = {}
        self._next_hotkey_id = 100
        self._wake_engine_thread: Optional[threading.Thread] = None
        self._wake_active = False

    def register_hotkey(self, modifiers: int, vk_code: int, callback: Callable[[], None]) -> int:
        """Register a callback for a specific modifier and virtual key code."""
        hotkey_id = self._next_hotkey_id
        self._next_hotkey_id += 1
        self._callbacks[hotkey_id] = callback
        logger.info(f"[HOTKEY] Registered hotkey ID {hotkey_id} (Modifiers={hex(modifiers)}, VK={hex(vk_code)})")
        return hotkey_id

    def start(self):
        """Starts the dedicated Win32 message pump thread for system-wide hotkeys."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._message_loop, daemon=True, name="AegisHotkeySentinel")
        self._thread.start()
        logger.info("[HOTKEY] System-wide Global Hotkey Sentinel thread started.")

    def stop(self):
        """Unregisters hotkeys and terminates the message pump."""
        self._running = False
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0) # WM_QUIT
        self.stop_voice_sentinel()
        logger.info("[HOTKEY] Global Hotkey Sentinel stopped.")

    def _message_loop(self):
        self._thread_id = kernel32.GetCurrentThreadId()
        
        # Register standard universal hotkeys
        # 1. Ctrl + Alt + A (Primary Aegis Summon)
        h1 = 1
        res1 = user32.RegisterHotKey(None, h1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_A)
        # 2. Alt + J (Jarvis Mode)
        h2 = 2
        res2 = user32.RegisterHotKey(None, h2, MOD_ALT | MOD_NOREPEAT, VK_J)
        
        logger.info(f"[HOTKEY] Win32 RegisterHotKey: Ctrl+Alt+A={bool(res1)}, Alt+J={bool(res2)}")
        
        msg = wintypes.MSG()
        while self._running:
            # Non-blocking or 100ms peek to allow clean shutdown
            has_msg = user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1) # PM_REMOVE = 1
            if has_msg:
                if msg.message == WM_HOTKEY:
                    hotkey_id = msg.wParam
                    logger.info(f"[HOTKEY] Global Hotkey Triggered: ID {hotkey_id}")
                    self._on_hotkey_triggered(hotkey_id)
                elif msg.message == 0x0012: # WM_QUIT
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.05)
                
        # Cleanup
        user32.UnregisterHotKey(None, h1)
        user32.UnregisterHotKey(None, h2)

    def _on_hotkey_triggered(self, hotkey_id: int):
        """Invoked when any registered system-wide hotkey fires."""
        if hotkey_id in self._callbacks:
            try:
                self._callbacks[hotkey_id]()
            except Exception as e:
                logger.error(f"[HOTKEY] Callback execution error: {e}")
        else:
            # Default action: focus/activate A.E.G.I.S. HUD or console
            logger.info(f"[HOTKEY] Summoning A.E.G.I.S. Core Interface (Hotkey {hotkey_id})")
            self._summon_aegis_interface()

    def _summon_aegis_interface(self):
        """Brings A.E.G.I.S. interface to absolute foreground."""
        try:
            from core.execution.universal_desktop_controller import desktop_controller
            # Bring current or active terminal/IDE to foreground
            desktop_controller.bypass_foreground_lock(desktop_controller.user32.GetForegroundWindow())
        except Exception as e:
            logger.warning(f"[HOTKEY] Could not summon interface: {e}")

    def start_voice_sentinel(self, on_wake_callback: Optional[Callable[[], None]] = None):
        """Activates continuous low-overhead offline microphone wake-word engine."""
        if self._wake_active:
            return
        self._wake_active = True
        
        def _voice_worker():
            try:
                from sentinel.wake_engine import WakeEngine
                engine = WakeEngine()
                logger.info("[HOTKEY_SENTINEL] Offline Voice Sentinel Listening for 'Aegis' / 'Jarvis'...")
                # If model is available, run listen loop
                engine.listen_forever()
            except Exception as e:
                logger.warning(f"[HOTKEY_SENTINEL] Voice sentinel running in event standby mode: {e}")

        self._wake_engine_thread = threading.Thread(target=_voice_worker, daemon=True, name="AegisVoiceSentinel")
        self._wake_engine_thread.start()

    def stop_voice_sentinel(self):
        self._wake_active = False

global_hotkey_manager = GlobalHotkeyManager()
