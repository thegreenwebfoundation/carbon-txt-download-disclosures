from typer.testing import CliRunner

from carbon_txt.cli import app  # type: ignore
import pathlib

runner = CliRunner(mix_stderr=False)


def test_lookup_domain_and_download_file():
    """
    Test that we can run the CLI with a custom plugin directory
    """
    assert not pathlib.Path("carbon-txt-downloads").exists(), (
        "The downloads directory should not exist before running the test. Please either move or delete it."
    )

    carbon_txt_url = (
        "https://used-in-tests.carbontxt.org/carbon-txt-with-csrd-and-renewables.txt"
    )

    result = runner.invoke(
        app,
        [
            "validate",
            "file",
            carbon_txt_url,
        ],
    )
    assert result.exit_code == 0
    assert "used-in-tests.carbontxt.org" in result.stdout

    download_path = pathlib.Path("carbon-txt-downloads")
    domain_directory = download_path / "used-in-tests.carbontxt.org"
    downloaded_file = domain_directory / "esrs-e1-efrag-2026-12-31-en.xhtml"

    # check that we see the directory created
    assert download_path.exists()

    # check that we see the file created
    assert domain_directory.exists()
    assert domain_directory.is_dir() and domain_directory.exists()

    assert downloaded_file.exists()

    # clean up after ourselves
    downloaded_file.unlink()
    domain_directory.rmdir()
    download_path.rmdir()
