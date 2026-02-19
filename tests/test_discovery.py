from pathlib import Path

from humanize_code.analyzer import iter_source_files


def test_iter_source_files_skips_tests_by_default(tmp_path: Path) -> None:
    src_file = tmp_path / "src" / "main.py"
    test_file = tmp_path / "tests" / "test_main.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("print('ok')\n", encoding="utf-8")
    test_file.write_text("def test_x():\n    assert True\n", encoding="utf-8")

    found = iter_source_files([tmp_path])
    found_set = {path.resolve() for path in found}

    assert src_file.resolve() in found_set
    assert test_file.resolve() not in found_set


def test_iter_source_files_can_include_tests(tmp_path: Path) -> None:
    src_file = tmp_path / "pkg" / "logic.py"
    test_file = tmp_path / "tests" / "test_logic.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("value = 1\n", encoding="utf-8")
    test_file.write_text("def test_value():\n    assert 1 == 1\n", encoding="utf-8")

    found = iter_source_files([tmp_path], include_tests=True)
    found_set = {path.resolve() for path in found}

    assert src_file.resolve() in found_set
    assert test_file.resolve() in found_set

