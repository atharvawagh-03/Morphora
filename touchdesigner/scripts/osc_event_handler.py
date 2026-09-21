# Paste into a CHOP Execute DAT inside TouchDesigner.
# Wire the Select CHOP for /gesture/event into this DAT's input.
#
# NOTE: Python sends events as STRING VALUES on the /gesture/event channel.
# The channel NAME is always "/gesture/event" — we must check the VALUE (val).

def onValueChange(channel, sampleIndex, val, prev):
    event = str(val).strip().strip('"')

    # Ignore zero/empty values (OSC In defaults)
    if not event or event == '0' or event == '0.0':
        return

    debug(f"Morphora event: {event}")

    # State changes are now driven by /gesture/state → state_handler DAT.
    # This handler is for any additional TD-side logic you want to trigger
    # on specific gesture events (e.g., triggering a one-shot animation).
    #
    # Example: trigger a particle burst on morph events
    # if event == 'left_fist_open':
    #     op('trig_burst').par.triggerpulse.pulse()

    return
