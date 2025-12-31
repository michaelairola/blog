
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import contextlib


from jinja2static import Config
from jinja2static import inject_data_function

logger = logging.getLogger(__name__)


def get_git_toplevel_for(file_path):
    logger.debug(f"Getting git repo for '{file_path}'")
    cmd = ['git', 'rev-parse', '--show-toplevel', str(file_path)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if stderr:
        logger.debug(f"Error getting creation date for {file_path}: {stderr}")
        return None
    return Path(stdout.strip().split('\n')[0])

def get_git_logs(file_path, filter_flag: str) -> datetime:
    """
    Retrieves the first and last commit date for a given file from git history.
    These can be thought of as the creation and last updated dates for the file.
    """
    logger.debug(f"Getting git commits for '{file_path}'")
    cmd = [
        "git", 
        "-C", str(file_path.parent),
        "--no-pager", "log", 
        filter_flag,
        "--pretty=format:%cI", "--follow", 
        "--", str(file_path.name)
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if stderr:
        logger.debug(f"Error getting creation date for {file_path}: {stderr}")
        return None
    date_str = stdout.strip().split('\n')[-1]
    try:
        return datetime.fromisoformat(date_str)
    except ValueError as e:
        logger.debug(f"Error parsing date '{date_str}': {e}")
        return None

def get_creation_datetime(file_path):
    return get_git_logs(file_path, "--diff-filter=A")

def get_last_updated_datetime(file_path):
    return get_git_logs(file_path, "-1")

def page_data(config, file_path):
    file_path = config.templates / file_path
    return {
        "file_creation_time": get_creation_datetime(file_path),
        "file_last_updated_time": get_last_updated_datetime(file_path)
    }

@inject_data_function
def get_file_datetimes(config: Config, file_path: Path):
    return page_data(config, file_path)


@inject_data_function
def get_pages(config: Config, file_path: Path):
    return {
        "pages": {
            page: page_data(config, file_path) for page in config.pages 
        }
    }