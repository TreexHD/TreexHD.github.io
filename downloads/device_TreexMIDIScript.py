# name=TreexMIDIScript v1.0 (user)
# url=https://treexhd.github.io/

# Simple FL Studio MIDI script:
# - Maps CC 19 -> Play/Pause (toggle)
# - Maps CC 20 -> Rewind (hold to rewind)
# - Sends CC 21 as beat indicator (127 on beat, 0 otherwise)
#
# Edit CC numbers below to match what your device sends.

import midi
import transport
import device

# === CONFIG ===
# CC numbers the Arduino sends for actions:
CC_PLAY_TOGGLE = 24    # when controller sends CC 19 with value>0 -> toggle play/pause
CC_REWIND = 25         # when CC 20 value>0 -> start rewind; when 0 -> stop rewind
CC_BEAT_LED = 22       # controller CC used for beat LED feedback

# MIDI channel to use when sending CC back to controller (0 = channel 1)
OUT_CHANNEL = 0

# Beat detection parameters
# LED flash duration in milliseconds
LED_FLASH_DURATION = 100

# === CALLBACKS ===

def OnInit():
    """Called once when script is loaded."""
    # Optionally, send LED off at start
    _send_cc(CC_BEAT_LED, 0)  # light up to show script active
    trace("ArduinoControlSurface script initialized.")


def OnDeInit():
    """Called when script is unloaded / FL closes."""
    # turn LED off
    _send_cc(CC_BEAT_LED, 0)


def OnMidiIn(msg):
    """
    msg is an FlMidiMsg-like object. Typical fields:
      msg.status  (status byte)
      msg.data1   (note or CC number)
      msg.data2   (value)
      msg.port    (port index)
    """

    # only process CC messages
    if (msg.status & 0xF0) != midi.MIDI_CONTROLCHANGE:
        return

    cc_num = msg.data1
    cc_val = msg.data2

    # PLAY/PAUSE toggle on CC_PLAY_TOGGLE (value > 0)
    if cc_num == CC_PLAY_TOGGLE and cc_val > 0:
        # Use globalTransport with FPT_Play to emulate DAW transport Play/Pause toggle
        # event.handled = True prevents FL default handling (like playing notes).
        transport.globalTransport(midi.FPT_Play, 10)
        msg.handled = True
        return

    # REWIND behavior: start on value>0, stop on value==0
    if cc_num == CC_REWIND:
        if cc_val > 0:
            # SS_Start constant requests starting the rewind action
            transport.globalTransport(midi.FPT_Rewind, midi.SS_Start)
        else:
            # SS_Stop stops the hold-style action
            transport.globalTransport(midi.FPT_Rewind, midi.SS_Stop)
        msg.handled = True
        return

    # (You can add more mappings here)

     
def OnUpdateBeatIndicator(id):
    """
    Called automatically by FL Studio on every beat/step.
    We'll pulse the beat LED here.
    """
    beat = transport.getHWBeatLEDState()  
    if(beat % 2) == 0:
        _send_cc(CC_BEAT_LED, 1)
    else:
        _send_cc(CC_BEAT_LED, 0)

# helper to send CC back to the controller
def _send_cc(cc_number, value):
    """
    Sends a CC message back to the linked device.
    Uses device.midiOutMsg(message, channel, data1, data2) interface.
    """
    try:
        # midi.MIDI_CONTROLCHANGE is the status constant for Control Change (0xB0)
        # second arg is channel (0..15)
        device.midiOutMsg(midi.MIDI_CONTROLCHANGE, OUT_CHANNEL, cc_number, int(value))
    except Exception as e:
        trace("Error sending CC {}: {}".format(cc_number, e))


# Optional: debug helper - FL Studio will show the trace text in the script output.
def trace(s):
    # if the API provides a trace/log function you can call it; otherwise just print
    try:
        print(s)
    except:
        pass