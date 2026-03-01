"""Language definitions and file extension mappings for vallm."""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import Optional


class Language(Enum):
    """Supported programming languages with their tree-sitter identifiers."""
    
    # Primary languages
    PYTHON = ("python", ".py", "Python")
    JAVASCRIPT = ("javascript", ".js", "JavaScript")
    TYPESCRIPT = ("typescript", ".ts", "TypeScript")
    JSX = ("jsx", ".jsx", "JSX")
    TSX = ("tsx", ".tsx", "TSX")
    
    # Systems languages
    C = ("c", ".c", "C")
    CPP = ("cpp", ".cpp", "C++")
    H = ("c", ".h", "C Header")  # Uses C parser
    HPP = ("cpp", ".hpp", "C++ Header")
    
    # JVM languages
    JAVA = ("java", ".java", "Java")
    KOTLIN = ("kotlin", ".kt", "Kotlin")
    SCALA = ("scala", ".scala", "Scala")
    
    # Web/Scripting
    GO = ("go", ".go", "Go")
    RUBY = ("ruby", ".rb", "Ruby")
    PHP = ("php", ".php", "PHP")
    
    # Functional
    RUST = ("rust", ".rs", "Rust")
    HASKELL = ("haskell", ".hs", "Haskell")
    
    # Data/Config
    SQL = ("sql", ".sql", "SQL")
    JSON = ("json", ".json", "JSON")
    YAML = ("yaml", ".yaml", "YAML")
    TOML = ("toml", ".toml", "TOML")
    
    # Shell
    BASH = ("bash", ".sh", "Bash")
    ZSH = ("bash", ".zsh", "Zsh")  # Uses bash parser
    POWERSHELL = ("powershell", ".ps1", "PowerShell")
    
    # Other
    SWIFT = ("swift", ".swift", "Swift")
    LUA = ("lua", ".lua", "Lua")
    R = ("r", ".r", "R")
    MATLAB = ("matlab", ".m", "MATLAB")
    PERL = ("perl", ".pl", "Perl")
    ELIXIR = ("elixir", ".ex", "Elixir")
    ERLANG = ("erlang", ".erl", "Erlang")
    OCAML = ("ocaml", ".ml", "OCaml")
    
    # Additional languages
    ZIG = ("zig", ".zig", "Zig")
    CRYSTAL = ("crystal", ".cr", "Crystal")
    DART = ("dart", ".dart", "Dart")
    GROOVY = ("groovy", ".groovy", "Groovy")
    CLOJURE = ("clojure", ".clj", "Clojure")
    FSHARP = ("fsharp", ".fs", "F#")
    COFFEESCRIPT = ("coffeescript", ".coffee", "CoffeeScript")
    PURESCRIPT = ("purescript", ".purs", "PureScript")
    REASON = ("reason", ".re", "ReasonML")
    RESCRIPT = ("rescript", ".res", "ReScript")
    NIM = ("nim", ".nim", "Nim")
    VALA = ("vala", ".vala", "Vala")
    D = ("d", ".d", "D")
    OBJECTIVE_C = ("objc", ".mm", "Objective-C")  # Using .mm to avoid conflict with MATLAB's .m
    ASSEMBLY = ("asm", ".asm", "Assembly")
    FORTRAN = ("fortran", ".f90", "Fortran")
    ADA = ("ada", ".ada", "Ada")
    COBOL = ("cobol", ".cob", "COBOL")
    LISP = ("lisp", ".lisp", "Lisp")
    SCHEME = ("scheme", ".scm", "Scheme")
    JULIA = ("julia", ".jl", "Julia")
    GLEAM = ("gleam", ".gleam", "Gleam")
    V = ("v", ".v", "V")
    WASM = ("wasm", ".wat", "WebAssembly Text")
    PROC = ("prolog", ".pro", "Prolog")  # Using .pro to avoid conflict with Perl's .pl
    TYPST = ("typst", ".typ", "Typst")
    TACL = ("tact", ".tact", "Tact")
    MOVE = ("move", ".move", "Move")
    CAIRO = ("cairo", ".cairo", "Cairo")
    NOIR = ("noir", ".nr", "Noir")
    CIRCOM = ("circom", ".circom", "Circom")
    SWAY = ("sway", ".sw", "Sway")
    
    def __init__(self, tree_sitter_id: str, extension: str, display_name: str):
        self.tree_sitter_id = tree_sitter_id
        self.extension = extension
        self.display_name = display_name
    
    @classmethod
    def from_extension(cls, ext: str) -> Optional[Language]:
        """Detect language from file extension (with or without dot)."""
        ext = ext.lower()
        if not ext.startswith("."):
            ext = "." + ext
        
        for lang in cls:
            if lang.extension == ext:
                return lang
        return None
    
    @classmethod
    def from_path(cls, path: str | Path) -> Optional[Language]:
        """Detect language from file path."""
        path = Path(path)
        return cls.from_extension(path.suffix)
    
    @classmethod
    def from_string(cls, name: str) -> Optional[Language]:
        """Detect language from string name (case-insensitive)."""
        name_lower = name.lower()
        
        # Direct match
        for lang in cls:
            if (lang.name.lower() == name_lower or 
                lang.tree_sitter_id.lower() == name_lower or
                lang.display_name.lower() == name_lower):
                return lang
        
        # Extension match (if user passes ".py" instead of "python")
        if name_lower.startswith("."):
            return cls.from_extension(name_lower)
        
        return None
    
    @property
    def is_compiled(self) -> bool:
        """Returns True if language typically requires compilation."""
        return self in {
            Language.C, Language.CPP, Language.H, Language.HPP,
            Language.RUST, Language.GO, Language.SWIFT,
            Language.JAVA, Language.KOTLIN, Language.SCALA,
            Language.ZIG, Language.NIM, Language.V, Language.D,
            Language.CRYSTAL, Language.DART, Language.OBJECTIVE_C,
            Language.FORTRAN, Language.ADA, Language.COBOL,
        }
    
    @property
    def is_scripting(self) -> bool:
        """Returns True if language is typically interpreted/scripting."""
        return self in {
            Language.PYTHON, Language.JAVASCRIPT, Language.TYPESCRIPT,
            Language.RUBY, Language.PHP, Language.LUA, Language.PERL,
            Language.BASH, Language.ZSH, Language.POWERSHELL,
        }
    
    @property
    def is_web(self) -> bool:
        """Returns True if language is primarily web-focused."""
        return self in {
            Language.JAVASCRIPT, Language.TYPESCRIPT, Language.JSX, Language.TSX,
            Language.PHP, Language.JSON, Language.YAML, Language.TOML,
        }


# Extension to language mapping for quick lookup
EXTENSION_MAP: dict[str, Language] = {
    lang.extension: lang for lang in Language
}


def detect_language(source: str | Path) -> Optional[Language]:
    """Auto-detect language from file path, extension, or name.
    
    Args:
        source: File path, extension (e.g., ".py"), or language name (e.g., "python")
    
    Returns:
        Language enum member or None if not recognized
    """
    source_str = str(source)
    
    # Try as file path first
    if "/" in source_str or "\\" in source_str or "." in source_str:
        lang = Language.from_path(source_str)
        if lang:
            return lang
    
    # Try as language name
    return Language.from_string(source_str)


def get_language_for_validation(source: str | Path, explicit: Optional[str] = None) -> str:
    """Get tree-sitter language ID for validation.
    
    Priority:
    1. Explicit language parameter
    2. Auto-detection from file path/extension
    3. Default to "python"
    """
    if explicit:
        lang = Language.from_string(explicit)
        if lang:
            return lang.tree_sitter_id
        return explicit  # Pass through as-is if not in enum
    
    lang = detect_language(source)
    if lang:
        return lang.tree_sitter_id
    
    return "python"  # Default fallback


# Supported languages for lizard complexity analysis
LIZARD_SUPPORTED = {
    Language.C, Language.CPP, Language.JAVA, Language.JAVASCRIPT,
    Language.TYPESCRIPT, Language.PYTHON, Language.GO, Language.RUBY,
    Language.PHP, Language.SCALA, Language.SWIFT, Language.RUST,
    Language.KOTLIN, Language.LUA,
}
