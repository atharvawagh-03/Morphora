"""
Run INSIDE TouchDesigner Textport to auto-build the Morphora network.

Setup:
  1. File -> New, save as touchdesigner/main.toe (in this repo)
  2. Dialogs -> Textport and DAT Editor
  3. Run:

     exec(open(r'D:/Morphora/touchdesigner/scripts/build_network.py').read())

  4. Review the morphora Base COMP — wire Window COMP to null_out if needed
  5. Run python/main.py or python/simulate_gestures.py alongside TD
"""

import os

# Paths (edit if your repo lives elsewhere)
REPO = os.environ.get("MORPHORA_ROOT", r"D:/Morphora")
MODELS = os.path.join(REPO, "touchdesigner", "models")
SHADERS = os.path.join(REPO, "touchdesigner", "shaders")

MORPH_SEC = 2.5
EXPLODE_SEC = 0.4
CUBE_SEC = 0.6
OSC_PORT = 7000


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _pos(op, x, y):
    op.nodeX = x
    op.nodeY = y


def _set(op, names, val):
    """Set the first parameter name that exists on this operator."""
    if isinstance(names, str):
        names = [names]
    for name in names:
        if hasattr(op.par, name):
            setattr(op.par, name, val)
            return True
    return False


def _pulse(op, names):
    """Pulse the first parameter name that exists."""
    if isinstance(names, str):
        names = [names]
    for name in names:
        if hasattr(op.par, name):
            getattr(op.par, name).pulse()
            return True
    return False


def _warn(msg):
    print("Morphora build warning:", msg)


def build():
    root = op("/project1")
    if root.op("morphora"):
        root.op("morphora").destroy()

    base = root.create(baseCOMP, "morphora")
    base.viewer = True
    _pos(base, 0, 0)

    # OSC
    osc = base.create(oscinCHOP, "osc_in")
    if not _set(osc, ["port", "netport", "networkport"], OSC_PORT):
        _warn("Could not set OSC In port — set to 7000 manually on osc_in")
    _pos(osc, -800, 400)

    for name, idx in [("select_state", 0), ("select_event", 1)]:
        sel = base.create(selectCHOP, name)
        sel.setInput(0, osc)
        _set(sel, ["chop", "chops"], osc)
        _set(sel, ["channames", "channelnames"], "*")
        _pos(sel, -600, 400 - idx * 120)

    for name in ("trig_morph_dragon", "trig_morph_lily", "trig_cube"):
        t = base.create(triggerCHOP, name)
        _pos(t, -400, {"trig_morph_dragon": 500, "trig_morph_lily": 380, "trig_cube": 260}[name])

    timer_morph = base.create(timerCHOP, "timer_morph")
    _set(timer_morph, "length", MORPH_SEC)
    _pulse(timer_morph, ["initialize", "init", "reset"])
    _pos(timer_morph, -200, 500)

    timer_explode = base.create(timerCHOP, "timer_explode")
    _set(timer_explode, "length", EXPLODE_SEC)
    _pos(timer_explode, -200, 380)

    timer_cube = base.create(timerCHOP, "timer_cube")
    _set(timer_cube, "length", CUBE_SEC)
    _pos(timer_cube, -200, 260)

    math_explode = base.create(mathCHOP, "math_explode")
    _set(math_explode, "preoff", 1)
    _set(math_explode, "gain", -1)
    math_explode.setInput(0, timer_explode)
    _pos(math_explode, 0, 380)

    handler = base.create(chopexecuteDAT, "event_handler")
    _set(handler, ["chop", "chops"], base.op("select_event"))
    _set(handler, ["valuechange", "valuechangef"], True)
    handler.text = _read(os.path.join(REPO, "touchdesigner", "scripts", "osc_event_handler.py"))
    _pos(handler, -400, 80)

    # Model SOP chains
    model_files = {
        "butterfly": "butterfly_10k.obj",
        "dragon": "dragon_10k.obj",
        "lily": "lily_10k.obj",
    }

    outs = {}
    x = 200
    for name, fname in model_files.items():
        path = os.path.join(MODELS, fname).replace("\\", "/")
        f = base.create(fileSOP, "file_" + name)
        _set(f, "file", path)
        _pos(f, x, 600)

        facet = base.create(facetSOP, "facet_" + name)
        _set(facet, ["unique", "uniquepoints"], True)
        facet.setInput(0, f)
        _pos(facet, x, 500)

        n = base.create(nullSOP, name + "_out")
        n.setInput(0, facet)
        _pos(n, x, 400)
        outs[name] = n
        x += 250

    switch_cur = base.create(switchSOP, "switch_current")
    switch_cur.setInput(0, outs["butterfly"])
    switch_cur.setInput(1, outs["dragon"])
    switch_cur.setInput(2, outs["lily"])
    _set(switch_cur, "input", 0)
    _pos(switch_cur, 350, 200)

    switch_tgt = base.create(switchSOP, "switch_target")
    switch_tgt.setInput(0, outs["dragon"])
    switch_tgt.setInput(1, outs["lily"])
    switch_tgt.setInput(2, outs["butterfly"])
    _set(switch_tgt, "input", 0)
    _pos(switch_tgt, 550, 200)

    script = base.create(scriptSOP, "morph_script")
    script.setInput(0, switch_cur)
    script.setInput(1, switch_tgt)
    script_dat = base.create(textDAT, "morph_targetp_dat")
    script_dat.text = _read(os.path.join(REPO, "touchdesigner", "scripts", "morph_targetp.py"))
    if not _set(script, ["callbackdat", "callbacks", "script"], script_dat):
        _warn("Could not link morph_targetp_dat to morph_script — link manually")
    _pos(script_dat, 750, 80)
    _pos(script, 750, 200)

    morph_ready = base.create(nullSOP, "morph_ready")
    morph_ready.setInput(0, script)
    _pos(morph_ready, 950, 200)

    # Particles
    geo = base.create(geometryCOMP, "geo_particles")
    _set(geo, "render", True)
    _set(geo, ["points", "renderpoints"], True)
    _set(geo, ["pointsize", "pointsize3d"], 3)
    _set(geo, "sop", morph_ready)
    _pos(geo, 950, 0)

    mat = base.create(glslMAT, "mat_particles")
    vert_src = _read(os.path.join(SHADERS, "particle_morph.vert"))
    frag_src = _read(os.path.join(SHADERS, "particle_morph.frag"))
    if not _set(mat, ["vertexshader", "vertshader"], vert_src):
        _warn("Could not set vertex shader on mat_particles — paste manually")
    if not _set(mat, ["pixelfshader", "pixelshader", "fragshader"], frag_src):
        _warn("Could not set pixel shader on mat_particles — paste manually")

    for uname, val in [("uSwirlStrength", 0.4), ("uNoiseAmp", 0.25), ("uPointSize", 3.0)]:
        if hasattr(mat.par, uname):
            setattr(mat.par, uname, val)

    _set(geo, "material", mat)
    _pos(mat, 750, 0)

    try:
        mat.par.uMorphT.expr = "op('timer_morph')['fraction']"
        mat.par.uExplodeAmt.expr = "op('math_explode')[0]"
        mat.par.uTime.expr = "absTime.seconds"
    except Exception as e:
        _warn("Wire uMorphT/uExplodeAmt manually on mat_particles: " + str(e))

    # Camera + lights + cube
    cam = base.create(cameraCOMP, "cam1")
    _set(cam, "tx", 0)
    _set(cam, "ty", 0)
    _set(cam, "tz", 4)
    _pos(cam, 200, -200)

    key = base.create(lightCOMP, "key")
    _set(key, "lighttype", "point")
    _set(key, "tx", -2)
    _set(key, "ty", 2)
    _set(key, "tz", 3)
    _pos(key, 350, -200)

    rim = base.create(lightCOMP, "rim")
    _set(rim, "lighttype", "point")
    _set(rim, "tx", 2)
    _set(rim, "ty", 1)
    _set(rim, "tz", -2)
    _set(rim, "dimmer", 0.4)
    _pos(rim, 500, -200)

    geo_cube = base.create(geometryCOMP, "geo_cube")
    box = geo_cube.create(boxSOP, "box1")
    _set(geo_cube, "render", True)
    _set(geo_cube, ["wireframe", "wireframefront"], True)
    _set(geo_cube, "sop", box)
    _set(geo_cube, "uniformscale", 1.2)
    _pos(geo_cube, 650, -200)

    # Render + composite
    render = base.create(renderTOP, "render1")
    _set(render, "camera", cam)
    _set(render, "geometry", geo)
    _set(render, "lights", key)
    _set(render, ["resolutionw", "resw"], 1280)
    _set(render, ["resolutionh", "resh"], 720)
    _pos(render, 950, -400)

    cam_bg = base.create(videodevinTOP, "videodevin1")
    _set(cam_bg, ["resolutionw", "resw"], 1280)
    _set(cam_bg, ["resolutionh", "resh"], 720)
    _pos(cam_bg, 750, -550)

    comp = base.create(compositeTOP, "composite1")
    comp.setInput(0, cam_bg)
    comp.setInput(1, render)
    _set(comp, "operand", "over")
    _pos(comp, 950, -550)

    bloom = base.create(bloomTOP, "bloom1")
    _set(bloom, "threshold", 0.65)
    bloom.setInput(0, comp)
    _pos(bloom, 1150, -550)

    level = base.create(levelTOP, "level1")
    level.setInput(0, bloom)
    _pos(level, 1350, -550)

    out = base.create(nullTOP, "null_out")
    out.setInput(0, level)
    _pos(out, 1550, -550)

    win = root.create(windowCOMP, "window1")
    _set(win, ["winop", "operator"], out)
    _set(win, "justifyh", "center")
    _set(win, "justifyv", "center")
    _pos(win, 1200, -800)

    print("=" * 60)
    print("Morphora network built under /project1/morphora")
    print("Next:")
    print("  1. Open /project1/morphora and check for yellow warning nodes")
    print("  2. Pulse trig_morph_dragon to test morph")
    print("  3. Run: python simulate_gestures.py")
    print("  4. File -> Save As -> touchdesigner/main.toe")
    print("=" * 60)


build()
