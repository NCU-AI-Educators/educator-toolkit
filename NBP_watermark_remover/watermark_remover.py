#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini Watermark Remover
========================

该脚本用于去除由 Google Gemini 生成的图片中的水印。

原理分析 (Based on https://github.com/journey-ad/gemini-watermark-remover):
1.  **水印合成原理**: Gemini 生成的图片会在右下角添加一个半透明的白色水印。
    合成公式大致为: `Output_Pixel = Alpha * Watermark_White + (1 - Alpha) * Original_Pixel`
    其中 `Watermark_White` 是纯白 (255, 255, 255)。

2.  **逆向去除原理**: 如果我们要恢复 `Original_Pixel`，可以通过逆运算：
    `Original_Pixel = (Output_Pixel - Alpha * 255) / (1 - Alpha)`

3.  **Alpha Map 获取**: 项目作者通过特定的背景图（如全黑背景）捕获了水印的 Alpha 通道信息。
    在全黑背景下 (`Original_Pixel = 0`)，`Output_Pixel = Alpha * 255`，因此 `Alpha = Output_Pixel / 255`。
    脚本中使用了预先提取的 `bg_48.png` and `bg_96.png` 作为 Alpha Map 的源。

4.  **自适应策略**:
    - 如果图片宽和高都大于 1024px，使用大号水印 (96px)，边距 64px。
    - 否则，使用小号水印 (48px)，边距 32px。

依赖:
    - Pillow (PIL)
    - numpy

安装依赖:
    pip install Pillow numpy

使用方法:
    python Tools/watermark_remover.py <input_image_path> [output_image_path]
"""

import os
import sys
import numpy as np
from PIL import Image

# 获取当前脚本所在目录，以便加载资源文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
BG_48_PATH = os.path.join(ASSETS_DIR, 'bg_48.png')
BG_96_PATH = os.path.join(ASSETS_DIR, 'bg_96.png')

# 常量定义
ALPHA_THRESHOLD = 0.002
MAX_ALPHA = 0.99
LOGO_VALUE = 255.0

class WatermarkRemover:
    def __init__(self):
        self.alpha_maps = {}
        self._load_assets()

    def _load_assets(self):
        """加载背景图并计算 Alpha Map"""
        if not os.path.exists(BG_48_PATH) or not os.path.exists(BG_96_PATH):
            raise FileNotFoundError(f"Assets not found. Please ensure {BG_48_PATH} and {BG_96_PATH} exist.")

        self.alpha_maps[48] = self._calculate_alpha_map(BG_48_PATH)
        self.alpha_maps[96] = self._calculate_alpha_map(BG_96_PATH)

    def _calculate_alpha_map(self, bg_path):
        """从背景图中计算 Alpha Map"""
        img = Image.open(bg_path).convert('RGB')
        # 转换为 numpy 数组，形状 (H, W, 3)
        img_arr = np.array(img, dtype=np.float32)
        
        # 取 RGB 中的最大值作为亮度，并归一化到 0-1
        # shape: (H, W)
        alpha_map = np.max(img_arr, axis=2) / 255.0
        return alpha_map

    def _detect_config(self, width, height):
        """根据图片尺寸检测水印配置"""
        if width > 1024 and height > 1024:
            return {
                'logo_size': 96,
                'margin_right': 64,
                'margin_bottom': 64
            }
        else:
            return {
                'logo_size': 48,
                'margin_right': 32,
                'margin_bottom': 32
            }

    def _calculate_position(self, width, height, config):
        """计算水印位置"""
        logo_size = config['logo_size']
        margin_right = config['margin_right']
        margin_bottom = config['margin_bottom']

        return {
            'x': width - margin_right - logo_size,
            'y': height - margin_bottom - logo_size,
            'width': logo_size,
            'height': logo_size
        }

    def process_image(self, input_path, output_path=None):
        """处理图片去除水印"""
        try:
            img = Image.open(input_path).convert('RGB')
        except Exception as e:
            print(f"Error opening image {input_path}: {e}")
            return False

        width, height = img.size
        img_arr = np.array(img, dtype=np.float32)

        # 1. 检测配置
        config = self._detect_config(width, height)
        logo_size = config['logo_size']
        
        # 2. 计算位置
        pos = self._calculate_position(width, height, config)
        x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']

        # 3. 获取对应的 Alpha Map
        alpha_map = self.alpha_maps[logo_size]

        # 4. 提取水印区域
        # 注意: numpy 索引是 [row, col] 即 [y, x]
        roi = img_arr[y:y+h, x:x+w]

        # 确保 ROI 和 Alpha Map 尺寸一致 (防止边缘溢出等情况，虽然理论上位置计算已保证)
        if roi.shape[:2] != alpha_map.shape:
            print(f"Warning: ROI shape {roi.shape} does not match Alpha Map shape {alpha_map.shape}. Skipping.")
            return False

        # 5. 应用逆向混合算法 (Vectorized operation)
        # 扩展 alpha_map 维度以匹配 RGB 通道: (H, W) -> (H, W, 1)
        alpha_expanded = alpha_map[:, :, np.newaxis]

        # 避免除以 0 或过大的 alpha
        # 这里的 clip 对应 JS 中的 Math.min(alpha, MAX_ALPHA)
        alpha_safe = np.clip(alpha_expanded, 0, MAX_ALPHA)
        
        # JS 逻辑: if (alpha < ALPHA_THRESHOLD) continue;
        # 我们可以使用 mask 来只处理 alpha 足够大的像素，或者直接计算全量 (numpy 很快)
        # 为了精确复刻，我们全量计算，因为小 alpha 对结果影响微乎其微，且除数 1-alpha 近似 1
        
        one_minus_alpha = 1.0 - alpha_safe

        # Original = (Watermarked - Alpha * 255) / (1 - Alpha)
        restored_roi = (roi - alpha_safe * LOGO_VALUE) / one_minus_alpha

        # Clip 结果到 0-255 并四舍五入
        restored_roi = np.clip(np.round(restored_roi), 0, 255)

        # 将处理后的 ROI 放回原图
        # 只有 alpha > threshold 的地方才替换，以避免对背景造成不必要的数值误差干扰
        # (虽然 JS 代码是对每个像素判断，如果不满足 threshold 就不动)
        mask = alpha_expanded > ALPHA_THRESHOLD
        
        # numpy where: condition, x, y. 如果 mask 为 True 使用 restored，否则保持 roi
        final_roi = np.where(mask, restored_roi, roi)

        img_arr[y:y+h, x:x+w] = final_roi

        # 6. 保存结果
        result_img = Image.fromarray(img_arr.astype(np.uint8))
        
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_clean{ext}"
        
        result_img.save(output_path)
        print(f"Successfully processed: {input_path} -> {output_path}")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python watermark_remover.py <input_image> [output_image]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    try:
        remover = WatermarkRemover()
        remover.process_image(input_path, output_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
