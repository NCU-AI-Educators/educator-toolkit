#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture Master 5-Layer Sequential Purifier & Auditor
依次对 *.master.md 的五层结构执行 V11 语态净化与专项合规校验：
  Pass 1 (body)          : 幻灯片可视区正文
  Pass 2 (script)        : 逐字稿 (<!-- - **类型**: 逐字稿 -->)
  Pass 3 (dialogue)      : 对白   (<!-- - **类型**: 对白 -->)
  Pass 4 (explanation)   : 自学解释 (<!-- - **类型**: 解释 -->)
  Pass 5 (teaching_plan) : 教学设计 (<!-- - **类型**: 教学设计 -->)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 1. 全局 V11 禁用词与确定性替换字典 (Global V11 Blacklist & Replacements)
# ============================================================================

GLOBAL_BLACKLIST_REPLACEMENTS: List[Tuple[str, str, str]] = [
    # (禁用词/正则, 建议替换词, 原因分类)
    ("级联失效", "连锁失效", "机械直译 Cascading"),
    ("级联错误", "连锁报错", "机械直译 Cascading"),
    ("级联放大", "连带放大", "机械直译 Cascading"),
    ("级联崩溃", "连锁崩溃", "机械直译 Cascading"),
    ("级联", "连锁", "机械直译 Cascading"),
    ("注意力雪崩", "注意力稀释", "浮夸文学修辞"),
    ("性能雪崩", "性能骤降", "浮夸文学修辞"),
    ("雪崩式", "连锁式", "浮夸文学修辞"),
    ("雪崩", "骤降", "浮夸文学修辞"),
    ("实操战场", "具体工程场景", "小说式情绪化用词"),
    ("绝境", "执行困境", "小说式情绪化用词"),
    ("坚不可摧", "高可靠性", "空泛夸大修辞"),
    ("生命线", "核心约束", "空泛抒情修辞"),
    ("上下文爆仓", "上下文窗口超限", "非正统工程术语"),
    ("撑爆窗口", "超出窗口上限", "非正统工程术语"),
    ("爆仓", "超限", "非正统工程术语"),
    ("撑爆", "超出上限", "非正统工程术语"),
    ("不言而喻，", "", "无信息量模板过渡词"),
    ("不言而喻", "", "无信息量模板过渡词"),
    ("众所周知，", "", "无信息量模板过渡词"),
    ("众所周知", "", "无信息量模板过渡词"),
    ("综上所述，", "总体而言，", "模板化过渡词"),
    ("物理真机", "真机", "冗余物理修饰"),
    ("物理仪器", "现场仪器", "冗余物理修饰"),
    ("物理意义上", "实际层面上", "冗余物理修饰"),
    ("底层物理机理", "底层技术成因", "冗余物理机理修饰"),
    ("物理机理", "技术原理", "冗余物理机理修饰"),
    ("高保真页面", "排版合规页面", "泛化滥用高保真"),
    ("高保真交付", "完整还原交付", "泛化滥用高保真"),
    ("高保真排版", "规范排版", "泛化滥用高保真"),
    ("高保真矢量", "无损矢量", "泛化滥用高保真"),
    ("正交子模块", "相互独立的子模块", "泛化滥用正交"),
    ("正交切分", "解耦切分", "泛化滥用正交"),
    ("职责正交", "职责互不重叠", "泛化滥用正交"),
    ("正交拆解", "解耦拆解", "泛化滥用正交"),
    ("正交维度", "相互独立的维度", "泛化滥用正交"),
    ("正交方向", "相互独立的方向", "泛化滥用正交"),
    ("正交视角", "互补视角", "泛化滥用正交"),
    ("范式跃迁", "方法转型", "大模型八股腔"),
    ("认知跃迁", "思维转变", "大模型八股腔"),
    ("角色跃迁", "角色转变", "大模型八股腔"),
    ("视觉跃迁", "视觉升级", "大模型八股腔"),
    ("范式升级", "工作方式调整", "大模型八股腔"),
    ("范式革命", "方法变革", "大模型八股腔"),
    ("彻底杜绝", "从机制上拦截", "绝对化承诺用词"),
    ("彻底消除", "有效规避", "绝对化承诺用词"),
    ("瞬间看懂", "直观定位", "自嗨式形容词"),
    ("定海神针", "核心机制", "自嗨式夸大修辞"),
    ("降维打击", "显著优势", "互联网营销黑话"),
    ("史诗级", "系统级", "互联网营销黑话"),
    ("救命稻草", "关键排障手段", "情绪化夸大修辞"),
    ("核武器", "核心工具", "情绪化夸大修辞"),
    ("灵魂拷问", "关键问题", "自媒体标题党"),
    ("灵魂一击", "核心追问", "自媒体标题党"),
    ("打通闭环", "形成完整闭环", "互联网汇报黑话"),
    ("心智主权", "决策主导权", "AI 生造词"),
    ("代码体力流", "基础编码工作", "AI 生造词"),
    ("执行剥离切割", "剔除异常数据", "AI 生造词"),
    ("逆向倒灌", "向上游蔓延", "AI 生造词"),
    ("底座核域", "核心底层模块", "AI 生造词"),
    ("斩截脱耦", "消除耦合依赖", "AI 生造词"),
    ("研究基座", "研究基础", "AI 生造词"),
    ("认知跨越", "思维转变", "AI 生造词"),
    ("极其要命的陷阱", "容易被忽略的风险", "情绪化修辞"),
    ("惨不忍睹", "存在较多缺陷", "情绪化修辞"),
    ("千疮百孔", "漏洞较多", "情绪化修辞"),
    ("小白痛点", "初学者常见问题", "非正式口语"),
    ("深水区", "复杂阶段", "自媒体黑话"),
    ("练兵场", "实践环节", "自媒体黑话"),
    ("试金石", "检验标准", "自媒体黑话"),
    ("生成翻车率", "生成偏离预期率", "非正式口语"),
    ("防翻车", "防偏离", "非正式口语"),
    ("代码翻车", "代码失效", "非正式口语"),
    ("翻车现场", "失控现场", "非正式口语"),
    ("翻车陷阱", "失效陷阱", "非正式口语"),
]

# 仅扫描告警（需结合语境人工/LLM改写，不盲目机械替换的敏感词）
AUDIT_ONLY_KEYWORDS: List[Tuple[str, str]] = [
    (r"赋能", "互联网黑话：建议改为「提供支持 / 提升效率 / 使……成为可能」"),
    (r"抓手", "互联网黑话：建议改为「切入点 / 具体工具 / 校验手段」"),
    (r"颗粒度", "互联网黑话：建议改为「精细度 / 统计口径 / 拆分粒度」"),
    (r"(?<!单例模式)(?<!Singleton\s)单例", "疑似 Exemplar 误译：若指示例请改为「范例 / 最小用例」"),
    (r"跃迁", "AI 八股高频词：除量子物理外建议改为「转变 / 变化 / 调整」"),
    (r"正交", "伪学术泛化：除非指严格数学内积为零/正交实验，否则建议改为「相互独立 / 互不重叠」"),
    (r"高保真", "空洞套话：建议改为「无损矢量 / 排版合规 / 完整还原」"),
    (r"满血", "自媒体黑话：建议改为「完整 / 全量 / 无损」"),
    (r"封神|神级", "自媒体黑话：建议改为「经典 / 成熟 / 业界标准」"),
    (r"绞肉机|命门|死结", "情绪化词汇：建议改为「瓶颈 / 关键制约因素」"),
    (r"(?:指令|提问方式|提示词|角色|行为|消费行为|三阶段|阶段|工作流|定位|架构)演进|演进预告", "AI 汇报腔：建议改为「变化 / 改进 / 怎么写清楚 / 划分阶段」等日常教学表达"),
    (r"结构化追问|发起指向性追问|指向性追问", "AI 汇报腔：建议直接写「继续追问 / 选中代码问 AI」"),
    (r"注入(?:网页|DOM\s*)?上下文|上下文注入|注入语境", "AI 汇报腔：建议直接写「写明标签结构 / 给出背景数据」"),
    (r"代码解构|数据承载格式|实践载体|单点验证与参数化批量|参数化批量|字典配置驱动", "AI 汇报腔：建议直接写「读懂代码 / 数据格式 / 练手场景 / 先跑通一个再批量抓 / 用字典管理循环」"),
    (r"科研数字资产|自动化数字资产|数字资产|回路内掌控|回路上监督|人类监督者|研究监督者|读懂流水线图纸|践行两项工程安全习惯|工程安全习惯", "AI 汇报腔：建议改为「可重复脚本 / 亲手写代码 vs 把关代码 / 研究者 / 查看代码步骤 / 防错好习惯」"),
    (r"混淆变量|混杂变量|阻断混杂|假说操作化|概念操作化|体检去噪|数据体检|诊断探针|链式算子|算子审计|算子统御|局部打样|多维分层交叉|双零静默|静默号|静默账号|静默逻辑偏差|实证洞察|Schema\s*契约|字段契约|输出契约|异构障碍|冲突治理|持久化落盘", "AI 生造复合词/概念包装：建议改为平实课堂口语（如干扰因素、控制变量、落到具体字段、初步检查、看前5行、零互动账号、分析发现、字段说明、格式差异）"),
    (r"非随机缺失|区间删失|规约注入|全链路", "超纲统计学/大厂汇报腔：建议改为平实教学表述（如区间名次折算、区间名次、准备规则文件、全流程/完整流程）"),
    (r"聚合遮蔽|遮蔽效应|空间密度场|闭环互证|归因审计|多元巡检矩阵|穿透聚合|认知升维|代码体系收束|能力收束|共因混杂|静默逻辑|静默编码", "AI 生造复合词/汇报腔：建议改为「总数掩盖内部差异 / 空间热力图 / 互相印证 / 区分相关与因果 / 多变量关联图表 / 拆开看结构 / 图形直观呈现 / 本章代码小结 / 共同影响因素 / 不报错却画错的隐蔽错误」"),
]

# Pass 3 对白层专属禁用词与句首清理正则
DIALOGUE_SYCOPHANTIC_PATTERNS: List[Tuple[str, str, str]] = [
    (r"(?:哈哈|哇|天哪|哎呀|噢)[，！!、\s]*", "", "对白层：情绪化拟声起手词"),
    (r"对对对[，！!、\s]*", "", "对白层：敷衍叠词口癖"),
    (r"太(?:扎心|形象|透彻|真实|巧妙|清爽|震撼|酷|有共鸣|到位|贴切)了[，！!。、\s]*", "", "对白层：吹捧式赞叹套话"),
    (r"(?:真是)?(?:一针见血|醍醐灌顶|豁然开朗)[，！!。、\s]*", "", "对白层：成语捧哏套话"),
    (r"比喻得(?:特别|太|非常)(?:到位|贴切|形象)(?:了)?[，！!。、\s]*", "", "对白层：吹捧比喻套话"),
    (r"(?:完全正确|非常准确|一点不错|问到点子上了|抓到了核心|观察得非常仔细|观察得很仔细|说得非常透彻|切中要害|满分通关)[，！!。、\s]*", "", "对白层：居高临下评判套话"),
]

# Pass 4 自学解释层专属禁用词（教案黑话倒灌）
EXPLANATION_FORBIDDEN_PATTERNS: List[Tuple[str, str]] = [
    (r"(?:旨在)?(?:引导|培养|考查|提高|启发|训练|帮助)学生", "自学解释层严禁倒灌第三人称教案黑话（请直接面向学生阐述技术机理）"),
    (r"布鲁姆|Bloom|加涅|Gagne|认知梯度|大纲评价体系|教学设计依据|课程思政融入点", "自学解释层严禁出现教学论/教研督导汇报术语"),
    (r"【自学导读】", "自学解释层 ### 标题禁止重复写【自学导读】前缀（脚本会自动挂载徽章）"),
]

# Pass 5 教学设计层专属禁用词（自夸式元评价）
TEACHING_PLAN_SELF_PRAISE_REPLACEMENTS: List[Tuple[str, str, str]] = [
    ("极具课堂互动效果", "有助于激发课堂讨论", "教学设计层：自夸式元评价"),
    ("极具视觉冲击力", "直观展示对比关系", "教学设计层：自夸式元评价"),
    ("巧妙呼应", "前后对照呼应", "教学设计层：自夸式元评价"),
    ("完美闭环", "形成完整验证闭环", "教学设计层：自夸式元评价"),
    ("瞬间抓人", "快速聚焦核心问题", "教学设计层：自夸式元评价"),
    ("实战眼力", "工程排障能力", "教学设计层：自夸式元评价"),
]


# ============================================================================
# 2. 数据结构与 Master 单页五层解析器 (Slide & 5-Layer Parser)
# ============================================================================

COMMENT_BLOCK_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
COMMENT_TYPE_RE = re.compile(
    r"^\s*-\s*\*\*类型\*\*\s*[:：]\s*(逐字稿|对白|解释|教学设计)\s*$",
    re.MULTILINE,
)

PASS_MAP = {
    "1": "body",
    "2": "script",
    "3": "dialogue",
    "4": "explanation",
    "5": "teaching_plan",
    "body": "body",
    "script": "script",
    "dialogue": "dialogue",
    "explanation": "explanation",
    "teaching_plan": "teaching_plan",
    "all": "all",
}

TYPE_TO_LAYER = {
    "逐字稿": "script",
    "对白": "dialogue",
    "解释": "explanation",
    "教学设计": "teaching_plan",
}

LAYER_CN_NAME = {
    "body": "Pass 1 [幻灯片正文 (Slide Body)]",
    "script": "Pass 2 [逐字稿 (Script)]",
    "dialogue": "Pass 3 [对白 (Dialogue)]",
    "explanation": "Pass 4 [自学解释 (Explanation)]",
    "teaching_plan": "Pass 5 [教学设计 (Teaching Plan)]",
}


@dataclass
class Issue:
    slide_idx: int
    layer: str
    rule: str
    detail: str
    snippet: str = ""


@dataclass
class SlideSegment:
    """表示单张幻灯片内的一个片段（可视区文本 或 HTML 注释块）"""
    is_comment: bool
    raw_text: str
    layer: str  # 'body' | 'script' | 'dialogue' | 'explanation' | 'teaching_plan' | 'other_comment'


@dataclass
class ParsedSlide:
    slide_idx: int  # 1-based slide index
    segments: List[SlideSegment] = field(default_factory=list)

    def reconstruct(self) -> str:
        return "".join(seg.raw_text for seg in self.segments)

    def get_layer_segments(self, layer_name: str) -> List[SlideSegment]:
        return [seg for seg in self.segments if seg.layer == layer_name]


def split_frontmatter_and_slides(content: str) -> Tuple[str, List[str]]:
    """
    分离顶部 YAML frontmatter 与各张幻灯片（以独立行 --- 为边界）。
    返回 (frontmatter_with_delimiter, slide_raw_strings)
    """
    # 匹配文件开头的 --- ... ---
    fm_match = re.match(r"\A(---\n.*?\n---\n)", content, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        rest = content[fm_match.end():]
    else:
        frontmatter = ""
        rest = content

    # 使用独立行的 \n---\n 切分幻灯片
    parts = re.split(r"(\n---\n)", rest)
    slides: List[str] = []
    # parts 结构: [slide1, '\n---\n', slide2, '\n---\n', slide3, ...]
    # 我们将分隔符保存在单独列表或拼回，为了无损还原，记录完整切分
    return frontmatter, parts


def parse_slide_segments(slide_idx: int, slide_text: str) -> ParsedSlide:
    """将单张幻灯片切分为可视区片段与四类注释舱片段，保证 reconstruct() 100% 无损还原。"""
    segments: List[SlideSegment] = []
    last_idx = 0
    for match in COMMENT_BLOCK_RE.finditer(slide_text):
        start, end = match.span()
        if start > last_idx:
            segments.append(
                SlideSegment(
                    is_comment=False,
                    raw_text=slide_text[last_idx:start],
                    layer="body",
                )
            )
        comment_full = match.group(0)
        comment_inner = match.group(1)
        type_match = COMMENT_TYPE_RE.search(comment_inner)
        if type_match:
            cn_type = type_match.group(1)
            layer = TYPE_TO_LAYER.get(cn_type, "other_comment")
        else:
            layer = "other_comment"
        segments.append(
            SlideSegment(
                is_comment=True,
                raw_text=comment_full,
                layer=layer,
            )
        )
        last_idx = end

    if last_idx < len(slide_text):
        segments.append(
            SlideSegment(
                is_comment=False,
                raw_text=slide_text[last_idx:],
                layer="body",
            )
        )

    return ParsedSlide(slide_idx=slide_idx, segments=segments)


# ============================================================================
# 3. 辅助保护工具：保护代码块、图片路径与 HTML 标签属性
# ============================================================================

PROTECTED_SPAN_RE = re.compile(
    r"(```.*?```|`[^`\n]+`|!\[[^\]]*\]\([^)]+\)|<style\b[^>]*>.*?</style>|<(?:/?[a-zA-Z])[^>]*>)",
    re.DOTALL,
)


def apply_outside_protected(text: str, transform_fn) -> str:
    """仅对代码块、行内代码、Markdown 图片语法和 HTML 标签外部的纯文本执行替换"""
    out = []
    last_idx = 0
    for m in PROTECTED_SPAN_RE.finditer(text):
        s, e = m.span()
        if s > last_idx:
            out.append(transform_fn(text[last_idx:s]))
        out.append(m.group(0))
        last_idx = e
    if last_idx < len(text):
        out.append(transform_fn(text[last_idx:]))
    return "".join(out)


def strip_protected_for_scan(text: str) -> str:
    """移除代码块、图片链接路径与 HTML 标签属性后用于纯文本扫描"""
    return PROTECTED_SPAN_RE.sub(" ", text)


# ============================================================================
# 4. 五层专项审查与净化实现 (Pass 1 ~ Pass 5)
# ============================================================================

def audit_and_fix_common_v11(
    slide_idx: int, layer: str, text: str, do_fix: bool
) -> Tuple[str, List[Issue]]:
    """通用 V11 黑名单扫描与替换（作用于全部 5 层）"""
    issues: List[Issue] = []

    def _replace_chunk(chunk: str) -> str:
        res = chunk
        for bad, good, reason in GLOBAL_BLACKLIST_REPLACEMENTS:
            if bad in res:
                issues.append(
                    Issue(
                        slide_idx=slide_idx,
                        layer=layer,
                        rule=f"V11黑名单[{reason}]",
                        detail=f"命中禁用词「{bad}」→ 建议替换为「{good or '(删除)'}」",
                        snippet=bad,
                    )
                )
                if do_fix:
                    res = res.replace(bad, good)
        return res

    updated_text = apply_outside_protected(text, _replace_chunk)

    # 扫描仅告警词汇
    scan_text = strip_protected_for_scan(updated_text)
    for pat, msg in AUDIT_ONLY_KEYWORDS:
        for m in re.finditer(pat, scan_text):
            issues.append(
                Issue(
                    slide_idx=slide_idx,
                    layer=layer,
                    rule="V11语境审查词",
                    detail=msg,
                    snippet=m.group(0),
                )
            )

    return updated_text, issues


# ----------------------------------------------------------------------------
# Pass 1: 幻灯片正文 (Slide Body)
# ----------------------------------------------------------------------------
def process_pass1_body(slide: ParsedSlide, do_fix: bool) -> List[Issue]:
    issues: List[Issue] = []
    for seg in slide.get_layer_segments("body"):
        new_text, v11_issues = audit_and_fix_common_v11(
            slide.slide_idx, "body", seg.raw_text, do_fix
        )
        issues.extend(v11_issues)

        scan_text = strip_protected_for_scan(new_text)

        # 1. 检查残留的 ssot.md 跨文档图表编号 (图 9-1, 表 9-2 等)
        for m in re.finditer(r"(?:图|表)\s*\d+\s*[-–—]\s*\d+", scan_text):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="body",
                    rule="SSOT跨文档编号残留",
                    detail=f"正文中残留母稿编号「{m.group(0)}」，应改为本页自然空间指代",
                    snippet=m.group(0),
                )
            )

        # 2. 检查标题党感叹号 (## 标题含 ！)
        for m in re.finditer(r"^#{1,3}\s+.*！.*$", scan_text, re.MULTILINE):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="body",
                    rule="标题感叹号克制",
                    detail=f"标题含感叹号：「{m.group(0).strip()}」",
                    snippet=m.group(0).strip(),
                )
            )

        # 3. 检查说教式第二人称
        for m in re.finditer(r"(?:你必须|你要知道|你们记住|帮你搞定|帮你拦截)", scan_text):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="body",
                    rule="正文说教第二人称",
                    detail=f"正文含说教口吻「{m.group(0)}」，建议改为客观第三人称工程陈述",
                    snippet=m.group(0),
                )
            )

        if do_fix:
            seg.raw_text = new_text

    # 检查整张 Slide 的 <div> 与 </div> 标签配对闭合
    full_body = "".join(s.raw_text for s in slide.get_layer_segments("body"))
    body_no_code = re.sub(r"```.*?```|`[^`\n]+`", "", full_body, flags=re.DOTALL)
    open_divs = len(re.findall(r"<div\b[^>]*>", body_no_code))
    close_divs = len(re.findall(r"</div\s*>", body_no_code))
    if open_divs != close_divs:
        issues.append(
            Issue(
                slide_idx=slide.slide_idx,
                layer="body",
                rule="HTML容器闭合校验",
                detail=f"<div> 开启数 ({open_divs}) 与 </div> 闭合数 ({close_divs}) 不一致",
            )
        )

    return issues


# ----------------------------------------------------------------------------
# Pass 2: 逐字稿 (Script)
# ----------------------------------------------------------------------------
def process_pass2_script(slide: ParsedSlide, do_fix: bool) -> List[Issue]:
    issues: List[Issue] = []
    for seg in slide.get_layer_segments("script"):
        new_text, v11_issues = audit_and_fix_common_v11(
            slide.slide_idx, "script", seg.raw_text, do_fix
        )
        issues.extend(v11_issues)

        # 提取内容正文区
        scan_text = strip_protected_for_scan(new_text)

        # 1. 检查禁用第二人称（你/你们/你的/帮你/咱们）
        for m in re.finditer(r"(?:你们|你的|帮你|咱们|(?<!迷你)你(?!好))", scan_text):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="script",
                    rule="逐字稿人称红线(Node07)",
                    detail=f"逐字稿出现禁用人称「{m.group(0)}」，应改用「大家 / 研究者 / 开发者」或省略主语",
                    snippet=m.group(0),
                )
            )

        # 2. 检查超长定语链（单分句 > 55 个汉字无标点停顿）
        clauses = re.split(r"[。！？；：，、\n]", scan_text)
        for cl in clauses:
            cjk_count = len(re.findall(r"[\u4e00-\u9fff]", cl))
            if cjk_count > 45:
                issues.append(
                    Issue(
                        slide_idx=slide.slide_idx,
                        layer="script",
                        rule="逐字稿超长分句(朗读测试)",
                        detail=f"单分句含 {cjk_count} 个汉字无标点停顿，不利于讲台朗读，需拆分为短句",
                        snippet=cl.strip()[:40] + "...",
                    )
                )

        # 3. 检查残留的母稿图表号或内部文件名
        for m in re.finditer(r"(?:图|表)\s*\d+\s*[-–—]\s*\d+|fig\d+_[a-zA-Z0-9_]+\.svg|\d{10,}\.png", scan_text):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="script",
                    rule="逐字稿内部编号/文件名泄露",
                    detail=f"逐字稿中含不可见编号或文件名「{m.group(0)}」，应改为「如屏幕右侧流程图所示」等口语指代",
                    snippet=m.group(0),
                )
            )

        # 4. 检查逐字稿句末独立换行与 2 空格缩进 (对齐 Node 11)
        inline_sent_matches = list(re.finditer(r"([。！？])(?![”’）\)\n\s])", new_text))
        if inline_sent_matches:
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="script",
                    rule="逐字稿句末独立换行(Node11)",
                    detail=f"发现 {len(inline_sent_matches)} 处句末未独立换行，需按完整句拆行并保持 2 空格缩进",
                )
            )
            if do_fix:
                new_text = re.sub(r"([。！？])(?![”’）\)\n\s])", r"\1\n  ", new_text)

        if do_fix:
            seg.raw_text = new_text

    return issues


# ----------------------------------------------------------------------------
# Pass 3: 对白 (Dialogue)
# ----------------------------------------------------------------------------
def process_pass3_dialogue(slide: ParsedSlide, do_fix: bool) -> List[Issue]:
    issues: List[Issue] = []
    for seg in slide.get_layer_segments("dialogue"):
        new_text, v11_issues = audit_and_fix_common_v11(
            slide.slide_idx, "dialogue", seg.raw_text, do_fix
        )
        issues.extend(v11_issues)

        # 1. 扫描并清理迎合赞叹词、情绪化拟声词与套路化表扬词
        for pat, repl, reason in DIALOGUE_SYCOPHANTIC_PATTERNS:
            for m in re.finditer(pat, new_text):
                issues.append(
                    Issue(
                        slide_idx=slide.slide_idx,
                        layer="dialogue",
                        rule=reason,
                        detail=f"命中戏剧化捧哏/评判口癖「{m.group(0).strip()}」",
                        snippet=m.group(0).strip(),
                    )
                )
            if do_fix:
                new_text = re.sub(pat, repl, new_text)

        # 2. 检查感叹号密度 (单页对白 ！ 总数 <= 1)
        excl_matches = list(re.finditer(r"！", new_text))
        if len(excl_matches) > 1:
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="dialogue",
                    rule="对白感叹号密度超标(Node07b)",
                    detail=f"单页对白含 {len(excl_matches)} 个感叹号「！」（规范要求 ≤ 1 个）",
                    snippet=f"共 {len(excl_matches)} 处「！」",
                )
            )
            if do_fix:
                # 保留最多 1 个感叹号（或者全部陈述句感叹号转为句号）
                count = 0
                chars = list(new_text)
                for idx, ch in enumerate(chars):
                    if ch == "！":
                        count += 1
                        if count >= 1:
                            chars[idx] = "。"
                new_text = "".join(chars)

        # 3. 检查音频播客中的强视觉依赖词
        for m in re.finditer(
            r"如(?:左|右|上|下)图所示|大家看这张图|看屏幕(?:左|右)侧|(?:左|右)栏|(?:左|右)表|(?:左|右)(?:上|下)角|底部(?:的)?[^，。；\n]{0,8}(?:图|表)|表格(?:第[一二三四五六七八九十\d]+列|最后一行|最(?:左|右)边)",
            new_text,
        ):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="dialogue",
                    rule="对白强视觉依赖词(Node07b)",
                    detail=f"双人播客对白应去视觉化，避免使用「{m.group(0)}」",
                    snippet=m.group(0),
                )
            )

        if do_fix:
            seg.raw_text = new_text

    return issues


# ----------------------------------------------------------------------------
# Pass 4: 自学解释 (Explanation)
# ----------------------------------------------------------------------------
def process_pass4_explanation(slide: ParsedSlide, do_fix: bool) -> List[Issue]:
    issues: List[Issue] = []
    for seg in slide.get_layer_segments("explanation"):
        new_text, v11_issues = audit_and_fix_common_v11(
            slide.slide_idx, "explanation", seg.raw_text, do_fix
        )
        issues.extend(v11_issues)

        # 1. 检查教案黑话倒灌与冗余【自学导读】前缀
        for pat, msg in EXPLANATION_FORBIDDEN_PATTERNS:
            for m in re.finditer(pat, new_text):
                issues.append(
                    Issue(
                        slide_idx=slide.slide_idx,
                        layer="explanation",
                        rule="自学解释视角与格式规范(Node08)",
                        detail=f"{msg}（命中：「{m.group(0)}」）",
                        snippet=m.group(0),
                    )
                )
        if do_fix:
            # 自动移除 ### 标题中的 【自学导读】冗余前缀
            new_text = re.sub(
                r"(###\s+\*\*)【自学导读】[:：]?\s*",
                r"\1",
                new_text,
            )

        # 2. 检查泄露底层文件名 (.svg / .png) 或 CSS 类名或母稿编号
        for m in re.finditer(
            r"fig\d+_[a-zA-Z0-9_]+\.svg|slide_[a-zA-Z0-9_]+\.svg|\d{10,}\.png|(?:图|表)\s*\d+\s*[-–—]\s*\d+",
            new_text,
        ):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="explanation",
                    rule="自学解释内部文件名/母稿编号泄露",
                    detail=f"严禁向学生暴露底层文件名或跨文档编号「{m.group(0)}」，请改为「如本页架构图所示」",
                    snippet=m.group(0),
                )
            )

        # 3. 检查字数区间 (建议 150 ~ 450 汉字)
        cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", new_text))
        if cjk_chars < 120:
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="explanation",
                    rule="自学解释信息密度偏低(Node08)",
                    detail=f"自学解释仅 {cjk_chars} 个汉字（标准要求 250~350 字，含核心结论、机理拆解、自学思考）",
                )
            )

        if do_fix:
            seg.raw_text = new_text

    return issues


# ----------------------------------------------------------------------------
# Pass 5: 教学设计 (Teaching Plan)
# ----------------------------------------------------------------------------
def process_pass5_teaching_plan(slide: ParsedSlide, do_fix: bool) -> List[Issue]:
    issues: List[Issue] = []
    for seg in slide.get_layer_segments("teaching_plan"):
        new_text, v11_issues = audit_and_fix_common_v11(
            slide.slide_idx, "teaching_plan", seg.raw_text, do_fix
        )
        issues.extend(v11_issues)

        # 1. 扫描并替换教学设计层自夸式元评价
        for bad, good, reason in TEACHING_PLAN_SELF_PRAISE_REPLACEMENTS:
            if bad in new_text:
                issues.append(
                    Issue(
                        slide_idx=slide.slide_idx,
                        layer="teaching_plan",
                        rule=reason,
                        detail=f"命中教案自夸表述「{bad}」→ 建议改为「{good}」",
                        snippet=bad,
                    )
                )
                if do_fix:
                    new_text = new_text.replace(bad, good)

        # 2. 检查泄露底层文件名或内部改稿备注
        for m in re.finditer(
            r"fig\d+_[a-zA-Z0-9_]+\.svg|\d{10,}\.png|保留原讲义第|注释舱",
            new_text,
        ):
            issues.append(
                Issue(
                    slide_idx=slide.slide_idx,
                    layer="teaching_plan",
                    rule="教学设计内部文件名/改稿备注残留",
                    detail=f"教学设计中残留内部标识「{m.group(0)}」",
                    snippet=m.group(0),
                )
            )

        if do_fix:
            seg.raw_text = new_text

    return issues


# ============================================================================
# 5. 主流程调度与 CLI 入口 (Main Orchestrator)
# ============================================================================

PASS_PROCESSORS = {
    "body": process_pass1_body,
    "script": process_pass2_script,
    "dialogue": process_pass3_dialogue,
    "explanation": process_pass4_explanation,
    "teaching_plan": process_pass5_teaching_plan,
}

ORDERED_LAYERS = ["body", "script", "dialogue", "explanation", "teaching_plan"]

_PART_SEQ_ORDER = {"上": 0, "中": 1, "下": 2}
_CN_NUM_SEQ_ORDER = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}
_NUMBERED_HEADING_RE = re.compile(
    r"^(?P<prefix>.+?)\s*[（(](?P<seq>上|中|下|[一二三四五六七八九十])[)）]"
)


def check_cross_slide_numbered_headings(
    parsed_slides: Dict[int, ParsedSlide],
) -> List[Issue]:
    """校验跨页连续括号序号标题（如（上/中/下）、（一/二/三））前缀一致且有配对"""
    issues: List[Issue] = []
    entries = []
    for k in sorted(parsed_slides.keys()):
        slide_obj = parsed_slides[k]
        body_raw = "".join(s.raw_text for s in slide_obj.get_layer_segments("body"))
        body_clean = strip_protected_for_scan(body_raw)
        m_h = re.search(r"^##\s+(.+)$", body_clean, re.MULTILINE)
        if not m_h:
            continue
        heading = m_h.group(1).replace("**", "").strip()
        m_num = _NUMBERED_HEADING_RE.match(heading)
        if not m_num:
            continue
        seq = m_num.group("seq")
        if seq in _PART_SEQ_ORDER:
            gtype, rank = "part", _PART_SEQ_ORDER[seq]
        else:
            gtype, rank = "num", _CN_NUM_SEQ_ORDER[seq]
        prefix = m_num.group("prefix").strip()
        entries.append((slide_obj.slide_idx, gtype, rank, prefix, seq, heading))

    if not entries:
        return issues

    groups = []
    curr_group = [entries[0]]
    for item in entries[1:]:
        prev = curr_group[-1]
        if (
            item[1] == prev[1]
            and item[0] - prev[0] <= 2
            and item[2] > prev[2]
        ):
            curr_group.append(item)
        else:
            groups.append(curr_group)
            curr_group = [item]
    groups.append(curr_group)

    for grp in groups:
        if len(grp) == 1:
            s_idx, _, _, _, seq, heading = grp[0]
            issues.append(
                Issue(
                    slide_idx=s_idx,
                    layer="body",
                    rule="孤立跨页序号标题",
                    detail=f"标题「{heading}」带有分篇序号「({seq})」，但相邻页未见配对分篇标题；若非同主题跨页延续请去掉序号改为独立主题标题",
                    snippet=heading,
                )
            )
            continue

        base_idx, _, _, base_prefix, _, _ = grp[0]
        for s_idx, _, _, prefix, _, heading in grp[1:]:
            if prefix != base_prefix:
                issues.append(
                    Issue(
                        slide_idx=s_idx,
                        layer="body",
                        rule="跨页序号标题前缀不一致",
                        detail=f"与前序配对页（Slide {base_idx:02d}，前缀「{base_prefix}」）相比，本页前缀「{prefix}」不一致；若非真并列/真递进，请去掉序号各自写出独立主题",
                        snippet=heading,
                    )
                )

    return issues


def process_master_file(
    file_path: str, target_pass: str = "all", do_fix: bool = False
) -> Tuple[List[Issue], bool]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 前置 UTF-8 闭环校验
    assert raw_content.encode("utf-8").decode("utf-8") == raw_content

    frontmatter, parts = split_frontmatter_and_slides(raw_content)

    # 解析每一张 Slide
    parsed_slides: Dict[int, ParsedSlide] = {}
    slide_counter = 0
    for idx, part in enumerate(parts):
        if part == "\n---\n":
            continue
        slide_counter += 1
        parsed_slides[idx] = parse_slide_segments(slide_counter, part)

    layers_to_run = (
        ORDERED_LAYERS if target_pass == "all" else [PASS_MAP[target_pass]]
    )

    all_issues: List[Issue] = []

    # 严格按层依次执行 (Pass 1 -> Pass 2 -> Pass 3 -> Pass 4 -> Pass 5)
    for layer_name in layers_to_run:
        processor = PASS_PROCESSORS[layer_name]
        for idx in sorted(parsed_slides.keys()):
            slide_obj = parsed_slides[idx]
            layer_issues = processor(slide_obj, do_fix=do_fix)
            all_issues.extend(layer_issues)
        if layer_name == "body":
            all_issues.extend(check_cross_slide_numbered_headings(parsed_slides))

    modified = False
    if do_fix:
        reconstructed_parts: List[str] = []
        for idx, part in enumerate(parts):
            if idx in parsed_slides:
                reconstructed_parts.append(parsed_slides[idx].reconstruct())
            else:
                reconstructed_parts.append(part)
        new_content = frontmatter + "".join(reconstructed_parts)

        # 后置 UTF-8 完整性闭环校验
        encoded_check = new_content.encode("utf-8").decode("utf-8")
        assert encoded_check == new_content, "UTF-8 round-trip check failed!"

        if new_content != raw_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            modified = True

    return all_issues, modified


def print_report(
    file_path: str,
    issues: List[Issue],
    target_pass: str,
    do_fix: bool,
    modified: bool,
) -> None:
    rel_name = os.path.basename(file_path)
    mode_label = "FIX (自动修复 + 审查)" if do_fix else "AUDIT (只读审查)"
    print(f"======================================================================")
    print(f"📄 文件: {rel_name}")
    print(f"🔧 模式: {mode_label} | 执行范围: {target_pass}")
    print(f"======================================================================")

    layers_to_show = (
        ORDERED_LAYERS if target_pass == "all" else [PASS_MAP[target_pass]]
    )

    for layer_name in layers_to_show:
        layer_issues = [i for i in issues if i.layer == layer_name]
        cn_title = LAYER_CN_NAME[layer_name]
        if not layer_issues:
            print(f"✅ {cn_title}: 0 项违例（通过）")
        else:
            print(f"⚠️  {cn_title}: 发现 {len(layer_issues)} 项待处理问题")
            for item in layer_issues:
                print(
                    f"   - [Slide {item.slide_idx:02d}] ({item.rule}) {item.detail}"
                )

    print("----------------------------------------------------------------------")
    if do_fix:
        status_str = "已原子写回更新 (UTF-8 校验通过)" if modified else "无需修改 (文件未变动)"
        print(f"💾 写入状态: {status_str}")
    print(f"📊 总计命中: {len(issues)} 项")
    print("======================================================================\n")


def main():
    parser = argparse.ArgumentParser(
        description="依次清理/审查 *.master.md 的五层结构（正文、逐字稿、对白、自学解释、教学设计）"
    )
    parser.add_argument("files", nargs="+", help="目标 *.master.md 文件路径")
    parser.add_argument(
        "--pass",
        dest="target_pass",
        choices=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "body",
            "script",
            "dialogue",
            "explanation",
            "teaching_plan",
            "all",
        ],
        default="all",
        help="指定要执行的层（1/body, 2/script, 3/dialogue, 4/explanation, 5/teaching_plan, 或 all）",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="执行确定性规则替换并原位写回文件（默认仅执行只读 --audit 诊断）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出审查报告",
    )

    args = parser.parse_args()

    all_results = {}
    for fp in args.files:
        if not os.path.exists(fp):
            print(f"Error: File not found: {fp}", file=sys.stderr)
            sys.exit(1)
        issues, modified = process_master_file(
            fp, target_pass=args.target_pass, do_fix=args.fix
        )
        if args.json:
            all_results[fp] = {
                "modified": modified,
                "issue_count": len(issues),
                "issues": [vars(i) for i in issues],
            }
        else:
            print_report(fp, issues, args.target_pass, args.fix, modified)

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

