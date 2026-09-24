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

    # ── Clear old nodes ──────────────────────────────────────────────────
    for child in list(root.children):
        try:
            child.destroy()
        except Exception:
            pass

    print("Building Morphora network...")

    # =====================================================================
    # 1. OSC RECEIVER
    # =====================================================================
    osc = root.create(oscinCHOP, "osc_in")
    _set(osc, ["port", "netport", "networkport"], OSC_PORT)
    _pos(osc, -800, 400)
    print("  [1/9] OSC In CHOP on port 7000")

    # ── Per-channel Select CHOPs ─────────────────────────────────────────
    sel_state = root.create(selectCHOP, "select_state")
    _set(sel_state, ["chop", "chops"], osc.name)
    _set(sel_state, ["channames", "channelnames"], "/gesture/state")
    _pos(sel_state, -600, 500)

    sel_event = root.create(selectCHOP, "select_event")
    _set(sel_event, ["chop", "chops"], osc.name)
    _set(sel_event, ["channames", "channelnames"], "/gesture/event")
    _pos(sel_event, -600, 400)

    sel_left = root.create(selectCHOP, "select_left")
    _set(sel_left, ["chop", "chops"], osc.name)
    _set(sel_left, ["channames", "channelnames"], "/gesture/left")
    _pos(sel_left, -600, 300)

    sel_right = root.create(selectCHOP, "select_right")
    _set(sel_right, ["chop", "chops"], osc.name)
    _set(sel_right, ["channames", "channelnames"], "/gesture/right")
    _pos(sel_right, -600, 200)

    # =====================================================================
    # 2. STATE MANAGEMENT — drive Switch SOP from OSC state integer
    # =====================================================================
    # Python sends state as int: 0=BUTTERFLY, 1=MORPH_TO_DRAGON, 2=DRAGON,
    #                            3=MORPH_TO_LILY, 4=LILY, 5=CUBE_OPEN
    #
    # Switch SOP needs a blend index: 0=butterfly, 1=dragon, 2=lily
    # Mapping:
    #   state 0 (BUTTERFLY)       → switch_index = 0.0
    #   state 1 (MORPH_TO_DRAGON) → switch_index = 0.0 → 1.0 (animated by lag)
    #   state 2 (DRAGON)          → switch_index = 1.0
    #   state 3 (MORPH_TO_LILY)   → switch_index = 1.0 → 2.0 (animated by lag)
    #   state 4 (LILY)            → switch_index = 2.0
    #   state 5 (CUBE_OPEN)       → switch_index = 2.0 (cube animates separately)

    # Constant CHOP holds the target switch index + cube_open flag
    state_const = root.create(constantCHOP, "target_morph_state")
    _set(state_const, "name0", "target_index")
    _set(state_const, "value0", 0.0)
    _set(state_const, "name1", "cube_open")
    _set(state_const, "value1", 0.0)
    _pos(state_const, -400, 500)

    # CHOP Execute DAT: reads the OSC state integer and maps it
    state_handler = root.create(chopexecuteDAT, "state_handler")
    _set(state_handler, ["chop", "chops"], sel_state.name)
    _set(state_handler, ["valuechange", "valuechangef"], True)
    state_handler.text = '''# State handler — maps OSC state integer to Switch SOP index
def onValueChange(channel, sampleIndex, val, prev):
    c = op('target_morph_state')
    if not c:
        return

    state = int(val)

    # Map state integer to switch index (0=butterfly, 1=dragon, 2=lily)
    state_to_index = {
        0: 0.0,   # BUTTERFLY
        1: 1.0,   # MORPH_TO_DRAGON (lag will animate 0→1)
        2: 1.0,   # DRAGON
        3: 2.0,   # MORPH_TO_LILY (lag will animate 1→2)
        4: 2.0,   # LILY
        5: 2.0,   # CUBE_OPEN (lily stays, cube animates)
    }

    # Map cube_open flag
    cube_open = 1.0 if state == 5 else 0.0

    target_idx = state_to_index.get(state, 0.0)
    c.par.value0 = target_idx
    c.par.value1 = cube_open

    debug(f"Morphora state={state} -> switch_index={target_idx}, cube={cube_open}")
    return
'''
    _pos(state_handler, -400, 600)

    # Smooth lag filter — animates between switch indices over 2.5s
    lag = root.create(lagCHOP, "morph_lag")
    _set(lag, ["lag1", "lag"], MORPH_SEC)
    _set(lag, ["lag2"], MORPH_SEC)
    _connect(state_const, lag, 0)
    _pos(lag, -200, 500)

    # ── Event handler for string events from /gesture/event ──────────────
    event_handler = root.create(chopexecuteDAT, "event_handler")
    _set(event_handler, ["chop", "chops"], sel_event.name)
    _set(event_handler, ["valuechange", "valuechangef"], True)
    event_handler.text = '''# OSC Event Handler for Morphora
# The /gesture/event channel carries string values like "left_fist_open"
# We check the VALUE of the channel, not the channel name.
def onValueChange(channel, sampleIndex, val, prev):
    event = str(val).strip().strip('"')

    if not event or event == '0' or event == '0.0':
        return

    debug(f"Morphora event received: {event}")

    # Events are informational — state changes are driven by /gesture/state
    # This handler is for logging/debugging and any additional TD-side logic
    return
'''
    _pos(event_handler, -400, 300)

    print("  [2/9] State management + OSC event handling")

    # =====================================================================
    # 3. PARTICLE GEOMETRY — 10,000-point models
    # =====================================================================
    geo = root.create(geometryCOMP, "geo_particles")
    _pos(geo, 400, 200)
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
        if not os.path.isfile(path):
            print(f"  WARNING: Model file not found: {path}")

        f = geo.create(fileSOP, "file_" + name)
        _set(f, "file", path)
        _pos(f, x, 600)

        # Facet SOP — unique points (per SETUP.md)
        facet = geo.create(facetSOP, "facet_" + name)
        _set(facet, ["unique", "uniquepoints"], True)
        _connect(f, facet, 0)
        _pos(facet, x, 525)

        # Color the points
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
        else:  # lily
            _set(col, ["cr", "colorr"], 0.95)
            _set(col, ["cg", "colorg"], 0.15)
            _set(col, ["cb", "colorb"], 0.60)

        _connect(facet, col, 0)
        _pos(col, x, 450)

        n = geo.create(nullSOP, name + "_out")
        _connect(col, n, 0)
        _pos(n, x, 300)
        outs[name] = n
        x += 250

    # ── Diagnostics: check File SOP loaded correctly ─────────────────────
    for name in model_files:
        try:
            fsop = geo.op("file_" + name)
            if fsop is not None:
                npts = fsop.numPoints if hasattr(fsop, 'numPoints') else '?'
                nprims = fsop.numPrims if hasattr(fsop, 'numPrims') else '?'
                print(f"    file_{name}: {npts} points, {nprims} prims")
            else:
                print(f"    WARNING: file_{name} SOP not found!")
        except Exception as e:
            print(f"    file_{name} diag error: {e}")

    # Switch SOP with blending — driven by morph_lag['target_index']
    switch = geo.create(switchSOP, "switch_morph")
    _connect(outs["butterfly"], switch, 0)
    _connect(outs["dragon"], switch, 1)
    _connect(outs["lily"], switch, 2)

    # Enable blend mode for smooth morphing
    _set(switch, ["blend", "blendinputs"], True)

    # Expression to read the lagged index from the parent level
    try:
        switch.par.index.expr = "op('../morph_lag')['target_index']"
    except Exception:
        try:
            switch.par.input.expr = "op('../morph_lag')['target_index']"
        except Exception:
            print("  WARNING: Could not set Switch SOP expression")

    _pos(switch, 300, 150)

    # ── Output Null SOP — NO Convert/Add SOP needed ──────────────────────
    # OBJ files now contain proper triangle faces, so File SOP creates
    # polygon primitives directly. The material handles point rendering.
    out_geo = geo.create(nullSOP, "out1")
    _connect(switch, out_geo, 0)
    try:
        out_geo.render = True
        out_geo.display = True
    except Exception:
        pass
    _pos(out_geo, 300, 0)

    # Geometry COMP rendering settings
    _set(geo, "render", True)
    _set(geo, "display", True)

    print("  [3/9] 3 x 10,000-point models loaded")

    # =====================================================================
    # 4. PARTICLE MATERIAL — constantMAT in GL_POINT draw mode
    # =====================================================================
    # constantMAT is universally available. We set its polygon draw mode
    # to POINT so only vertices render (as point sprites), not filled faces.
    mat_pts = root.create(constantMAT, "mat_particles")

    # White base color so vertex Cd passes through
    _set(mat_pts, ["colorr", "cr"], 1.0)
    _set(mat_pts, ["colorg", "cg"], 1.0)
    _set(mat_pts, ["colorb", "cb"], 1.0)
    _set(mat_pts, ["alpha", "colora"], 1.0)

    # ── KEY FIX: Set polygon draw mode to POINT (not Fill/Wireframe) ─────
    # In OpenGL terms: GL_POINT = only vertices are drawn as dots.
    # TD constantMAT parameter 'polygondrawmode' or 'drawmode':
    #   0 = Fill (solid surface), 1 = Line (wireframe), 2 = Point
    # We try every known parameter name for this across TD versions.
    point_mode_set = False
    for pname in ["polygondrawmode", "drawmode", "fillmode", "polygonfront",
                   "frontfacemode", "rendermode", "drawprim"]:
        if _set(mat_pts, pname, 2):
            print(f"    Set {pname} = 2 (Point mode) on mat_particles")
            point_mode_set = True
            break

    if not point_mode_set:
        # Fallback: try wireframe mode (at least shows edges, not filled tris)
        _set(mat_pts, ["wireframe", "wireframefront"], True)
        print("    Fallback: wireframe mode on mat_particles")

    # Point size — larger = more visible
    _set(mat_pts, ["pointsize", "psize"], 6.0)

    _pos(mat_pts, 200, 200)

    # Assign material to geo_particles
    try:
        geo.par.material = mat_pts
    except Exception:
        try:
            geo.par.material = mat_pts.path
        except Exception:
            _set(geo, ["material", "mat"], mat_pts.path)

    print(f"  [4/9] Particle material (constantMAT)")

    # =====================================================================
    # 5. WIREFRAME CUBE
    # =====================================================================
    geo_cube = root.create(geometryCOMP, "geo_cube")
    _pos(geo_cube, 400, -100)
    for c in list(geo_cube.children):
        c.destroy()

    box = geo_cube.create(boxSOP, "box1")
    _set(box, ["sizex", "sx"], 1.6)
    _set(box, ["sizey", "sy"], 1.6)
    _set(box, ["sizez", "sz"], 1.6)
    try:
        box.render = True
        box.display = True
    except Exception:
        pass

    # Cube rotation
    try:
        geo_cube.par.ry.expr = "absTime.seconds * 12"
        geo_cube.par.rx.expr = "15 + sin(absTime.seconds * 0.5) * 5"
    except Exception:
        pass

    # Cube scale driven by cube_open flag from morph_lag
    try:
        geo_cube.par.sx.expr = "1.2 + op('morph_lag')['cube_open'] * 0.5"
        geo_cube.par.sy.expr = "1.2 + op('morph_lag')['cube_open'] * 0.5"
        geo_cube.par.sz.expr = "1.2 + op('morph_lag')['cube_open'] * 0.5"
    except Exception:
        pass

    _set(geo_cube, "render", True)
    _set(geo_cube, "display", True)

    # Cube material — wireframe
    mat_cube = root.create(constantMAT, "mat_cube")
    _set(mat_cube, ["wireframe", "wireframefront"], True)
    _set(mat_cube, ["wirewidth", "width"], 2)
    _set(mat_cube, ["colorr", "cr"], 0.0)
    _set(mat_cube, ["colorg", "cg"], 0.6)
    _set(mat_cube, ["colorb", "cb"], 0.95)
    _set(mat_cube, ["alpha", "colora"], 0.5)
    _pos(mat_cube, 200, -100)

    try:
        geo_cube.par.material = mat_cube
    except Exception:
        try:
            geo_cube.par.material = mat_cube.path
        except Exception:
            _set(geo_cube, ["material", "mat"], mat_cube.path)

    print("  [5/9] Wireframe cube")

    # =====================================================================
    # 6. CAMERA
    # =====================================================================
    cam = root.create(cameraCOMP, "cam1")
    _set(cam, "tx", 0)
    _set(cam, "ty", 0)
    _set(cam, "tz", 3.5)
    _pos(cam, 0, -300)
    print("  [6/9] Camera")

    # =====================================================================
    # 7. LIGHT — required for some materials, helps visibility
    # =====================================================================
    light = root.create(lightCOMP, "light1")
    _set(light, "tx", 2.0)
    _set(light, "ty", 3.0)
    _set(light, "tz", 4.0)
    _set(light, ["dimmer", "intensity"], 1.0)
    _pos(light, 0, -200)

    # Optional second fill light
    light2 = root.create(lightCOMP, "light2")
    _set(light2, "tx", -2.0)
    _set(light2, "ty", -1.0)
    _set(light2, "tz", 3.0)
    _set(light2, ["dimmer", "intensity"], 0.4)
    _pos(light2, 0, -100)

    print("  [7/9] Lights")

    # =====================================================================
    # 8. RENDER & BLOOM PIPELINE
    # =====================================================================
    render = root.create(renderTOP, "render1")
    _set(render, ["camera", "cam"], cam.path)
    _set(render, ["resolutionw", "resw"], 1920)
    _set(render, ["resolutionh", "resh"], 1080)

    # Set geometry — use wildcard to capture both geo_particles and geo_cube
    _set(render, ["geometry", "geo"], "*")

    # Explicit lights
    _set(render, ["lights", "light"], "*")

    _pos(render, 700, -100)

    # Background — dark/black
    _set(render, ["bgcolorr", "bgr"], 0.02)
    _set(render, ["bgcolorg", "bgg"], 0.02)
    _set(render, ["bgcolorb", "bgb"], 0.04)

    # Bloom post-processing
    try:
        bloom = root.create(bloomTOP, "bloom1")
        _set(bloom, "threshold", 0.25)
        _set(bloom, ["intensity", "bloomintensity"], 2.0)
        _set(bloom, ["size", "bloomsize"], 10)
        _connect(render, bloom, 0)
        _pos(bloom, 900, -100)
        last_top = bloom
    except Exception:
        print("  Note: Bloom TOP not available, skipping")
        last_top = render

    print("  [8/9] Render + bloom pipeline")

    # =====================================================================
    # 9. OUTPUT & WINDOW
    # =====================================================================
    out = root.create(nullTOP, "out1")
    _connect(last_top, out, 0)
    out.display = True
    out.render = True
    _pos(out, 1100, -100)

    # Window COMP for perform mode (F1)
    win = root.create(windowCOMP, "window1")
    _set(win, ["winop", "operator"], out.path)
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

    print("  [9/9] Output + Window COMP")

    # =====================================================================
    # DONE
    # =====================================================================
    print("")
    print("=" * 60)
    print("  Morphora 3D Network Successfully Built!")
    print("=" * 60)
    print("")
    print("  ✓ OSC In on port 7000")
    print("  ✓ State handler maps /gesture/state → Switch SOP blend")
    print("  ✓ 10,000-point Butterfly (Cyan)")
    print("  ✓ 10,000-point Dragon (Red)")
    print("  ✓ 10,000-point Lily (Pink)")
    print("  ✓ constantMAT with vertex colors")
    print("  ✓ Wireframe cube with scale animation")
    print("  ✓ Camera + 2 Lights")
    print("  ✓ Render + Bloom → out1")
    print("  ✓ Window COMP for Perform Mode")
    print("")
    print("  NEXT STEPS:")
    print("  1. Press F1 to enter Perform Mode")
    print("  2. Run: python main.py (or simulate_gestures.py)")
    print("  3. File → Save as touchdesigner/main.toe")
    print("")
    print("  VERIFICATION:")
    print("  - You should see CYAN particles (butterfly) on screen")
    print("  - Check osc_in CHOP for incoming channels")
    print("  - Run simulate_gestures.py to test morphing")
    print("=" * 60)


build()
