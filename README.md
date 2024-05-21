# Jenkins config/build parser

This script parses Jenkins `build.xml` and `config.xml` files and outputs their attributes to a CSV.

The following attributes are supported:


| Field | Description |
| ----- | ----------- |
| config_modified_time | Modified time of the `config.xml` file associated with the build |
| build_modified_time | Modified time of the `build.xml` file associated with the build |
| build_start_time | Start time of the build |
| keep_log | Boolean that indicates whether the build kept the log |
| username | User associated with the build |
| build_number | Build number |
| result | Result status of the build |
| job_name | Name of the job with the build |
| config_description | Description of the job associated with the build |

Each jenkins job on the server should have a corresponding `config.xml` file that contains configuration data for the job. Each jenkins build is associated with a job and will have a corresponding `build.xml` that is generated when it completes.

When you extract the `build.xml` and `config.xml` files from a jenkins server, make sure that you keep the original file timestamps and original directory structure.

## Usage

Python 3.11 is required to run this script.

To run this script, you must provide the path that contains all of your `build.xml` and `config.xml` files. These files will be extracted recursively. The script assumes that you have preserved the original directory structure from the Jenkins server (i.e., that each `config.xml` and `build.xml` has a unique parent directory), and that you have preserved the original modified times of the files and folders therein.

Use `poetry` to install the dependencies for this script.
```
poetry install
```

If you're on a system without access to the internet, you can use a local pip server to install dependencies using the `requirements.txt` file.
```
pip install -r requirements.txt -i <url-to-local-pip-server>
```
```
poetry run python parse_jenkins_builds.py <path-to-input-dir>
```

When finished, the script will write to a file called `jenkins_jobs.csv` in your current working directory.

If you encounter any errors, reach out to Julia Paluch on Slack or over email at julia.paluch@strozfrideberg.com.