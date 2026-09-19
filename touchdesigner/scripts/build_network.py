"""
Run INSIDE TouchDesigner Textport to auto-build the Morphora network.

Setup:
  1. File -> New, save as touchdesigner/main.toe (in this repo)
  2. Dialogs -> Textport and DAT Editor (or Alt+T)
  3. Run:

     exec(open(r'D:/Morphora/touchdesigner/scripts/build_network.py').read())

  4. Run python/main.py or python/simulate_gestures.py alongside TD
"""

import os

# Paths (edit if your repo lives elsewhere)
REPO = os.environ.get("MORPHORA_ROOT", r"D:/Morphora").replace("\\", "/")
MODELS = os.path.join(REPO, "touchdesigner", "models").replace("\\", "/")
SHADERS = os.path.join(REPO, "touchdesigner", "shaders").replace("\\", "/")

MORPH_SEC = 2.5
EXPLODE_SEC = 0.4
CUBE_SEC = 0.6
OSC_PORT = 7000


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _pos(op, x, y):
    try:
        op.nodeX = x
        op.nodeY = y
    except Exception:
        pass


def _set(op, names, val):
    """Set the first parameter name that exists on this operator."""
    if isinstance(names, str):
        names = [names]
    for name in names:
        if hasattr(op.par, name):
            try:
                setattr(op.par, name, val)
                return True
            except Exception:
                pass
    return False


def _connect(src, dst, in_idx=0):
    """Connect source operator to destination operator using TouchDesigner connectors."""
    if src is None or dst is None:
        return
    try:
        if hasattr(dst, "inputConnectors") and len(dst.inputConnectors) > in_idx:
            dst.inputConnectors[in_idx].connect(src)
        elif hasattr(dst, "setInput"):
            dst.setInput(in_idx, src)
    except Exception as e:
        _warn(f"Could not connect {getattr(src, 'name', src)} to {getattr(dst, 'name', dst)}: {e}")


def _pulse(op, names):
    """Pulse the first parameter name that exists."""
    if isinstance(names, str):
        names = [names]
    for name in names:
        if hasattr(op.par, name):
            try:
                getattr(op.par, name).pulse()
                return True
            except Exception:
                pass
    return False


def _warn(msg):
    print("Morphora build warning:", msg)


def build():
    root = op("/project1")
    if not root:
        root = op("/")

    if root.op("morphora"):
        root.op("morphora").destroy()

    base = root.create(baseCOMP, "morphora")
    base.viewer = True
    _pos(base, 0, 0)

    # 1. OSC Receiver
    osc = base.create(oscinCHOP, "osc_in")
    _set(osc, ["port", "netport", "networkport"], OSC_PORT)
    _pos(osc, -800, 400)

    # Select CHOPs (selectCHOP uses 'chop' parameter, NOT wires)
    for name, idx in [("select_state", 0), ("select_event", 1)]:
        sel = base.create(selectCHOP, name)
        _set(sel, ["chop", "chops"], osc.name)
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
    _connect(timer_explode, math_explode, 0)
    _pos(math_explode, 0, 380)

    handler = base.create(chopexecuteDAT, "event_handler")
    _set(handler, ["chop", "chops"], base.op("select_event").name)
    _set(handler, ["valuechange", "valuechangef"], True)
    try:
        handler.text = _read(os.path.join(REPO, "touchdesigner", "scripts", "osc_event_handler.py"))
    except Exception as e:
        _warn(f"Could not load osc_event_handler.py: {e}")
    _pos(handler, -400, 80)

    # 2. Model SOP chains
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
        _connect(f, facet, 0)
        _pos(facet, x, 500)

        n = base.create(nullSOP, name + "_out")
        _connect(facet, n, 0)
        _pos(n, x, 400)
        outs[name] = n
        x += 250

    switch_cur = base.create(switchSOP, "switch_current")
    _connect(outs["butterfly"], switch_cur, 0)
    _connect(outs["dragon"], switch_cur, 1)
    _connect(outs["lily"], switch_cur, 2)
    _set(switch_cur, ["input", "index"], 0)
    _pos(switch_cur, 350, 200)

    switch_tgt = base.create(switchSOP, "switch_target")
    _connect(outs["dragon"], switch_tgt, 0)
    _connect(outs["lily"], switch_tgt, 1)
    _connect(outs["butterfly"], switch_tgt, 2)
    _set(switch_tgt, ["input", "index"], 0)
    _pos(switch_tgt, 550, 200)

    script = base.create(scriptSOP, "morph_script")
    _connect(switch_cur, script, 0)
    _connect(switch_tgt, script, 1)
    script_dat = base.create(textDAT, "morph_targetp_dat")
    try:
        script_dat.text = _read(os.path.join(REPO, "touchdesigner", "scripts", "morph_targetp.py"))
    except Exception as e:
        _warn(f"Could not load morph_targetp.py: {e}")
    _set(script, ["callbackdat", "callbacks", "script"], script_dat.name)
    _pos(script_dat, 750, 80)
    _pos(script, 750, 200)

    morph_ready = base.create(nullSOP, "morph_ready")
    _connect(script, morph_ready, 0)
    _pos(morph_ready, 950, 200)

    # 3. Particle Geometry & Material
    geo = base.create(geometryCOMP, "geo_particles")
    _set(geo, "render", True)
    _set(geo, ["points", "renderpoints"], True)
    _set(geo, ["pointsize", "pointsize3d"], 3)
    _set(geo, "sop", morph_ready.name)
    _pos(geo, 950, 0)

    mat = base.create(glslMAT, "mat_particles")
    try:
        vert_src = _read(os.path.join(SHADERS, "particle_morph.vert"))
        frag_src = _read(os.path.join(SHADERS, "particle_morph.frag"))
        _set(mat, ["vertexshader", "vertshader"], vert_src)
        _set(mat, ["pixelfshader", "pixelshader", "fragshader"], frag_src)
    except Exception as e:
        _warn(f"Could not load shaders: {e}")

    for uname, val in [("uSwirlStrength", 0.4), ("uNoiseAmp", 0.25), ("uPointSize", 3.0)]:
        if hasattr(mat.par, uname):
            setattr(mat.par, uname, val)

    _set(geo, "material", mat.name)
    _pos(mat, 750, 0)

    try:
        if hasattr(mat.par, "uMorphT"):
            mat.par.uMorphT.expr = "op('timer_morph')['fraction']"
        if hasattr(mat.par, "uExplodeAmt"):
            mat.par.uExplodeAmt.expr = "op('math_explode')[0]"
        if hasattr(mat.par, "uTime"):
            mat.par.uTime.expr = "absTime.seconds"
    except Exception as e:
        _warn("Expression on mat_particles: " + str(e))

    # 4. Camera, Lights & Wireframe Cube
    cam = base.create(cameraCOMP, "cam1")
    _set(cam, "tx", 0)
    _set(cam, "ty", 0)
    _set(cam, "tz", 4.5)
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
    _set(geo_cube, "sop", box.name)
    _set(geo_cube, "uniformscale", 1.3)
    _pos(geo_cube, 650, -200)

    # 5. Render & Visual Post-Processing Pipeline
    render = base.create(renderTOP, "render1")
    _set(render, "camera", cam.name)
    _set(render, "geometry", "geo_particles geo_cube")
    _set(render, "lights", key.name)
    _set(render, ["resolutionw", "resw"], 1920)
    _set(render, ["resolutionh", "resh"], 1080)
    _pos(render, 950, -400)

    bloom = base.create(bloomTOP, "bloom1")
    _set(bloom, "threshold", 0.55)
    _set(bloom, "intensity", 1.2)
    _connect(render, bloom, 0)
    _pos(bloom, 1150, -400)

    level = base.create(levelTOP, "level1")
    _set(level, "gamma1", 1.1)
    _connect(bloom, level, 0)
    _pos(level, 1350, -400)

    out = base.create(nullTOP, "null_out")
    _connect(level, out, 0)
    _pos(out, 1550, -400)

    try:
        out.display = True
        out.render = True
    except Exception:
        pass

    # 6. Window COMP (Perform Mode Output)
    win = root.op("window1")
    if not win:
        win = root.create(windowCOMP, "window1")
    _set(win, ["winop", "operator"], out.path)
    _set(win, "justifyh", "center")
    _set(win, "justifyv", "center")
    _pos(win, 1200, -800)

    print("=" * 60)
    print("Morphora network built successfully under /project1/morphora!")
    print("Next steps:")
    print("  1. Press F1 to enter Perform Mode")
    print("  2. Watch the glowing 3D particles morph with your hand gestures!")
    print("  3. File -> Save to keep the network saved")
    print("=" * 60)


build()
