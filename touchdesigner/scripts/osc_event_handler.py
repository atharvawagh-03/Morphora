# Paste into a CHOP Execute DAT inside TouchDesigner.
# Wire the OSC In CHOP channel that carries /gesture/event into this DAT's input.
#
# Name sibling Trigger CHOPs exactly:
#   trig_morph_dragon, trig_morph_lily, trig_cube

def _pulse(name):
    trig = op(name)
    if trig is None:
        debug(f"Morphora: missing {name}")
        return
    trig.par.triggerpulse.pulse()


def onValueChange(channel, sampleIndex, val, prev):
    event = str(val).strip().strip('"')
    if event == "left_fist_open":
        state = int(op("select_state")[0]) if op("select_state") else -1
        # 0 BUTTERFLY or 2 DRAGON → start a morph
        if state in (0, 2):
            _pulse("trig_morph_dragon" if state == 0 else "trig_morph_lily")
    elif event == "right_pinch":
        _pulse("trig_cube")
    elif event == "two_hand_open":
        _pulse("trig_reset_butterfly")  # optional: snap clouds back
    return
