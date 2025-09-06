import json, base64
from pathlib import Path
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dots Viewer", layout="wide")

# Load config and image
cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
img_path = Path(cfg.get("image_path", ""))
dots = cfg.get("dots", [])

img = Image.open(img_path)
w, h = img.size
buf = base64.b64encode(img_path.read_bytes()).decode("ascii")
dots_json = json.dumps(dots)

st.sidebar.success("Viewer mode: users can only view dots.\n\nTo change dots, edit config.json and redeploy.")
st.sidebar.write(f"Image: {img_path}  |  size: {w}×{h}")

html = f"""
<style>
  :root {{ --dot-size:16px; --dot:#0b5fff; --ring:#bcd2ff; --panel:#fff; --panel-border:#d0d7de; }}
  .stage {{ position:relative; width:100%; max-width:1100px; margin:0 auto; border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; background:#fff; aspect-ratio: {w}/{h}; }}
  .inner {{ position:absolute; inset:0; }}
  .bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:contain; display:block; }}
  .dot {{ position:absolute; width:var(--dot-size); height:var(--dot-size); margin-left:calc(var(--dot-size)/-2); margin-top:calc(var(--dot-size)/-2); background:var(--dot); border-radius:50%; box-shadow:0 0 0 6px var(--ring); cursor:pointer; }}
  .tooltip {{ position:absolute; max-width:320px; transform:translate(-50%,-130%); background:var(--panel); border:1px solid var(--panel-border); box-shadow:0 6px 24px rgba(0,0,0,.12); border-radius:10px; padding:10px 12px; font:14px/1.35 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; opacity:0; pointer-events:none; transition:opacity .12s ease; }}
  .tooltip.visible {{ opacity:1; }}
  .tooltip .title {{ font-weight:700; margin-bottom:4px; }}
  .legend {{ margin:8px 0 0 0; font:13px/1.3 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color:#444; }}
</style>
<div class="stage" id="stage">
  <div class="inner">
    <img class="bg" alt="diagram" src="data:image/png;base64,{buf}" />
    <div id="hotspots"></div>
    <div id="tip" class="tooltip" aria-hidden="true">
      <div class="title"></div>
      <div class="desc"></div>
    </div>
  </div>
</div>
<div class="legend">Hover or click dots to see details. (Viewer-only.)</div>
<script>
  const DOTS = {dots_json};
  const stage = document.getElementById('stage');
  const hotspots = document.getElementById('hotspots');
  const tip = document.getElementById('tip');
  const titleEl = tip.querySelector('.title');
  const descEl  = tip.querySelector('.desc');

  DOTS.forEach(d => {{
    const el = document.createElement('button');
    el.className = 'dot';
    el.style.left = d.x + '%';
    el.style.top  = d.y + '%';
    el.setAttribute('aria-label', d.title || 'dot');
    el.addEventListener('mouseenter', (e) => showTip(e.currentTarget, d));
    el.addEventListener('mouseleave', hideTip);
    el.addEventListener('click', (e) => showTip(e.currentTarget, d, true));
    hotspots.appendChild(el);
  }});

  function showTip(target, data, sticky=false) {{
    titleEl.textContent = data.title || '';
    descEl.textContent  = data.desc  || '';
    const r = target.getBoundingClientRect();
    const s = stage.getBoundingClientRect();
    tip.style.left = (r.left + r.width/2 - s.left) + 'px';
    tip.style.top  = (r.top - s.top) + 'px';
    tip.classList.add('visible');
    tip.setAttribute('aria-hidden', 'false');
    if (sticky) {{
      const close = (evt) => {{
        if (!tip.contains(evt.target) && evt.target !== target) {{
          hideTip(); window.removeEventListener('click', close);
        }}
      }};
      window.addEventListener('click', close);
    }}
  }}
  function hideTip() {{
    tip.classList.remove('visible');
    tip.setAttribute('aria-hidden', 'true');
  }}
</script>
"""
import streamlit.components.v1 as components
height_hint = int(1100 * (h / w)) + 120
components.html(html, height=height_hint, scrolling=False)
