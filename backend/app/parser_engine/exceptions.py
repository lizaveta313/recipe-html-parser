"""Parser engine exceptions."""


class ParserEngineError(Exception):
    """Base parser engine error."""


class TokenizationError(ParserEngineError):
    """Raised when tokenizer cannot process HTML input."""


class DomParserError(ParserEngineError):
    """Raised when DOM tree construction fails unexpectedly."""


class RecipeExtractionError(ParserEngineError):
    """Raised when recipe extraction cannot continue."""


class HtmlAnalysisError(ParserEngineError):
    """Raised when HTML analysis cannot continue."""

