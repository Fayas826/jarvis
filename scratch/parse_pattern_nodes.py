import os
import re
import json

touch_file = r'c:\jarvis AI\jarvis\scratch\touch_events_live.txt'
config_file = r'c:\jarvis AI\jarvis\data\mobile_security_config.json'

points = []
with open(touch_file, 'r', encoding='utf-8', errors='ignore') as f:
    cur_x, cur_y = None, None
    for line in f:
        if 'ABS_MT_POSITION_X' in line:
            m = re.search(r'ABS_MT_POSITION_X\s+([0-9a-fA-F]+)', line)
            if m: cur_x = int(m.group(1), 16)
        elif 'ABS_MT_POSITION_Y' in line:
            m = re.search(r'ABS_MT_POSITION_Y\s+([0-9a-fA-F]+)', line)
            if m: cur_y = int(m.group(1), 16)
        if cur_x is not None and cur_y is not None:
            # Convert raw driver coordinates to 1080x2400 screen pixels
            px = int(cur_x / 10.0)
            py = int(cur_y / 10.0)
            points.append((px, py))
            cur_x, cur_y = None, None

# 3x3 Grid centroids (px)
grid = {
    1: (270, 1100), 2: (540, 1100), 3: (810, 1100),
    4: (270, 1370), 5: (540, 1370), 6: (810, 1370),
    7: (270, 1640), 8: (540, 1640), 9: (810, 1640)
}

def get_closest_node(x, y):
    best_node = None
    min_dist = 999999
    for node, (nx, ny) in grid.items():
        dist = (x - nx)**2 + (y - ny)**2
        if dist < min_dist:
            min_dist = dist
            best_node = node
    # Only return node if within 180px threshold
    if min_dist < 180**2:
        return best_node
    return None

sequence = []
for p in points:
    node = get_closest_node(p[0], p[1])
    if node is not None:
        if not sequence or sequence[-1] != node:
            sequence.append(node)

print(f"EXTRACTED PATTERN LOCK SEQUENCE FROM KERNEL GESTURE: {sequence}")

if sequence:
    # Update mobile_security_config.json with exact recorded pattern
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    cfg["pattern_sequence"] = sequence
    cfg["auto_unlock_enabled"] = True
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
    print(f"SUCCESSFULLY SAVED PATTERN SEQUENCE {sequence} TO DATABASE!")
