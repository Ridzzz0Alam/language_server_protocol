import logging
import sys
from pygls.server import LanguageServer
from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    InitializeParams,
    InitializeResult,
    Position,
    Range,
    ServerCapabilities,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
)

logging.basicConfig(level=logging.DEBUG, format='[cclsp] %(message)s')

ls = LanguageServer(name="cclsp", version="0.1")

@ls.feature(INITIALIZE)
def on_initialize(ls: LanguageServer, params: InitializeParams):
    logging.info("Received method: initialize")
    caps = ServerCapabilities(
        text_document_sync=TextDocumentSyncOptions(
            open_close=True,
            change=TextDocumentSyncKind.INCREMENTAL,
        ),
        completion_provider=CompletionOptions(
            resolve_provider=False,
            trigger_characters=[".", "C"]
        ),
    )
    logging.info(f"Connected client info: {getattr(params, 'capabilities', None)}")
    return InitializeResult(capabilities=caps)

@ls.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    uri = params.text_document.uri
    text = params.text_document.text
    logging.info(f"Received method : textDocument/didOpen")
    logging.info(f"Opened: {uri}")
    logging.info(f"Content preview: {text[:100]!r}")
    check_and_publish_diagnostics(ls, uri, text)

@ls.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    uri = params.text_document.uri
    if params.content_changes:
        last_change = params.content_changes[-1]
        if hasattr(last_change, "text"):
            text = last_change.text
        else:
            text = ls.workspace.get_document(uri).source
    else:
        try:
            text = ls.workspace.get_document(uri).source
        except Exception:
            text = ""
    logging.info(f"Received method: textDocument/didChange for {uri}")
    logging.info(f"New content preview:\n{text[:200]!r}")
    check_and_publish_diagnostics(ls, uri, text)

def check_and_publish_diagnostics(ls: LanguageServer, uri: str, text: str):
    diagnostics = []
    lines = text.splitlines()

    def make_diag(line_idx: int, start_col: int, end_col: int, message: str, severity=DiagnosticSeverity.Warning):
        diag = Diagnostic(
            range=Range(
                start=Position(line=line_idx, character=start_col),
                end=Position(line=line_idx, character=end_col),
            ),
            message=message,
            severity=severity,
            source="cclsp",
        )
        return diag
    
    for i, line in enumerate(lines):
        phrase1 = "Watching a Video"
        idx1 = line.find(phrase1)
        if idx1 != -1:
            msg = "It's much better to learn by doing! Try Coding Challenges instead."
            diagnostics.append(make_diag(i, idx1, idx1 + len(phrase1), msg, DiagnosticSeverity.Information))
        
        phrase2 = "Coding Challenges"
        idx2 = line.find(phrase2)
        if idx2 != -1:
            msg = "This is the way!"
            diagnostics.append(make_diag(i, idx2, idx2 + len(phrase2), msg, DiagnosticSeverity.Hint))
    
    ls.publish_diagnostics(uri, diagnostics)
    logging.info(f"Published {len(diagnostics)} diagnostics for {uri}")

@ls.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: LanguageServer, params: CompletionParams):
    logging.info("Received method: textDocument/completion")
    item = CompletionItem(
        label="CodingChallenges",
        kind=CompletionItemKind.Keyword,
        detail="Completion for the Coding Challenge example",
        documentation="Insert the 'CodingChallenges' completion item",
    )
    return CompletionList(is_incomplete=False, items=[item])

def main():
    logging.info("CC LSP is running")
    ls.start_io(sys.stdin.buffer, sys.stdout.buffer)

if __name__ == "__main__":
    main()