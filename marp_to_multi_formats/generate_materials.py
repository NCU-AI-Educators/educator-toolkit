import re
import os
import textwrap
import sys

# --- 模块级常量 ---
STYLE_BLOCK = '''<style>
/* 盒子通用样式 */
.styled-box {
  display: block; padding: 0.2em 1.2em; margin-top: 1em; border-left: 5px solid;
  font-size: 0.42em; color: #333; border-radius: 5px; line-height: 1.6;
}
.styled-box p, .styled-box ul, .styled-box ol, .styled-box li {
  font-size: inherit !important; margin-block-start: 0.5em !important; margin-block-end: 0.5em !important;
}
/* 减小盒子内列表的左侧缩进 */
.styled-box ul, .styled-box ol {
  padding-inline-start: 18px;
}
.styled-box .box-title { display: block; margin-bottom: 0.5em; font-size: 1.1em; font-weight: bold; }

/* 不同盒子内的内容高亮(strong)分别定义颜色 */
.explanation-box { background: #fffbe6; border-color: #ffd33a; }
.explanation-box .box-title { color: #d98200; }
.explanation-box p strong, .explanation-box li strong { color: #BF7F00; font-weight: bold; }

.note-box { background: #e6f7ff; border-color: #1890ff; }
.note-box .box-title { color: #0050b3; }
.note-box p strong, .note-box li strong { color: #003a8c; font-weight: bold; }

.activity-box { background: #f6ffed; border-color: #52c41a; }
.activity-box .box-title { color: #237804; }
.activity-box p strong, .activity-box li strong { color: #135200; font-weight: bold; }

.design-box { background: #fdf2f8; border-color: #eb4899; }
.design-box .box-title { color: #9d2667; }
.design-box p strong, .design-box li strong { color: #780650; font-weight: bold; }

/* --- 专门为盒子内的H3标题设计的样式 --- */
.styled-box h3 {
  font-size: 1.2em; /* 相对于盒子的基础字号，比正文稍大 */
  color: #d98200; /* 与解释盒子的主题色一致 */
  margin-top: 0.8em;
  margin-bottom: 0.4em;
  padding-bottom: 0.2em;
  border-bottom: 1px solid #ffd33a; /* 添加一条细下划线 */
  font-weight: bold;
}

/* --- A4主题 H1 字体大小修正 --- */
h1 {
  font-size: 1.5em;
}

/* --- 列表缩进样式修正 --- */
.columns table {
  font-size: 14px; /* 调整为更合适的字体大小 */
  width: 100%;
}
.columns table th, .columns table td {
  padding: 6px 8px; /* 适当减小内边距 */
}
</style>'''

A4_FRONTMATTER = '''---
marp: true
theme: A4
paginate: true
--- '''

# --- 元数据解析函数 ---

def parse_metadata_from_comment(comment_content):
    type_match = re.search(r"-\s*\*\*类型\*\*:\s*(.*?)\n", comment_content)
    content_match = re.search(r"-\s*\*\*内容\*\*:\s*([\s\S]*)", comment_content)
    block_type = type_match.group(1).strip() if type_match else None
    raw_content = content_match.group(1).strip() if content_match else ""
    if raw_content.startswith("|"):
        raw_content = raw_content.lstrip("|")
        if raw_content.startswith("\n"):
            raw_content = raw_content[1:]
    else:
        raw_content = raw_content.strip('\"')
    return block_type, textwrap.dedent(raw_content)

def parse_style_replacement_from_comment(comment_content):
    type_match = re.search(r"-\s*\*\*类型\*\*:\s*(样式替换)", comment_content)
    if not type_match:
        return None
    versions_match = re.search(r"-\s*\*\*版本\*\*:\s*\[(.*?)\]", comment_content)
    versions = [v.strip() for v in versions_match.group(1).split(',')] if versions_match else []
    find_match = re.search(r"-\s*\*\*查找\*\*:\s*\|?\s*([\s\S]*?)(?=-\s*\*\*替换\*\*|$)", comment_content)
    # The replace block is terminated by the "次数" field or the end of the comment.
    replace_match = re.search(r"-\s*\*\*替换\*\*:\s*\|?\s*([\s\S]*?)(?=-\s*\*\*次数\*\*|$)", comment_content)
    count_match = re.search(r"-\s*\*\*次数\*\*:\s*(.*)", comment_content)

    if find_match and replace_match:
        # Per user's request, only strip leading/trailing newlines from the find_str,
        # preserving all user-defined indentation.
        find_str = find_match.group(1).strip('\n')
        # Strip quotes from the replace string to handle empty string replacement.
        replace_str = textwrap.dedent(replace_match.group(1)).strip()
        if len(replace_str) > 1 and replace_str.startswith('"') and replace_str.endswith('"'):
            replace_str = replace_str[1:-1]
        
        count = 1
        if count_match:
            count_str = count_match.group(1).strip()
            if count_str == '*':
                count = -1  # In Python's str.replace, -1 or omitting count replaces all.
            else:
                try:
                    count = int(count_str)
                except ValueError:
                    count = 1 # Default to 1 if not a valid number
        
        return {'find': find_str, 'replace': replace_str, 'versions': versions, 'count': count}
    return None

def parse_page_break_from_comment(comment_content):
    type_match = re.search(r"-\s*\*\*类型\*\*:\s*(换页)", comment_content)
    if not type_match:
        return None
    versions_match = re.search(r"-\s*\*\*版本\*\*:\s*\[(.*?)\]", comment_content)
    versions = [v.strip() for v in versions_match.group(1).split(',')] if versions_match else []
    return {'versions': versions}

def parse_all_metadata_from_page(page_content):
    """从单个页面内容中解析所有元数据注释块。"""
    metadata = {
        'notes': [], 'handouts': [], 'teacher_notes': [],
        'style_replacements': [], 'page_breaks': []
    }
    comment_pattern = re.compile(r"<!--([\s\S]*?)-->", re.DOTALL)
    for match in comment_pattern.finditer(page_content):
        full_comment_block = match.group(0)
        inner_content = match.group(1)
        
        block_type, content = parse_metadata_from_comment(inner_content)
        if block_type == "逐字稿":
            metadata['notes'].append({'full_block': full_comment_block, 'content': content})
        elif block_type == "解释":
            metadata['handouts'].append({'full_block': full_comment_block, 'content': content})
        elif block_type == "教学设计":
            metadata['teacher_notes'].append({'full_block': full_comment_block, 'content': content})
        
        style_rule = parse_style_replacement_from_comment(inner_content)
        if style_rule:
            metadata['style_replacements'].append({'full_block': full_comment_block, **style_rule})

        page_break_rule = parse_page_break_from_comment(inner_content)
        if page_break_rule:
            metadata['page_breaks'].append({'full_block': full_comment_block, **page_break_rule})
    return metadata

# --- 核心处理流程 ---

def split_document(master_content):
    """分离文档头和文档体，并将文档体按 '---' 分割为页面列表。"""
    header_pattern = r"(\A---\s*[\s\S]*?---\s*\n(?:<style>[\s\S]*?<\/style>\s*\n)*)"
    header_match = re.search(header_pattern, master_content, re.DOTALL)
    
    header = ""
    body = master_content
    if header_match:
        header = header_match.group(0)
        body = master_content[header_match.end():]

    # 仅基于 '---' 分隔符分割页面
    pages_content = body.split('\n---\n')
    # 将页面内容重新包装为带分隔符信息的字典列表，以兼容后续处理流程
    pages = [{'separator': '\n---\n' if i > 0 else '', 'content': content} for i, content in enumerate(pages_content)]
            
    return header, pages

def rebuild_document(header, processed_pages):
    """根据处理后的页面列表重组文档。"""
    # 移除头部可能存在的 frontmatter
    header_cleaned = re.sub(r"\A---[\s\S]*?---", "", header, count=1).strip()
    
    # 用 '---' 连接所有页面内容
    body_content = '\n---\n'.join(p['content'] for p in processed_pages)
    
    return header_cleaned, body_content

# --- 文件生成函数 ---

def generate_a4_version(version_type, master_content, module_dir, master_filename):
    """生成A4版式的文档 (teacher 或 handout)。"""
    header, pages = split_document(master_content)
    
    processed_pages = []
    for i, page_data in enumerate(pages):
        page_content = page_data['content']
        metadata = parse_all_metadata_from_page(page_content)

        processed_page = page_content

        if not any(metadata.values()):
            processed_pages.append(page_data)
            continue

        # 应用页面换页规则
        for rule in metadata['page_breaks']:
            if not rule['versions'] or version_type in rule['versions']:
                processed_page = processed_page.replace(rule['full_block'], '\n---\n', 1)

        # 插入特定版本的内容块 (例如 教学设计, 解释)
        if version_type == 'teacher':
            for block_info in metadata['teacher_notes']:
                design_box = f'''<div class="styled-box design-box">
<strong class="box-title">[教学设计]</strong>

{block_info['content']}

</div>'''
                processed_page = processed_page.replace(block_info['full_block'], design_box)
        elif version_type == 'handout':
            for block_info in metadata['handouts']:
                explanation_box = f'''<div class="styled-box explanation-box">
<strong class="box-title">[解释]</strong>

{block_info['content']}

</div>'''
                processed_page = processed_page.replace(block_info['full_block'], explanation_box)

        # 最后应用样式替换规则，确保它们能作用于新插入的内容
        for rule in metadata['style_replacements']:
            if not rule['versions'] or version_type in rule['versions']:
                processed_page = processed_page.replace(rule['find'], rule['replace'], rule['count'])
        
        page_data['content'] = processed_page
        processed_pages.append(page_data)

    # 组合并清理
    header_cleaned, body_content = rebuild_document(header, processed_pages)
    final_content = f"{A4_FRONTMATTER}\n{header_cleaned}\n{STYLE_BLOCK}\n{body_content}"
    final_content = re.sub(r"<!--([\s\S]*?)-->", "", final_content)
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    # 写入文件
    output_filename = master_filename.replace(".master.", f".{version_type}.")
    output_path = os.path.join(module_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content.strip())
    print(f"  -> 已生成 {version_type} 版本: {os.path.basename(output_path)}")

def generate_slides_version(master_content, module_dir, master_filename):
    """生成幻灯片版本。"""
    header, pages = split_document(master_content)

    processed_pages = []
    for page_data in pages:
        page_content = page_data['content']
        metadata = parse_all_metadata_from_page(page_content)

        processed_page = page_content

        if not any(metadata.values()):
            processed_pages.append(page_data)
            continue

        # 应用规则
        for rule in metadata['page_breaks']:
            if not rule['versions'] or 'slides' in rule['versions']:
                processed_page = processed_page.replace(rule['full_block'], '\n---\n', 1)
        for rule in metadata['style_replacements']:
            if not rule['versions'] or 'slides' in rule['versions']:
                processed_page = processed_page.replace(rule['find'], rule['replace'], rule['count'])

        # 移除不应出现在幻灯片中的元数据块
        blocks_to_remove = metadata['handouts'] + metadata['teacher_notes'] + metadata['style_replacements'] + metadata['page_breaks']
        for block in blocks_to_remove:
            processed_page = processed_page.replace(block['full_block'], "")

        # 转换逐字稿
        for block_info in metadata['notes']:
            marp_note = f"<!--\n{block_info['content']}\n-->"
            processed_page = processed_page.replace(block_info['full_block'], marp_note)
        
        page_data['content'] = processed_page
        processed_pages.append(page_data)

    # 组合并清理
    _, body_content = rebuild_document(header, processed_pages)
    final_content = f"{header}{body_content}"
    final_content = re.sub(r'\n{3,}', '\n\n', final_content.strip())

    # 写入文件
    output_path = os.path.join(module_dir, master_filename.replace(".master.", ".slides."))
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"  -> 已生成 slides 版本: {os.path.basename(output_path)}")

def main():
    """主函数，协调解析和生成过程。"""
    if len(sys.argv) != 2:
        print("错误: 请提供一个 master Markdown 文件的路径作为参数。")
        sys.exit(1)

    master_path = sys.argv[1]
    if not os.path.exists(master_path):
        print(f"错误: 输入文件未找到 -> {master_path}")
        sys.exit(1)
    
    print(f"--- 正在处理输入文件 ---\n  -> {os.path.abspath(master_path)}\n")

    try:
        with open(master_path, 'r', encoding='utf-8') as f:
            master_content = f.read()
    except Exception as e:
        print(f"错误: 读取文件时出错 -> {e}")
        sys.exit(1)

    print("--- 开始生成文件 ---")
    
    module_dir = os.path.dirname(master_path)
    master_filename = os.path.basename(master_path)

    # 派发任务到各个生成器
    generate_a4_version('teacher', master_content, module_dir, master_filename)
    generate_a4_version('handout', master_content, module_dir, master_filename)
    generate_slides_version(master_content, module_dir, master_filename)
    
    print("\n--- 所有操作完成 ---")

if __name__ == "__main__":
    main()
