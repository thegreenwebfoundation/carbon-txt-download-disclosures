from pathlib import Path
from urllib.parse import urlparse

from typing import Optional

import logging
import httpx
from carbon_txt.plugins import hookimpl
from structlog import get_logger

logger = get_logger()


def log_safely(log_message: str, logs: Optional[list], level=logging.INFO):
    """
    Log a message, and append it to a list of logs
    """
    logger.log(level, log_message)
    if logs is not None:
        logs.append(log_message)


plugin_name = "carbon_txt_download_disclosures"


def download_document(document, response, logs):
    """
    Download a document and save it to the local filesystem,
    returning the path to the file if successful
    """

    parsed_url = urlparse(document.url)
    hostname = parsed_url.hostname
    path = parsed_url.path.lstrip("/").replace("/", "-")

    # Create the directory structure
    base_dir = Path("carbon-txt-downloads")
    hostname_dir = base_dir / hostname
    hostname_dir.mkdir(parents=True, exist_ok=True)

    # Define the file path
    file_path = hostname_dir / path

    if file_path.exists():
        log_safely(
            f"The file at {document.url} has already been downloaded to {file_path}. Not doing anything to avoid overwriting it.",
            logs,
            level=logging.WARNING,
        )
        return

    # Otherwise write the contents of the URL to the file
    file_path.write_bytes(response.content)

    log_safely(f"The file at {document.url} has been written to {file_path}", logs)
    return file_path


@hookimpl
def process_document(
    document,
    logs: Optional[list],
):
    """
    Download every disclosure document linked in a carbon.txt file
    """
    results = []

    # fetch our file
    response = httpx.get(document.url, follow_redirects=True)

    if response.status_code == 200:
        log_safely(f"Downloaded file from {document.url} ", logs)

        # try writing the file to local filesystem
        if file_path := download_document(document, response, logs):
            results = [
                {
                    "domain": document.domain,
                    "url": document.url,
                    "file_location": file_path,
                }
            ]

    # return the results of processing the document - either an empty list, or a list containing
    # a dictionary with the domain, url, where we write the file to
    return {
        "plugin_name": plugin_name,
        "document_results": results,
        "logs": logs,
    }
