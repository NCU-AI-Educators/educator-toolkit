import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// Load markdown-it and plugins via require
const MarkdownIt = require('markdown-it');
const tm = require('markdown-it-texmath');
const katex = require('katex');
const hljs = require('highlight.js');

// Custom Ruby Plugin for [text]{pinyin}
function customRubyPlugin(md: any) {
    md.inline.ruler.push('custom_ruby', (state: any, silent: boolean) => {
        if (state.src.charCodeAt(state.pos) !== 0x5B /* [ */) return false;

        const max = state.posMax;
        const start = state.pos;
        
        let pos = start + 1;
        let foundCloseBracket = false;
        while (pos < max) {
            if (state.src.charCodeAt(pos) === 0x5D /* ] */) {
                foundCloseBracket = true;
                break;
            }
            pos++;
        }
        if (!foundCloseBracket) return false;
        const textContent = state.src.slice(start + 1, pos);

        pos++; // Skip ]
        if (pos >= max || state.src.charCodeAt(pos) !== 0x7B /* { */) return false;
        
        let foundCloseBrace = false;
        let braceStart = pos;
        pos++;
        while (pos < max) {
            if (state.src.charCodeAt(pos) === 0x7D /* } */) {
                foundCloseBrace = true;
                break;
            }
            pos++;
        }
        if (!foundCloseBrace) return false;
        const rubyContent = state.src.slice(braceStart + 1, pos);
        
        if (!silent) {
            state.pos = start;
            const tokenRubyOpen = state.push('ruby_open', 'ruby', 1);
            const tokenText = state.push('text', '', 0);
            tokenText.content = textContent;
            const tokenRtOpen = state.push('rt_open', 'rt', 1);
            const tokenRtText = state.push('text', '', 0);
            tokenRtText.content = rubyContent;
            const tokenRtClose = state.push('rt_close', 'rt', -1);
            const tokenRubyClose = state.push('ruby_close', 'ruby', -1);
            state.pos = pos + 1;
        } else {
            state.pos = pos + 1;
        }
        return true;
    });
}

const AlertIcons: any = {
    note: '<svg class="octicon octicon-info" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" style="fill:currentColor;margin-right:8px;vertical-align:text-bottom;"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm6.5-.25A.75.75 0 017.25 7h1a.75.75 0 01.75.75v2.75h.25a.75.75 0 010 1.5h-2a.75.75 0 010-1.5h.25v-2h-.25a.75.75 0 01-.75-.75zM8 6a1 1 0 100-2 1 1 0 000 2z"></path></svg>',
    tip: '<svg class="octicon octicon-light-bulb" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" style="fill:currentColor;margin-right:8px;vertical-align:text-bottom;"><path fill-rule="evenodd" d="M8 1.5c-2.363 0-4 1.69-4 3.75 0 .984.424 1.625.984 2.304l.214.277a.25.25 0 00.042.028C5.484 8.1 5.75 8.57 5.75 9.25c0 .414.336.75.75.75h3a.75.75 0 00.75-.75c0-.68.266-1.15.51-1.384l.214-.277c.56-.679.984-1.32.984-2.304 0-2.06-1.637-3.75-4-3.75zM2.5 5.25c0-2.846 2.11-5.25 5.5-5.25S13.5 2.404 13.5 5.25c0 1.414-.622 2.474-1.366 3.376l-.214.28c-.416.536-.67 1.054-.67 1.594 0 .625.425 1.25 1.25 1.25H12a.75.75 0 010 1.5h-1.5a.75.75 0 01-.75-.75v-.25H6.25v.25a.75.75 0 01-.75.75H4a.75.75 0 010-1.5h-.5c.825 0 1.25-.625 1.25-1.25 0-.54-.254-1.058-.67-1.594l-.214-.28C3.122 7.724 2.5 6.664 2.5 5.25zm6.5 9a.75.75 0 00-1.5 0v.5c0 .414.336.75.75.75h3a.75.75 0 00.75-.75v-.5a.75.75 0 00-1.5 0H9z"></path></svg>',
    warning: '<svg class="octicon octicon-alert" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" style="fill:currentColor;margin-right:8px;vertical-align:text-bottom;"><path fill-rule="evenodd" d="M8.22 1.754a.25.25 0 00-.44 0L1.698 13.132a.25.25 0 00.22.368h12.164a.25.25 0 00.22-.368L8.22 1.754zm-1.763-.707c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0114.082 15H1.918a1.75 1.75 0 01-1.543-2.575L6.457 1.047zM9 11a1 1 0 11-2 0 1 1 0 012 0zm-.25-5.25a.75.75 0 00-1.5 0v2.5a.75.75 0 001.5 0v-2.5z"></path></svg>',
    important: '<svg class="octicon octicon-report" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" style="fill:currentColor;margin-right:8px;vertical-align:text-bottom;"><path fill-rule="evenodd" d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0114.25 13H8.06l-2.573 2.573A1.457 1.457 0 013 14.543V13H1.75A1.75 1.75 0 010 11.25v-9.5zM1.75 1.5a.25.25 0 00-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 01.75.75v2.19l2.72-2.72a.75.75 0 01.53-.22h6.5a.25.25 0 00.25-.25v-9.5a.25.25 0 00-.25-.25H1.75zM6 9a1 1 0 11-2 0 1 1 0 012 0zm0-5a1 1 0 11-2 0 1 1 0 012 0zm5 5a1 1 0 11-2 0 1 1 0 012 0zm0-5a1 1 0 11-2 0 1 1 0 012 0z"></path></svg>',
    caution: '<svg class="octicon octicon-stop" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" style="fill:currentColor;margin-right:8px;vertical-align:text-bottom;"><path fill-rule="evenodd" d="M4.47.22A.75.75 0 015 0h6a.75.75 0 01.53.22l4.25 4.25c.141.14.22.331.22.53v6a.75.75 0 01-.22.53l-4.25 4.25A.75.75 0 0111 16H5a.75.75 0 01-.53-.22L.22 11.53A.75.75 0 010 11V5a.75.75 0 01.22-.53L4.47.22zm.84 1.28L1.5 5.31v5.38l3.81 3.81h5.38l3.81-3.81V5.31L10.69 1.5H5.31zM8 4a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 018 4zm0 8a1 1 0 100-2 1 1 0 000 2z"></path></svg>'
};

// Custom GitHub Alerts Plugin Implementation
function githubAlertsPlugin(md: any) {
    md.core.ruler.after('block', 'github_alerts', (state: any) => {
        const tokens = state.tokens;
        for (let i = 0; i < tokens.length; i++) {
            if (tokens[i].type === 'blockquote_open') {
                let j = i + 1;
                while (j < tokens.length && tokens[j].type !== 'paragraph_open' && tokens[j].type !== 'blockquote_close') {
                    j++;
                }

                if (j < tokens.length && tokens[j].type === 'paragraph_open') {
                    const inlineToken = tokens[j + 1];
                    if (inlineToken && inlineToken.type === 'inline') {
                        const match = inlineToken.content.match(/^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]/i);
                        if (match) {
                            const type = match[1].toLowerCase();
                            const title = type.charAt(0).toUpperCase() + type.slice(1);
                            tokens[i].attrJoin('class', `markdown-alert markdown-alert-${type}`);
                            inlineToken.content = inlineToken.content.replace(/^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s?/i, '');
                            
                            const icon = AlertIcons[type] || AlertIcons.note;
                            const openTitle = new state.Token('html_block', '', 0);
                            openTitle.content = `<div class="markdown-alert-title">${icon} ${title}</div>`;
                            tokens.splice(i + 1, 0, openTitle);
                            i++;
                        }
                    }
                }
            }
        }
    });
}

export class StyledHtmlPanel {
    public static currentPanel: StyledHtmlPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _currentDocument: vscode.TextDocument | undefined;

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.onDidChangeViewState(e => { if (this._panel.visible) { this._update(); } }, null, this._disposables);
        this._panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'alert': vscode.window.showErrorMessage(message.text); return;
                case 'export': vscode.commands.executeCommand('mdStyledHtml.export'); return;
            }
        }, null, this._disposables);
    }

    public get currentDocument(): vscode.TextDocument | undefined { return this._currentDocument; }

    public static async createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;
        if (StyledHtmlPanel.currentPanel) {
            StyledHtmlPanel.currentPanel._panel.reveal(column);
            await StyledHtmlPanel.currentPanel._update();
            return;
        }
                const panel = vscode.window.createWebviewPanel(
                    'styledHtmlPreview',
                    'Styled HTML Preview',
                    column || vscode.ViewColumn.One,
                    {
                        enableScripts: true,
                        localResourceRoots: [vscode.Uri.file(path.join(extensionUri.fsPath, 'media'))]
                    }
                );
        StyledHtmlPanel.currentPanel = new StyledHtmlPanel(panel, extensionUri);
        await StyledHtmlPanel.currentPanel._update();
    }

    public dispose() {
        StyledHtmlPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) { x.dispose(); }
        }
    }

    private async _update() {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'markdown') return;
        this._currentDocument = editor.document;
        const markdownContent = editor.document.getText();
        this._panel.webview.html = await this._getHtmlForWebview(markdownContent);
    }

    public static async generateHtml(markdownContent: string, extensionPath: string): Promise<string> {
        try {
            const MarkdownIt = require('markdown-it');
            const hljs = require('highlight.js');
            const md = new MarkdownIt({
                html: true, breaks: true, linkify: true, typographer: true,
                highlight: function (str: string, lang: string) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>';
                        } catch (__) {}
                    }
                    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
                }
            });

            md.use(customRubyPlugin);
            md.use(githubAlertsPlugin);
            md.use(tm, { engine: katex, delimiters: 'dollars', katexOptions: { macros: { "\RR": "\mathbb{R}" } } });

            const bodyContent = md.render(markdownContent);
            const assetsPath = path.join(extensionPath, 'media');
            const templatePath = path.join(assetsPath, 'template.html');
            const cssPath = path.join(assetsPath, 'default.css');

            let templateContent = fs.readFileSync(templatePath, 'utf-8');
            let cssContent = fs.readFileSync(cssPath, 'utf-8');

            const extraCss = `
/* Highlight.js Theme (GitHub) - Enforced */
pre.hljs, .hljs { display: block; overflow-x: auto; padding: 1em !important; color: #333 !important; background: #f8f8f8 !important; border-radius: 5px; font-family: var(--font-family-mono); }
.hljs-comment, .hljs-quote { color: #998; font-style: italic; }
.hljs-keyword, .hljs-selector-tag, .hljs-subst { color: #333; font-weight: 700; }
.hljs-literal, .hljs-number, .hljs-tag .hljs-attr, .hljs-template-variable, .hljs-variable { color: teal; }
.hljs-doctag, .hljs-string { color: #d14; }
.hljs-section, .hljs-selector-id, .hljs-title { color: #900; font-weight: 700; }
.hljs-subst { font-weight: 400; }
.hljs-class .hljs-title, .hljs-type { color: #458; font-weight: 700; }
.hljs-attribute, .hljs-name, .hljs-tag { color: navy; font-weight: 400; }
.hljs-link, .hljs-regexp { color: #009926; }
.hljs-bullet, .hljs-symbol { color: #990073; }
.hljs-built_in, .hljs-builtin-name { color: #0086b3; }
.hljs-meta { color: #999; font-weight: 700; }
.hljs-deletion { background: #fdd; }
.hljs-addition { background: #dfd; }
.hljs-emphasis { font-style: italic; }
.hljs-strong { font-weight: 700; }
            `;

            let finalHtml = templateContent.replace('/* {{ CSS_BLOCK }} */', cssContent + '\n' + extraCss);
            const katexCdn = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">';
            finalHtml = finalHtml.replace('</head>', `${katexCdn}\n</head>`);
            finalHtml = finalHtml.replace('{{ MARKDOWN_CONTENT }}', bodyContent);
            return finalHtml;
        } catch (e: any) {
            return `<h1>Error generating HTML</h1><pre>${e.message}\n${e.stack}</pre>`;
        }
    }

    private async _getHtmlForWebview(markdownContent: string): Promise<string> {
        let html = await StyledHtmlPanel.generateHtml(markdownContent, this._extensionUri.fsPath);
        if (this._currentDocument) {
            const documentDir = path.dirname(this._currentDocument.fileName);
            html = html.replace(/<img([^>]+)src=["']([^"']+)["']([^>]*)>/g, (match, before, url, after) => {
                 const isAbsolute = /^(?:[a-z]+:)?\/\//i.test(url) || /^data:/.test(url) || /^file:/.test(url);
                 if (!isAbsolute) {
                     try {
                        const absolutePath = path.join(documentDir, url);
                        const webviewUri = this._panel.webview.asWebviewUri(vscode.Uri.file(absolutePath));
                        return `<img${before}src="${webviewUri}"${after}>`;
                     } catch (e) { return match; }
                 }
                 return match;
            });
        }
        const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' ${this._panel.webview.cspSource} https:; script-src 'unsafe-inline' ${this._panel.webview.cspSource}; img-src data: https: ${this._panel.webview.cspSource}; font-src ${this._panel.webview.cspSource} https:;">`;
        html = html.replace('<head>', `<head>\n    ${cspMeta}`);
        const exportScript = `
        <div id="vscode-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 10000; font-family: sans-serif;">
            <button onclick="triggerExport()" style="padding: 10px 15px; background: var(--primary-color, #017fc0); color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.1s;" onmousedown="this.style.transform='scale(0.95)'" onmouseup="this.style.transform='scale(1)'">导出 HTML</button>
        </div>
        <script>
            const vscode = acquireVsCodeApi();
            function triggerExport() { vscode.postMessage({ command: 'export' }); }
        </script>
        `;
        html = html.replace('</body>', `${exportScript}\n</body>`);
        return html;
    }
}
