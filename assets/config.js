/* ============================================================
   AIRXVC 领航 —— 推广位配置（唯一需要改动的文件）
   aff  : 各机场官网推广跳转链接（slug 为键）
   code : 优惠码（留空则页面自动隐藏优惠码框）
   ============================================================ */
window.SITE = {
  aff: {
    "mitce": "https://t.rtxk.us/t/ycfdvtk",
    "westdata": "https://t.rtxk.us/t/x2m8qpb",
    "candycloud": "https://t.rtxk.us/t/vubhdhq",
    "hongxing": "https://i.rtxk.us/i/mycugbg",
    "niubi": "https://i.rtxk.us/i/ktcfmqn",
    "liangxin": "https://t.rtxk.us/t/dedzags",
    "shouhou": "https://s.rtxk.us/s/scm3m2j",
    "yun69": "https://t.rtxk.us/t/fdr3mkg",
    "qingfeng": "https://i.rtxk.us/i/nvynky7",
    "ouo": "https://t.rtxk.us/t/s85fnp6",
    "niceduck": "https://i.rtxk.us/i/nu95jmp",
    "taoqitu": "https://t.rtxk.us/t/ywcc7ms",
    "yuyun": "https://t.rtxk.us/t/txppfd7",
    "shenlong": "https://i.rtxk.us/i/ayhb9d7",
    "yifen": "https://i.rtxk.us/i/x67y75t",
    "llguang": "https://s.rtxk.us/s/6pqsn8c",
    "yousun": "https://s.rtxk.us/s/2fhtsh7",
    "freecat": "https://t.rtxk.us/t/twfhqma",
    "lingyun": "https://i.rtxk.us/i/utvdfdb",
    "jisu": "https://i.rtxk.us/i/d3fvey6",
    "feigou": "https://t.rtxk.us/t/gvn847t",
    "xueshan": "https://s.rtxk.us/s/vvdrepn",
    "hneko": "https://s.rtxk.us/s/bvaumhm",
    "dingji": "https://s.rtxk.us/s/shk6g2s",
    "peiqian": "https://s.rtxk.us/s/n9gmxan",
    "juanwang": "https://i.rtxk.us/i/33zu397",
    "danta": "https://t.rtxk.us/t/k67qxy6",
    "chaoshihui": "https://s.rtxk.us/s/c5n9usc",
    "nicecloud": "https://s.rtxk.us/s/u879gws",
    "kuailei": "https://t.rtxk.us/t/cp2d6j8",
    "ktmcloud": "https://i.rtxk.us/i/fs2n9ra",
    "tapcloud": "https://s.rtxk.us/s/5qv7zcn",
    "lvpn": "https://s.rtxk.us/s/bnwjgrx",
    "shunchang": "https://t.rtxk.us/t/k2pajrb",
    "tifa": "https://i.rtxk.us/i/muxcy6r",
    "wugui": "https://s.rtxk.us/s/5krgzu4",
    "kuajing": "https://s.rtxk.us/s/4dhmqvu"
  },
  code: {
    "mitce": "like20",
    "candycloud": "Candytally",
    "hongxing": "lu88",
    "westdata": "WD-DDR6",
    "niubi": "",
    "liangxin": "",
    "shouhou": "",
    "yun69": "",
    "qingfeng": "",
    "ouo": "",
    "niceduck": "",
    "taoqitu": "",
    "yuyun": "",
    "shenlong": "",
    "yifen": "",
    "llguang": "",
    "yousun": "",
    "freecat": "",
    "lingyun": "",
    "jisu": "",
    "feigou": "",
    "xueshan": "",
    "hneko": "",
    "dingji": "",
    "peiqian": "",
    "juanwang": "",
    "danta": "",
    "chaoshihui": "",
    "nicecloud": "",
    "kuailei": "",
    "ktmcloud": "",
    "tapcloud": "xiaoqi",
    "lvpn": "",
    "shunchang": "",
    "tifa": "",
    "wugui": "",
    "kuajing": ""
  }
};

/* ---- 自动把配置写入页面按钮，无需改动 ---- */
(function () {
  function apply() {
    var S = window.SITE || { aff: {}, code: {} };
    document.querySelectorAll("[data-aff]").forEach(function (el) {
      var key = el.getAttribute("data-aff");
      var url = (S.aff && S.aff[key]) ? S.aff[key].trim() : "";
      if (url) {
        el.setAttribute("href", url);
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "nofollow sponsored noopener");
        el.removeAttribute("data-pending");
      } else {
        el.setAttribute("data-pending", "1");
        el.setAttribute("title", "推广链接待配置");
      }
    });
    document.querySelectorAll("[data-code]").forEach(function (el) {
      var key = el.getAttribute("data-code");
      var code = (S.code && S.code[key]) ? S.code[key].trim() : "";
      var box = el.closest("[data-codebox]");
      if (code) { el.textContent = code; }
      else if (box) { box.style.display = "none"; }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", apply);
  else apply();
})();
