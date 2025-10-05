const path = require('path');
const vscode = require('vscode');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');

let client;

function activate(context) {
    // Path to your Python language server script
    const serverScript = context.asAbsolutePath(
        path.join('cclsp_server.py')
    );

    // Command to run the Python server
    const serverOptions = {
        command: 'python3',
        args: [serverScript],
        transport: TransportKind.stdio
    };

    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'plaintext' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.txt')
        }
    };

    // Create the language client
    client = new LanguageClient(
        'ccLsp',
        'Coding Challenge Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client (and the server)
    client.start();
    vscode.window.showInformationMessage('CC LSP activated!');
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
