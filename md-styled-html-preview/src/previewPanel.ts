import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export class StyledHtmlPanel {
    public static currentPanel: StyledHtmlPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _currentDocument: vscode.TextDocument | undefined;

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Update the content based on view state changes
        this._panel.onDidChangeViewState(
            e => {
                if (this._panel.visible) {
                    this._update();
                }
            },
            null,
            this._disposables
        );

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'alert':
                        vscode.window.showErrorMessage(message.text);
                        return;
                    case 'export':
                        vscode.commands.executeCommand('mdStyledHtml.export');
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public get currentDocument(): vscode.TextDocument | undefined {
        return this._currentDocument;
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (StyledHtmlPanel.currentPanel) {
            StyledHtmlPanel.currentPanel._panel.reveal(column);
            StyledHtmlPanel.currentPanel._update(); // Update content on show
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            'styledHtmlPreview',
            'Styled HTML Preview',
            column || vscode.ViewColumn.One,
            {
                // Enable javascript in the webview
                enableScripts: true,
                // And restrict the webview to only loading content from our extension's `media` directory.
                // localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')] 
                // We are using CDNs, so strict localResourceRoots might be tricky without correct CSP.
            }
        );

        StyledHtmlPanel.currentPanel = new StyledHtmlPanel(panel, extensionUri);
        StyledHtmlPanel.currentPanel._update();
    }

    public dispose() {
        StyledHtmlPanel.currentPanel = undefined;

        // Clean up our resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        if (editor.document.languageId !== 'markdown') {
             // Optional: Handle non-markdown files or just ignore
             return;
        }
        
        this._currentDocument = editor.document;

        const markdownContent = editor.document.getText();
        this._panel.webview.html = this._getHtmlForWebview(markdownContent);
    }



    public static generateHtml(markdownContent: string, extensionPath: string): string {
        try {
            const assetsPath = path.join(extensionPath, 'src', 'assets');
            const templatePath = path.join(assetsPath, 'template.html');
            const cssPath = path.join(assetsPath, 'default.css');

            let templateContent = fs.readFileSync(templatePath, 'utf-8');
            const cssContent = fs.readFileSync(cssPath, 'utf-8');

            // Inject CSP for VS Code Webview environment if needed.
            // But the generated HTML is also used for export, where we DON'T want VS Code specific CSP.
            // Ideally, we handle them slightly differently. 
            // For now, let's just stick to the original replacements.
            
            // NOTE: Replicating the logic from md_to_styled_html.py
            let finalHtml = templateContent.replace('/* {{ CSS_BLOCK }} */', cssContent);
            finalHtml = finalHtml.replace('{{ MARKDOWN_CONTENT }}', markdownContent);
            
            return finalHtml;
        } catch (e) {
            console.error(e);
            return `<h1>Error generating HTML</h1><pre>${e}</pre>`;
        }
    }

    private _getHtmlForWebview(markdownContent: string): string {
        let html = StyledHtmlPanel.generateHtml(markdownContent, this._extensionUri.fsPath);
        
        // Inject CSP for Webview
        // We need to allow cdn.jsdelivr.net for scripts and styles, and unsafe-inline for the injected content.
        const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'unsafe-inline' https://cdn.jsdelivr.net; img-src data: https:; font-src https://cdn.jsdelivr.net;">`;
        
        // Insert after <head>
        html = html.replace('<head>', `<head>\n    ${cspMeta}`);

        // Inject Export Button and Script (Only for Webview)
        const exportScript = `
        <div id="vscode-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 10000; font-family: sans-serif;">
            <button onclick="triggerExport()" style="
                padding: 10px 15px; 
                background: var(--primary-color, #017fc0); 
                color: white; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-weight: bold;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.1s;
            " onmousedown="this.style.transform='scale(0.95)'" onmouseup="this.style.transform='scale(1)'">
                导出 HTML
            </button>
        </div>
        <script>
            const vscode = acquireVsCodeApi();
            function triggerExport() {
                vscode.postMessage({ command: 'export' });
            }
        </script>
        `;
        
        html = html.replace('</body>', `${exportScript}\n</body>`);
        
        return html;
    }
}
