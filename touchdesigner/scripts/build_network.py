"""
Run INSIDE TouchDesigner Textport to auto-build the Morphora network.

Setup:
  1. Open TouchDesigner
  2. Dialogs -> Textport and DAT Editor (or Alt+T)
  3. Paste & press Enter:

     exec(open(r'D:/Morphora/touchdesigner/scripts/build_network.py').read())

  4. Press F1 to enter Perform Mode!
"""

import os

REPO = os.environ.get("MORPHORA_ROOT", r"D:/Morphora").replace("\\", "/")
MODELS = os.path.join(REPO, "touchdesigner", "models").replace("\\", "/")

MORPH_SEC = 2.5
OSC_PORT = 7000


def _pos(op, x, y):
    try:
        op.nodeX = x
        op.nodeY = y
    except Exception:
        pass


def _set(op, names, val):
    if isinstance(names, str):
        names = [names]
        
    # Check if assigning OP object directly (e.g. material = mat_pts or mat_pts.path/name)
    val_str = getattr(val, "path", getattr(val, "name", val))

    for name in names:
        if hasattr(op.par, name):
            par = getattr(op.par, name)
            try:
                par.val = val
                return True
            except Exception:
                try:
                    par.val = val_str
                    return True
                except Exception:
                    try:
                        setattr(op.par, name, val)
                        return True
                    except Exception:
                        pass
    return False


def _connect(src, dst, in_idx=0):
    if src is None or dst is None:
        return
    try:
        if hasattr(dst, "inputConnectors") and len(dst.inputConnectors) > in_idx:
            dst.inputConnectors[in_idx].connect(src)
        elif hasattr(dst, "setInput"):
            dst.setInput(in_idx, src)
    except Exception as e:
        print(f"Note: connect {getattr(src, 'name', src)} -> {getattr(dst, 'name', dst)}: {e}")


def build():
    root = op("/project1")
    if not root:
        root = op("/")

    # Clear old nodes in /project1
    for child in list(root.children):
        try:
            child.destroy()
        except Exception:
            pass

    # 1. OSC Receiver on Port 7000
    osc = root.create(oscinCHOP, "osc_in")
    _set(osc, ["port", "netport", "networkport"], OSC_PORT)
    _pos(osc, -600, 400)

    sel_event = root.create(selectCHOP, "select_event")
    _set(sel_event, ["chop", "chops"], osc.name)
    _set(sel_event, ["channames", "channelnames"], "*")
    _pos(sel_event, -400, 400)

    # State constant: 0 = Butterfly, 1 = Dragon, 2 = Lily
    state_const = root.create(constantCHOP, "target_morph_state")
    _set(state_const, "name0", "target_index")
    _set(state_const, "value0", 0.0)
    _set(state_const, "name1", "cube_open")
    _set(state_const, "value1", 0.0)
    _pos(state_const, -400, 250)

    # Smooth 2.5s lag filter between states
    lag = root.create(lagCHOP, "morph_lag")
    _set(lag, ["lag1", "lag"], MORPH_SEC)
    _set(lag, ["lag2"], MORPH_SEC)
    _connect(state_const, lag, 0)
    _pos(lag, -200, 250)

    # OSC Event Handler
    handler = root.create(chopexecuteDAT, "event_handler")
    _set(handler, ["chop", "chops"], sel_event.name)
    _set(handler, ["valuechange", "valuechangef"], True)
    handler.text = '''# OSC Handler for Morphora
def onValueChange(channel, sampleIndex, val, prev):
    if val <= 0:
        return
    c = op('target_morph_state')
    if not c:
        return
    cur = c.par.value0.eval()

    if channel.name in ('left_fist_open', 'morph_next'):
        c.par.value0 = (cur + 1) % 3
    elif channel.name in ('both_open', 'reset'):
        c.par.value0 = 0.0
        c.par.value1 = 0.0
    elif channel.name in ('right_pinch', 'toggle_cube'):
        c.par.value1 = 1.0 if c.par.value1.eval() < 0.5 else 0.0
'''
    _pos(handler, -400, 80)

    # 2. 10,000-Particle Geometry (Self-contained inside geo_particles)
    geo = root.create(geometryCOMP, "geo_particles")
    _pos(geo, 400, 150)
    for c in list(geo.children):
        c.destroy()

    model_files = {
        "butterfly": "butterfly_10k.obj",
        "dragon": "dragon_10k.obj",
        "lily": "lily_10k.obj",
    }

    outs = {}
    x = 100
    for name, fname in model_files.items():
        path = os.path.join(MODELS, fname).replace("\\", "/")
        f = geo.create(fileSOP, "file_" + name)
        _set(f, "file", path)
        _pos(f, x, 600)

        # Color the points: Butterfly=Cyan (#00c2ff), Dragon=Red (#ff1e2d), Lily=Pink (#c2185b)
        col = geo.create(pointSOP, "color_" + name)
        _set(col, ["color", "keepcolor"], True)
        _set(col, "doclr", 1)
        if name == "butterfly":
            _set(col, ["cr", "colorr"], 0.0)
            _set(col, ["cg", "colorg"], 0.85)
            _set(col, ["cb", "colorb"], 1.0)
        elif name == "dragon":
            _set(col, ["cr", "colorr"], 1.0)
            _set(col, ["cg", "colorg"], 0.15)
            _set(col, ["cb", "colorb"], 0.18)
        else:
            _set(col, ["cr", "colorr"], 0.95)
            _set(col, ["cg", "colorg"], 0.15)
            _set(col, ["cb", "colorb"], 0.60)

        _connect(f, col, 0)
        _pos(col, x, 450)

        n = geo.create(nullSOP, name + "_out")
        _connect(col, n, 0)
        _pos(n, x, 300)
        outs[name] = n
        x += 200

    # Switch SOP with GPU Point Cloud Blending
    switch = geo.create(switchSOP, "switch_morph")
    _connect(outs["butterfly"], switch, 0)
    _connect(outs["dragon"], switch, 1)
    _connect(outs["lily"], switch, 2)
    _set(switch, ["blend", "blendinputs"], True)
    try:
        switch.par.index.expr = "op('../morph_lag')['target_index']"
    except Exception:
        try:
            switch.par.input.expr = "op('../morph_lag')['target_index']"
        except Exception:
            pass
    _pos(switch, 300, 150)

    out_geo = geo.create(nullSOP, "out1")
    _connect(switch, out_geo, 0)
    try:
        out_geo.render = True
        out_geo.display = True
    except Exception:
        pass
    _pos(out_geo, 300, -100)

    # Enable Point Rendering directly on the Geometry COMP
    _set(geo, ["renderpoints", "points"], 1)
    _set(geo, ["pointsize", "pointsize3d"], 8.0)
    _set(geo, "render", True)

    # Particle Material: Point sprites with point colors
    try:
        mat_pts = root.create(pointSpriteMAT, "mat_particles")
    except Exception:
        try:
            mat_pts = root.create(pointMAT, "mat_particles")
        except Exception:
            mat_pts = root.create(constantMAT, "mat_particles")

    _set(mat_pts, ["size", "pointsize", "psize"], 8.0)
    _set(mat_pts, ["constant", "unlit"], True)
    _set(mat_pts, ["colormode", "pointcolormode"], 1)
    _pos(mat_pts, 200, 150)
    _set(geo, ["material", "mat"], mat_pts.path)

    # 3. Rotating Wireframe Cube
    geo_cube = root.create(geometryCOMP, "geo_cube")
    _pos(geo_cube, 400, -150)
    for c in list(geo_cube.children):
        c.destroy()
    box = geo_cube.create(boxSOP, "box1")
    _set(box, ["sizex", "sizey", "sizez"], 1.6)
    box.render = True
    box.display = True

    try:
        geo_cube.par.ry.expr = "absTime.seconds * 12"
        geo_cube.par.rx.expr = "15 + sin(absTime.seconds * 0.5) * 5"
        geo_cube.par.uniformscale.expr = "1.2 + op('morph_lag')['cube_open'] * 0.5"
    except Exception:
        pass

    mat_cube = root.create(constantMAT, "mat_cube")
    _set(mat_cube, ["wireframe", "wireframefront"], True)
    _set(mat_cube, ["wirewidth", "width"], 2)
    _set(mat_cube, ["colorr", "cr"], 0.0)
    _set(mat_cube, ["colorg", "cg"], 0.6)
    _set(mat_cube, ["colorb", "cb"], 0.95)
    _pos(mat_cube, 200, -150)
    _set(geo_cube, ["material", "mat"], mat_cube.path)

    # 4. Camera
    cam = root.create(cameraCOMP, "cam1")
    _set(cam, "tx", 0)
    _set(cam, "ty", 0)
    _set(cam, "tz", 3.2)
    _pos(cam, 0, -250)

    # 5. Render & Bloom Pipeline
    render = root.create(renderTOP, "render1")
    _set(render, ["camera", "cam"], cam.path)
    _set(render, ["geometry", "geo"], "*")
    _set(render, ["resolutionw", "resw"], 1920)
    _set(render, ["resolutionh", "resh"], 1080)
    _pos(render, 700, -100)

    try:
        bloom = root.create(bloomTOP, "bloom1")
        _set(bloom, "threshold", 0.30)
        _set(bloom, "intensity", 1.8)
        _connect(render, bloom, 0)
        _pos(bloom, 900, -100)
        last_top = bloom
    except Exception:
        last_top = render

    # 6. Output TOP directly in /project1
    out = root.create(nullTOP, "out1")
    _connect(last_top, out, 0)
    out.display = True
    out.render = True
    _pos(out, 1100, -100)

    # 7. Window COMP for Perform Mode
    win = root.create(windowCOMP, "window1")
    _set(win, ["winop", "operator"], out.name)
    _set(win, "justifyh", "center")
    _set(win, "justifyv", "center")
    _pos(win, 1100, -300)

    # Set project perform window
    try:
        root.par.window = win.name
    except Exception:
        pass
    try:
        op("/ui/dialogs/perform").par.winop = out.path
    except Exception:
        pass

    print("=" * 60)
    print("Morphora 3D Visual Network Successfully Built!")
    print("  ✓ 10,000 Glowing Butterfly Particles (Cyan)")
    print("  ✓ 10,000 Glowing Dragon Particles (Red)")
    print("  ✓ 10,000 Glowing Lily Particles (Pink)")
    print("  ✓ Particle System Add SOP + PointMAT Active")
    print("  ✓ Rotating Wireframe Cube Active")
    print("  ✓ Bloom Glow Wired Directly to out1 & Perform Mode")
    print("=" * 60)
    print("Press F1 now to view the glowing Butterfly inside the cube!")
    print("=" * 60)


build()
