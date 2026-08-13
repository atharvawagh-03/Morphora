# Script SOP — copy targetP from input 1 onto points of input 0
# Inputs: 0 = current cloud, 1 = target cloud

node = me
cur = node.inputs[0]
tgt = node.inputs[1]

if cur is None or tgt is None:
    return

nc = len(cur.points)
nt = len(tgt.points)
if nc != nt:
    debug(f"Morphora: point count mismatch {nc} vs {nt}")
    return

for i in range(nc):
    node.points[i].P = cur.points[i].P
    node.points[i].Cd = cur.points[i].Cd
    node.points[i].targetP = tgt.points[i].P
