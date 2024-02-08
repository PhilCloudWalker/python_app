from files.compare import sync
import pytest


def make_file(path, file_name, content):
    p = path / file_name
    p.write_text(content)
    return p


@pytest.fixture
def src_path(tmp_path):
    src_path = tmp_path / "src"
    src_path.mkdir()
    return src_path


@pytest.fixture
def dest_path(tmp_path):
    dest_path = tmp_path / "dest"
    dest_path.mkdir()
    return dest_path


def test_create_file(src_path):
    content = "test"
    file = make_file(src_path, "hello.txt", content)
    assert file.read_text() == content
    assert len(list(src_path.iterdir())) == 1


def test_copy_file(src_path, dest_path):
    """If a file exists in the source but not in the destination, copy the file over."""

    file_name = "new.txt"
    make_file(src_path, file_name, "Initial file")
    sync(src_path, dest_path)

    assert len(list(dest_path.iterdir())) == 1
    assert (dest_path / file_name).name == file_name


def test_delete_file(src_path, dest_path):
    """If a file exists in the source, but it has a different name than in the destination, rename the destination file to match."""

    file_name = "delete.txt"
    make_file(dest_path, file_name, "dest file")
    sync(src_path, dest_path)

    assert len(list(dest_path.iterdir())) == 0


def test_rename_file(src_path, dest_path):
    """If a file exists in the destination but not in the source, remove it."""
    content = "same content"
    make_file(src_path, "original.txt", content)
    make_file(dest_path, "to_be_renamed.txt", content)
    sync(src_path, dest_path)

    assert len(list(dest_path.iterdir())) == 1
    assert (dest_path / "original.txt").name == "original.txt"
    assert (dest_path / "original.txt").read_text() == content


def test_when_a_file_has_been_renamed_in_the_source(src_path, dest_path):
    content = "I am a file that was renamed"
    source_path = src_path / "source-filename"
    old_dest_path = dest_path / "dest-filename"
    expected_dest_path = dest_path / "source-filename"
    source_path.write_text(content)
    old_dest_path.write_text(content)

    sync(src_path, dest_path)

    assert old_dest_path.exists() is False
    assert expected_dest_path.read_text() == content
