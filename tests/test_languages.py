"""Tests for Language enum and language detection."""

import pytest

from vallm.core.languages import Language, detect_language, get_language_for_validation, LIZARD_SUPPORTED


class TestLanguageEnum:
    """Test Language enum functionality."""
    
    def test_all_languages_have_properties(self):
        """Test that all languages have required properties."""
        for lang in Language:
            assert lang.tree_sitter_id
            assert lang.extension.startswith(".")
            assert lang.display_name
    
    def test_python_properties(self):
        """Test Python language properties."""
        assert Language.PYTHON.tree_sitter_id == "python"
        assert Language.PYTHON.extension == ".py"
        assert Language.PYTHON.display_name == "Python"
        assert Language.PYTHON.is_scripting is True
        assert Language.PYTHON.is_compiled is False
    
    def test_rust_properties(self):
        """Test Rust language properties."""
        assert Language.RUST.tree_sitter_id == "rust"
        assert Language.RUST.extension == ".rs"
        assert Language.RUST.display_name == "Rust"
        assert Language.RUST.is_compiled is True
        assert Language.RUST.is_scripting is False
    
    def test_javascript_properties(self):
        """Test JavaScript language properties."""
        assert Language.JAVASCRIPT.is_web is True
        assert Language.JAVASCRIPT.is_scripting is True
    
    def test_go_properties(self):
        """Test Go language properties."""
        assert Language.GO.is_compiled is True
        assert Language.GO.is_scripting is False


class TestFromExtension:
    """Test language detection from file extensions."""
    
    def test_common_extensions(self):
        """Test detection of common file extensions."""
        assert Language.from_extension(".py") == Language.PYTHON
        assert Language.from_extension(".js") == Language.JAVASCRIPT
        assert Language.from_extension(".ts") == Language.TYPESCRIPT
        assert Language.from_extension(".go") == Language.GO
        assert Language.from_extension(".rs") == Language.RUST
        assert Language.from_extension(".java") == Language.JAVA
        assert Language.from_extension(".c") == Language.C
        assert Language.from_extension(".cpp") == Language.CPP
    
    def test_extension_without_dot(self):
        """Test detection without leading dot."""
        assert Language.from_extension("py") == Language.PYTHON
        assert Language.from_extension("js") == Language.JAVASCRIPT
    
    def test_case_insensitive(self):
        """Test case-insensitive extension matching."""
        assert Language.from_extension(".PY") == Language.PYTHON
        assert Language.from_extension(".Js") == Language.JAVASCRIPT
    
    def test_unknown_extension(self):
        """Test that unknown extensions return None."""
        assert Language.from_extension(".unknown") is None
        assert Language.from_extension(".xyz") is None


class TestFromPath:
    """Test language detection from file paths."""
    
    def test_simple_paths(self):
        """Test detection from simple file paths."""
        assert Language.from_path("script.py") == Language.PYTHON
        assert Language.from_path("app.js") == Language.JAVASCRIPT
        assert Language.from_path("main.go") == Language.GO
    
    def test_paths_with_directories(self):
        """Test detection from paths with directories."""
        assert Language.from_path("/home/user/project/main.py") == Language.PYTHON
        assert Language.from_path("src/components/App.tsx") == Language.TSX
        assert Language.from_path("./relative/path/lib.rs") == Language.RUST
    
    def test_path_objects(self):
        """Test detection from Path objects."""
        from pathlib import Path
        assert Language.from_path(Path("test.py")) == Language.PYTHON


class TestFromString:
    """Test language detection from string names."""
    
    def test_by_name(self):
        """Test detection by language name."""
        assert Language.from_string("python") == Language.PYTHON
        assert Language.from_string("javascript") == Language.JAVASCRIPT
        assert Language.from_string("typescript") == Language.TYPESCRIPT
    
    def test_by_display_name(self):
        """Test detection by display name."""
        assert Language.from_string("Python") == Language.PYTHON
        assert Language.from_string("JavaScript") == Language.JAVASCRIPT
        assert Language.from_string("TypeScript") == Language.TYPESCRIPT
    
    def test_by_tree_sitter_id(self):
        """Test detection by tree-sitter ID."""
        assert Language.from_string("python") == Language.PYTHON
        assert Language.from_string("javascript") == Language.JAVASCRIPT
    
    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        assert Language.from_string("PYTHON") == Language.PYTHON
        assert Language.from_string("JavaScript") == Language.JAVASCRIPT
        assert Language.from_string("go") == Language.GO
    
    def test_by_extension(self):
        """Test detection by extension string."""
        assert Language.from_string(".py") == Language.PYTHON
        assert Language.from_string(".rs") == Language.RUST
    
    def test_unknown(self):
        """Test that unknown strings return None."""
        assert Language.from_string("unknown") is None
        assert Language.from_string("xyz") is None


class TestDetectLanguage:
    """Test the main detect_language function."""
    
    def test_from_path(self):
        """Test detection from various path formats."""
        assert detect_language("main.py") == Language.PYTHON
        assert detect_language("/path/to/file.rs") == Language.RUST
    
    def test_from_extension(self):
        """Test detection from extension."""
        assert detect_language(".go") == Language.GO
        assert detect_language(".java") == Language.JAVA
    
    def test_from_name(self):
        """Test detection from language name."""
        assert detect_language("kotlin") == Language.KOTLIN
        assert detect_language("scala") == Language.SCALA
    
    def test_unknown(self):
        """Test that unknown inputs return None."""
        assert detect_language("unknown.xyz") is None
        assert detect_language(".unknown") is None


class TestGetLanguageForValidation:
    """Test get_language_for_validation function."""
    
    def test_explicit_language(self):
        """Test with explicit language parameter."""
        result = get_language_for_validation("file.txt", "rust")
        assert result == "rust"
    
    def test_auto_detection(self):
        """Test auto-detection from file path."""
        result = get_language_for_validation("main.py")
        assert result == "python"
    
    def test_auto_detection_from_path(self):
        """Test auto-detection from Path object."""
        from pathlib import Path
        result = get_language_for_validation(Path("script.js"))
        assert result == "javascript"
    
    def test_default_fallback(self):
        """Test fallback to python when detection fails."""
        result = get_language_for_validation("unknown.xyz")
        assert result == "python"
    
    def test_explicit_overrides_auto(self):
        """Test that explicit language overrides auto-detection."""
        result = get_language_for_validation("script.py", "javascript")
        assert result == "javascript"


class TestLizardSupported:
    """Test LIZARD_SUPPORTED set."""
    
    def test_common_languages_supported(self):
        """Test that common languages are in LIZARD_SUPPORTED."""
        assert Language.PYTHON in LIZARD_SUPPORTED
        assert Language.JAVASCRIPT in LIZARD_SUPPORTED
        assert Language.TYPESCRIPT in LIZARD_SUPPORTED
        assert Language.GO in LIZARD_SUPPORTED
        assert Language.RUST in LIZARD_SUPPORTED
        assert Language.JAVA in LIZARD_SUPPORTED
        assert Language.C in LIZARD_SUPPORTED
        assert Language.CPP in LIZARD_SUPPORTED
        assert Language.RUBY in LIZARD_SUPPORTED
        assert Language.PHP in LIZARD_SUPPORTED
    
    def test_newer_languages(self):
        """Test newer/less common languages."""
        assert Language.SWIFT in LIZARD_SUPPORTED
        assert Language.KOTLIN in LIZARD_SUPPORTED
        assert Language.SCALA in LIZARD_SUPPORTED


class TestNewLanguages:
    """Test the newly added languages."""
    
    def test_zig(self):
        """Test Zig language."""
        assert Language.ZIG.tree_sitter_id == "zig"
        assert Language.ZIG.extension == ".zig"
        assert Language.ZIG.is_compiled is True
    
    def test_dart(self):
        """Test Dart language."""
        assert Language.DART.tree_sitter_id == "dart"
        assert Language.DART.extension == ".dart"
    
    def test_clojure(self):
        """Test Clojure language."""
        assert Language.CLOJURE.tree_sitter_id == "clojure"
        assert Language.CLOJURE.extension == ".clj"
    
    def test_julia(self):
        """Test Julia language."""
        assert Language.JULIA.tree_sitter_id == "julia"
        assert Language.JULIA.extension == ".jl"
    
    def test_nim(self):
        """Test Nim language."""
        assert Language.NIM.tree_sitter_id == "nim"
        assert Language.NIM.extension == ".nim"
        assert Language.NIM.is_compiled is True
    
    def test_v(self):
        """Test V language."""
        assert Language.V.tree_sitter_id == "v"
        assert Language.V.extension == ".v"
        assert Language.V.is_compiled is True
    
    def test_zig_detection(self):
        """Test Zig auto-detection."""
        assert detect_language("main.zig") == Language.ZIG
        assert detect_language(".zig") == Language.ZIG
    
    def test_julia_detection(self):
        """Test Julia auto-detection."""
        assert detect_language("script.jl") == Language.JULIA
        assert detect_language(".jl") == Language.JULIA
    
    def test_all_languages_detectable(self):
        """Test that all languages can be detected from their extension."""
        for lang in Language:
            detected = detect_language(f"file{lang.extension}")
            assert detected == lang, f"Failed to detect {lang.name} from extension {lang.extension}"
