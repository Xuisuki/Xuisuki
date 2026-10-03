# Artwork sources

- `gojo-3d.png` — stylized Satoru Gojo render created with OpenAI's built-in image generation tool; original transparent PNG. Generation prompt: `gojo-prompt.txt`.
- `pxost-original.svg` — pxost's existing project mark, used without changing its geometry.
- `plazma-original.svg` — original Plazma Kino logo from its public site, https://plazmazerkalo.fun/.
- `krypta-original.jpg` — original public Krypta bot avatar, https://t.me/KryptaVpn_Robot.
- Language and technology marks — canonical Simple Icons paths and brand colors stored in `tools/icons.json` (CC0).

The composition, typography, light field, depth layers, and CSS animation are built in `tools/build.py`. Each published SVG embeds its own bitmap assets; no external resource or script is required. Reduced-motion preferences disable animation. Compact compositions serve narrow viewports through `<picture>`.
