# -*- coding: utf-8 -*-
"""
渲染质检器（WP-A，设计稿 docs/渲染质检工具-设计.md §2）
一键对全部（或指定）--genre 渲染并做可编程布局质检（4 维度），输出"款 × 问题"报告。
不依赖截图尺寸（纯布局量测，画布边界从渲染 DOM 实测）。

用法（cwd 任意，脚本内部定位 scripts/）：
  python scripts/validate_quality.py --all  --photo D:/cover-plan/_t.jpg --out report.md
  python scripts/validate_quality.py --genre blue_note --genre film --photo <p> --out r.md
  --photo 支持 nargs='+' 多张对照样图（对比条目按样图分组，评审 #6）
"""
import argparse
import html as _html
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
CHROME = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
ENGINE = 'engine_v2.py'

# ---- 白名单（设计 §2.3）----
# 条目 = 维度token 或 维度token@限定；限定 vertical-rl 匹配 computed writingMode（评审 #4）
WHITELIST = {
    'layered':          ['offcanvas', 'scrollW'],   # left_giant 巨字有意出血压边（设计语言）
    'deep_interlock':   ['offcanvas', 'scrollW', 'contrast'],  # 咬合巨字压深底为设计延展（val 58 边缘，实测确认）
    'declassified_file': ['scrollW', 'contrast'],    # 档案涂黑块 val=0（遮盖语义）+ 章面 ARCHIVE 边缘项
    'zen':              ['scrollW@vertical-rl', 'contrast@vertical-rl'],  # 竖排：印章/注脚小字压暗章底为设计语义
    'slender_zen':      ['scrollW@vertical-rl', 'contrast@vertical-rl'],
    'stone':            ['scrollW@vertical-rl', 'contrast@vertical-rl'],
    # super_index（设计语言族）：照片右下白 mono 注脚（date · VOL.001）压亮调照片为设计语义
    # （探针定稿 §1.5；text-shadow 0 1px 8px 保读、目测可读；对比回退命中照片下采样白砖区，
    # 口径同 oriental_zhuokai 先例〔该款 2026-09-14 微调批2 用户拍板彻底删除；先例语义保留〕
    # ——豁免注明理由，2026-09-06 §5-5 新款零✗ 门槛）。
    'super_index':      ['contrast'],
    # ~~oriental_zhuokai~~（字体驱动款，骨架 oriental_plain_paper）2026-09-14 微调批2 用户拍板
    # 彻底删除 → 其死豁免条目（原 ['contrast@vertical-rl']）随之删除（款不存在则豁免无对象）。
    # 豁免先例口径仍为 zen/slender_zen/stone 竖排先例（2026-09-05 §2.4#2 新款零✗ 门槛）。
    # torn_journal（设计语言族第 14 款，2026-09-09）：①照片白竖排短语（思い出を、ここに。）
    # 压照片右缘=拼贴语义（text-shadow 保读、目测可读；对比回退命中照片右缘浅色区），
    # 豁免口径同 oriental_zhuokai contrast@vertical-rl 先例〔该款 2026-09-14 微调批2 已彻底删除，
    # 先例语义保留〕；②go! 白字压蓝椭圆徽章：
    # 质检器 _bgLumaAt 背景回退命中撕纸纸色(247)而非徽章填充(161 实测，diff≈94 实际过关)，
    # 伪影豁免。新款零✗ 门槛（2026-09-06 §5-5）。
    'torn_journal':     ['contrast@vertical-rl', 'contrast'],
    # torn_peephole（设计语言族第 16 款，2026-09-10）：主标/副标/揭语白字（#fdf8ec）压牛皮纸
    # 封面 = 探针定稿的有意设计（用户目视验收 + text-shadow 保读）。本条 ✗ 为质检器伪影：
    # 可见底色是 SVG 渐变填充（url(#tpg) 的 <path>），非可采样的 DOM background-color →
    # _bgLumaAt 回退命中 stage 底色 #e9e2cf（luma 226，bgSrc 记「渐变下层主色」）→ diff=22。
    # 实测可见底色 = 牛皮纸渐变三停 #bc9f72/#ab8c5e/#97794d（luma 162.5/144.0/124.9），
    # 与 ink 248 的 diff = 85.5/104.1/123.2 全部 > 60 阈值，实际过关。
    # 豁免口径同 torn_journal contrast / 2026-09-05 §2.4#2 新款零✗ 门槛。
    'torn_peephole':    ['contrast'],
}
# token 词表：scrollW=维度1横向溢出 / offcanvas=维度1越界 / overlap=维度3 / contrast=维度4
TOKEN_GLOSSARY = ('token 词表: scrollW=维度1横向溢出(scrollWidth>clientWidth) | '
                  'offcanvas=维度1越界(rect超画布) | overlap=维度3文字互叠 | contrast=维度4对比不足')

# ---- 检测 JS（注入 </body> 前；设计 §2.2）----
# 关键：document.fonts.ready 后才量测（评审 #2：@font-face 未加载按回退字体量测会误判）；
# virtual-time-budget 会推进虚拟时间等异步完成后 dump-dom 才捕获。
_DETECT_JS_TEMPLATE = r'''<script>
(function(){
  function _luma(col){ // 与 type_guard.luma 同公式 0.299/0.587/0.114，支持 #rgb #rrggbb rgb() rgba()
    if(!col) return null;
    var m;
    if((m = col.match(/^#([0-9a-f]{3})$/i))){ var h=m[1];
      return 0.299*parseInt(h[0]+h[0],16)+0.587*parseInt(h[1]+h[1],16)+0.114*parseInt(h[2]+h[2],16); }
    if((m = col.match(/^#([0-9a-f]{6})$/i))){ var h=m[1];
      return 0.299*parseInt(h.slice(0,2),16)+0.587*parseInt(h.slice(2,4),16)+0.114*parseInt(h.slice(4,6),16); }
    if((m = col.match(/^rgba?\(([^)]+)\)$/i))){
      var p = m[1].split(',').map(function(s){return parseFloat(s)});
      var a = (p.length>3 && p[3]===0) ? 0 : (p.length>3 ? p[3] : 1);
      if(a===0) return null;
      return 0.299*p[0]+0.587*p[1]+0.114*p[2];
    }
    return null;
  }
  function _hitStack(cx, cy){ // elementsFromPoint 受视口裁剪（headless 视口≈window-size-95px，
    // 越界点位返回空数组——music 落款 y=1256>1255 实证）。回退：DOM 几何命中（覆盖该点且 z 序最高的非文字元素链）。
    var direct = [];
    try { direct = document.elementsFromPoint(cx, cy); } catch(e){}
    if(direct && direct.length>0) return direct;
    var hits = [];
    document.querySelectorAll('div,section,img,span,p,h1,h2,h3,h4,td,th,footer,header').forEach(function(e){
      var r = e.getBoundingClientRect();
      if(cx>=r.left && cx<=r.right && cy>=r.top && cy<=r.bottom) hits.push(e);
    });
    hits.sort(function(a,b){
      var za = parseInt(getComputedStyle(a).zIndex)||0, zb = parseInt(getComputedStyle(b).zIndex)||0;
      if(za!==zb) return zb-za;
      return b.querySelectorAll('*').length - a.querySelectorAll('*').length; // 深的在上
    });
    return hits;
  }
  function _bgLumaAt(el, cx, cy, bgFallback){ // 评审 #5 算法：先自身背景，再命中栈上溯（混色/渐变规则见下）
    // 0) 文字元素自身有背景色时，它就是落点背景（铭牌/色带字），必须先查（否则穿透到照片误报）
    var selfSt = getComputedStyle(el);
    var selfL = _luma(selfSt.backgroundColor);
    if(selfL !== null) return {v:selfL, src:'self-bg'};
    var stack;
    try { stack = _hitStack(cx, cy); } catch(e){ stack = [el]; }
    var _trace = (window.__VQ_TRACE__ ? stack.slice(0,4).map(function(e){
      var s=getComputedStyle(e);
      return e.tagName+'.'+String(e.className).slice(0,10)+'|'+s.backgroundColor.slice(0,24)+'|'+(s.backgroundImage==='none'?'no-grad':'grad');
    }).join(' / ') : null);
    for (var i=0;i<stack.length;i++){
      var e = stack[i];
      var isText = (e.childNodes.length>0 && [].some.call(e.childNodes,function(n){return n.nodeType===3 && n.textContent.trim();}));
      if(isText) continue;
      var st = getComputedStyle(e);
      var l = _luma(st.backgroundColor);
      if(l!==null){
        // 有底色：若同时有渐变图层，backgroundColor 仍以 alpha 混入渐变之上——v1 近似取底色（纹饰多为 ≤6% 透明度细线，影响小）
        return {v:l, src: 'bg:'+e.tagName + (st.backgroundImage!=='none' ? '(带渐变,取底色近似)' : '')};
      }
      // backgroundColor 透明：若有渐变图层，该层可能是"纹理/谱线"（主色=下层卡纸）或"整幅色带"（主色=渐变自身）。
      // v1 策略：**继续沿栈向下**找第一个不透明纯色 backgroundColor 作为主色近似；一路到底全透明才交照片回退。
      // （谱线纸/纹饰线 → 命中下层卡纸 ✓；蓝图整幅渐变色带 → 下层 stage 也透明 → 照片回退 ✓）
      if(st.backgroundImage && st.backgroundImage!=='none'){
        for (var k=i+1;k<stack.length;k++){
          var e2=stack[k];
          var isText2 = (e2.childNodes.length>0 && [].some.call(e2.childNodes,function(n){return n.nodeType===3 && n.textContent.trim();}));
          if(isText2) continue;
          var s2=getComputedStyle(e2);
          var l2=_luma(s2.backgroundColor);
          if(l2!==null) return {v:l2, src:'bg:'+e2.tagName+'(渐变下层主色)', trace:_trace};
        }
        return {v: null, src: '图层/渐变', trace:_trace};
      }
    }
    if (bgFallback && bgFallback.top!==undefined) return {v: null, src: '照片', trace:_trace};
    return {v: null, src: '未知', trace:_trace};
  }
  window.__ERRS__=[];
  window.onerror=function(m){ window.__ERRS__.push(String(m).slice(0,80)); };
  function _isTextNode(el){
    return el && el.childNodes && [].some.call(el.childNodes, function(n){ return n.nodeType===3 && n.textContent.trim(); });
  }
  function _isDecor(el){ // 装饰件祖先链（印章/铭牌等：rotate 或 box-shadow 容器内）——有意叠于文字上的设计件
    var e = el;
    var depth = 0;
    while(e && e !== document.body && depth < 8){
      var st = getComputedStyle(e);
      if(st.transform && st.transform !== 'none') return true;
      if(st.boxShadow && st.boxShadow !== 'none' && e.children.length>0) return true;
      e = e.parentElement; depth++;
    }
    return false;
  }
  function measure(){
    var stage = document.querySelector('.stage');
    var W, H;
    if(stage){ var r = stage.getBoundingClientRect(); W=r.width; H=r.height; }
    else { W=document.documentElement.clientWidth; H=document.documentElement.clientHeight; }
    var bgFallback = window.__BG_LUMA__ || {};
    var texts = [];
    document.querySelectorAll('div,span,p,h1,h2,h3,h4,h5,li,figcaption,footer,header,td,th,button,a').forEach(function(el){
      if(_isTextNode(el)){
        var t=(el.textContent||'').trim(); if(!t) return;
        var r=el.getBoundingClientRect();
        if(r.width<1 && r.height<1) return;
        texts.push({el:el, text:t, rect:r});
      }
    });
    var bad=[];
    // 维度1+2：逐文字元素
    texts.forEach(function(it){
      var el=it.el, r=it.rect;
      var st=getComputedStyle(el);
      var wm = st.writingMode || 'horizontal-tb';
      var why=[], sw=el.scrollWidth, cw=el.clientWidth, sh=el.scrollHeight, ch=el.clientHeight;
      var isVertical = wm.indexOf('vertical')===0;
      // font_guard 兜底 span（style 含 font-family:'思源宋体'）：逐字 span 拆散标题文本节点，
      // 其水平位置由父级流式布局决定，单独量测 center/offcanvas 均为伪影（2026-09-05 §2.2）——跳过。
      var isFbSpan = (el.tagName==='SPAN' && (st.fontFamily||'').indexOf('思源宋体')>=0);
      // 逐字装饰 span（style 内联 transform:rotate —— torn_journal 主标逐字微旋转）：
      // 每字 span 自身中心 vs 父容器中心必然偏移（逐字排布+旋转是对齐手段非居中信号），
      // 单独量测 center 为伪影（同 isFbSpan 豁免口径，2026-09-09）。
      var isRotSpan = (el.tagName==='SPAN' && (el.getAttribute('style')||'').indexOf('rotate(')>=0
                       && (el.getAttribute('style')||'').indexOf('transform')>=0);
      if(!isFbSpan && !isRotSpan && !isVertical && sw>cw+3) why.push('scrollW');
      if(!isFbSpan && !isRotSpan && (r.left<-2 || r.top<-2 || r.right>W+2 || r.bottom>H+2)) why.push('offcanvas');
      if(isVertical && sh>ch+3) why.push('scrollH-vertical');
      // 维度2：text-align:center 的文字块（含祖先声明）中心 vs 容器中心
      if(!isFbSpan && !isRotSpan) {
      var ta = st.textAlign;
      if(ta==='center'){
        var cont = el.parentElement;
        var pd = getComputedStyle(cont||el);
        var flexLayout = cont && ((getComputedStyle(cont).display==='flex') || (getComputedStyle(cont).display==='inline-flex'));
        if(cont && !flexLayout){ // flex 均分行内的 span 自带 text-align:center 是对齐手段，非居中偏移信号
          // position:absolute 定位盒（torn_journal 气泡/go! 文字）：位置由 top/left/right 决定，
          // 父中心比较无意义（同 flex 排除 spirit，2026-09-09）。
          var posAbs = (st.position==='absolute');
          if(!posAbs){
          var cr = cont.getBoundingClientRect();
          var off = Math.abs((r.left+r.right)/2 - (cr.left+cr.right)/2);
          if(off > 0.02*W) { bad.push({why:'center', text:it.text.replace(/\s+/g,' ').slice(0,26),
            r:[Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)],
            val: Math.round(off), container:[Math.round(cr.left),Math.round(cr.width)], wm:wm}); }
          }
        }
      }
      } // end !isFbSpan
      if(why.length){
        bad.push({why:why.join('+'), text:it.text.replace(/\s+/g,' ').slice(0,26),
          sw:sw, cw:cw, wm:wm});
      }
      // 维度4：对比（颜色 vs 落点背景 luma；元素 opacity 计入 ink 有效亮度）
      var ink = _luma(st.color);
      if(ink!==null){
        var op = parseFloat(st.opacity); if(isNaN(op)) op=1;
        if(op < 1){ // 有效墨色 = 字色向背景亮度混合（近似：向分区背景亮度收敛）
          var approxBg = (function(){
            var fb = bgFallback && bgFallback.top!==undefined ? bgFallback : {top:128,bottom:128};
            var cyRatio = (r.top+r.height/2)/H; return cyRatio<0.5?fb.top:fb.bottom;
          })();
          ink = ink*op + approxBg*(1-op);
        }
        var bg = _bgLumaAt(el, r.left+r.width/2, r.top+r.height/2, bgFallback);
        var bgv = bg.v;
        var _dbg = null;
        try {
          var _stack = document.elementsFromPoint(r.left+r.width/2, r.top+r.height/2);
          _dbg = _stack.slice(0,4).map(function(e){var s=getComputedStyle(e);
            return e.tagName+'.'+String(e.className).slice(0,10)+'|bg='+s.backgroundColor.slice(0,22);}).join(' / ');
        } catch(e2){}
        if(bgv===null && bg.src==='照片' && bgFallback.top!==undefined){
          // 照片背景：按元素中心 y 落顶/底半区取分区亮度
          var cyRatio = (r.top+r.height/2) / H;
          bgv = (cyRatio < 0.5) ? bgFallback.top : bgFallback.bottom;
          bg.src += '(top=' + Math.round(bgFallback.top) + ',bottom=' + Math.round(bgFallback.bottom) + ')';
        }
        if(bgv!==null){
          var diff = Math.abs(ink - bgv);
          if(diff < 60){
            bad.push({why:'contrast', text:it.text.replace(/\s+/g,' ').slice(0,26),
              r:[Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)],
              val: Math.round(diff), ink: Math.round(ink), bg: Math.round(bgv), bgSrc: bg.src, wm:wm, dbg:(bg.trace||_dbg)});
          }
        }
      }
    });
    // 维度3：两两文字元素 bbox 相交 >15% 较小者（父子/同父豁免）
    for (var i=0;i<texts.length;i++){
      for (var j=i+1;j<texts.length;j++){
        var a=texts[i], b=texts[j];
        if(a.el.contains(b.el) || b.el.contains(a.el)) continue; // 父子豁免
        if(a.el.parentElement && a.el.parentElement===b.el.parentElement) continue; // 同父豁免
        if(_isDecor(a.el) || _isDecor(b.el)) continue; // 装饰件豁免（印章/铭牌有意叠于文字，评审 #7 同类）
        var ra=a.rect, rb=b.rect;
        var ix = Math.max(0, Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left));
        var iy = Math.max(0, Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top));
        if(ix<=0||iy<=0) continue;
        var inter = ix*iy;
        var aArea=(ra.width*ra.height), bArea=(rb.width*rb.height);
        var small=Math.max(1, Math.min(aArea,bArea));
        if(inter/small > 0.15){
          bad.push({why:'overlap', text:(a.text.replace(/\s+/g,' ').slice(0,14)+' × '+b.text.replace(/\s+/g,' ').slice(0,14)),
            r:[Math.round(Math.max(ra.left,rb.left)),Math.round(Math.max(ra.top,rb.top)),
               Math.round(Math.min(ra.right,rb.right)),Math.round(Math.min(ra.bottom,rb.bottom))],
            val: Math.round(inter/small*100), wm:'-'});
        }
      }
    }
    var d=document.createElement('div'); d.id='OVF'; d.setAttribute('data-ovf','1');
    d.textContent='OVF::'+JSON.stringify(bad.concat(window.__ERRS__||[]).map(function(x){return typeof x==='string'?{why:'JSERR',text:x}:x;})); document.body.appendChild(d);
  }
  if(document.fonts && document.fonts.ready && document.fonts.ready.then){
    // 评审 #2：等字体就绪；实测还需再留 layout/合成层就绪时间（50ms 时 elementsFromPoint 返回空数组，
    // 探针 300-400ms 正常）——fonts.ready 后统一 400ms，virtual-time-budget=6000 内可完成
    document.fonts.ready.then(function(){ setTimeout(measure, 400); });
  } else { setTimeout(measure, 600); }
})();
</script>
</body>'''


def _photo_zone_luma(photo):
    """Python 侧预计算样图 top/bottom 分区亮度（注入为 JS 常量）。复用 analyze_pixel.measure（其
    brightness 为上/下三分之一平均亮度，与引擎 _bg_luma_for 同源），失败回退 PIL 同口径。"""
    try:
        sys.path.insert(0, SCRIPTS)
        import analyze_pixel
        fn = getattr(analyze_pixel, 'measure', None)
        if fn:
            res = fn(photo)
            b = res.get('brightness') or {}
            return {'top': float(b.get('top')), 'bottom': float(b.get('bottom'))}
    except Exception:
        pass
    # 回退：PIL 同口径（上/下二分之一平均亮度——与 analyze_pixel 三分之一口径略差，仅兜底）
    try:
        from PIL import Image
        im = Image.open(photo).convert('L')
        w, h = im.size
        top = im.crop((0, 0, w, h // 2)).resize((1, 1)).getpixel((0, 0))
        bot = im.crop((0, h // 2, w, h)).resize((1, 1)).getpixel((0, 0))
        return {'top': float(top), 'bottom': float(bot)}
    except Exception:
        return None


def _genres():
    """engine_v2.py 是唯一 CLI 入口，--genre 路由全部 60 款（2026-09-07 +彩活四款、
    2026-09-10 +撕纸两款、2026-09-14 −fashion_vogue、2026-09-14 微调批2 −5 款、
    2026-09-15 +新款入库批两款后计数链：13 引擎
    + 13 装裱 + 2 别名 + 7 载体 + 6 蓝图 + 19 设计语言）。
    直接 import 引擎常量取 choices（engine_v2 导入无 CLI 副作用，main 有 __main__ 守卫）。"""
    sys.path.insert(0, SCRIPTS)
    import engine_v2 as ev
    return (list(ev.GENRE.keys()) + list(ev.MATTING_IDS) + list(ev.MATTING_ALIAS)
            + list(ev.METAPHOR_IDS) + list(ev.BLUEPRINT_IDS) + list(ev.DESIGN_IDS))


def run_genre(genre, photos, outdir):
    """渲染一个 genre（多张样图各渲一份），返回 {photo: dump_dom_str} 与错误信息。"""
    results, err = {}, None
    for pi, photo in enumerate(photos):
        tag = os.path.splitext(os.path.basename(photo))[0]
        html_path = os.path.join(outdir, f'_vq_{genre}_{pi}_{tag}.html')
        cmd = ['python', ENGINE, '--photo', photo, '--genre', genre,
               '--title', '湖心塔影', '--sub', '夜西湖', '--date', '2026',
               '--location', 'HANGZHOU', '--lens', '35MM', '--out', html_path]
        try:
            r = subprocess.run(cmd, cwd=SCRIPTS, capture_output=True, timeout=60)
            if r.returncode != 0:
                err = f'engine rc={r.returncode} {r.stderr.decode("utf-8", "replace")[-200:]}'
                continue
        except Exception as e:
            err = f'engine ex={e}'
            continue
        dom = _detect(html_path, photo)
        if dom is not None:
            results[photo] = dom
    return results, err, html_path


def _font_fallback_from_html(html_path):
    """解析引擎写进 html 的 font_guard 注释（2026-09-05 §2.2 接入点 B）。
    返回 (fallback_chars, uncoverable_chars)：
      fallback_chars     —— 兜底字符列表（[font-coverage] 提示行，只提示不计 ✗）
      uncoverable_chars  —— 兜底字体也缺的字符（升格 ✗ 条目）
    无注释/读不到 → ([], [])。"""
    try:
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
    except OSError:
        return [], []
    import re as _re
    m = _re.search(r'<!--\s*font-fallback(-segment)?:\s*([^>]*?)\s*-->', html)
    fb = []
    if m:
        raw = m.group(2).split('|')[0].strip()  # segment 版含 coverage 统计尾巴，只取字符段
        fb = [c for c in raw if not c.isspace() and c != ',']
    m2 = _re.search(r'<!--\s*font-uncoverable:\s*([^>]*?)\s*-->', html)
    unc = [c for c in (m2.group(1).strip() if m2 else '') if not c.isspace() and c != ','] if m2 else []
    return fb, unc


def _detect(html_path, photo):
    """注入检测 JS → chrome dump-dom → 抽取 OVF JSON（失败返回 None）。"""
    html = open(html_path, encoding='utf-8').read()
    bg = _photo_zone_luma(photo)
    bg_js = json.dumps(bg) if bg else '{}'
    inject = f'<script>window.__BG_LUMA__={bg_js};</script>' + _DETECT_JS_TEMPLATE
    if '</body>' in html:
        html = html.replace('</body>', inject)
    else:
        html += inject
    tmp = html_path.replace('.html', '_detect.html')
    open(tmp, 'w', encoding='utf-8').write(html)
    if os.environ.get('VQ_KEEP_TMP'):
        print(f'  [tmp kept] {tmp}')
    # 视口尺寸必须匹配画布（教训：dump-dom 默认 800×600，超出视口的点位 elementsFromPoint 返回空数组
    # → 背景检测穿透到照片回退 → 装裱族等低 y 位文字误报）。从 html 读 WxH，与截图管线同规则。
    m_size = re.search(r'html,body\{width:(\d+)px;height:(\d+)px', html)
    vw, vh = (int(m_size.group(1)), int(m_size.group(2))) if m_size else (1280, 1600)
    try:
        r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            '--allow-file-access-from-files',
                            '--window-size=%d,%d' % (vw, vh),
                            '--virtual-time-budget=6000',
                            '--dump-dom', 'file:///' + tmp.replace('\\', '/')],
                           capture_output=True, timeout=60)
        dom = r.stdout.decode('utf-8', 'replace')
    except Exception as e:
        print(f'  [chrome ex] {e}')
        return None
    finally:
        if not os.environ.get('VQ_KEEP_TMP'):
            try: os.remove(tmp)
            except OSError: pass
    m = re.search(r'<div id="OVF" data-ovf="1">OVF::(.*?)</div>', dom, re.S)
    if os.environ.get('VQ_KEEP_TMP') and m:
        raw = _html.unescape(m.group(1))
        print('  [OVF RAW]', raw[:500])
    if not m:
        return None
    try:
        return json.loads(_html.unescape(m.group(1)).strip())
    except Exception as e:
        print(f'  [ovf parse ex] {e}')
        return None


def _exempt(genre, item):
    """白名单匹配（设计 §2.3）：token 相同，且若带 @限定则限定匹配 writingMode。"""
    rules = WHITELIST.get(genre, [])
    for rule in rules:
        if '@' in rule:
            tok, qual = rule.split('@', 1)
            if item.get('why', '').startswith(tok):
                wm = item.get('wm', '') or ''
                if wm.startswith(qual):
                    return True
        else:
            if item.get('why', '').startswith(rule):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description='渲染质检器（WP-A）')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--all', action='store_true', help='全部 60 款（13 引擎+13 装裱+2 别名+7 载体+6 蓝图+19 设计语言）')
    g.add_argument('--genre', action='append', help='指定款（可多次）')
    ap.add_argument('--photo', nargs='+', default=['D:/cover-plan/_t.jpg'],
                    help='样图（可多张对照，对比条目按样图分组）')
    ap.add_argument('--out', default=None, help='报告输出路径（缺省打印）')
    args = ap.parse_args()

    genres = _genres() if args.all else args.genre
    if not genres:
        print('未取得 genre 列表'); sys.exit(1)
    outdir = os.path.join(ROOT, 'examples', '_vq')
    os.makedirs(outdir, exist_ok=True)
    photos = args.photo

    report = [f'# 渲染质检报告（WP-A validate_quality.py）',
              f'',
              f'- 样图：{", ".join(photos)}',
              f'- 款数：{len(genres)}',
              f'- {TOKEN_GLOSSARY}',
              f'- 判定语义：对比条目(diff<60)计入该款 ✗；SKIP(设计豁免)不计入。',
              f'- 生成时间：__TIMESTAMP__',
              f'']
    pass_n = fail_n = 0
    for gi, genre in enumerate(genres):
        line = f'## {genre}'
        all_items = []
        errs = []
        font_fb_chars, font_unc_chars = [], []
        for photo in photos:
            results, err, html_path = run_genre(genre, [photo], outdir)
            if err:
                errs.append(err)
            # [font-coverage] 新维度（§2.2 接入点 B）：解析引擎兜底注释；
            # 兜底=提示行（不计 ✗）；兜底字体也缺字=升格 ✗ 条目（why='font-uncoverable'）。
            fb, unc = _font_fallback_from_html(html_path)
            if fb or unc:
                font_fb_chars.extend(fb)
                font_unc_chars.extend(unc)
            items = results.get(photo, None)
            if items is None:
                errs.append('chrome/dump 未捕获 OVF')
                continue
            kept, skipped = [], 0
            for it in items:
                if _exempt(genre, it):
                    skipped += 1
                else:
                    kept.append(it)
            if skipped:
                all_items.append(('SKIP', skipped, photo))
            for it in kept:
                all_items.append(('FIND', it, photo))
        detail = []
        this_fail = False
        if font_fb_chars:
            chars = ' '.join('"%s"' % c for c in dict.fromkeys(font_fb_chars))
            detail.append(f'  - [font-coverage] 兜底字符（款字体缺字→思源宋兜底，只提示不计 ✗）: {chars}')
        if font_unc_chars:
            this_fail = True  # 兜底字体也缺字：升格 ✗（§2.2 v2.1，不静默）
            chars = ' '.join('"%s"' % c for c in dict.fromkeys(font_unc_chars))
            detail.append(f'  - [font-uncoverable] 兜底字体仍缺字（升格 ✗）: {chars}')
        for kind, payload, photo in all_items:
            if kind == 'SKIP':
                detail.append(f'  - SKIP(设计豁免) ×{payload} [{os.path.basename(photo)}]')
            else:
                this_fail = True
                it = payload
                detail.append(f'  - [{it["why"]}] "{it["text"]}" val={it.get("val")} '
                              f'r={it.get("r")} wm={it.get("wm")} ink={it.get("ink")} '
                              f'bg={it.get("bg")}({it.get("bgSrc")}) dbg={it.get("dbg")} [{os.path.basename(photo)}]')
        if errs:
            this_fail = True
            for e in errs:
                detail.append(f'  - ERROR: {e}')
        # [face-constraint] 款约束提示（2026-09-07 彩活四款，docs/批量设计-彩活四款-设计.md §3）：
        # collage_man 蛋窗构图只适合单人照/半身（多人照切脸）——质检器无像素人脸计数能力，
        # 标注人工核项（提醒"建议换款"），只提示不计 ✗（设计语义：不阻断渲染；
        # 未来若有人脸分割能力可升级为自动检测，本期不做——§6 风险）。
        if genre == 'collage_man':
            detail.append('  - [face-constraint] 单人照限定（蛋窗构图）：多脸合照请建议换款 '
                          '（duo_pop/doodle_summer 或护脸款）；人工核项，不计 ✗')
        verdict = '✓' if not this_fail else '✗'
        if this_fail: fail_n += 1
        else: pass_n += 1
        report.append(line + f'  → {verdict}')
        report.extend(detail if detail else ['  - （无问题条目）'])
    report.append('')
    report.append(f'## 统计：✓ {pass_n} / ✗ {fail_n} / 共 {len(genres)}')
    text = '\n'.join(report)
    import datetime
    text = text.replace('__TIMESTAMP__', datetime.datetime.now().isoformat(timespec='seconds'))
    if args.out:
        open(args.out, 'w', encoding='utf-8').write(text)
        print(f'报告 → {args.out}')
    print(text[-2500:] if args.out else text)


if __name__ == '__main__':
    main()
