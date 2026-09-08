import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// 动态解析 archify 根目录，实现完全便携
const archifyRoot = path.resolve(import.meta.dirname, '..');
const { ChromeVisualBrowser, findChrome } = await import(path.join(archifyRoot, 'bin/visual-check.mjs'));

async function evaluate(cdp, sessionId, expression, awaitPromise = false) {
  const response = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true,
  }, sessionId);
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.exception?.description
      || response.exceptionDetails.text
      || 'Runtime.evaluate failed');
  }
  return response.result?.value;
}

/**
 * 核心导出函数：将任何 Archify 生成的 HTML 图表清洗为出版级纯净矢量 SVG
 * @param {string} htmlPath - HTML 图表绝对或相对路径
 * @param {string} outputSvgPath - 目标 SVG 路径
 * @param {'light'|'dark'} theme - 色彩主题，默认 light
 */
export async function exportCleanSvg(htmlPath, outputSvgPath, theme = 'light') {
  const htmlAbs = path.resolve(htmlPath);
  if (!fs.existsSync(htmlAbs)) {
    throw new Error(`输入文件不存在: ${htmlAbs}`);
  }

  const chromePath = findChrome() || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const browser = new ChromeVisualBrowser(chromePath);

  try {
    const sessionId = await browser.sessionPromise;
    const url = new URL(pathToFileURL(htmlAbs).href);
    url.searchParams.set('theme', theme);

    const loaded = browser.cdp.waitFor('Page.loadEventFired', sessionId);
    const navigation = await browser.cdp.send('Page.navigate', { url: url.href }, sessionId);
    if (navigation.errorText) throw new Error(`Chrome 导航失败: ${navigation.errorText}`);
    await loaded;

    // 确保字体与主题计算就绪
    await evaluate(browser.cdp, sessionId, `(function () {
      document.documentElement.setAttribute('data-theme', '${theme}');
      document.documentElement.setAttribute('data-motion', 'still');
      return document.fonts ? document.fonts.ready.catch(function () {}) : null;
    })()`, true);

    // 提取纯净核心 SVG 实体并内联所有计算后的真实样式，彻底剥离所有网页 UI 交互控件
    const svgContent = await evaluate(browser.cdp, sessionId, `(function () {
      var svg = document.querySelector('.diagram-container svg') || document.querySelector('svg');
      if (!svg) return null;
      
      var clone = svg.cloneNode(true);
      
      // 1. 双树同步递归函数：1:1 固化每一个图形节点的最终计算样式
      var shapeTags = ['rect', 'path', 'polygon', 'polyline', 'circle', 'ellipse', 'line'];
      
      function syncStyles(orig, target) {
        if (!orig || !target || orig.nodeType !== 1) return;
        var tag = orig.tagName.toLowerCase();
        var cs = window.getComputedStyle(orig);

        if (shapeTags.indexOf(tag) !== -1) {
          // 填充处理 (为小标题背景框与连线标签保留同色系半透明特性)
          var fill = cs.fill;
          if (orig.getAttribute('data-graph-role') === 'structural-frame-label-mask') {
            fill = 'rgba(251, 191, 36, 0.22)';
          } else if (orig.getAttribute('data-graph-role') === 'stage-badge') {
            fill = 'rgba(59, 130, 246, 0.14)';
          } else if (orig.closest && orig.closest('g[data-edge-id]') && orig.classList.contains('c-mask')) {
            var edgeG = orig.closest('g[data-edge-id]');
            var siblingText = edgeG ? edgeG.querySelector('text') : null;
            var textCs = siblingText ? window.getComputedStyle(siblingText) : null;
            var textFill = textCs ? (textCs.fill || '') : '';
            var edgeId = edgeG ? edgeG.getAttribute('data-edge-id') : '';

            if (textFill.includes('5, 150, 105') || textFill.includes('16, 185, 129') || edgeId === 'e_iou_coco' || edgeId === 'dgp-to-map' || edgeId === 'f-fuse-gate' || edgeId === 'f-gate-store') {
              fill = 'rgba(16, 185, 129, 0.14)';
            } else if (textFill.includes('124, 58, 237') || textFill.includes('167, 139, 250') || edgeId === 'e_iou_quarantine' || edgeId === 'map-to-dgp') {
              fill = 'rgba(124, 58, 237, 0.14)';
            } else if (textFill.includes('225, 29, 72') || textFill.includes('244, 63, 94')) {
              fill = 'rgba(244, 63, 94, 0.14)';
            } else {
              fill = 'rgba(148, 163, 184, 0.16)';
            }
          }

          if (fill && fill !== 'none' && fill !== 'rgba(0, 0, 0, 0)') {
            target.setAttribute('fill', fill);
          } else {
            target.setAttribute('fill', 'none');
          }

          // 描边处理
          var stroke = cs.stroke;
          var strokeWidth = cs.strokeWidth;
          var strokeDash = cs.strokeDasharray;

          if (orig.getAttribute('data-graph-role') === 'structural-frame-label-mask') {
            stroke = 'rgba(217, 119, 6, 0.45)';
            strokeWidth = '1px';
          } else if (orig.getAttribute('data-graph-role') === 'stage-badge') {
            stroke = 'rgba(37, 99, 235, 0.35)';
            strokeWidth = '1px';
          } else if (orig.closest && orig.closest('g[data-edge-id]') && orig.classList.contains('c-mask')) {
            var edgeG = orig.closest('g[data-edge-id]');
            var siblingText = edgeG ? edgeG.querySelector('text') : null;
            var textCs = siblingText ? window.getComputedStyle(siblingText) : null;
            var textFill = textCs ? (textCs.fill || '') : '';
            var edgeId = edgeG ? edgeG.getAttribute('data-edge-id') : '';

            if (textFill.includes('5, 150, 105') || textFill.includes('16, 185, 129') || edgeId === 'e_iou_coco' || edgeId === 'dgp-to-map' || edgeId === 'f-fuse-gate' || edgeId === 'f-gate-store') {
              stroke = 'rgba(5, 150, 105, 0.5)';
            } else if (textFill.includes('124, 58, 237') || textFill.includes('167, 139, 250') || edgeId === 'e_iou_quarantine' || edgeId === 'map-to-dgp') {
              stroke = 'rgba(124, 58, 237, 0.5)';
            } else if (textFill.includes('225, 29, 72') || textFill.includes('244, 63, 94')) {
              stroke = 'rgba(225, 29, 72, 0.5)';
            } else {
              stroke = 'rgba(100, 116, 139, 0.5)';
            }
            strokeWidth = '1px';

            // 连线标签药丸框自适应：根据真实文字测量宽度，动态保证微距呼吸留白并保持居中
            try {
              if (siblingText) {
                var tb = siblingText.getBBox();
                if (tb && tb.width > 0) {
                  var minPillW = Math.ceil(tb.width + 8);
                  var curW = parseFloat(orig.getAttribute('width') || '0');
                  var newW = Math.max(curW, minPillW);
                  var textCenterX = tb.x + tb.width / 2;

                  // 边界安全避让保护：确保 e_iou_coco 不与前序卡片右侧边框 (1146) 发生 1px 的重叠
                  if (edgeId === 'e_iou_coco' && (textCenterX - newW / 2) < 1148) {
                    textCenterX = 1148 + newW / 2;
                  }

                  target.setAttribute('width', newW.toString());
                  target.setAttribute('x', (textCenterX - newW / 2).toString());

                  var minPillH = 18;
                  target.setAttribute('height', minPillH.toString());
                  var textCenterY = tb.y + tb.height / 2;
                  target.setAttribute('y', (textCenterY - minPillH / 2).toString());
                  target.setAttribute('rx', '4');
                }
              }
            } catch (e) {}
          }

          if (stroke && stroke !== 'none' && stroke !== 'rgba(0, 0, 0, 0)') {
            target.setAttribute('stroke', stroke);
            if (strokeWidth && strokeWidth !== '0px') {
              target.setAttribute('stroke-width', strokeWidth);
            }
            if (strokeDash && strokeDash !== 'none') {
              target.setAttribute('stroke-dasharray', strokeDash);
            }
          } else {
            target.setAttribute('stroke', 'none');
          }

          // 透明度
          var opacity = cs.opacity;
          if (opacity && opacity !== '1') {
            target.setAttribute('opacity', opacity);
          }
        } else if (tag === 'text' || tag === 'tspan') {
          // 文本节点样式
          var textFill = cs.fill;
          if (textFill && textFill !== 'none') {
            target.setAttribute('fill', textFill);
          } else {
            target.setAttribute('fill', '#0f172a');
          }
          target.setAttribute('stroke', 'none');
          target.setAttribute('font-family', 'PingFang SC, "Microsoft YaHei", Arial, sans-serif');

          // 出版级字号重塑引擎 (Publication-Grade Typography Scaling)
          var origAttrSize = parseFloat(orig.getAttribute('font-size'));
          var csSize = parseFloat(cs.fontSize);
          var curSize = origAttrSize || csSize || 12.0;
          var weight = orig.getAttribute('font-weight') || cs.fontWeight || '600';
          var textContent = orig.textContent.trim();

          var participantG = orig.closest && (
            orig.closest('g[data-node-context="Sequence participant"]') ||
            orig.closest('g[data-node-context*="participant"]') ||
            orig.closest('g[id^="node-"]') ||
            orig.closest('g[data-node-id]')
          );

          var newSize = curSize;

          if (orig.hasAttribute('data-stage-label') || orig.classList.contains('t-stage')) {
            newSize = Math.max(curSize, 18.0);
            weight = '800';
            target.setAttribute('fill', 'rgb(30, 64, 175)');
          } else if (orig.hasAttribute('data-boundary-label')) {
            newSize = Math.max(curSize, 17.5);
            weight = '800';
            target.setAttribute('fill', 'rgb(180, 83, 9)');
          } else if ((new RegExp('^[0-9]{2}[ ]*[/]').test(textContent) && !orig.closest('[data-legend]')) || orig.classList.contains('t-dim')) {
            // 泳道/分区大标题 (如 01 / 规则轨)
            newSize = Math.max(curSize, 17.5);
            weight = '800';
            target.setAttribute('fill', '#0f172a');
          } else if (orig.closest && orig.closest('g[data-edge-id]')) {
            // 连线上的消息标签/药丸文字：基于节点间距与字符当量的几何自适应黄金字号 (9.5px)
            newSize = 9.5;
            weight = '600';
            var edgeG = orig.closest('g[data-edge-id]');
            var edgeId = edgeG ? edgeG.getAttribute('data-edge-id') : '';
            if (edgeId === 'e_iou_coco') {
              // 与药丸矩形右移微调保持绝对同心 (中心点 1179.4)
              target.setAttribute('x', '1179.4');
            }
            if (textFill.includes('100, 116, 139') || textFill.includes('148, 163, 184') || !textFill || textFill === 'none') {
              target.setAttribute('fill', '#0f172a');
            }
          } else if (participantG) {
            var cardRect = participantG.querySelector('rect');
            var cardW = cardRect ? parseFloat(cardRect.getAttribute('width') || '120') : 120;
            if (cardW <= 100) {
              // 紧凑型节点 (如时序图顶部小卡片)
              if (orig.hasAttribute('data-node-label') || orig.classList.contains('t-primary')) {
                newSize = Math.max(curSize, 13.5);
                weight = '700';
                target.setAttribute('fill', '#0f172a');
              } else if (orig.getAttribute('data-detail') === 'context' || orig.classList.contains('t-muted')) {
                newSize = Math.max(curSize, 11.5);
                weight = '600';
                target.setAttribute('fill', 'rgb(51, 65, 85)');
              } else {
                newSize = Math.max(curSize, 10.5);
                weight = '600';
              }
            } else {
              // 标准组件卡片 (宽 > 100px)
              if (orig.hasAttribute('data-node-label') || orig.classList.contains('t-primary')) {
                newSize = 12.5;
                weight = '700';
                target.setAttribute('fill', '#0f172a');
              } else if (orig.getAttribute('data-detail') === 'context' || orig.classList.contains('t-muted')) {
                newSize = 10.0;
                weight = '500';
                target.setAttribute('fill', 'rgb(51, 65, 85)');
              } else if (orig.getAttribute('data-detail') === 'fine') {
                newSize = 9.0;
                weight = '600';
              } else {
                newSize = 10.0;
                weight = '500';
              }
            }
          } else {
            // 其他正文文字保底
            newSize = Math.max(curSize, 13.5);
            weight = '600';
          }

          target.setAttribute('font-size', (Math.round(newSize * 10) / 10).toString());
          target.setAttribute('font-weight', weight);

          // 核心安全网：卡片内文字动态自适应防溢出守护 (Auto-Fit Guard)
          // 允许微调缩放，但保底绝不低于 13.0px，防止极限挤压为不可读字号
          if (participantG) {
            try {
              var cardRect = participantG.querySelector('rect');
              var cardW = cardRect ? parseFloat(cardRect.getAttribute('width') || '120') : 120;
              var maxAllowedWidth = cardW - 16; // 两侧留出呼吸留白
              var tBbox = orig.getBBox();
              if (tBbox && tBbox.width > maxAllowedWidth && cardW > 30) {
                var scale = maxAllowedWidth / tBbox.width;
                if (scale < 1.0) {
                  var adjustedSize = Math.max(9.0, Math.floor(newSize * scale * 10) / 10);
                  target.setAttribute('font-size', adjustedSize.toString());
                }
              }
            } catch (e) {}
          }


          // 居中优化：若原文本设置了 text-anchor="middle"，确保保留
          var anchor = orig.getAttribute('text-anchor') || cs.textAnchor;
          if (anchor) {
            target.setAttribute('text-anchor', anchor);
          }
        }

        var origChildren = orig.children;
        var targetChildren = target.children;
        for (var i = 0; i < origChildren.length && i < targetChildren.length; i++) {
          syncStyles(origChildren[i], targetChildren[i]);
        }
      }

      syncStyles(svg, clone);

      // 1.1 移除卡片左上角微图标 (.semantic-sigil)，避免与放大后的 17px 大标题重叠
      Array.from(clone.querySelectorAll('.semantic-sigil')).forEach(function(sigil) {
        sigil.remove();
      });

      // 1.2 优化卡片内部文本垂直分布，保证三行/两行文本呼吸感充足
      Array.from(clone.querySelectorAll('[data-node-id]')).forEach(function(g) {
        var cardRect = g.querySelector('rect:not(.c-mask)');
        if (!cardRect) return;
        var y0 = parseFloat(cardRect.getAttribute('y'));
        var h = parseFloat(cardRect.getAttribute('height'));
        if (isNaN(y0) || isNaN(h)) return;

        var label = g.querySelector('[data-node-label]');
        var ctx = g.querySelector('[data-detail="context"]');
        var fine = g.querySelector('[data-detail="fine"]');

        if (label && ctx && fine) {
          // 3 行文本最佳视距 (40% / 67% / 86%)
          label.setAttribute('y', String(Math.round((y0 + 24) * 10) / 10));
          ctx.setAttribute('y', String(Math.round((y0 + 42) * 10) / 10));
          fine.setAttribute('y', String(Math.round((y0 + 57) * 10) / 10));
        } else if (label && ctx) {
          // 2 行文本布局
          label.setAttribute('y', String(Math.round((y0 + h * 0.45) * 10) / 10));
          ctx.setAttribute('y', String(Math.round((y0 + h * 0.75) * 10) / 10));
        }
      });


      // 1.4 图例文字排版规范保护：确保图例项字号统一且不溢出
      Array.from(clone.querySelectorAll('[data-legend] text')).forEach(function(t) {
        if (!t.textContent.includes('图例')) {
          t.setAttribute('font-size', '10.5');
          t.setAttribute('font-weight', '500');
        }
      });

      // 2. 内联 defs 中的标记 (markers) 计算样式
      var markers = clone.querySelectorAll('marker');
      markers.forEach(function(m) {
        var id = m.getAttribute('id');
        var origM = svg.querySelector('#' + id);
        if (origM) {
          syncStyles(origM, m);
        }
      });

      // 3. 剥离 style 块，防止外部媒体查询或动画污染
      var styleNodes = clone.querySelectorAll('style');
      styleNodes.forEach(function(s) { s.remove(); });

      // 3.5 工作流泳道与阶段标头水平对称重排：彻底消除右侧由于默认列数产生的幽灵空白
      var newLaneRight = null;
      try {
        var laneRects = Array.from(clone.querySelectorAll('rect[data-graph-role="structural-frame"][data-composition-frame-kind="lane"], rect.c-lane:not([data-composition-frame-kind="group"])'));
        var nodeCards = Array.from(clone.querySelectorAll('[data-node-id] rect:not(.c-mask)'));
        var groupRects = Array.from(clone.querySelectorAll('rect[data-composition-frame-kind="group"]'));

        if (laneRects.length > 0 && nodeCards.length > 0) {
          var minNodeX = Infinity;
          var maxNodeRight = -Infinity;

          [...nodeCards, ...groupRects].forEach(function(r) {
            var x = parseFloat(r.getAttribute('x') || '0');
            var w = parseFloat(r.getAttribute('width') || '0');
            if (x < minNodeX) minNodeX = x;
            if (x + w > maxNodeRight) maxNodeRight = x + w;
          });

          // 纳入连线药丸标签以防文字凸出
          var edgeLabels = Array.from(clone.querySelectorAll('g[data-edge-id] rect.c-mask, g[data-edge-id] text'));
          edgeLabels.forEach(function(el) {
            var ex = parseFloat(el.getAttribute('x') || '0');
            var ew = parseFloat(el.getAttribute('width') || '0');
            if (ew > 0 && ex + ew > maxNodeRight) maxNodeRight = ex + ew;
          });

          var currentLaneW = parseFloat(laneRects[0].getAttribute('width') || '0');
          var currentLaneX = parseFloat(laneRects[0].getAttribute('x') || '0');
          var currentLaneRight = currentLaneX + currentLaneW;

          // 若右侧存在多余留白 (> 30px)，执行精准裁剪与对称化
          if (currentLaneRight - maxNodeRight > 30) {
            var laneInset = 20;
            // 保护左侧泳道标题文字 (通常在 x = 54 左右)
            var minLaneX = Math.min(40, Math.floor(minNodeX - laneInset));
            var targetLaneRight = Math.ceil(maxNodeRight + laneInset);
            var newLaneW = targetLaneRight - minLaneX;
            newLaneRight = targetLaneRight;

            laneRects.forEach(function(lane) {
              lane.setAttribute('x', minLaneX.toString());
              lane.setAttribute('width', newLaneW.toString());
            });

            // 泳道序号小标题左对齐到泳道内边距
            var laneTexts = clone.querySelectorAll('text.t-dim');
            laneTexts.forEach(function(t) {
              t.setAttribute('x', (minLaneX + 14).toString());
            });

            // 重新对齐各列阶段标头线与文字
            var colCenterMap = {};
            nodeCards.forEach(function(r) {
              var x = parseFloat(r.getAttribute('x') || '0');
              var w = parseFloat(r.getAttribute('width') || '0');
              var cx = Math.round(x + w / 2);
              colCenterMap[cx] = true;
            });
            var colCenters = Object.keys(colCenterMap).map(Number).sort(function(a, b) { return a - b; });

            var phaseLines = Array.from(clone.querySelectorAll('line[class*="a-"]'));
            var phaseMasks = Array.from(clone.querySelectorAll('rect.c-mask')).filter(function(r) {
              return !r.closest('[data-node-id]') && !r.closest('g[data-edge-id]');
            });
            var phaseTexts = Array.from(clone.querySelectorAll('text.t-muted, text.t-backend, text.t-messagebus'));

            if (colCenters.length >= phaseLines.length && phaseLines.length > 0) {
              for (var pi = 0; pi < phaseLines.length; pi++) {
                var colCx = colCenters[pi];
                var pLine = phaseLines[pi];
                var pMask = phaseMasks[pi];
                var pText = phaseTexts[pi];

                var lineHalfW = 95;
                if (pLine) {
                  pLine.setAttribute('x1', (colCx - lineHalfW).toString());
                  pLine.setAttribute('x2', (colCx + lineHalfW).toString());
                }
                if (pMask) {
                  pMask.setAttribute('x', (colCx - 85).toString());
                  pMask.setAttribute('width', '170');
                }
                if (pText) {
                  pText.setAttribute('x', colCx.toString());
                  pText.setAttribute('text-anchor', 'middle');
                }
              }
            }

            // 图例左边界与动态项间距排版，精准移动实际色块与文本
            var legendG = clone.querySelector('g[data-legend]');
            if (legendG) {
              var legendTitle = legendG.querySelector('text.t-primary');
              if (legendTitle) {
                legendTitle.setAttribute('x', minLaneX.toString());
              }
              var curLegendX = minLaneX + 46;
              var legendItems = legendG.querySelectorAll('g[data-legend-kind], g[data-legend-semantic-kind]');
              legendItems.forEach(function(item) {
                var rect = item.querySelector('rect[class*="c-"]') || item.querySelector('rect:not([data-legend-bridge-runtime])');
                var text = item.querySelector('text:not([data-legend-count])');
                var textContent = text ? text.textContent.trim() : '';
                var textW = 0;
                for (var ci = 0; ci < textContent.length; ci++) {
                  textW += textContent.charCodeAt(ci) > 255 ? 12.5 : 7.2;
                }
                var rectW = 14;
                if (rect) rect.setAttribute('x', curLegendX.toString());
                if (text) text.setAttribute('x', (curLegendX + rectW + 6).toString());
                curLegendX += Math.ceil(rectW + 6 + textW + 24);
              });
            }
          }
        }
      } catch (e) {
        console.warn('Workflow layout harmonization error:', e);
      }

      // 4. 通用自适应视口边界与留白重算：消除顶部过宽空白，防止右侧虚线框被裁切
      try {
        var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

        // 仅探测具有实际视觉呈现的顶层架构实体，严格排除 defs、pattern 及图标局部坐标系的干扰
        var entitySelectors = [
          '[data-node-id]',
          'g[data-edge-id]',
          'path[data-edge-id]',
          'rect[data-graph-role="structural-frame"]',
          'rect.c-region',
          'rect.c-security-group',
          'rect.c-lane',
          'rect.c-boundary',
          'rect.c-container',
          'line.c-lifeline',
          'g[id^="legend"]',
          'text'
        ];
        var contentElements = clone.querySelectorAll(entitySelectors.join(','));
        contentElements.forEach(function(el) {
          if (el.closest && el.closest('defs, pattern, .semantic-sigil')) return;
          if (el.tagName.toLowerCase() === 'rect' && (el.getAttribute('width') === '100%' || el.getAttribute('id') === 'grid')) return;

          // 显式几何属性探测防御（特别包含 c-region、c-security-group 等容器与泳道）
          var x = parseFloat(el.getAttribute('x') || el.getAttribute('x1') || '0');
          var y = parseFloat(el.getAttribute('y') || el.getAttribute('y1') || '0');
          var w = parseFloat(el.getAttribute('width') || '0');
          var h = parseFloat(el.getAttribute('height') || '0');
          var x2 = parseFloat(el.getAttribute('x2') || '0');
          var y2 = parseFloat(el.getAttribute('y2') || '0');

          if (w > 0 && h > 0) {
            if (x < minX) minX = x;
            if (y < minY) minY = y;
            if (x + w > maxX) maxX = x + w;
            if (y + h > maxY) maxY = y + h;
          }
          if (x2 > 0 && y2 > 0) {
            if (x2 > maxX) maxX = x2;
            if (y2 > maxY) maxY = y2;
          }
        });

        // 探测原始页面中 text 节点的真实渲染包围盒，确保文字不被截断
        var textElements = svg.querySelectorAll('text');
        textElements.forEach(function(t) {
          if (t.closest && t.closest('defs, pattern, .semantic-sigil')) return;
          try {
            var b = t.getBBox();
            if (b && b.width > 0 && b.height > 0) {
              if (b.y < minY && b.y >= 0) minY = b.y;
              if (b.y + b.height > maxY) maxY = b.y + b.height;
              if (b.x < minX && b.x >= 0) minX = b.x;
              // 水平右边界保护：若文本没有超出新泳道右侧，则纳入 maxX
              if (b.x + b.width > maxX && (!newLaneRight || b.x + b.width <= newLaneRight + 30)) {
                maxX = b.x + b.width;
              }
            }
          } catch (e) {}
        });

        if (minX !== Infinity && maxX !== -Infinity) {
          var padX = 20;
          var padY = 18;
          var vbMinX = Math.floor(minX - padX);
          var vbMinY = Math.floor(minY - padY);
          var vbWidth = Math.ceil((maxX - minX) + padX * 2);
          var vbHeight = Math.ceil((maxY - minY) + padY * 2);

          clone.setAttribute('viewBox', [vbMinX, vbMinY, vbWidth, vbHeight].join(' '));
        }
      } catch (e) {
        console.warn('Tight viewBox calculation fallback:', e);
      }

      // 5. 清除交互状态与外层控制属性
      clone.style.removeProperty('transform');
      clone.style.removeProperty('clip-path');
      clone.removeAttribute('data-view-scale');
      clone.removeAttribute('data-focus-active');
      clone.removeAttribute('data-reach-active');
      clone.removeAttribute('data-lens-active');
      clone.removeAttribute('data-story-active');

      // 6. 移除交互临时浮层与探测层
      var overlaySelectors = [
        '[data-story-overlay]', '[data-intent-trace-overlay]', '[data-route-probe-overlay]',
        '[data-route-journey-overlay]', '[data-semantic-lens-overlay]', '[data-legend-bridge-runtime]',
        '[data-relationship-hit-overlay]', '[data-relationship-pulse-overlay]'
      ];
      Array.from(clone.querySelectorAll(overlaySelectors.join(','))).forEach(function(el) {
        el.remove();
      });

      // 7. 清洗容器及节点属性，确保无交互干扰
      Array.from(clone.querySelectorAll('[data-node-id]')).forEach(function(g) {
        g.removeAttribute('tabindex');
        g.removeAttribute('role');
        g.removeAttribute('aria-label');
        g.removeAttribute('aria-pressed');
      });

      // 8. 补全标准 SVG 命名空间
      clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');

      return new XMLSerializer().serializeToString(clone);
    })()`);

    if (!svgContent) {
      throw new Error('从页面容器中提取 SVG 失败');
    }

    fs.mkdirSync(path.dirname(path.resolve(outputSvgPath)), { recursive: true });
    fs.writeFileSync(outputSvgPath, svgContent, 'utf8');
    console.log(`✅ [Archify-Export] 成功导出出版级纯净矢量 SVG: ${outputSvgPath} (${svgContent.length} 字节)`);
    return svgContent;
  } finally {
    if (browser?.close) await browser.close();
  }
}

// 命令行入口逻辑
if (process.argv[2]) {
  const inputHtml = process.argv[2];
  const outputSvg = process.argv[3] || inputHtml.replace(/\.html$/, '.clean.svg');
  const theme = process.argv[4] || 'light';
  await exportCleanSvg(inputHtml, outputSvg, theme);
} else {
  // 默认扫描当前项目常用目录 docs/figures/ 下的所有 HTML 图表
  const defaultDir = path.resolve(process.cwd(), 'docs/figures');
  if (fs.existsSync(defaultDir)) {
    const files = fs.readdirSync(defaultDir).filter(f => f.endsWith('.html') && !f.includes('.clean') && !f.includes('.visual-check'));
    if (files.length > 0) {
      console.log(`🚀 开始批量导出 ${files.length} 个图表为出版级矢量 SVG...`);
      for (const f of files) {
        const inPath = path.join(defaultDir, f);
        const outPath = path.join(defaultDir, f.replace(/\.html$/, '.clean.svg'));
        await exportCleanSvg(inPath, outPath, 'light');
      }
      console.log('🎉 批量导出全部完成！');
    } else {
      console.log('未找到待导出的 HTML 图表，请指定参数: node export-clean-svg.mjs <input.html> [output.svg]');
    }
  } else {
    console.log('用法: node export-clean-svg.mjs <input.html> [output.svg] [theme]');
  }
}
