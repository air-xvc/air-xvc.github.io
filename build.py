#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRXVC 领航 —— 静态站生成器
------------------------------------------------------------
单一数据源 data/airports.json  ->  生成全部页面：
  · 每个机场的独立 SEO 详情页  /<slug>/index.html
  · 机场大全索引页            /airports/index.html
  · 首页注入：榜单卡 / 决策卡 / 对比表 / 页脚链接
  · sitemap.xml

用法：  python3 build.py
新增机场：编辑 data/airports.json 追加一个对象 -> 运行本脚本 -> 发布
"""
import os, re, json, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(BASE, "data", "airports.json"), encoding="utf-8"))
SITE = DATA["site"]
AIRPORTS = DATA["airports"]
B = SITE["base"].rstrip("/")
UPDATED = SITE.get("updated", "2026-07")
esc = html.escape

# 从 assets/config.js 读推广链接映射，把真实邀请链接直接写进按钮 href（不再只靠 config.js 运行时注入，
# 这样静态 HTML 里就带真实短链：hover 可见、不依赖 JS、任何域名/缓存都生效；config.js 仍作运行时兜底）。
def load_aff():
    txt = open(os.path.join(BASE, "assets", "config.js"), encoding="utf-8").read()
    m = re.search(r"aff\s*:\s*\{(.*?)\}", txt, re.S)
    aff = {}
    if m:
        for k, v in re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', m.group(1)):
            if v.strip():
                aff[k] = v.strip()
    return aff

AFF = load_aff()
def aff_href(slug, fallback):
    return esc(AFF[slug]) if AFF.get(slug) else fallback
def aff_tgt(slug):
    return ' target="_blank"' if AFF.get(slug) else ''

# ----------------------------------------------------------------------------- AI 订阅指南引流（姊妹站）
# 机场用户与 AI 订阅用户高度重合：很多人买机场就是为了流畅用 ChatGPT / Claude / Gemini，
# 「能连上」之后往往卡在「会员怎么开、国内卡付不了、代充值踩坑」——正好由姊妹站 AI 订阅指南承接。
# 三卡分别精准直达对应指南页；底部主按钮进指南首页（含 30 秒选择器）。改域名/文案只需改这一处。
AI_GUIDE = "https://555735.xyz"
AI_CARDS = [
    {"key": "gemini", "name": "Gemini", "c1": "#4989F5", "c2": "#9168F0", "sym": "✦",
     "badge": "长周期最划算", "role": "Google 生态 · 多模态 · 长周期",
     "chips": ["12 / 18 个月", "CDK 秒发", "成品账号"], "go": "看 Gemini 怎么买最省"},
    {"key": "chatgpt", "name": "ChatGPT", "c1": "#10A37F", "c2": "#19C79A", "sym": "✺",
     "badge": "用得最广", "role": "通用生产力 · 图像 · Codex 编程",
     "chips": ["Plus / Pro", "代充值", "Codex 已接码"], "go": "看 ChatGPT 怎么开通"},
    {"key": "claude", "name": "Claude", "c1": "#E8825A", "c2": "#D96C43", "sym": "✳",
     "badge": "码农刚需", "role": "代码 · 长文本 · Claude Code",
     "chips": ["Pro / Max", "代充值", "独享成品号"], "go": "看 Claude 怎么充值"},
]

def ai_promo_html():
    cards = []
    for c in AI_CARDS:
        chip_html = "".join('<span class="chip">%s</span>' % esc(x) for x in c["chips"])
        cards.append(
            '<a class="ai-card %s" href="%s/guides/%s.html" target="_blank" rel="noopener sponsored" '
            'aria-label="查看 %s 订阅购买指南">'
            '<span class="ai-badge">%s</span>'
            '<span class="ai-logo" style="--c1:%s;--c2:%s" aria-hidden="true">%s</span>'
            '<h3>%s</h3><p class="ai-role">%s</p>'
            '<div class="tagrow">%s</div>'
            '<span class="ai-go">%s →</span></a>'
            % (c["key"], AI_GUIDE, c["key"], esc(c["name"]), esc(c["badge"]),
               c["c1"], c["c2"], c["sym"], esc(c["name"]), esc(c["role"]), chip_html, esc(c["go"])))
    return (
        '<section class="section wrap ai-promo" id="ai-guide" aria-label="AI 订阅指南推广">'
        '<div class="ai-shell">'
        '<div class="ai-head center">'
        '<span class="eyebrow center">🤖 AI 订阅指南</span>'
        '<h2>机场帮你连上 AI，<span class="grad-text">会员别买贵了</span></h2>'
        '<p>ChatGPT、Claude、Gemini 官方订阅又贵、国内卡还常常付不了？代充值、成品号、CDK 到底怎么选，'
        '「AI 订阅指南」一篇讲清——<b>先看懂再下单，同样的会员少花一半</b>。</p></div>'
        '<div class="ai-grid">%s</div>'
        '<div class="ai-foot">'
        '<div class="ai-foot-txt"><b>拿不准选哪家？</b>指南里有 30 秒选择器，回答两个问题就帮你选对产品和档位，再进商城下单。</div>'
        '<a class="btn btn-primary btn-lg" href="%s" target="_blank" rel="noopener sponsored">进入 AI 订阅指南 ↗</a>'
        '</div></div></section>' % ("\n".join(cards), AI_GUIDE)
    )

def ai_banner_html():
    # 详情页上部紧凑钩子条：放在规格表后、正文前，填补留白，新标签打开保留机场页
    return (
        '<div class="wrap" style="margin-top:30px"><a class="ai-banner" href="%s" target="_blank" '
        'rel="noopener sponsored" aria-label="AI 订阅指南：ChatGPT、Claude、Gemini 怎么买更省">'
        '<span class="ai-banner-dots" aria-hidden="true"><i style="--c:#4989F5"></i>'
        '<i style="--c:#10A37F"></i><i style="--c:#E8825A"></i></span>'
        '<span class="ai-banner-txt"><b>选好机场，AI 会员也别买贵了</b> '
        'ChatGPT / Claude / Gemini 代充值、成品号、CDK 一篇看懂，同样会员少花一半</span>'
        '<span class="ai-banner-cta">AI 订阅指南 ↗</span></a></div>'
    ) % AI_GUIDE

# ----------------------------------------------------------------------------- 花渡攻略博客引流（互导流）
# 机场用户＝AI 重度用户：连上机场后最常卡在「反重力装不上、Gemini 被封、谷歌账号申诉」。
# 花渡博客(guide.rtxk.us)有成体系实用教程正好承接。这里只精选「与机场强相关」的教程做原生延伸阅读位，
# 不搬机场评测(与本站重复)。改域名/选文只改这一处。所有出站链接一律新标签打开，保机场页留存。
BLOG = "https://guide.rtxk.us"
HD_GROUPS = [
    {"t": "反重力 Antigravity", "c": "#7E7BFF", "links": [
        ("下载 · 安装 · 中文汉化", "/tutorial/google-antigravity-download-install-chinese.html"),
        ("配机场代理 / TUN 节点", "/tutorial/antigravity-proxy-tun-node-setup.html"),
        ("登录卡在扫码验证？", "/tutorial/antigravity/antigravity-qr-verify.html")]},
    {"t": "Gemini", "c": "#35E0D4", "links": [
        ("养号防封实战指南", "/tutorial/gemini-account-nurturing.html"),
        ("打不开 / 连不上排查", "/tutorial/gemini-access-troubleshooting.html"),
        ("高效使用 & 中文技巧", "/tutorial/gemini-tips-prompt-multimodal.html")]},
    {"t": "谷歌账号", "c": "#FF6AD5", "links": [
        ("被封停？申诉解封全流程", "/tutorial/google-account-appeal.html"),
        ("“电话无法验证”怎么破", "/tutorial/google-account-phone-verification.html"),
        ("注册 · 避坑全指南", "/tutorial/google-account-register-guide.html")]},
]

def _hd_group(g):
    links = "".join(
        '<a class="hd-link" href="%s%s" target="_blank" rel="noopener">%s<span aria-hidden="true">↗</span></a>'
        % (BLOG, path, esc(label)) for (label, path) in g["links"])
    return ('<div class="hd-group-h"><span class="hd-dot" style="--c:%s" aria-hidden="true"></span>%s</div>%s'
            % (g["c"], esc(g["t"]), links))

def hd_rail_html():
    # 详情页正文右栏「延伸阅读」浮动广告位：桌面靠右绕排、手机全宽堆叠。只推与机场强相关的教程。
    groups = "".join('<div class="hd-group">%s</div>' % _hd_group(g) for g in HD_GROUPS)
    return (
        '<aside class="hd-rail" aria-label="花渡攻略推荐">'
        '<div class="hd-rail-top"><span class="hd-eyebrow">🌸 花渡攻略</span>'
        '<p class="hd-hook">机场连上了，AI 却打不开、老被封号？<b>这些坑，花渡博客替你趟平了。</b></p></div>'
        '%s'
        '<a class="hd-more" href="%s" target="_blank" rel="noopener">花渡博客 · 更多实用攻略 ↗</a>'
        '</aside>' % (groups, BLOG))

def hd_dock_html():
    # 屏幕右缘悬浮件：与 .hd-rail 同源内容。app.js 用 IntersectionObserver 观察 in-flow 的 .hd-rail，
    # 正文区(rail 在场)隐藏、滚过 rail 后加 .is-live 由把手接棒 —— 二者互斥，绝不同屏重复。
    # 宽屏(≥1760)展开落在右侧空白 in-gutter 零遮挡；窄屏点击→右侧抽屉+遮罩；手机→右下 FAB→底部 sheet。
    groups = "".join('<div class="hd-group">%s</div>' % _hd_group(g) for g in HD_GROUPS)
    return (
        '<div class="hd-dock">'
        '<div class="hd-scrim"></div>'
        '<button class="hd-handle" type="button" aria-expanded="false" aria-label="展开花渡攻略推荐">'
        '<span class="ic" aria-hidden="true">🌸</span>花渡攻略<span class="go" aria-hidden="true">↗</span></button>'
        '<aside class="hd-dock-panel" aria-label="花渡攻略推荐">'
        '<button class="hd-panel-close" type="button" data-hd-close aria-label="收起">×</button>'
        '<span class="hd-eyebrow">🌸 花渡攻略</span>'
        '<p class="hd-hook">机场连上了，AI 却打不开、老被封号？<b>这些坑，花渡博客替你趟平了。</b></p>'
        '%s'
        '<a class="hd-more" href="%s" target="_blank" rel="noopener">花渡博客 · 更多实用攻略 ↗</a>'
        '</aside></div>' % (groups, BLOG))

def hd_home_html():
    # 首页 / 机场大全「花渡攻略博客」区块：三组精选教程 + 进入博客主按钮。
    cols = "".join('<div class="hd-home-col">%s</div>' % _hd_group(g) for g in HD_GROUPS)
    return (
        '<section class="section wrap hd-home" id="huadu" aria-label="花渡攻略博客推广">'
        '<div class="hd-home-head center"><span class="eyebrow center">🌸 花渡攻略博客</span>'
        '<h2>机场只是船票，<span class="grad-text">上岸后怎么玩转 AI</span></h2>'
        '<p>Gemini 养号防封、谷歌账号申诉解封、反重力 Antigravity 汉化配置……机场用户最常踩的 AI 坑，'
        '花渡博客手把手替你趟平。看懂了，机场才没白买。</p></div>'
        '<div class="hd-home-grid">%s</div>'
        '<div class="hd-home-foot"><a class="btn btn-primary btn-lg" href="%s" target="_blank" rel="noopener">进入花渡博客 ↗</a></div>'
        '</section>' % (cols, BLOG))

# ----------------------------------------------------------------------------- helpers
def chips(items, cls=""):
    return "".join('<span class="chip %s">%s</span>' % (cls, esc(x)) for x in items)

def emby_badge(a):
    # Emby 影音库高亮徽章（紫色描边 chip，克制而醒目；无 emby 标记则不输出）
    return '<span class="chip emby">🎬 Emby 影音库</span>' if a.get("emby") else ""

def emblem(a, size=64):
    s, slug = size, a["slug"]
    c1, c2 = a["accent"]
    return (
      '<svg class="emb" width="%d" height="%d" viewBox="0 0 64 64" role="img" aria-label="%s 图标">'
      '<defs><linearGradient id="em-%s" x1="0" y1="0" x2="64" y2="64">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
      '<rect width="64" height="64" rx="16" fill="url(#em-%s)"/>'
      '<text x="32" y="43" text-anchor="middle" font-family="Space Grotesk,sans-serif" '
      'font-size="30" font-weight="700" fill="#08122b">%s</text></svg>'
    ) % (s, s, esc(a["name"]), slug, c1, c2, slug, esc(a["initial"]))

def client_hint(a):
    p = " ".join(a["protocols"]).lower()
    if "hysteria2" in p:
        return ('<div class="callout"><b>客户端提示：</b>本机场含 Hysteria2 节点，请使用 '
                'v2rayN / Hiddify / Karing 等支持该协议的客户端；Xray-core、老版本 Clash '
                '无法连接，导入会报错。</div>')
    if "trojan" in p:
        return ('<div class="callout"><b>客户端提示：</b>Trojan 协议兼容性好，'
                'Clash Verge / v2rayN / Shadowrocket 等主流客户端均可直接导入使用。</div>')
    return ('<div class="callout"><b>客户端提示：</b>主流协议，'
            'Clash 系 / Shadowrocket 等常见客户端都可导入，粘贴订阅即可。</div>')

# ----------------------------------------------------------------------------- shared chrome
def nav_html():
    return (
'<header class="nav"><nav class="wrap nav-in" aria-label="主导航">'
'<a class="brand" href="/" aria-label="AIRXVC 领航 首页">'
'<svg class="mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">'
'<defs><linearGradient id="bg1" x1="0" y1="0" x2="40" y2="40">'
'<stop offset="0" stop-color="#35E0D4"/><stop offset=".5" stop-color="#7E7BFF"/><stop offset="1" stop-color="#FF6AD5"/>'
'</linearGradient></defs><circle cx="20" cy="20" r="18" stroke="url(#bg1)" stroke-width="1.6" opacity=".5"/>'
'<path d="M20 5 L26 32 L20 27 L14 32 Z" fill="url(#bg1)"/><circle cx="20" cy="20" r="2.4" fill="#fff"/></svg>'
'<span>机场推荐榜<small>AIRXVC 领航 · 专业实测</small></span></a>'
'<button class="nav-toggle" aria-label="展开菜单" aria-expanded="false">☰</button>'
'<div class="nav-links">'
'<a href="/#board">机场榜单</a><a href="/#emby">Emby影音</a><a href="/airports/">机场大全</a>'
'<a href="/#guide">怎么选</a><a href="/#compare">参数对比</a><a href="/#faq">常见问题</a>'
'<a class="nav-ai" href="' + AI_GUIDE + '" target="_blank" rel="noopener sponsored">AI订阅 ↗</a>'
'<a class="nav-blog" href="' + BLOG + '" target="_blank" rel="noopener">攻略博客 ↗</a>'
'<a class="btn btn-primary nav-cta" href="/airports/">全部机场</a></div></nav></header>')

def footer_html():
    links = "\n".join('<a href="/%s/">%s %s</a>' % (a["slug"], esc(a["name"]), esc(a["en"]))
                      for a in AIRPORTS if a.get("featured"))
    return (
'<footer class="foot"><div class="wrap"><div class="foot-grid">'
'<div><a class="brand" href="/" style="margin-bottom:14px">'
'<svg class="mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">'
'<circle cx="20" cy="20" r="18" stroke="url(#bg1)" stroke-width="1.6" opacity=".5"/>'
'<path d="M20 5 L26 32 L20 27 L14 32 Z" fill="url(#bg1)"/></svg>'
'<span>AIRXVC<small>领航 · 机场推荐榜</small></span></a>'
'<p style="color:var(--ink-2);font-size:14px;max-width:34ch">' + esc(SITE["tagline"]) + '</p></div>'
'<div><h5>机场评测</h5>' + links + '</div>'
'<div><h5>指南</h5><a href="/#guide">怎么选机场</a><a href="/#compare">参数对比</a>'
'<a href="/airports/">机场大全</a><a href="/#faq">常见问题</a></div></div>'
'<div class="disc"><p><b>免责声明：</b>本站为第三方信息与推荐平台，非任何机场官方；页面内含推广链接，'
'若你通过链接注册或购买，我们可能获得一定佣金，但<b>不会增加你的任何成本</b>。'
'各机场的线路、价格、优惠码可能随时变动，请以对应官网实时信息为准。'
'代理/加密技术的使用需遵守你所在国家或地区的法律法规，本站内容仅供学习与技术研究参考。</p>'
'<p style="margin-top:10px">© <span data-year>2026</span> AIRXVC 领航 · air-xvc.github.io</p></div></div></footer>')

SKIP_STYLE = ('<style>.skip{position:absolute;left:-999px;top:0;z-index:100;background:var(--amber);'
              'color:#241300;padding:10px 16px;border-radius:0 0 10px 0;font-weight:600}.skip:focus{left:0}</style>')

# 多域自认领：canonical/hreflang 已相对化（任何访问域名自动解析成本域）。
# 下面这段在浏览器/搜索引擎渲染时，把 og/twitter/JSON-LD 里的主域改写成“当前访问域名”，
# 让每个镜像域名都被独立收录；在主域上执行为 no-op，对 GitHub Pages 无影响。
ORIGIN_JS = (
    '<script>(function(){var o=location.origin,P=%s;if(o===P)return;'
    'document.querySelectorAll(\'meta[property="og:url"],meta[property="og:image"],meta[name="twitter:image"]\')'
    '.forEach(function(m){var c=m.getAttribute("content");if(c)m.setAttribute("content",c.split(P).join(o));});'
    'var s=document.querySelector(\'script[type="application/ld+json"]\');'
    'if(s)s.textContent=s.textContent.split(P).join(o);})();</script>'
) % json.dumps(B)

def head(title, desc, canonical, keywords, og_image, jsonld, og_type="article"):
    j = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))
    cpath = canonical[len(B):] if canonical.startswith(B) else canonical  # 相对路径：每个访问域名自动自认领
    cpath = cpath or "/"
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="keywords" content="%s">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#060917">
<link rel="canonical" href="%s">
<link rel="alternate" hreflang="zh-CN" href="%s">
<link rel="alternate" hreflang="x-default" href="%s">
<meta property="og:type" content="%s">
<meta property="og:site_name" content="AIRXVC 领航 · 机场推荐榜">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
%s
<script type="application/ld+json">%s</script>
%s
</head>
<body>
<a class="skip" href="#main">跳到主内容</a>
<div class="bg-grid" aria-hidden="true"></div>
""" % (esc(title), esc(desc), esc(keywords), cpath, cpath, cpath, og_type,
       esc(title), esc(desc), canonical, og_image, esc(title), esc(desc), og_image,
       SKIP_STYLE, j, ORIGIN_JS)

SCRIPTS = '<script src="/assets/config.js"></script>\n<script src="/assets/app.js" defer></script>\n</body>\n</html>\n'

# ----------------------------------------------------------------------------- detail page
def render_detail(a):
    slug, name, en = a["slug"], a["name"], a["en"]
    url = "%s/%s/" % (B, slug)
    og = "%s/assets/og/%s.png" % (B, slug)
    full = name if (not en or en == name) else name + " " + en
    en_disp = "" if (not en or en == name) else en
    title = "%s 机场评测 2026｜线路 · 套餐 · 优惠 · 教程 · AIRXVC 领航" % full

    # spec strip
    spec = [
        ("上线年份", a["year"]),
        ("线路类型", a["type"]),
        ("主要协议", " · ".join(a["protocols"])),
        ("覆盖地区", a["regions"]),
        ("计费方式", a["billing"]),
        ("流媒体解锁", " · ".join(a["unlock"])),
    ]
    spec_html = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in spec)

    # TOC + sections
    toc, body = [], []
    for i, sec in enumerate(a["sections"]):
        sid = "s%d" % i
        toc.append('<a href="#%s">%s</a>' % (sid, esc(sec["h"])))
        body.append('<h2 id="%s">%s</h2>' % (sid, esc(sec["h"])))
        for para in sec.get("p", []):
            body.append('<p>%s</p>' % esc(para))
        if sec.get("list"):
            body.append('<ul class="dots">' + "".join('<li>%s</li>' % esc(x) for x in sec["list"]) + '</ul>')
        if sec.get("note"):
            body.append('<div class="callout">%s</div>' % esc(sec["note"]))

    # plans
    rows = "".join('<tr><td>%s</td><td class="p">%s</td><td class="muted">%s</td></tr>'
                   % (esc(r[0]), esc(r[1]), esc(r[2])) for r in a["plans"])
    toc.append('<a href="#plans">套餐与价格</a>')
    plans_html = (
        '<h2 id="plans">套餐与价格</h2>'
        '<table class="plan-table"><thead><tr><th>套餐</th><th>参考价</th><th>说明</th></tr></thead>'
        '<tbody>%s</tbody></table><p class="muted" style="font-size:13px">%s</p>' % (rows, esc(a["plan_note"])))

    # pros / cons
    toc.append('<a href="#pc">优点与缺点</a>')
    pc_html = (
        '<h2 id="pc">优点与缺点</h2><div class="pc">'
        '<div class="col pros"><h4>优点</h4><ul>%s</ul></div>'
        '<div class="col cons"><h4>要注意</h4><ul>%s</ul></div></div>'
    ) % ("".join('<li>%s</li>' % esc(x) for x in a["pros"]),
         "".join('<li>%s</li>' % esc(x) for x in a["cons"]))

    # fit / unfit
    toc.append('<a href="#fit">适合谁</a>')
    fit_html = (
        '<h2 id="fit">适合谁 / 谁要三思</h2><div class="grid-2">'
        '<div class="card"><h3>适合入手</h3><ul class="dots">%s</ul></div>'
        '<div class="card"><h3>建议三思</h3><ul class="dots">%s</ul></div></div>'
    ) % ("".join('<li>%s</li>' % esc(x) for x in a["fit"]),
         "".join('<li>%s</li>' % esc(x) for x in a["unfit"]))

    # tutorial
    toc.append('<a href="#howto">新手上手</a>')
    howto_html = (
        '<h2 id="howto">新手上手：4 步开用</h2>' + client_hint(a) +
        '<ol class="steps">'
        '<li><b>注册并购买套餐。</b>打开 %s 官网注册账号，按需求选一档套餐下单。</li>'
        '<li><b>复制订阅链接。</b>在用户中心找到“一键订阅 / 复制订阅地址”，复制你的专属链接。</li>'
        '<li><b>安装客户端。</b>Windows 用 Clash Verge / v2rayN，安卓用 Hiddify / Karing，iOS 用 Shadowrocket。</li>'
        '<li><b>导入并选节点。</b>把订阅粘贴进客户端、更新节点，挑一个延迟低的节点开启即可。</li>'
        '</ol>' % esc(name))

    # faq
    faq_items = a.get("faq", [])
    toc.append('<a href="#faq">常见问题</a>')
    faq_html = '<h2 id="faq">常见问题</h2><div class="faq">' + "".join(
        '<details%s><summary>%s</summary><div class="a">%s</div></details>'
        % (" open" if i == 0 else "", esc(q["q"]), esc(q["a"])) for i, q in enumerate(faq_items)
    ) + '</div>'

    prose = "\n".join(body) + plans_html + pc_html + fit_html + howto_html + faq_html
    toc_html = '<aside class="toc"><div class="lb">本页目录</div>' + "".join(toc) + '</aside>'

    # jsonld
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": B + "/"},
            {"@type": "ListItem", "position": 2, "name": "机场大全", "item": B + "/airports/"},
            {"@type": "ListItem", "position": 3, "name": full, "item": url}]},
        {"@type": "Article", "headline": title, "description": a["meta_desc"], "inLanguage": "zh-CN",
         "author": {"@type": "Organization", "name": "AIRXVC 领航"},
         "publisher": {"@type": "Organization", "name": "AIRXVC 领航", "logo": {"@type": "ImageObject", "url": B + "/assets/og.png"}},
         "mainEntityOfPage": url, "image": og, "datePublished": "2026-06-01", "dateModified": UPDATED + "-01"},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in faq_items]},
    ]}

    label = ('<span class="chip hot">%s</span>' % esc(a["rank_label"])) if a.get("rank_label") else ""
    out = head(title, a["meta_desc"], url, a["keywords"], og, jsonld)
    out += nav_html()
    out += '<main id="main"><section class="section wrap" style="padding-bottom:0">'
    out += ('<nav class="crumbs" aria-label="面包屑"><a href="/">首页</a><span>/</span>'
            '<a href="/airports/">机场大全</a><span>/</span><span>%s</span></nav>' % esc(name))
    # hero-detail
    out += '<div class="hero-detail">'
    out += '<div>'
    en_span = ('<span style="color:var(--ink-3);font-family:var(--font-mono);font-size:.5em;font-weight:400">%s</span>' % esc(en_disp)) if en_disp else ""
    out += '<div style="display:flex;align-items:center;gap:16px;margin-bottom:18px">%s<div><h1 style="font-size:clamp(30px,5vw,46px)">%s %s</h1><div class="tagrow" style="margin-top:8px">%s%s%s</div></div></div>' % (
        emblem(a, 64), esc(name), en_span,
        '<span class="chip cy">%s · %s</span>' % (esc(a["type_short"]), esc(a["year"])), label, emby_badge(a))
    out += '<p class="lead" style="color:var(--ink-2);font-size:17px;margin:8px 0 18px">%s</p>' % esc(a["tagline"])
    out += '<div class="verdict"><b>一句话点评：</b>%s</div>' % esc(a["verdict"])
    out += '<div class="tagrow" style="margin-top:18px">%s%s</div>' % (
        chips(a["protocols"]), chips(a["unlock"], "on"))
    out += '</div>'
    # buybox
    out += ('<aside class="buybox"><div class="price-lead">起步参考价</div>'
            '<div class="price-big">%s<span>%s</span></div>'
            '<div class="tagrow" style="margin:12px 0 16px">%s</div>'
            '<a class="btn btn-primary btn-block btn-lg" data-aff="%s" href="%s"%s rel="nofollow sponsored noopener">前往%s官网 ↗</a>'
            '<a class="btn btn-ghost btn-block" href="#plans" style="margin-top:10px">查看套餐</a>'
            '<div data-codebox><div class="price-lead" style="margin-top:18px">专属优惠码</div>'
            '<div class="codebox"><code data-code="%s">—</code><button class="copybtn" type="button">复制</button></div></div>'
            '<p class="muted" style="font-size:12px;margin-top:14px">通过本站链接注册不额外收费；价格 / 优惠以官网为准。</p></aside>'
            ) % (esc(a["price_from"]), esc(a["price_unit"]), chips(a["unlock"], "on"),
                 slug, aff_href(slug, "#plans"), aff_tgt(slug), esc(name), slug)
    out += '</div>'  # hero-detail
    # spec strip
    out += '<dl class="spec" style="margin-top:36px">%s</dl>' % spec_html
    # AI 引流钩子条：规格表后、正文前，填补此处留白
    out += ai_banner_html()
    out += '</section>'
    # doc
    out += '<section class="section wrap"><div class="doc">%s<div class="prose">%s</div>%s</div></section>' % (toc_html, prose, hd_rail_html())
    # 花渡右缘悬浮件（fixed 定位，DOM 位置不影响；放 .doc 之后确保 .hd-rail 先入 DOM 供 IO 观察）
    out += hd_dock_html()
    # AI 订阅指南引流专区（姊妹站）
    out += ai_promo_html()
    # cta band
    out += ('<section class="section-sm wrap"><div class="band"><span class="eyebrow center">准备起飞</span>'
            '<h2>觉得 %s 合适？<span class="grad-text">月付先试一档</span></h2>'
            '<p>新机场先小额验证再续费，试错成本很低。价格与优惠以官网实时为准。</p>'
            '<a class="btn btn-primary btn-lg" data-aff="%s" href="%s"%s rel="nofollow sponsored noopener">前往 %s 官网 ↗</a>'
            '<div style="margin-top:16px"><a class="chip" href="/airports/">← 返回机场大全</a></div></div></section>'
            ) % (esc(name), slug, aff_href(slug, "#plans"), aff_tgt(slug), esc(name))
    out += '</main>'
    out += footer_html()
    out += SCRIPTS
    return out

# ----------------------------------------------------------------------------- airports hub
def render_hub():
    url = B + "/airports/"
    title = "机场大全｜全部科学上网机场推荐与评测榜单 · AIRXVC 领航"
    desc = "AIRXVC 领航机场大全：汇总我们实测收录的全部机场（%s 等），按线路类型、协议、解锁能力与价格对比，点进各家看完整评测。持续更新。" % "、".join(a["name"] for a in AIRPORTS if a.get("featured"))
    cards = []
    for a in AIRPORTS:
        cards.append(
            '<article class="card air-card">'
            '<div style="display:flex;gap:14px;align-items:center;margin-bottom:14px">%s'
            '<div><h3 style="font-size:19px">%s <small>%s</small></h3>'
            '<div class="tagrow" style="margin-top:6px"><span class="chip cy">%s</span></div></div></div>'
            '<p style="color:var(--ink-2);font-size:14.5px;min-height:63px">%s</p>'
            '<div class="tagrow" style="margin:12px 0">%s</div>'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px">'
            '<span style="font-family:var(--font-mono);font-size:14px"><b>%s</b><span class="muted">%s</span></span>'
            '<a class="btn btn-aurora" href="/%s/">查看评测 →</a></div></article>'
            % (emblem(a, 52), esc(a["name"]), esc(a["en"]), esc(a["type"]),
               esc(a["tagline"]), chips(a["unlock"], "on"),
               esc(a["price_from"]), esc(a["price_unit"]), a["slug"]))
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": B + "/"},
            {"@type": "ListItem", "position": 2, "name": "机场大全", "item": url}]},
        {"@type": "CollectionPage", "name": "机场大全", "url": url, "description": desc,
         "inLanguage": "zh-CN"},
        {"@type": "ItemList", "numberOfItems": len(AIRPORTS), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": "%s %s" % (a["name"], a["en"]),
             "url": "%s/%s/" % (B, a["slug"])} for i, a in enumerate(AIRPORTS)]},
    ]}
    out = head(title, desc, url, "机场大全,机场推荐,机场评测,科学上网,翻墙机场,机场榜单", B + "/assets/og.png", jsonld, "website")
    out += nav_html()
    out += '<main id="main"><section class="section wrap">'
    out += ('<nav class="crumbs" aria-label="面包屑"><a href="/">首页</a><span>/</span><span>机场大全</span></nav>')
    out += ('<div class="sec-head"><span class="eyebrow">机场大全 · 持续更新</span>'
            '<h2>全部收录机场<span class="grad-text">总览</span></h2>'
            '<p>我们实测收录的机场都在这里，按需求点进去看完整评测。共 %d 家，持续增加中。</p></div>' % len(AIRPORTS))
    out += '<div class="grid-3">%s</div>' % "\n".join(cards)
    out += ('<div style="text-align:center;margin-top:44px"><a class="btn btn-ghost" href="/#guide">还不知道怎么选？看选购指南 →</a></div>')
    out += '</section>'
    # AI 订阅指南引流专区（姊妹站）
    out += ai_promo_html()
    out += hd_home_html()
    out += '</main>'
    out += footer_html()
    out += SCRIPTS
    return out

# ----------------------------------------------------------------------------- homepage fragments
def render_board():
    """首页榜单：按 airports 数组顺序，仅 featured；名次 01/02/03… 与榜序一致。"""
    out = []
    rank = 0
    for a in AIRPORTS:
        if not a.get("featured"):
            continue
        rank += 1
        gate = "%02d" % rank
        best = ('<span class="best">%s</span>' % esc(a["rank_label"])) if a.get("rank_label") and rank == 1 else ""
        label = '<span class="chip cy">%s</span>' % esc(a["rank_label"]) if a.get("rank_label") else ""
        tags = chips([a["type_short"] + " 线路"] + a["protocols"]) + chips(a["unlock"][:2], "on")
        out.append(
            '<article class="rank">%s<div class="gate"><span class="no">%s</span><span class="lb">GATE</span></div>'
            '<div class="rank-main"><h3>%s %s %s</h3><p class="tagline">%s</p><div class="tagrow">%s</div></div>'
            '<div class="rank-side"><div class="price"><b>%s</b>起 %s</div>'
            '<a class="btn btn-aurora btn-block" href="/%s/">查看评测</a>'
            '<a class="btn btn-ghost btn-block" data-aff="%s" href="%s"%s rel="nofollow sponsored noopener">前往官网 ↗</a></div></article>'
            % (best, gate, esc(a["name"]), esc(a["en"]) if a["en"] != a["name"] else "", label,
               esc(a["tagline"]), tags, esc(a["price_from"]), esc(a["price_unit"]),
               a["slug"], a["slug"], aff_href(a["slug"], "/%s/#plans" % a["slug"]), aff_tgt(a["slug"])))
    return "\n".join(out)

def render_pick():
    # 决策卡只取榜单前 4，避免挤满屏
    out = []
    for a in [x for x in AIRPORTS if x.get("featured")][:4]:
        out.append(
            '<a class="pick-card" href="/%s/"><div class="q">// %s</div><h3>%s</h3>'
            '<p>%s</p><span class="rec">推荐 %s'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">'
            '<path d="M5 12h14M13 6l6 6-6 6" stroke-linecap="round"/></svg></span></a>'
            % (a["slug"], esc(a["best_for"]), esc(a["scene"]), esc(a["tagline"][:40] + "…"), esc(a["name"])))
    return "\n".join(out)

def render_compare():
    out = []
    for a in [x for x in AIRPORTS if x.get("featured")]:
        out.append(
            '<tr><td class="name">%s</td><td>%s</td><td class="mono">%s</td><td>%s</td>'
            '<td class="mono">%s %s</td><td>%s</td><td><a class="chip cy" href="/%s/">评测 →</a></td></tr>'
            % (esc(a["name"]), esc(a["type"]), esc(" · ".join(a["protocols"])),
               esc(" · ".join(a["unlock"])), esc(a["price_from"]), esc(a["price_unit"]),
               esc(a["best_for"]), a["slug"]))
    return "\n".join(out)

def render_footer_airports():
    return "\n".join('<a href="/%s/">%s %s</a>' % (a["slug"], esc(a["name"]), esc(a["en"]))
                     for a in AIRPORTS if a.get("featured"))

def render_emby():
    """首页「Emby 影音专区」：只收录带 emby 标记的机场（不依赖 featured）。"""
    out = []
    for a in AIRPORTS:
        if not a.get("emby"):
            continue
        en = esc(a["en"]) if a["en"] != a["name"] else ""
        small = ("<small>%s</small>" % en) if en else ""
        out.append(
            '<article class="card emby-card">'
            '<div class="emby-head">%s'
            '<div><h3>%s%s</h3>'
            '<div class="tagrow" style="margin-top:7px">%s</div></div></div>'
            '<p class="desc">%s</p>'
            '<div class="emby-foot"><span class="price"><b>%s</b>%s</span>'
            '<a class="btn btn-aurora" href="/%s/">看评测 →</a></div></article>'
            % (emblem(a, 46), esc(a["name"]), small, emby_badge(a), esc(a["tagline"]),
               esc(a["price_from"]), esc(a["price_unit"]), a["slug"]))
    return "\n".join(out)

def inject(text, name, inner):
    pat = re.compile(r"(<!--GEN:%s:START-->).*?(<!--GEN:%s:END-->)" % (name, name), re.S)
    return pat.sub(lambda m: m.group(1) + "\n" + inner + "\n" + m.group(2), text)

# ----------------------------------------------------------------------------- sitemap
def render_sitemap():
    today = "2026-07-04"
    urls = [(B + "/", "1.0", "weekly"), (B + "/airports/", "0.8", "weekly")]
    urls += [("%s/%s/" % (B, a["slug"]), "0.7", "monthly") for a in AIRPORTS]
    items = "".join(
        '<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>'
        % (u, today, cf, pr) for (u, pr, cf) in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % items

def render_wall():
    chips = "".join('<a class="wall-chip" href="/%s/">%s<span>%s</span></a>' % (a["slug"], emblem(a, 26), esc(a["name"])) for a in AIRPORTS)
    n = len(AIRPORTS)
    return ('<section class="section-sm"><div class="wrap center">'
            '<span class="eyebrow center">机场墙 · 持续增加</span>'
            '<h2 style="font-size:clamp(22px,3.2vw,34px)">已收录 <span class="grad-text">%d</span> 家机场，一站挑齐</h2>'
            '<p class="muted" style="max-width:52ch;margin:12px auto 0">从老牌 IEPL 专线到平价大流量，点任意一家看完整评测与最新价格。</p>'
            '</div><div class="wall"><div class="wall-track">%s%s</div>'
            '<div class="wall-track rev">%s%s</div></div></section>') % (n, chips, chips, chips, chips)

def render_readme():
    """生成面向 Google / GitHub 检索优化的 README。"""
    A = B
    n = len(AIRPORTS)
    featured = [a for a in AIRPORTS if a.get("featured")]
    top_names = "、".join(
        (a["name"] if a["en"] == a["name"] else "%s %s" % (a["name"], a["en"]))
        for a in AIRPORTS[:6]
    )
    L = []

    # --- 首屏：H1 含核心搜索词，首段即 Google 摘要素材 ---
    L.append('<p align="center">')
    L.append('<img src="assets/og.png" alt="机场推荐榜 2026 · 科学上网机场评测 · AIRXVC 领航" width="820">')
    L.append("</p>")
    L.append("")
    L.append("# 机场推荐 2026｜科学上网机场评测与对比 · AIRXVC 领航")
    L.append("")
    L.append(
        "**AIRXVC 领航** 是独立的 **机场推荐 / 机场评测** 开源仓库与站点，"
        "汇总 %d 家高速稳定 **科学上网机场**（翻墙机场 / 代理订阅服务），"
        "按线路类型（IEPL 专线、直连、中转）、协议（Trojan、VLESS、Reality、Hysteria2、Shadowsocks）、"
        "Netflix / Disney+ / ChatGPT 解锁与性价比横向对比，帮你 3 分钟选对机场。"
        % n
    )
    L.append("")
    L.append(
        "在线站点：**[%s](%s/)** ｜ 本仓库：**[air-xvc/air-xvc.github.io](https://github.com/air-xvc/air-xvc.github.io)** ｜ 数据更新：%s"
        % (A.replace("https://", ""), A, UPDATED)
    )
    L.append("")
    L.append(
        "精选包括：%s 等。价格与优惠码可能随官网调整，请以各机场官网为准。"
        % top_names
    )
    L.append("")
    L.append("---")
    L.append("")

    # --- 目录：提升停留与抓取结构 ---
    L.append("## 目录")
    L.append("")
    L.append("- [本仓库是什么](#本仓库是什么)")
    L.append("- [2026 精选机场榜单](#2026-精选机场榜单)")
    L.append("- [Emby 影音机场推荐](#emby-影音机场推荐)")
    L.append("- [机场快速对比表](#机场快速对比表)")
    L.append("- [30 秒教你怎么选机场](#30-秒教你怎么选机场)")
    L.append("- [新手入门：第一次用机场](#新手入门第一次用机场)")
    L.append("- [常见问题 FAQ](#常见问题-faq)")
    L.append("- [相关搜索词](#相关搜索词)")
    L.append("- [免责声明](#免责声明)")
    L.append("")
    L.append("---")
    L.append("")

    # --- 项目说明：仓库定位 + 可被检索的实体词 ---
    L.append("## 本仓库是什么")
    L.append("")
    L.append(
        "很多人搜索「**机场推荐**」「**哪家机场好**」「**科学上网机场**」「**稳定机场评测**」时，"
        "会刷到大量广告站或过期榜单。本项目把 **评测内容、对比表、决策指南** 开源在 GitHub，"
        "并同步发布到 GitHub Pages，方便检索、收藏与二次核对。"
    )
    L.append("")
    L.append("| 项目 | 说明 |")
    L.append("| --- | --- |")
    L.append("| 仓库名 | `air-xvc/air-xvc.github.io` |")
    L.append("| 线上站点 | [%s](%s/) |" % (A, A))
    L.append("| 收录机场 | **%d** 家（榜单 + 机场大全） |" % n)
    L.append("| 更新节奏 | 随套餐 / 线路变动维护（当前 %s） |" % UPDATED)
    L.append("| 数据来源 | 公开套餐信息 + 场景向评测摘要 |")
    L.append("| 使用方式 | 打开站点挑机场，或直接读下方榜单与对比表 |")
    L.append("")
    L.append("**你会得到：**")
    L.append("")
    L.append("- 按稳定性 / 性价比 / 追剧 / 大流量等场景的 **机场推荐**")
    L.append("- 每家机场的 **线路类型、协议、解锁、起步价、适合人群**")
    L.append("- 独立 SEO 详情页（可分享、可搜索）：例如 "
              + " · ".join("[%s](%s/%s/)" % (a["name"], A, a["slug"]) for a in AIRPORTS[:4])
              + " …")
    L.append("- 新手避坑：月付试水、多机场容灾、客户端与协议匹配")
    L.append("")
    L.append(
        "English: Independent **proxy / VPN-like subscription (机场)** reviews and rankings for 2026 — "
        "compare IEPL dedicated lines, VLESS Reality, Hysteria2, Trojan, Netflix & ChatGPT unlock, and pricing."
    )
    L.append("")
    L.append("---")
    L.append("")

    # --- 榜单 ---
    L.append("## 2026 精选机场榜单")
    L.append("")
    L.append(
        "以下为 **%d 家机场** 的推荐与评测摘要，按「综合稳定性 + 性价比 + 场景适配」整理。"
        "完整图文评测见各机场详情页。"
        % n
    )
    L.append("")
    for i, a in enumerate(AIRPORTS):
        title = a["name"] if a["en"] == a["name"] else "%s %s" % (a["name"], a["en"])
        label = "  ·  " + ("「%s」" % a["rank_label"]) if a.get("rank_label") else ""
        L.append("### %02d. %s 机场推荐%s" % (i + 1, title, label))
        L.append("")
        L.append(
            '<img src="assets/og/%s.png" alt="%s 机场评测与推荐 · 科学上网" width="720">'
            % (a["slug"], title)
        )
        L.append("")
        L.append("> %s" % a["tagline"])
        L.append("")
        L.append("- **线路类型**：%s" % a["type"])
        L.append("- **主要协议**：%s" % " · ".join(a["protocols"]))
        L.append("- **流媒体解锁**：%s" % " · ".join(a["unlock"]))
        L.append("- **覆盖地区**：%s" % a["regions"])
        L.append("- **起步价**：%s 起 %s（%s）" % (a["price_from"], a["price_unit"], a["billing"]))
        L.append("- **最适合**：%s" % a["best_for"])
        L.append("")
        L.append(a["verdict"])
        L.append("")
        L.append("**完整评测与优惠信息 → [%s 机场评测](%s/%s/)**" % (title, A, a["slug"]))
        L.append("")

    # --- Emby 影音机场 ---
    emby_list = [a for a in AIRPORTS if a.get("emby")]
    if emby_list:
        L.append("## Emby 影音机场推荐")
        L.append("")
        L.append(
            "下面这几家在订阅之外还 **内置 / 赠送 Emby 私人影视库**：装上 Emby 客户端、用机场提供的账号登录即可在线看片，"
            "相当于自带一个「私人奈飞」，省去自己找片源。它们 **稳定、速度快，UP 主与追剧党常用**。"
            "片源、清晰度与可用性以各机场官网实时信息为准。"
        )
        L.append("")
        for a in emby_list:
            title = a["name"] if a["en"] == a["name"] else "%s %s" % (a["name"], a["en"])
            L.append("- 🎬 **[%s](%s/%s/)** — %s" % (title, A, a["slug"], a["tagline"]))
        L.append("")

    # --- 对比表 ---
    L.append("## 机场快速对比表")
    L.append("")
    L.append(
        "一张表看懂 **机场对比**：线路、协议、解锁能力、起步价与适用场景。"
        "适合搜索「机场哪家好」「机场性价比对比」时快速筛选。"
    )
    L.append("")
    L.append("| 机场 | 线路类型 | 主要协议 | 解锁 | 起步价 | 最适合 |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for a in AIRPORTS:
        L.append("| [%s](%s/%s/) | %s | %s | %s | %s %s | %s |" % (
            a["name"], A, a["slug"], a["type"], " · ".join(a["protocols"]),
            " · ".join(a["unlock"]), a["price_from"], a["price_unit"], a["best_for"]))
    L.append("")

    # --- 决策 ---
    L.append("## 30 秒教你怎么选机场")
    L.append("")
    for a in featured:
        L.append("- **%s** → 选 [%s](%s/%s/)" % (a["scene"], a["name"], A, a["slug"]))
    L.append("")
    L.append("更多场景与全部收录见线上 **[机场大全](%s/airports/)**。" % A)
    L.append("")

    # --- 新手 ---
    L.append("## 新手入门：第一次用机场")
    L.append("")
    L.append("1. **选机场**：按上面场景选 1 家主力 + 1 家备用（降低跑路 / 故障风险）。")
    L.append("2. **买套餐**：优先 **月付 / 小流量**，确认晚高峰与解锁后再考虑季付年付。")
    L.append("3. **装客户端**：Windows 用 Clash Verge / v2rayN；macOS 用 Clash Verge；Android 用 Hiddify / v2rayNG；iOS 用 Shadowrocket。")
    L.append("4. **导入订阅**：复制机场订阅链接 → 客户端更新节点 → 选延迟低的节点连接。")
    L.append("5. **协议注意**：含 **Hysteria2** 的机场，请用支持该协议的客户端，否则导入会报错。")
    L.append("")
    L.append("### 避坑要点")
    L.append("")
    L.append("- 先买月付 / 小流量档验证稳定性，别一上来就大额年付。")
    L.append("- 老牌机场通常更稳；新机场先小档试水。")
    L.append("- 同时备用 2–3 家机场互为容灾。")
    L.append("- 价格、节点、优惠码以官网实时信息为准。")
    L.append("")

    # --- FAQ：利于长尾与精选摘要 ---
    L.append("## 常见问题 FAQ")
    L.append("")
    L.append("### 机场是什么？和 VPN 有什么区别？")
    L.append("")
    L.append(
        "「**机场**」是对提供 Shadowsocks / V2Ray / Trojan / VLESS 等 **代理订阅服务** 的俗称："
        "购买套餐后得到订阅链接，导入客户端即可使用多个节点。"
        "相比传统单一入口 VPN，机场通常 **节点更多、切换更灵活**，更常用于流媒体解锁与低延迟场景。"
    )
    L.append("")
    L.append("### 2026 年怎么选靠谱的科学上网机场？")
    L.append("")
    L.append(
        "先明确需求：要 **IEPL/IPLC 专线稳定**、要 **性价比口粮**、还是要 **Netflix/Emby 追剧**。"
        "再看运营时长、是否支持月付、晚高峰表现与解锁列表。本仓库的 [精选榜单](#2026-精选机场榜单) 与 [对比表](#机场快速对比表) 就是按这个逻辑整理的。"
    )
    L.append("")
    L.append("### 机场会不会跑路？怎么降低风险？")
    L.append("")
    L.append(
        "行业存在停服 / 跑路风险。建议：优先运营时间较长的机场；**月付试水**；"
        "**2–3 家备用**；不要把大额年付压在单一新站上。"
    )
    L.append("")
    L.append("### 本仓库和官方站是什么关系？")
    L.append("")
    L.append(
        "本仓库与 [%s](%s/) 为 **第三方信息与推荐平台**，非任何机场官方。"
        "页面可能含推广链接；你通过链接注册或购买时我们可能获得佣金，**不会增加你的成本**。"
        % (A.replace("https://", ""), A)
    )
    L.append("")

    # --- 关键词簇：自然收束，便于长尾命中 ---
    L.append("## 相关搜索词")
    L.append("")
    L.append(
        "若你是通过以下关键词找到本页，说明路线对了："
        "**机场推荐**、**机场评测**、**科学上网机场**、**翻墙机场推荐**、**稳定机场**、"
        "**IEPL 专线机场**、**性价比机场**、**不限量机场**、**Netflix 解锁机场**、"
        "**ChatGPT 机场**、**Clash 订阅机场**、**V2Ray 机场**、**Trojan 机场**、"
        "**VLESS Reality 机场**、**Hysteria2 机场**、**2026 机场榜单**。"
    )
    L.append("")
    L.append(
        "品牌相关：" + "、".join(
            a["name"] if a["en"] == a["name"] else "%s / %s" % (a["name"], a["en"])
            for a in AIRPORTS[:12]
        ) + " 等机场评测均可在本站检索。"
    )
    L.append("")

    # --- 免责 ---
    L.append("## 免责声明")
    L.append("")
    L.append(
        "本仓库与站点为第三方信息与推荐平台，非任何机场官方；页面内含推广链接，"
        "若你通过链接注册或购买，我们可能获得一定佣金，但不会增加你的任何成本。"
        "各机场的线路、价格、优惠码可能随时变动，请以对应官网实时信息为准。"
        "代理 / 加密技术的使用需遵守你所在国家或地区的法律法规，本站内容仅供学习与技术研究参考。"
    )
    L.append("")
    L.append("---")
    L.append("")
    L.append(
        "<p align=\"center\">⭐ 觉得有用请给仓库点 Star，方便以后搜索「AIRXVC」「机场推荐 github」时找到我们<br>"
        "<a href=\"%s/\">访问机场推荐站</a> · "
        "<a href=\"https://github.com/air-xvc/air-xvc.github.io\">GitHub 仓库</a> · "
        "<a href=\"%s/airports/\">机场大全</a></p>"
        % (A, A)
    )
    L.append("")
    return "\n".join(L) + "\n"

# ----------------------------------------------------------------------------- main
def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)
    print("  ✓", path)

def main():
    print("AIRXVC build — %d airports" % len(AIRPORTS))
    for a in AIRPORTS:
        write("%s/index.html" % a["slug"], render_detail(a))
    write("airports/index.html", render_hub())
    write("sitemap.xml", render_sitemap())
    write("README.md", render_readme())
    idx_path = os.path.join(BASE, "index.html")
    idx = open(idx_path, encoding="utf-8").read()
    idx = inject(idx, "BOARD", render_board())
    idx = inject(idx, "EMBY", render_emby())
    idx = inject(idx, "PICK", render_pick())
    idx = inject(idx, "COMPARE", render_compare())
    idx = inject(idx, "WALL", render_wall())
    idx = inject(idx, "FOOTER_AIRPORTS", render_footer_airports())
    idx = inject(idx, "COUNT", str(len(AIRPORTS)))
    idx = inject(idx, "AIPROMO", ai_promo_html())
    idx = inject(idx, "HDPROMO", hd_home_html())
    open(idx_path, "w", encoding="utf-8").write(idx)
    print("  ✓ index.html (injected)")
    # 404 页也注入同一引流专区，保持「全站每页都挂」
    p404 = os.path.join(BASE, "404.html")
    t404 = open(p404, encoding="utf-8").read()
    t404 = inject(t404, "AIPROMO", ai_promo_html())
    open(p404, "w", encoding="utf-8").write(t404)
    print("  ✓ 404.html (injected)")
    print("Done.")


if __name__ == "__main__":
    main()
