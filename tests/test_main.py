import main


def test_run_returns_0_on_success(valid_files, tmp_path, capsys):

    file_a, file_b = valid_files
    output = tmp_path / "out" / "report.xlsx"

    exit_code = main.run(file_a, file_b, output)

    assert exit_code == 0
    assert output.is_file()
    assert "ERROR" not in capsys.readouterr().err


def test_run_returns_1_when_files_are_missing(tmp_path, capsys):

    output = tmp_path / "report.xlsx"

    exit_code = main.run(
        tmp_path / "missing_a.xlsx",
        tmp_path / "missing_b.xlsx",
        output,
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ERROR" in captured.err
    assert "File A not found" in captured.err
    assert "File B not found" in captured.err
    assert "Traceback" not in captured.err
    assert not output.exists()


def test_run_returns_1_for_invalid_file_content(
    make_excel, tmp_path, capsys
):

    file_a = make_excel("a.xlsx", [(1, "John", "john@example.com", "Active")])
    file_b = make_excel(
        "b.xlsx",
        [(1, "John", "john@example.com")],
        columns=["Customer ID", "Name", "Email"],
    )
    output = tmp_path / "report.xlsx"

    exit_code = main.run(file_a, file_b, output)

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Missing required columns: Status" in captured.err
    assert "Traceback" not in captured.err
    assert not output.exists()


class FakeTk:
    """Replaces tkinter.Tk so the tests do not open any windows."""

    def withdraw(self):
        pass

    def attributes(self, *args):
        pass

    def destroy(self):
        pass


def test_main_returns_0_with_valid_selected_files(
    valid_files, tmp_path, monkeypatch
):

    file_a, file_b = valid_files
    selected = iter([str(file_a), str(file_b)])
    output = tmp_path / "out" / "report.xlsx"

    monkeypatch.setattr(main.tk, "Tk", FakeTk)
    monkeypatch.setattr(main, "select_file", lambda title: next(selected))
    monkeypatch.setattr(main, "OUTPUT_FILE", str(output))

    assert main.main() == 0
    assert output.is_file()


def test_main_returns_1_when_selected_file_does_not_exist(
    tmp_path, monkeypatch, capsys
):

    selected = iter([
        str(tmp_path / "missing_a.xlsx"),
        str(tmp_path / "missing_b.xlsx"),
    ])

    monkeypatch.setattr(main.tk, "Tk", FakeTk)
    monkeypatch.setattr(main, "select_file", lambda title: next(selected))
    monkeypatch.setattr(main, "OUTPUT_FILE", str(tmp_path / "report.xlsx"))

    assert main.main() == 1
    assert "File A not found" in capsys.readouterr().err


def test_main_exits_when_no_file_is_selected(monkeypatch):

    monkeypatch.setattr(main.tk, "Tk", FakeTk)
    monkeypatch.setattr(main, "select_file", lambda title: "")

    try:
        main.main()
    except SystemExit as exit_info:
        assert "File A" in str(exit_info.code)
    else:
        raise AssertionError("SystemExit was expected")
