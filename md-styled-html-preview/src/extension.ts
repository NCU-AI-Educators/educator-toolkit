import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { StyledHtmlPanel } from './previewPanel';

export function activate(context: vscode.ExtensionContext) {
    console.log('Hawk Styled Preview: Extension Activated');

	// 1. Command: Preview
	let previewDisposable = vscode.commands.registerCommand('mdStyledHtml.preview', async () => {
        console.log('Hawk Styled Preview: Command Triggered');
        try {
		    await StyledHtmlPanel.createOrShow(context.extensionUri);
            console.log('Hawk Styled Preview: Panel Created/Shown');
        } catch (e) {
            console.error('Hawk Styled Preview: Error showing panel', e);
            vscode.window.showErrorMessage('Hawk Styled Preview Error: ' + e);
        }
	});

	// 2. Command: Export
	let exportDisposable = vscode.commands.registerCommand('mdStyledHtml.export', async () => {
        console.log('Hawk Styled Preview: Export Command Triggered');
		let editor = vscode.window.activeTextEditor;
		let document: vscode.TextDocument | undefined;

		if (editor) {
			document = editor.document;
		} else {
			if (StyledHtmlPanel.currentPanel && StyledHtmlPanel.currentPanel.currentDocument) {
				document = StyledHtmlPanel.currentPanel.currentDocument;
			}
		}

		if (!document) {
			vscode.window.showErrorMessage('No active editor or preview found');
			return;
		}

		if (document.languageId !== 'markdown') {
			vscode.window.showWarningMessage('Active file is not a Markdown file');
		}

		const markdownContent = document.getText();
        console.log('Hawk Styled Preview: Generating HTML for export...');
		
		// generateHtml is now async
		const htmlContent = await StyledHtmlPanel.generateHtml(markdownContent, context.extensionUri.fsPath);
        console.log('Hawk Styled Preview: HTML Generated');

		// Propose a filename
		const originalUri = document.uri;
		const originalBasename = path.basename(originalUri.fsPath, path.extname(originalUri.fsPath));
		const defaultUri = vscode.Uri.file(path.join(path.dirname(originalUri.fsPath), `${originalBasename}.html`));

		const saveUri = await vscode.window.showSaveDialog({
			defaultUri: defaultUri,
			filters: {
				'HTML': ['html']
			},
			title: 'Export Styled HTML'
		});

		if (saveUri) {
			try {
				fs.writeFileSync(saveUri.fsPath, htmlContent, 'utf-8');
				vscode.window.showInformationMessage(`Successfully exported to ${path.basename(saveUri.fsPath)}`);
			} catch (err: any) {
				vscode.window.showErrorMessage(`Failed to export: ${err.message}`);
			}
		}
	});

	context.subscriptions.push(previewDisposable);
	context.subscriptions.push(exportDisposable);
}

export function deactivate() {}
