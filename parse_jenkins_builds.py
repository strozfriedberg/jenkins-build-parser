# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "lxml",
#     "tqdm",
# ]
# ///
import argparse
import glob
import os
import csv
import logging
import pathlib


from tqdm import tqdm
from multiprocessing import Pool
from bs4 import BeautifulSoup
from itertools import repeat

from datetime import datetime, timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler("jenkins_build_parser.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

fieldnames = [
    "config_modified_time",
    "build_modified_time",
    "build_start_time",
    "keep_log",
    "username",
    "build_number",
    "result",
    "job_name",
    "config_description",
]


def from_unix(unix_timestamp):
    try:
        ts = int(unix_timestamp)
    except ValueError:
        return None
    try:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.fromtimestamp(ts / 1000, timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


def get_attribute_from_soup(attr, soup, file_):
    try:
        tags = soup.findAll(attr)
        if len(tags) > 1:
            logger.warning(
                f"Multiple {attr} tags found in {file_}. Using the first one."
            )
        return tags[0].text
    except IndexError:
        return ""


def get_build_attributes(build_file):
    handle = open(build_file)
    soup = BeautifulSoup(handle, "xml")
    return {
        "username": get_attribute_from_soup("userId", soup, build_file),
        "build_start_time": from_unix(
            get_attribute_from_soup("startTime", soup, build_file)
        ),
        "keep_log": bool(get_attribute_from_soup("keepLog", soup, build_file)),
        "result": get_attribute_from_soup("result", soup, build_file),
    }


def parse_build(job_to_config, build_path):
    path = pathlib.Path(build_path).parts

    try:
        # Example path to build config: <job_name>/builds/<build_number>/build.xml
        job_name = path[-4]
        build_number = path[-2]
    except IndexError:
        logger.error(f"Could not parse job name or build number from {build_path}")
        raise
    job = job_to_config.get(job_name, {})
    build_dict = {
        "job_name": job_name,
        "build_number": build_number,
        "config_modified_time": job.get("modified_time"),
        "build_modified_time": from_unix(os.path.getmtime(build_path)),
        "config_description": job.get("description"),
        **get_build_attributes(build_path),
    }
    return build_dict


def parse_config(config_path):
    path = pathlib.Path(config_path).parts
    modified_time = os.path.getmtime(config_path)
    formatted_modified_time = from_unix(modified_time)

    try:
        # Example path to job config: <job_name>/config.xml
        job_name = path[-2]
    except IndexError:
        logger.error(f"Could not parse job name from {config_path}")
        raise

    try:
        with open(config_path, "r") as f:
            soup = BeautifulSoup(f, "xml")
            description = (
                get_attribute_from_soup("description", soup, config_path)
                .replace("\n", "\\n")
                .encode("utf-8")
            )
    except Exception as e:
        logger.error(f"Could not parse description from {config_path}: {e}")
        raise e
    job_attrs = {
        "modified_time": formatted_modified_time,
        "description": description,
    }
    return job_name, job_attrs


def setup_argparse():
    parser = argparse.ArgumentParser(
        prog="parse_jenkins_builds.py",
        description="Parses Jenkins build.xml and config.xml files and aggregates into a csv file.",
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to directory containing Jenkins config.xml and build.xml files. Processed recursively.",
    )
    return parser.parse_args()

def main():
    parser = setup_argparse()
    path = parser.path
    print("Getting all build.xml files...")
    builds = glob.glob(path + "/**/build.xml", recursive=True)
    print("Getting all config.xml files...")
    configs = glob.glob(path + "/**/config.xml", recursive=True)
    job_to_config = {}

    print("Parsing configs...")
    for config_path in tqdm(configs):
        job_name, job_attrs = parse_config(config_path)
        job_to_config[job_name] = job_attrs

    print("Parsing and writing builds...")
    with open("jenkins_jobs.csv", "w") as jobs_csv:
        writer = csv.DictWriter(jobs_csv, fieldnames=fieldnames)
        writer.writeheader()
        with Pool() as pool:
            for result in pool.starmap(
                parse_build, tqdm(zip(repeat(job_to_config), builds), total=len(builds))
            ):
                writer.writerow(result)
                jobs_csv.flush()


if __name__ == "__main__":
    main()
