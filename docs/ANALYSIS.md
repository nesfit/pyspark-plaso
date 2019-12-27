# Log2Timeline Analysis

## Browser Search Use Case

### [tests/analysis/browser_search.py](../../tests/analysis/browser_search.py)

*   utilizes Plaso components
    * parser = [plaso.parsers.sqlite.SQLiteParser()](../../plaso/parsers/sqlite.py)
    * plugin = [plaso.analysis.browser_search.BrowserSearchPlugin()](../../plaso/analysis/browser_search.py)
*   runs `_ParseAndAnalyzeFile(['History'], parser, plugin)` from [tests/analysis/test_lib.py](../../tests/analysis/test_lib.py)
*   checks its return StorageWriter object for the analysis results

### `_ParseAndAnalyzeFile(...)` in [tests/analysis/test_lib.py](../../tests/analysis/test_lib.py)

*   initialize an empty knowledge base [plaso.engine.knowledge_base.KnowledgeBase()](../../plaso/engine/knowledge_base.py)
    *   the **knowledge base** is a key-value storage which contains information from the source data needed for parsing
    *   e.g., the knowledge base can store/be initialized with:
        *   user accounts relevant to the analyses
        *   hostname, operating systems, time-zone, and code-page of the data
*   create a fake storage writer [plaso.storage.fake.writer.FakeStorageWriter(session)](../../plaso/storage/fake/writer.py)
    on [plaso.containers.sessions.Session()](../../plaso/containers/sessions.py)
    *   the **session** is to monitor the task's progress
    *   the **storage writer** is to store:
        *   parsing/analysis results as events and their data, sources, and tags
        *   set the session progress
*   create a mediator [plaso.parsers.mediator.ParserMediator(storage_writer, knowledge_base_object)](../../plaso/parsers/mediator.py)
    on the storage writer and the knowledge base storage
    *   the **mediator** is preparing the task (parsers, etc.) and:
        *   manages a list/chain of parsers to apply on the data
        *   manages a file (see an file entry below) to process by the parsers
        *   prepare events by setting their input files, parsers, and another relevant data (e.g., from the knowledge base);
            see `ProcessEvent(self, event, parser_chain, file_entry, query)`
        *   finally, the event (optionally including its data) is added into the storage writer
    *   the **file entry** provided by the mediator is, e.g., [plaso.containers.EventSource](../../plaso/containers/event_sources.py)
        implementation of [plaso.containers.interface.AttributeContainer](../../plaso/containers/interface.py)
*   adds a file entry of the input file into the mediator
*   runs the **parser** by [parser.Parse(mediator, file_entry.GetFileObject())](../../plaso/parsers/interface.py)
    of a particular parser implementation
    *   the input of the parser can be just a file entry or its file object (i.e., its content)
    *   the parser runs each **plugin** defined in this task
        to processes and generates events and updates chain of parsers in the mediator (to trigger subsequent parsing)
        by [plaso.parsers.plugins.BasePlugin](../../plaso/parsers/plugins.py) implementations
        *   i.e., it updates the parser chain object held by the mediator, transfers control to the plugin-specific `Process()` method,
            and updates the chain again once the processing is complete
*   in the case of `SQLiteParser` in this use case (when applied on data of a particular web browser), the `Parse(...)`
    is calling [plaso.parsers.sqlite_plugins.interface.SQLitePlugin(plugins.BasePlugin)](../../plaso/parsers/sqlite_plugins/interface.py)
    which is
    *   is looking for mathing schema (tables) as defined by the plugin
    *   and runs the particular plugin implementation on the opened database, e.g.,
        [plaso.parsers.sqlite_plugins.FirefoxHistoryPlugin](../../plaso/parsers/sqlite_plugins/firefox.py)
*   the `plugin = BrowserSearchPlugin` is utilized then by calling [plugin.ExamineEvent(mediator, event)](../../plaso/analysis/browser_search.py)
    for event string `History` (after formatting inside the method, it is known as `WEBHIST`)
    which will analyze results of the history plugin above by
    *   searching for particular URLs (see `_URL_FILTERS` in the plugin)
    *   and extracting their relevant parts (searched keywords) by their corresponding callback methods
*   finally, the `plugin = BrowserSearchPlugin` is utilized then by calling [plugin.CompileReport(mediator)](../../plaso/analysis/browser_search.py)
    to compile report from the events which is eventually stored by `storage_writer.AddAnalysisReport(analysis_report)` 

## Important Components to Adapt

*   [plaso.parsers.mediator.Mediator](../../plaso/parsers/mediator.py) to link input resources, manage and route events,
    and itegrate other components (e.g., the session and the storage writer)
*   [plaso.storage.interface.StorageWriter](../../plaso/storage/interface.py),
    e.g., as [plaso.storage.fake.writer.FakeStorageWriter](../../plaso/storage/fake/writer.py),
    to store resulting data (and events)
*   optionally also [plaso.engine.knowledge_base.KnowledgeBase](../../plaso/engine/knowledge_base.py)
    to provide a shared knowledge base for the plugins (if they will be distributed, i.e., run on different nodes)
