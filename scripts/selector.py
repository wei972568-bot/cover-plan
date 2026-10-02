#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 封面计划 · SKILL 选版式规则（位置先行版）
# 输入照片 → 优先按主体位置(h/v)选版式，占比/亮度作辅助。纯像素启发，多模态可替换。
import argparse

def _edge(v):
    return sum(abs(a-b) for a,b in zip(v,v[1:]))/len(v) if len(v)>1 else 0

def detect_subject(photo):
    """主体位置(h/v, 主判据) + 占比(辅助) + 亮度(暗调判断)。"""
    try:
        from PIL import Image
        im=Image.open(photo).convert('L').resize((32,32)); px=list(im.getdata())
        def cell(x0,x1,y0,y1):
            v=[px[y*32+x] for y in range(y0,y1) for x in range(x0,x1)]
            return sum(v)/len(v), _edge(v)
        TL=cell(0,16,0,16);TR=cell(16,32,0,16);BL=cell(0,16,16,32);BR=cell(16,32,16,32)
        def w(c): m,e=c; return e*(1+abs(m-128)/128)
        wl=w(TL)+w(BL);wr=w(TR)+w(BR);wt=w(TL)+w(TR);wb=w(BL)+w(BR)
        h='center'
        if wr>wl*1.18: h='right'
        elif wl>wr*1.18: h='left'
        v='center'
        if wb>wt*1.18: v='bottom'
        elif wt>wb*1.18: v='top'
        # 占比（辅助）：边缘强细胞占比，仅当明确≥2 象限强才判"占大"
        edges=[TL[1],TR[1],BL[1],BR[1]]; emax=max(edges)
        strong=sum(1 for e in edges if e>emax*0.6)
        ratio=strong/4.0
        mean=sum(px)/len(px)
        lum='dark' if mean<85 else ('bright' if mean>175 else 'mid')
        return {'h':h,'v':v,'ratio':round(ratio,2),'lum':lum}
    except Exception:
        return {'h':'center','v':'center','ratio':0.25,'lum':'mid'}

def select_genre(feat):
    """位置先行：先看主体位置(h/v)，亮度辅助，占比只作二次确认。"""
    h=feat['h']; v=feat['v']; ratio=feat['ratio']; lum=feat['lum']
    darkish = lum=='dark'
    # 暗调优先（暗调该配暗色大字）
    if darkish and h=='center':
        return 'nocturne', '暗调居中→时尚夜曲'
    # 主体偏右（左留白）→ 字偏左型
    if h=='right' and not darkish:
        return 'zen', '主体偏右+左留白→东方泼墨(字躲左)'
    # 主体偏左（右留白）→ 字偏右型
    if h=='left' and not darkish:
        return 'stone', '主体偏左+右留白→金石碑拓(字偏右)'
    # 主体上/下留白 → 天地夹字
    if v=='top':
        return 'monumental', '上部留白→天幕巨字'
    if v=='bottom':
        return 'dual_portals', '下部留白→天地双极'
    # 主体居中且占极大(明确满幅) → 边缘装裱
    if h=='center' and v=='center' and ratio>=0.75:
        return 'film', '居中满幅→胶片齿孔(边缘装裱)'
    # 亮调居中留白（B11：nordic 已删，改为推荐科考标本/画廊卡纸护脸款）
    if lum=='bright':
        return 'specimen', '亮调留白→科考标本(护脸卡纸)'
    return 'pulip', '默认→先锋大刊'

if __name__ == '__main__':
    import json
    p=argparse.ArgumentParser(); p.add_argument('--photo', required=True); a=p.parse_args()
    feat=detect_subject(a.photo)
    g,why=select_genre(feat)
    # 统一输出 UTF-8（终端乱码不影响逻辑）
    print(json.dumps({'feat':feat,'selected':g,'why':why}, ensure_ascii=False))
