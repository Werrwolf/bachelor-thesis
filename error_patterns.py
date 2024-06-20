"""This file holds the regular expression pattern configurations used by extract-build-failure.py.
Available dictionaries:
    - BUILD_PATTERNS: patterns describing a build error
    - INFRA_PATTERNS: patterns describing an infrastructure error
Dictionary structure:
    Each pattern dictionary consists of key, that describe the <tool> that caused the error. The
    corresponding values can be either
        - a list, containing regular expression patterns that can be used to detect the error
        - another dictionary, where the key is a special error type (e.g. compiler errors
          distinguish between GCC, GHS and VS) and the value is a list of regular expressions
Each pattern can contain any of the following capture groups that will be shown in the generated
message:
    - file: file in which the error occurred
    - line: line in which the error occurred
    - type: error type (e.g. error code)
    - details: error details. If not given, the whole match will be used as "details".
"""

"""When adding new regex, please add example error message to test/data/all_errors.json in order to ensure further
correctness of the regex"""

INFRA_PATTERNS = {
    "Infrastructure": {
        "": [
            r"Unexpected failure during module execution.",
            r"Failed to update apt cache",
            # r"ssh: .+Connection timed out",
            r"^.+extended fault data: .+",
            r"WebException .+",
            r"HTTP error \d+ .+",
            # r"^Connection failure: .+$",
        ],
        "Host unreachable": [
            r"(Data could not be sent to remote host|Make sure this host can be reached|No address associated with hostname).+$"
        ],
    },
    "Infrastructure - Ansible": {r"Timeout \(.*\) waiting for privilege escalation prompt"},
    "Infrastructure - Artifactory": {
        "": [
            r"\[Error\].* Artifactory response: (?P<type>.+)\n<.+>\n(?P<details>[^<]+)",
            r"\[Error\].* Artifactory response: (?P<type>.+)" r"(\n(.+\n)*.+errors[^{]+{\n(?P<details>[^{}]+)})?",
            r"^.*http.client.IncompleteRead: IncompleteRead.*",
            r"unauthorized: The client does not have permission to push to the repository",
            r"ConnectionError: .+artifactory\.cc\.bmwgroup\.net.*$",
            r"Failure downloading https:\/\/(.*)artifactory.cc.bmwgroup.net\/(.*), Connection failure: The read operation timed out",
            r"Error downloading 'https:\/\/(.*)\.artifactory\.cc\.bmwgroup\.net(.*)The remote name could not be resolved: '(.*)\.artifactory\.cc\.bmwgroup\.net'",
            r"artifactory-cc-bmwgroup-net-artifactory.*connection reset by peer$",
        ],
        "Bazel download error": [r"could not download Bazel:.+unable to complete request.+$"],
        "Download error": [r"could not download .* failed with error.*$"],
        "Unexpected EOF": [r"could not download .* unexpected EOF$"],
        "Checksum mismatch": [
            r"Error in download: java\.io\.IOException: Error downloading \[.+\] to .+: Checksum was [a-f0-9]+ but wanted [a-f0-9]+"
        ],
        "Content-Length mismatch": [
            r"Error downloading\s\[http(s)?:\/\/(\w+)\.artifactory\.cc\.bmwgroup\.net\/artifactory\/.* Bytes read [0-9]* but wanted [0-9]*"
        ],
        "Operation failed": [r"^.*Non-zero return code from art_cli:.*"],
        "Operation timed out": [
            r"Error downloading 'https:\/\/(.*)\.artifactory\.cc\.bmwgroup\.net(.*)to(.*)\: The operation has timed out"
        ],
        "Permission": [r"403 Client Error: Forbidden for url.*"],
        "Unknown host (ddad)": [r"Unknown\shost:\sddad\.artifactory\.cc\.bmwgroup\.net"],
        "Unknown host (codecraft)": [r"Unknown\shost:\scodecraft(.*)artifactory(.*)\.cc\.bmwgroup\.net"],
        "Fetch failed": [
            r"ERROR:.+An error occurred during the fetch of repository.+(\n.+){1,5}\nError in download.+",
            r"^.*E: Failed to fetch https:\/\/.*artifactory\.cc\.bmwgroup\.net\/.* File has unexpected size \(.* != .*\)\. Mirror sync in progress\?.*$",
        ],
        "Service unreachable": [r"artifactory\.cc\.bmwgroup\.net[^\s]*\s(?P<details>[^\(]*\(?Service Unavailable\)?)"],
    },
    "Infrastructure - Bazel remote cache": {
        "Inaccessible remote cache": [
            r"WARNING: Writing to Remote Cache:\nio.grpc.StatusRuntimeException: UNKNOWN: operation not permitted",
            r"WARNING: Writing to Remote Cache:\nio.grpc.StatusRuntimeException: UNKNOWN: EOF",
            r"ERROR: Failed to query remote execution capabilities: UNAVAILABLE: Unable to resolve host buildbarn\.cc\.bmwgroup\.net",
            r"^java.io.IOException: io.grpc.StatusRuntimeException: UNAVAILABLE: Unable to resolve host buildbarn.cc.bmwgroup.net$",
        ],
        "Build without the bytes": [
            r"^ERROR: .* Failed to fetch file with hash '.*' because it does not exist remotely\..*$",
            r"^(?:\s+|\\t)?(Suppressed: )?java\.io\.IOException: Failed to fetch file with hash '.*' because it does not exist remotely\..*$",
            r"ERROR: .* failed: failed to create _solib symbolic link .* to target .*: Missing digest: .*",
            r"ERROR: .*: Exec failed due to IOException: null",
            r"^ERROR: .*io\.grpc\.StatusRuntimeException: UNAVAILABLE: io exception.*$",
            r"^(java.io.IOException:|ERROR:).*io.grpc.StatusRuntimeException: UNAVAILABLE: upstream connect error or disconnect/reset before headers.*$",
        ],
        "Connection closed": [
            r"^.*Suppressed: java.io.IOException: An existing connection was forcibly closed by the remote host.*$"
        ],
        "Connection timed out": [r"ERROR: Failed to query remote execution capabilities: [Cc]onnection timed out.+$"],
        "Connection refused": [
            r"ERROR: Failed to query remote execution capabilities: Connection refused",
            r"ERROR: Failed to query remote execution capabilities: finishConnect\(\.\.\) failed: Connection refused: buildbarn\.cc\.bmwgroup\.net/.*$",
            r"^Caused by:.*UNAVAILABLE:.*connection error",
            r"^.*UNAVAILABLE.*connection error.*connection refused.*",
        ],
        "Deadline exceeded": [r"^.*DEADLINE_EXCEEDED:.*deadline exceeded.*"],
        "Handshake timed out": [r"ERROR: Failed to query remote execution capabilities: handshake timed out after.+$"],
        "Invalid Certificate": [
            r"^ERROR: Failed to init TLS infrastructure using '.*' as client certificate: File does not contain valid certificates: .*"
        ],
        "No route to host": [
            r"ERROR: Failed to query remote execution capabilities: finishConnect\(\.\.\) failed: No route to host:.+$"
        ],
        "No healthy upstream": [
            r"^java.io.IOException: io.grpc.StatusRuntimeException: UNAVAILABLE: no healthy upstream$",
            r"^ERROR: .*io\.grpc\.StatusRuntimeException: UNAVAILABLE: no healthy upstream$",
        ],
        "Resource exhausted": [r"^ERROR:.*io\.grpc\.StatusRuntimeException: RESOURCE_EXHAUSTED.*$"],
        "Resource not found": [r"^.*Traceback.+\n( .+\n)+.+ResourceNotFound.*"],
        "Generic status runtime exception": [r"^ERROR:.+io\.grpc\.StatusRuntimeException:.+$"],
    },
    "Infrastructure - Bazel Remote Execution": {
        "Operation not found": [r"^ERROR: .+\(Exit 34\): NOT_FOUND: Operation not found:.+$"],
        "Docker pull failed": [r"^ERROR: .+\(Exit 34\): INVALID_ARGUMENT: Unable to start docker container.+$"],
    },
    "Infrastructure - BES upload": {
        "Failure": [r"^ERROR: The Build Event Protocol upload failed.*"],
        "Timeout": [r"^ERROR: The Build Event Protocol upload timed out.*"],
    },
    "Infrastructure - Bazel test logs reporter": [r"bazel_test_logs_reporter - Unexpected error: (?P<details>.+)"],
    "Infrastructure - Git LFS": [r"^.*Request Time-out.*", r"batch response: Fatal error: (?P<details>.+)"],
    "Infrastructure - PyPI server not responding (possible AF auth failure)": [
        r"Could not find a version that satisfies the requirement .+"
    ],
    "Infrastructure - Git": [
        r"Unable to checkout .+ in submodule path .+",
        "error: failed to push .+",
        r"ERROR:.+An error occurred during the fetch of repository.+(\n.+){1,}\nError in fail: error running 'git fetch.+",
        r"fatal:.+Could not read from remote repository.+",
    ],
    "Infrastructure - Docker": [
        r"=+\n.+\n=+\n+Cannot connect to the Docker daemon .+",
        r"=+\n.+\n=+\n+Error response .+",
        r"^.*Error: unable to pull ddad.artifactory.cc.bmwgroup.net.*",
        r"Error\: error logging into \"ddad\.artifactory\.cc\.bmwgroup\.net\"\: invalid username\/password",
        r"Error response from daemon(.*)artifactory\.cc\.bmwgroup\.net[^\s]*\s(?P<details>.*)",
        r"manifest for artifactory\.cc\.bmwgroup\.net\/.*\:latest not found\: manifest unknown\: The named manifest is not known to the registry",
        r"^Error: Error parsing image configuration: unable to retrieve auth token: invalid username/password: unknown: Bad props auth token(:?).*$",
    ],
    "Infrastructure - Tasking licenses exhausted": [
        r"^(ctc|ltc) .*E109",
        r"^ERROR: (ctc|ltc) .*: protection error: .*License expired\. No valid license found for.*",
    ],
    "Infrastructure - ZipArchive": [r"^failed to unpack .* to .*$"],
    "Infrastructure - OpenShift CLI": [r"^Error from server \(.*\): .+$"],
    "Infrastructure - Winrm failure": [
        r"winrm connection error: .+",
        r"winrm send_input failed",
        r"winrm connection error: HTTPSConnectionPool",
    ],
    "Infrastructure - xpad-build-integration": {
        "Copy ITF test images to cache server": [r"^cp: failed to close '\/mnt\/itf-images\/.*': Input\/output error$"],
        "Signing server unresolvable": [
            r"ssh: Could not resolve hostname xpad-ci-dev.sign.extern.cc.bmwgroup.net: Temporary failure in name resolution"
        ],
        "Signing server connection error": [
            r"connect to host xpad-ci-dev.sign.extern.cc.bmwgroup.net port 22: No route to host"
        ],
        "Signing failure": [
            r"^subprocess\.CalledProcessError: Command .*/.xpad_sign\/bin\/sign.* returned non-zero exit status [1-9]*\.$",
            r"^.*signature generation failed$",
        ],
    },
    "Infrastructure - License Server": [
        r"FlexNet Licensing error:.*\n.*",
        r"ERROR:(.*)Not able to obtain FlexLM license(.*)",
    ],
    "Infrastructure - License Server (CAS)": [
        r"ERROR:(.*)License request for vsxrtegenerator feature failed(.*)",
    ],
    "Infrastructure - License Server (QNX)": [
        r"Feature:.*kwbuildproject.*\n.*License path:.*([0-9]{4})@([a-z+0-9]+).muc:.*\n.*",
    ],
    "Infrastructure - Network": {
        "License": [r"^.*: protection error: .*Hostname lookup failed .* No valid license found for.*"],
        "Traffic Monitoring": [r"^Could not find the requested service network_traffic_monitoring\: host.*"],
    },
    "Infrastructure - IOException": [r"^.*Exec failed due to IOException.*"],
    "Infrastructure - netrc": [r"ERROR: There was a problem ensuring netrc entries"],
    "Infrastructure - Matlab License": [r"License checkout failed."],
}