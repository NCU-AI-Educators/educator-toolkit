
import os
import argparse
import sys

def generate_reader(input_path, output_path=None, css_path=None):
    # 0. Setup Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()
    
    # 1. Resolve Files
    if not os.path.isabs(input_path):
        input_path = os.path.abspath(input_path)
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    # Determine CSS
    if css_path:
        if not os.path.isabs(css_path):
            css_path = os.path.abspath(css_path)
        if not os.path.exists(css_path):
            print(f"Warning: Custom CSS '{css_path}' not found. Falling back to default.")
            css_path = os.path.join(script_dir, 'default.css')
    else:
        css_path = os.path.join(script_dir, 'default.css')

    # Determine Output
    if not output_path:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(current_dir, base_name + '.html')
    
    # 2. Read Content
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"Error reading markdown: {e}")
        sys.exit(1)

    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    except Exception as e:
        print(f"Error reading CSS: {e}")
        sys.exit(1)

    try:
        template_path = os.path.join(script_dir, 'template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        sys.exit(1)

    # 3. Inject Content
    # Escape sequence for HTML script tag injections if necessary, but here we just paste raw
    # We should be careful about script tags in markdown, but this is a local tool.
    
    # Simple replacement
    final_html = template_content.replace('/* {{ CSS_BLOCK }} */', css_content)
    final_html = final_html.replace('{{ MARKDOWN_CONTENT }}', markdown_content)

    # 4. Write Output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ Successfully generated reader: {output_path}")
        print(f"   - Input: {os.path.basename(input_path)}")
        print(f"   - Style: {os.path.basename(css_path)}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hawk MReader: Convert Markdown to Standalone HTML Reader')
    parser.add_argument('input', help='Input Markdown file path')
    parser.add_argument('css', nargs='?', help='Optional custom CSS file path')
    parser.add_argument('-o', '--output', help='Output HTML file path')

    args = parser.parse_args()
    
    generate_reader(args.input, args.output, args.css)
