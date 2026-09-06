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
            var edgeId = edgeG ? edgeG.getAttribute('data-edge-id') : '';
            if (edgeId === 'dgp-to-map' || edgeId === 'f-fuse-gate' || edgeId === 'f-gate-store') {
              fill = 'rgba(16, 185, 129, 0.14)';
            } else if (edgeId === 'map-to-dgp') {
              fill = 'rgba(124, 58, 237, 0.14)';
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
            var edgeId = edgeG ? edgeG.getAttribute('data-edge-id') : '';
            if (edgeId === 'dgp-to-map' || edgeId === 'f-fuse-gate' || edgeId === 'f-gate-store') {
              stroke = 'rgba(5, 150, 105, 0.5)';
            } else if (edgeId === 'map-to-dgp') {
              stroke = 'rgba(124, 58, 237, 0.5)';
            } else {
              stroke = 'rgba(100, 116, 139, 0.5)';
            }
            strokeWidth = '1px';

            // 连线标签药丸框自适应：根据真实文字测量宽度，动态保证两侧各有至少 8px 舒适呼吸内边距并保持居中
            try {
              var siblingText = edgeG ? edgeG.querySelector('text') : null;
              if (siblingText) {
                var tb = siblingText.getBBox();
                if (tb && tb.width > 0) {
                  var minPillW = Math.ceil(tb.width + 16);
                  var curW = parseFloat(orig.getAttribute('width') || '0');
                  var newW = Math.max(curW, minPillW);
                  var textCenterX = tb.x + tb.width / 2;
                  target.setAttribute('width', newW.toString());
                  target.setAttribute('x', (textCenterX - newW / 2).toString());

                  var minPillH = Math.max(parseFloat(orig.getAttribute('height') || '16'), 17);
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

          // 直接读取 HTML 重构后的字号与字重，并应用出版级保底阈值
          var origAttrSize = parseFloat(orig.getAttribute('font-size'));
          var csSize = parseFloat(cs.fontSize);
          var newSize = origAttrSize || csSize || 14.0;
          var weight = orig.getAttribute('font-weight') || cs.fontWeight || '600';
          var textContent = orig.textContent.trim();

          // 检查是否属于时序图参与者节点（Sequence participant）或者小卡片容器
          var participantG = orig.closest && (
            orig.closest('g[data-node-context="Sequence participant"]') ||
            orig.closest('g[data-node-context*="participant"]') ||
            orig.closest('g[id^="node-"]')
          );

          if (participantG) {
            var cardRect = participantG.querySelector('rect');
            var cardW = cardRect ? parseFloat(cardRect.getAttribute('width') || '86') : 86;
            // 当卡片宽度小于等于 100px 时（时序图顶部参与者节点，如 86x54）
            if (cardW <= 100) {
              if (orig.hasAttribute('data-node-label') || orig.classList.contains('t-primary')) {
                newSize = 12.0;
                weight = '700';
              } else if (orig.getAttribute('data-detail') === 'context' || orig.classList.contains('t-muted')) {
                newSize = 8.0;
                weight = '500';
                target.setAttribute('fill', 'rgb(71, 85, 105)');
              }
            } else {
              // 架构图大卡片节点
              if (orig.hasAttribute('data-node-label') || orig.classList.contains('t-primary')) {
                newSize = Math.max(newSize, 17.0);
                weight = '700';
              } else if (orig.getAttribute('data-detail') === 'context') {
                newSize = Math.max(newSize, 13.0);
                weight = '600';
                if (textFill.includes('100, 116, 139') || textFill.includes('148, 163, 184')) {
                  target.setAttribute('fill', 'rgb(51, 65, 85)');
                }
              }
            }
          } else if (orig.hasAttribute('data-stage-label')) {
            newSize = 16.0;
            weight = '800';
            target.setAttribute('fill', 'rgb(30, 64, 175)');
          } else if (orig.hasAttribute('data-boundary-label')) {
            newSize = 16.5;
            weight = '800';
            target.setAttribute('fill', 'rgb(180, 83, 9)');
          } else if (orig.closest && orig.closest('g[data-edge-id]')) {
            // 连线上的消息标签，保持清晰紧凑
            newSize = Math.min(Math.max(newSize, 9.0), 9.5);
            weight = '500';
          } else if (orig.getAttribute('data-detail') === 'context') {
            newSize = Math.max(newSize, 13.0);
            weight = '600';
          } else if (orig.getAttribute('data-detail') === 'fine') {
            newSize = Math.max(newSize, 11.5);
            weight = '700';
          }

          target.setAttribute('font-size', newSize.toString());
          target.setAttribute('font-weight', weight);

          // 溢出防护拦截：对于卡片内文字，若测得渲染宽度仍超过可用宽度，动态缩减字号确保绝不溢出
          if (participantG) {
            try {
              var cardRect = participantG.querySelector('rect');
              var cardW = cardRect ? parseFloat(cardRect.getAttribute('width') || '86') : 86;
              var tBbox = orig.getBBox();
              if (tBbox && tBbox.width > cardW - 8 && cardW > 20) {
                var scale = (cardW - 10) / tBbox.width;
                if (scale < 1.0) {
                  var adjustedSize = Math.max(7.0, Math.floor(newSize * scale * 10) / 10);
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

      // 4. 通用自适应视口边界与留白重算：消除右侧大片空白，保证虚线泳道框完整闭合
      try {
        var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

        // 探测所有具有实际视觉呈现的内容元素（排除全屏背景 rect）
        var contentSelectors = [
          '[data-node-id]', 'g[data-edge-id]', 'rect.c-lane', 'rect.c-boundary',
          'rect.c-container', 'line', 'path', 'text', 'polygon', 'circle', 'ellipse'
        ];
        var contentElements = svg.querySelectorAll(contentSelectors.join(','));
        contentElements.forEach(function(el) {
          if (el.tagName.toLowerCase() === 'rect' && (el.getAttribute('width') === '100%' || el.getAttribute('id') === 'grid')) return;
          if (el.closest && el.closest('defs')) return;
          try {
            var b = el.getBBox();
            if (b && b.width > 0 && b.height > 0) {
              if (b.x < minX) minX = b.x;
              if (b.y < minY) minY = b.y;
              if (b.x + b.width > maxX) maxX = b.x + b.width;
              if (b.y + b.height > maxY) maxY = b.y + b.height;
            }
          } catch (e) {}
        });

        // 进一步探测显式坐标属性（防止特殊 path / lifeline 的边界偏差）
        var allLanes = svg.querySelectorAll('rect.c-lane, rect.c-boundary, rect.c-container, line.c-lifeline');
        allLanes.forEach(function(r) {
          var y = parseFloat(r.getAttribute('y') || r.getAttribute('y1') || '0');
          var h = parseFloat(r.getAttribute('height') || '0');
          var y2 = parseFloat(r.getAttribute('y2') || '0');
          var bottom = Math.max(y + h, y2);
          var x = parseFloat(r.getAttribute('x') || r.getAttribute('x1') || '0');
          var w = parseFloat(r.getAttribute('width') || '0');
          var x2 = parseFloat(r.getAttribute('x2') || '0');
          var right = Math.max(x + w, x2);

          if (!isNaN(bottom) && bottom > maxY) maxY = bottom;
          if (!isNaN(right) && right > maxX) maxX = right;
          if (!isNaN(y) && y < minY) minY = y;
          if (!isNaN(x) && x < minX) minX = x;
        });

        if (minX !== Infinity && maxX !== -Infinity) {
          // 对称优雅的留白：左右留出 24px，上下留出 24px
          var padX = 24;
          var padY = 24;
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
