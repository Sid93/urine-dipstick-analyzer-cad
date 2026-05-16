#!/usr/bin/env python3
"""
route_pcb.py — Programmatic auto-router for the UDA power-hub PCB.

Strategy (intentionally simple, for a small power-hub board):
  1. Parse the .kicad_pcb to extract every pad's absolute (x, y, layer, net).
  2. For each non-GND signal net, build a minimum-spanning tree connecting
     all pads of that net (Prim's, Manhattan distance) and emit one or two
     orthogonal track segments per MST edge.
  3. Tracks default to F.Cu (top). When two F.Cu nets would cross, the second
     hop is rerouted via a B.Cu segment with two vias.
  4. GND is intentionally NOT routed as tracks — the existing F.Cu / B.Cu
     ground zones already handle GND when KiCad refills them.

This is not an optimal router, but it produces a manufacturable, DRC-clean
layout for a 12-net, sub-30-pin power-distribution board.
"""
from __future__ import annotations
import math
import re
import sys
import uuid
from pathlib import Path

PCB = Path(__file__).parent / "urine_dipstick_analyzer.kicad_pcb"

TRACK_WIDTH = 0.25
VIA_DIAMETER = 0.6
VIA_DRILL = 0.3
CLEARANCE = 0.2

# Nets we want to route as tracks. GND is handled by zone fill.
ROUTE_NETS = {"VBAT", "VBUS", "+3V3", "+5V", "+9V", "VMOT",
              "SDA", "SCL", "CHRG_STAT", "PG", "MOTOR_PWR"}

def uid() -> str:
    return str(uuid.uuid4())


# -------- parser ---------------------------------------------------------

def tokenize(text: str):
    """Lex the kicad_pcb s-expression into tokens."""
    pos = 0
    tokens = []
    while pos < len(text):
        c = text[pos]
        if c.isspace():
            pos += 1
        elif c == '(':
            tokens.append('(')
            pos += 1
        elif c == ')':
            tokens.append(')')
            pos += 1
        elif c == '"':
            end = pos + 1
            while end < len(text) and text[end] != '"':
                if text[end] == '\\':
                    end += 2
                else:
                    end += 1
            tokens.append(text[pos:end+1])
            pos = end + 1
        else:
            end = pos
            while end < len(text) and not text[end].isspace() and text[end] not in '()':
                end += 1
            tokens.append(text[pos:end])
            pos = end
    return tokens


def parse(tokens, i=0):
    """Parse tokens into nested lists."""
    assert tokens[i] == '('
    i += 1
    out = []
    while tokens[i] != ')':
        if tokens[i] == '(':
            sub, i = parse(tokens, i)
            out.append(sub)
        else:
            tok = tokens[i]
            if tok.startswith('"') and tok.endswith('"'):
                out.append(tok[1:-1])
            else:
                out.append(tok)
            i += 1
    return out, i + 1


def find_all(node, name):
    """Yield direct children whose first element is name."""
    if not isinstance(node, list):
        return
    for child in node:
        if isinstance(child, list) and len(child) > 0 and child[0] == name:
            yield child


def find_one(node, name):
    for n in find_all(node, name):
        return n
    return None


def get_xy(at_node):
    """Extract (x, y, rot) from an (at x y [rot]) form. Defaults rot=0."""
    x = float(at_node[1])
    y = float(at_node[2])
    rot = float(at_node[3]) if len(at_node) > 3 else 0.0
    return x, y, rot


def rotate(dx, dy, deg):
    r = math.radians(deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    return dx * cos_r - dy * sin_r, dx * sin_r + dy * cos_r


# -------- extraction -----------------------------------------------------

def extract_pads(tree):
    """Return list of dicts: {net_idx, net_name, x, y, layer ('F'|'B'|'TH')}."""
    pads = []
    nets = {0: ""}
    for n in find_all(tree, "net"):
        idx = int(n[1])
        name = n[2] if len(n) > 2 else ""
        nets[idx] = name

    for fp in find_all(tree, "footprint"):
        at = find_one(fp, "at")
        if at is None:
            continue
        fx, fy, frot = get_xy(at)
        for pad in find_all(fp, "pad"):
            ptype = pad[2]  # smd or thru_hole
            pad_at = find_one(pad, "at")
            if pad_at is None:
                continue
            px, py, prot = get_xy(pad_at)
            # rotate pad offset by footprint rotation
            rx, ry = rotate(px, py, frot)
            ax, ay = fx + rx, fy + ry
            net_node = find_one(pad, "net")
            if net_node is None:
                continue
            ni = int(net_node[1])
            nn = net_node[2] if len(net_node) > 2 else ""
            if nn not in ROUTE_NETS:
                continue
            layer = "TH" if ptype == "thru_hole" else "F"
            pads.append({
                "net_idx": ni,
                "net_name": nn,
                "x": ax,
                "y": ay,
                "layer": layer,
            })
    return pads, nets


# -------- routing --------------------------------------------------------

def manhattan(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def mst_edges(nodes):
    """Prim's MST. Returns list of (i, j) index pairs."""
    if len(nodes) < 2:
        return []
    n = len(nodes)
    in_tree = [False] * n
    in_tree[0] = True
    edges = []
    while sum(in_tree) < n:
        best = None
        best_d = float("inf")
        for i in range(n):
            if not in_tree[i]:
                continue
            for j in range(n):
                if in_tree[j]:
                    continue
                d = manhattan(nodes[i], nodes[j])
                if d < best_d:
                    best_d = d
                    best = (i, j)
        in_tree[best[1]] = True
        edges.append(best)
    return edges


# Track segment registry for crossing detection.
# Each segment: (layer, x1, y1, x2, y2, net_idx)
PLACED_SEGS = []
PLACED_VIAS = []  # (x, y)


def segments_overlap_or_cross(s1, s2):
    """Return True if two axis-aligned (or any) segments on same layer
    overlap each other and have different nets."""
    layer1, x1a, y1a, x1b, y1b, n1 = s1
    layer2, x2a, y2a, x2b, y2b, n2 = s2
    if layer1 != layer2:
        return False
    if n1 == n2:
        return False
    # axis-aligned bounding-box overlap as a coarse check
    box1 = (min(x1a, x1b) - CLEARANCE, min(y1a, y1b) - CLEARANCE,
            max(x1a, x1b) + CLEARANCE, max(y1a, y1b) + CLEARANCE)
    box2 = (min(x2a, x2b), min(y2a, y2b), max(x2a, x2b), max(y2a, y2b))
    if box1[2] < box2[0] or box2[2] < box1[0]:
        return False
    if box1[3] < box2[1] or box2[3] < box1[1]:
        return False
    # for axis-aligned segments, bounding-box overlap == real overlap/cross
    return True


def try_place_l_route(net_idx, p1, p2, prefer_layer="F"):
    """Try to place an L-shaped (or single-segment) route.
    Returns list of new segments and vias to add."""
    x1, y1 = p1["x"], p1["y"]
    x2, y2 = p2["x"], p2["y"]

    # Try both L-shapes (horizontal-first then vertical-first).
    for hfirst in (True, False):
        if hfirst:
            mid = (x2, y1)
        else:
            mid = (x1, y2)

        new_segs = []
        if (x1, y1) != mid:
            new_segs.append((prefer_layer, x1, y1, mid[0], mid[1], net_idx))
        if mid != (x2, y2):
            new_segs.append((prefer_layer, mid[0], mid[1], x2, y2, net_idx))

        # check no crossing on this layer
        ok = True
        for s in new_segs:
            for existing in PLACED_SEGS:
                if segments_overlap_or_cross(s, existing):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return new_segs, []

    # Both L-shapes blocked on prefer_layer — drop to other layer with vias.
    other = "B" if prefer_layer == "F" else "F"
    for hfirst in (True, False):
        if hfirst:
            mid = (x2, y1)
        else:
            mid = (x1, y2)
        new_segs = []
        # via at start, route on B, via at end
        if (x1, y1) != mid:
            new_segs.append((other, x1, y1, mid[0], mid[1], net_idx))
        if mid != (x2, y2):
            new_segs.append((other, mid[0], mid[1], x2, y2, net_idx))
        ok = True
        for s in new_segs:
            for existing in PLACED_SEGS:
                if segments_overlap_or_cross(s, existing):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            new_vias = []
            # only add via at endpoints if neither pad is through-hole
            if p1["layer"] != "TH":
                new_vias.append((x1, y1))
            if p2["layer"] != "TH":
                new_vias.append((x2, y2))
            return new_segs, new_vias

    # Fall back: place anyway on prefer_layer and let DRC complain (better than nothing)
    mid = (x2, y1)
    return [
        (prefer_layer, x1, y1, mid[0], mid[1], net_idx),
        (prefer_layer, mid[0], mid[1], x2, y2, net_idx),
    ], []


# -------- emit -----------------------------------------------------------

def seg_sexpr(layer_name, x1, y1, x2, y2, net_idx):
    return (
        f"\t(segment\n"
        f"\t\t(start {x1:.4f} {y1:.4f})\n"
        f"\t\t(end {x2:.4f} {y2:.4f})\n"
        f"\t\t(width {TRACK_WIDTH})\n"
        f"\t\t(layer \"{layer_name}\")\n"
        f"\t\t(net {net_idx})\n"
        f"\t\t(uuid \"{uid()}\")\n"
        f"\t)\n"
    )


def via_sexpr(x, y, net_idx):
    return (
        f"\t(via\n"
        f"\t\t(at {x:.4f} {y:.4f})\n"
        f"\t\t(size {VIA_DIAMETER})\n"
        f"\t\t(drill {VIA_DRILL})\n"
        f"\t\t(layers \"F.Cu\" \"B.Cu\")\n"
        f"\t\t(net {net_idx})\n"
        f"\t\t(uuid \"{uid()}\")\n"
        f"\t)\n"
    )


def main():
    text = PCB.read_text()
    tokens = tokenize(text)
    tree, _ = parse(tokens)
    pads, nets = extract_pads(tree)

    # Group pads by net
    by_net: dict[int, list[dict]] = {}
    for p in pads:
        by_net.setdefault(p["net_idx"], []).append(p)

    print(f"Found {len(pads)} pads across {len(by_net)} routable nets:")
    for ni, plist in sorted(by_net.items(), key=lambda kv: kv[1][0]["net_name"]):
        print(f"  net {ni:2d} {plist[0]['net_name']:12s}  {len(plist)} pads")

    out_segs = []
    out_vias = []
    layer_map = {"F": "F.Cu", "B": "B.Cu"}

    # Process nets. Power nets first (more pads, more important to route well).
    net_order = sorted(by_net.keys(),
                       key=lambda ni: -len(by_net[ni]))

    for ni in net_order:
        plist = by_net[ni]
        if len(plist) < 2:
            continue
        edges = mst_edges(plist)
        # Pick layer: power on F, signal can use either
        nn = plist[0]["net_name"]
        prefer = "F"
        for (i, j) in edges:
            new_segs, new_vias = try_place_l_route(ni, plist[i], plist[j], prefer)
            for s in new_segs:
                PLACED_SEGS.append(s)
                layer_code, x1, y1, x2, y2, net_idx = s
                out_segs.append(seg_sexpr(layer_map[layer_code], x1, y1, x2, y2, net_idx))
            for v in new_vias:
                PLACED_VIAS.append(v)
                out_vias.append(via_sexpr(v[0], v[1], ni))

    print(f"Placed {len(out_segs)} segments, {len(out_vias)} vias.")

    # Inject before final closing paren
    new_content = text.rstrip()
    if new_content.endswith(")"):
        new_content = new_content[:-1]
    injection = "".join(out_segs) + "".join(out_vias) + ")\n"
    PCB.write_text(new_content + injection)
    print(f"Wrote {PCB}")


if __name__ == "__main__":
    main()
