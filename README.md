# Equalize Edge Lengths (Blender Add-on)

Make all **selected edges** the same length (average or custom) while preserving each edge’s direction.  
Adds an entry to **W (Context Menu)** and **Mesh → Edge**.

## Features
- Equalize to **Average** of selection or **Custom** length
- Option to **Preserve Midpoint** (keeps edge center in place)
- Works with scattered, non-loop edges
- Undo-safe, Blender 4.x+

## Install
1. `Blender → Edit → Preferences → Add-ons → Install…`
2. Select `addon_equalize_edge_lengths.py`
3. Enable the add-on

## Use
- Edit Mode → Edge select → pick edges  
- Press **W** → **Equalize Edge Lengths**  
- Adjust settings in the operator panel (F9)

## Notes
- Zero-length edges are skipped
- Intended for modeling utilities; does not change topology

## License
MIT
