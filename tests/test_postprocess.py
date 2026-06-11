import zipfile
from pathlib import Path

import pytest

from torrentor.core.postprocess import cleanup, format_size, slugify, zip_and_move


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self) -> None:
        assert slugify("This is My Movie! YTS") == "this-is-my-movie-yts"

    def test_parentheses_and_year(self) -> None:
        assert slugify("My Movie (2024)") == "my-movie-2024"

    def test_multiple_spaces_and_dashes(self) -> None:
        assert slugify("some - - file   name") == "some-file-name"

    def test_unicode(self) -> None:
        assert slugify("café résumé") == "cafe-resume"

    def test_dots_and_underscores(self) -> None:
        assert slugify("file_name.with.dots") == "file_namewithdots"

    def test_empty_string(self) -> None:
        assert slugify("") == "download"

    def test_only_special_chars(self) -> None:
        assert slugify("!!!???") == "download"

    def test_already_slugified(self) -> None:
        assert slugify("already-slugified") == "already-slugified"

    def test_leading_trailing_hyphens(self) -> None:
        assert slugify("--hello--") == "hello"


class TestFormatSize:
    def test_bytes(self) -> None:
        assert format_size(500) == "500 B"

    def test_kilobytes(self) -> None:
        result = format_size(1024)
        assert "KB" in result

    def test_megabytes(self) -> None:
        result = format_size(1024 * 1024 * 5)
        assert "MB" in result

    def test_gigabytes(self) -> None:
        result = format_size(1024**3)
        assert "GB" in result

    def test_zero(self) -> None:
        assert format_size(0) == "0 B"


class TestZipAndMove:
    def test_single_file(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "My Test File!.txt").write_text("hello world")

        output_dir = tmp_path / "output"
        result = zip_and_move(source_dir, output_dir)

        assert result.exists()
        assert result.suffix == ".zip"
        assert result.parent == output_dir
        assert "my-test-file" in result.stem

        with zipfile.ZipFile(result) as zf:
            assert len(zf.namelist()) == 1

    def test_directory_with_multiple_files(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("a")
        (source_dir / "file2.txt").write_text("b")
        sub = source_dir / "subdir"
        sub.mkdir()
        (sub / "file3.txt").write_text("c")

        output_dir = tmp_path / "output"
        result = zip_and_move(source_dir, output_dir)

        assert result.exists()
        with zipfile.ZipFile(result) as zf:
            assert len(zf.namelist()) == 3

    def test_empty_source(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "empty"
        source_dir.mkdir()
        output_dir = tmp_path / "output"

        with pytest.raises(FileNotFoundError):
            zip_and_move(source_dir, output_dir)

    def test_output_dir_created(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("test")

        output_dir = tmp_path / "deep" / "nested" / "output"
        result = zip_and_move(source_dir, output_dir)

        assert result.exists()
        assert output_dir.exists()

    def test_duplicate_name_handling(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("test")

        output_dir = tmp_path / "output"

        first = zip_and_move(source_dir, output_dir)
        second = zip_and_move(source_dir, output_dir)

        assert first != second
        assert first.exists()
        assert second.exists()


class TestCleanup:
    def test_removes_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "to_remove"
        target.mkdir()
        (target / "file.txt").write_text("data")

        cleanup(target)
        assert not target.exists()

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        cleanup(tmp_path / "nonexistent")
