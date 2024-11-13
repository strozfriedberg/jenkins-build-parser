# Jenkins config/build parser

This script parses Jenkins build configuration files and plugin configuration files and outputs
their attributes to two CSV files.

The script extracts the following attributes for Jenkins jobs and places them in a CSV titled
`jenkins_jobs.csv`:

| Field | Description |
| ----- | ----------- |
| config_modified_time | Modified time of the `config.xml` file associated with the build |
| build_modified_time | Modified time of the `build.xml` file associated with the build |
| build_start_time | Start time of the build |
| keep_log | Boolean that indicates whether the build kept the log |
| username | User associated with the build |
| build_number | Build number |
| result | Result status of the build |
| job_name | Name of the job associated with the build |
| config_description | Description of the job associated with the build |

Each Jenkins job on the server should have a corresponding `config.xml` file that contains
configuration data for the job. Each Jenkins build is associated with a job and will have a
corresponding `build.xml` that is generated when it completes.

Note that this script uses file modified times to populate `config_modified_time` and
`build_modified_time` in the `jenkins_jobs` CSV. Make sure that you preserve original file
timestamps if you're not mounting an image or running this script on a live system.

The script extracts the following attributes for Jenkins plugins and places them in a CSV titled
`jenkins_plugins.csv`:

| Field | Description |
| ----- | ----------- |
| name | Friendly name of the plugin |
| version | Version of the plugin |
| url | URL associated with the plugin |

## Usage

Python 3.11 is required to run this script.

To run this script, you must provide the path to the $JENKINS_HOME directory. The script will look
for `build.xml` and `config.xml` files in `$JENKINS_HOME/jobs` to populate `jenkins_jobs.csv`, and
will look for `pom.xml` files in `$JENKINS_HOME/plugins` to populate `jenkins_plugins.csv`.

Use `uv` to install the dependencies for this script and run it in a virtualenv.
```
uv run parse_jenkins_builds.py <path-to-input-dir>
```

If you're on a system without access to the internet, you can pass the URL to your local package
server to the `--default-index` option.
```
uv run --default-index <url-to-local-package-server> parse_jenkins_builds.py <path-to-input-dir> 
```

If you'd prefer not to use `uv`, you can use the included `requirements.txt` file to install the
dependencies instead, and run the script normally.

```
pip install -r requirements.txt
python parse_jenkins_builds.py <path-to-input-dir>
```

If the script encounters any warnings or errors, they will be logged to a file named
`jenkins_build_parser.log`. For example, if there is more than one userID found in a build file,
a warning containing the file path of the config file will be logged.

If you encounter any errors, feel free to open an issue.