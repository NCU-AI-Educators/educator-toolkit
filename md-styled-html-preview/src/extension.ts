import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { StyledHtmlPanel } from './previewPanel';

export function activate(context: vscode.ExtensionContext) {

	// 1. Command: Preview
	let previewDisposable = vscode.commands.registerCommand('mdStyledHtml.preview', () => {
		StyledHtmlPanel.createOrShow(context.extensionUri);
	});

	// 2. Command: Export
	let exportDisposable = vscode.commands.registerCommand('mdStyledHtml.export', async () => {
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
			// We can proceed or stop. Let's warn but proceed just in case user wants to force it.
		}

		const markdownContent = document.getText();
		const htmlContent = StyledHtmlPanel.generateHtml(markdownContent, context.extensionUri.fsPath);

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
