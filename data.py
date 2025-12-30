
import subprocess
import logging
from datetime import datetime
from pathlib import Path

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
    GIT_TOP_LEVEL = get_git_toplevel_for(file_path)
    GIT_FILE_PATH = str(file_path.relative_to(GIT_TOP_LEVEL))
    logger.debug(f"Getting git commits for '{GIT_FILE_PATH}'")
    cmd = [
        "git", "--no-pager", "log", 
        filter_flag,
        "--pretty=format:%cI", "--follow", "--", GIT_FILE_PATH
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

@inject_data_function
def get_file_datetimes(config: Config, filepath: Path):
    return {
        "file_creation_time": get_creation_datetime(filepath),
        "file_last_updated_time": get_last_updated_datetime(filepath)
    }


@inject_data_function
def get_pages(config: Config, filepath: Path):
    return {
        "pages": {
            page: {
                "file_creation_time": get_creation_datetime(filepath),
                "file_last_updated_time": get_last_updated_datetime(filepath)
            } for page in config.pages 
        }
    }