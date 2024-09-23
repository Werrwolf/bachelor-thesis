patterns = {
    "Infrastructure - Bazel test logs reporter": {
        "": ["bazel_test_logs_reporter - Unexpected error: (?P<details>.+)"]
    },
    "Infrastructure - Git LFS": {
        "": ["^.*Request Time-out.*", "batch response: Fatal error: (?P<details>.+)"]
    },
    "Infrastructure - PyPI server not responding (possible AF auth failure)": {
        "": ["Could not find a version that satisfies the requirement .+"]
    },
    "Infrastructure - ZipArchive": {
        "": ["^failed to unpack .* to .*$"]
    },
    "Infrastructure - OpenShift CLI": {
        "": ["^Error from server \\(.*\\): .+$"]
    },
    "Infrastructure - Winrm failure": {
        "": ["winrm connection error: .+", "winrm send_input failed", "winrm connection error: HTTPSConnectionPool"]
    },
    "Infrastructure - License Server": {
        "": ["FlexNet Licensing error:.*\\n.*", "ERROR:(.*)Not able to obtain FlexLM license(.*)"]
    },
    "Infrastructure - License Server (CAS)": {
        "": ["ERROR:(.*)License request for vsxrtegenerator feature failed(.*)"]
    },
    "Infrastructure - License Server (QNX)": {
        "": ["Feature:.*kwbuildproject.*\\n.*License path:.*([0-9]{4})@([a-z+0-9]+).muc:.*\\n.*"]
    },
    "Infrastructure - IOException": {
        "": ["^.*Exec failed due to IOException.*"]
    },
    "Infrastructure - netrc": {
        "": ["ERROR: There was a problem ensuring netrc entries"]
    },
    "Infrastructure - Matlab License": {
        "": ["License checkout failed."]
    },
    "Infrastructure - Tasking licenses exhausted": {
        "": ["^(ctc|ltc) .*E109", "^ERROR: (ctc|ltc) .*: protection error: .*License expired\\. No valid license found for.*"]
    },
    "Infrastructure - Ansible": {
        "": ["Timeout \\(.*\\) waiting for privilege escalation prompt"]
    },
    "": {
        "Infrastructure - Unexpected failure during module execution.": ["Failed to update apt cache", "^.+extended fault data: .+", "WebException .+", "HTTP error \\d+ .+"],
        "Infrastructure - Host unreachable": ["(Data could not be sent to remote host|Make sure this host can be reached|No address associated with hostname).+$"]
    },
    "Infrastructure - Artifactory": {
        "": ["\\[Error\\].* Artifactory response: (?P<type>.+)\\n<.+>\\n(?P<details>[^<]+)", "\\[Error\\].* Artifactory response: (?P<type>.+)(\\n(.+\\n)*.+errors[^{]+{\\n(?P<details>[^{}]+)})?", "^.*http.client.IncompleteRead: IncompleteRead.*", "unauthorized: The client does not have permission to push to the repository", "ConnectionError: .+artifactory\\.cc\\.bmwgroup\\.net.*$", "Failure downloading https:\\/\\/(.*)artifactory.cc.bmwgroup.net\\/(.*), Connection failure: The read operation timed out", "Error downloading 'https:\\/\\/(.*)\\.artifactory\\.cc\\.bmwgroup\\.net(.*)The remote name could not be resolved: '(.*)\\.artifactory\\.cc\\.bmwgroup\\.net'", "artifactory-cc-bmwgroup-net-artifactory.*connection reset by peer$"],
        "Bazel download error": ["could not download Bazel:.+unable to complete request.+$"],
        "Download error": ["could not download .* failed with error.*$"],
        "Unexpected EOF": ["could not download .* unexpected EOF$"],
        "Checksum mismatch": ["Error in download: java\\.io\\.IOException: Error downloading \\[.+\\] to .+: Checksum was [a-f0-9]+ but wanted [a-f0-9]+"],
        "Content-Length mismatch": ["Error downloading\\s\\[http(s)?:\\/\\/(\\w+)\\.artifactory\\.cc\\.bmwgroup\\.net\\/artifactory\\/.* Bytes read [0-9]* but wanted [0-9]*"],
        "Operation failed": ["^.*Non-zero return code from art_cli:.*"],
        "Operation timed out": ["Error downloading 'https:\\/\\/(.*)\\.artifactory\\.cc\\.bmwgroup\\.net(.*)to(.*)\\: The operation has timed out"],
        "Permission": ["403 Client Error: Forbidden for url.*"],
        "Unknown host (ddad)": ["Unknown\\shost:\\sddad\\.artifactory\\.cc\\.bmwgroup\\.net"],
        "Unknown host (codecraft)": ["Unknown\\shost:\\scodecraft(.*)artifactory(.*)\\.cc\\.bmwgroup\\.net"],
        "Fetch failed": ["ERROR:.+An error occurred during the fetch of repository.+(\\n.+){1,5}\\nError in download.+", "^.*E: Failed to fetch https:\\/\\/.*artifactory\\.cc\\.bmwgroup\\.net\\/.* File has unexpected size \\(.* != .*\\)\\. Mirror sync in progress\\?.*$"],
        "Service unreachable": ["artifactory\\.cc\\.bmwgroup\\.net[^\\s]*\\s(?P<details>[^\\(]*\\(?Service Unavailable\\)?)"]
    },
    "Infrastructure - Bazel remote cache": {
        "Inaccessible remote cache": ["WARNING: Writing to Remote Cache:\\nio.grpc.StatusRuntimeException: UNKNOWN: operation not permitted", "WARNING: Writing to Remote Cache:\\nio.grpc.StatusRuntimeException: UNKNOWN: EOF", "ERROR: Failed to query remote execution capabilities: UNAVAILABLE: Unable to resolve host buildbarn\\.cc\\.bmwgroup\\.net", "^java.io.IOException: io.grpc.StatusRuntimeException: UNAVAILABLE: Unable to resolve host buildbarn.cc.bmwgroup.net$"],
        "Build without the bytes": ["^ERROR: .* Failed to fetch file with hash '.*' because it does not exist remotely\\..*$", "^(?:\\s+|\\\\t)?(Suppressed: )?java\\.io\\.IOException: Failed to fetch file with hash '.*' because it does not exist remotely\\..*$", "ERROR: .* failed: failed to create _solib symbolic link .* to target .*: Missing digest: .*", "ERROR: .*: Exec failed due to IOException: null", "^ERROR: .*io\\.grpc\\.StatusRuntimeException: UNAVAILABLE: io exception.*$", "^(java.io.IOException:|ERROR:).*io.grpc.StatusRuntimeException: UNAVAILABLE: upstream connect error or disconnect/reset before headers.*$"],
        "Connection closed": ["^.*Suppressed: java.io.IOException: An existing connection was forcibly closed by the remote host.*$"],
        "Connection timed out": ["ERROR: Failed to query remote execution capabilities: [Cc]onnection timed out.+$"],
        "Connection refused": ["ERROR: Failed to query remote execution capabilities: Connection refused", "ERROR: Failed to query remote execution capabilities: finishConnect\\(\\.\\.\\) failed: Connection refused: buildbarn\\.cc\\.bmwgroup\\.net/.*$", "^Caused by:.*UNAVAILABLE:.*connection error", "^.*UNAVAILABLE.*connection error.*connection refused.*"],
        "Deadline exceeded": ["^.*DEADLINE_EXCEEDED:.*deadline exceeded.*"],
        "Handshake timed out": ["ERROR: Failed to query remote execution capabilities: handshake timed out after.+$"],
        "Invalid Certificate": ["^ERROR: Failed to init TLS infrastructure using '.*' as client certificate: File does not contain valid certificates: .*"],
        "No route to host": ["ERROR: Failed to query remote execution capabilities: finishConnect\\(\\.\\.\\) failed: No route to host:.+$"],
        "No healthy upstream": ["^java.io.IOException: io.grpc.StatusRuntimeException: UNAVAILABLE: no healthy upstream$", "^ERROR: .*io\\.grpc\\.StatusRuntimeException: UNAVAILABLE: no healthy upstream$"],
        "Resource exhausted": ["^ERROR:.*io\\.grpc\\.StatusRuntimeException: RESOURCE_EXHAUSTED.*$"],
        "Resource not found": ["^.*Traceback.+\\n( .+\\n)+.+ResourceNotFound.*"],
        "Generic status runtime exception": ["^ERROR:.+io\\.grpc\\.StatusRuntimeException:.+$"]
    },
    "Infrastructure - Bazel Remote Execution": {
        "Operation not found": ["^ERROR: .+\\(Exit 34\\): NOT_FOUND: Operation not found:.+$"],
        "Docker pull failed": ["^ERROR: .+\\(Exit 34\\): INVALID_ARGUMENT: Unable to start docker container.+$"]
    },
    "Infrastructure - BES upload": {
        "Failure": ["^ERROR: The Build Event Protocol upload failed.*"],
        "Timeout": ["^ERROR: The Build Event Protocol upload timed out.*"]
    },
    "Infrastructure - Git": {
        "": ["Unable to checkout .+ in submodule path .+", "error: failed to push .+", "ERROR:.+An error occurred during the fetch of repository.+(\\n.+){1,}\\nError in fail: error running 'git fetch.+", "fatal:.+Could not read from remote repository.+"]
    },
    "Infrastructure - Docker": {
        "": ["=+\\n.+\\n=+\\n+Cannot connect to the Docker daemon .+", "=+\\n.+\\n=+\\n+Error response .+", "^.*Error: unable to pull ddad.artifactory.cc.bmwgroup.net.*", "Error\\: error logging into \\\"ddad\\.artifactory\\.cc\\.bmwgroup\\.net\\\"\\: invalid username\\/password", "Error response from daemon(.*)artifactory\\.cc\\.bmwgroup\\.net[^\\s]*\\s(?P<details>.*)", "manifest for artifactory\\.cc\\.bmwgroup\\.net\\/.*\\:latest not found\\: manifest unknown\\: The named manifest is not known to the registry", "^Error: Error parsing image configuration: unable to retrieve auth token: invalid username/password: unknown: Bad props auth token(:?).*$"]
    },
    "Infrastructure - xpad-build-integration": {
        "Copy ITF test images to cache server": ["^cp: failed to close '\\/mnt\\/itf-images\\/.*': Input\\/output error$"],
        "Signing server unresolvable": ["ssh: Could not resolve hostname xpad-ci-dev.sign.extern.cc.bmwgroup.net: Temporary failure in name resolution"],
        "Signing server connection error": ["connect to host xpad-ci-dev.sign.extern.cc.bmwgroup.net port 22: No route to host"],
        "Signing failure": ["^subprocess\\.CalledProcessError: Command .*/.xpad_sign\\/bin\\/sign.* returned non-zero exit status [1-9]*\\.$", "^.*signature generation failed$"]
    },
    "Infrastructure - Network": {
        "License": ["^.*: protection error: .*Hostname lookup failed .* No valid license found for.*"],
        "Traffic Monitoring": ["^Could not find the requested service network_traffic_monitoring\\: host.*"]
    },
    "Build - test-msg": {
        "": ["Check if msg is being posted to PR"]
    },
    "Build - cc-test": {
        "": ["CC-ERROR: .*"]
    },
    "Build - tresos": {
        "": ["Error \\d+: ERROR .+? \\((?P<type>.+?)\\) .+"]
    },
    "Build - gtest": {
        "": [
            "^(?P<file>.+?):(?P<line>\\d+): Failure.*\\n(?P<details>[^.[]*)(\\[  FAILED  \\].+)?",
            "^(?P<file>.+?)\\((?P<line>\\d+)\\): error: (?P<details>.+\\n([^.[].+\\n)*)(\\[  FAILED  \\].+)?"
        ]
    },
    "Build - CTest": {
        "": ["Errors while running CTest"]
    },
    "Build - Codeowners Validator": {
        "Duplicated Pattern Checker": ["\\s+\\[err\\]\\s+Pattern .* is defined \\d+ times in lines:.*"],
        "File Exist Checker": ["\\s+\\[err\\]\\sline\\s\\d+:.*does not match any files in repository"],
        "Valid Syntax Checker": ["CODEOWNERS group .*does not match regex expression.*and not found in.*file"],
        "Not Owned File Checker": ["\\s+\\[err\\](.*)Found (\\d*) not owned files"]
    },
    "Build - Codify": {
        "MappingsCheck - Violation detected": ["ERROR Mappings.*Check - Violation detected"],
        "Code generation": [
            "ERROR(.*)Codify generating code(.*)failed(.*)codify.exe failed(.*)",
            "ERROR(.*)Generating resolved json(.*)failed(.*)codify.exe failed(.*)",
            "ERROR(.*)Generating codify-data for(.*)failed(.*)codify_bin failed(.*)"
        ],
        "Unresolved references": ["ERROR DefaultLogger \\- All references have to be resolved! .*? are unresolved\\:"]
    },
    "Build - Coverage": {
        "": ["fatal error: test coverage is too low for target .*"]
    },
    "Build - Compiler": {
        "clang-tidy": [
            "(?s)^ERROR: .*Running clang-tidy on file (?P<file>.*) failed: \\(Exit.*(?P<details>INFO: \\d+ counting clang-tidy .*\\nINFO:.*\\n.*?At least one clang-tidy finding was treated as error)"
        ],
        "clang": [
            "^ERROR: .*: Compiling .* failed: \\(Exit \\d\\): clang\\+\\+ failed: error executing command"
        ],
        "gnu": [
            "^ERROR: .*: Compiling .* failed: \\(Exit \\d\\): x86_64-linux-gnu-g\\+\\+ failed: error executing command.*$"
        ],
        "gcc - Failure while compiling C++": [
            "^(?P<file>.+?):(?P<line>\\d+).*: ERROR:.+BUILD(.bazel)?:[0-9]+:[0-9]+: C\\+\\+.*gcc failed.*$",
            "^(?P<file>.+?):(?P<line>\\d+).*: ERROR:.+BUILD(.bazel)?:[0-9]+:[0-9]+: C\\+\\+ compilation of rule.* failed.*$",
            "^(?P<file>.+?):(?P<line>\\d+).*: C\\+\\+ compilation of rule.* failed.*$"
        ],
        "qcc - Failure executing command": [
            "^ERROR:.+ Compiling application.+qcc failed: error executing command.+\\)"
        ],
        "ghs": [
            "^(\\S.+\\n)?\"(?P<file>.+?)\", line (?P<line>\\d+): (?P<type>(fatal )?error #.+)\\n(?P<details>(\\s.+\\n)+)",
            "FAILED: (?P<file>.+)\\n.+\\n(?P<details>FATAL ERROR: .+)"
        ],
        "NDS": ["^ERROR.*Converting physical model from NDS to C\\+\\+ Headers"],
        "ltc": ["^.*ltc E106: unresolved external.*"],
        "vs": [
            "^(?!\\s|\\d|>)(?P<file>.+?)\\((?P<line>.+)\\):( fatal)? error (?P<type>(C|MSB)\\d+): (?P<details>.+)",
            "MT: command \".+\" failed .+\\s+mt :.* error (?P<type>\\w+): .+"
        ],
        "Warnings": ["Compiler warnings filter evaluation complete. Num lines evaluated is .+: Errors [1-9].+"],
        "Tasking ctc": [
            "^ERROR: .*: Compiling .* failed: \\(Exit \\d\\): cctc_wrapper\\.bat failed: error executing command$",
            "^ctc E\\d+: \\[\\\"(?P<file>.+?)\\\" (?P<line>\\d+)/\\d+\\] .+$"
        ],
        "Typescript": [
            "^ERROR:.*: Compiling TypeScript project.*[tsc -p .*] failed: .*"
        ]
    },
    "Build - Converter": {
        "franca_arxml_converter": ["ERROR:.*franca_arxml_converter failed: error executing command"]
    },
    "Build - Driving Approval Automation Tool (DAAT)": {
        "Incorrect Config Template. Follow the steps in tool README correctly": ["E.*:.*Verification.*failed"],
        "Tool failure": ["ERROR:root:DAAT.*"]
    },
    "Build - Linker": {
        "gcc": ["error: ld returned \\d+ exit status\\n?"],
        "ghs": [
            "^.+\\n\\[elxr\\] \\(error #.+\\) (?P<type>.+?):.*\\n(?P<details>([^\\[]*\\n)+\\[elxr\\] \\(error\\).+)?",
            "(\\[elxr\\] \\(error #.+\\).+\\n)+"
        ],
        "vs": ["^(?P<file>.+?):( fatal)? error (?P<type>LNK\\d+): (?P<details>.+)"],
        "": ["^ERROR: .*: Linking .* failed: \\(Exit \\d\\): .* failed: error executing command"]
    },
    "Build - Mentor": {
        "mentor_generator timeout": ["ERROR in mentor_generator\\.py\\s+\\-\\stimeout\\sexpired"]
    },
    "Build - Memory": {
        "double free or corruption": ["^double free or corruption \\(out\\)$"],
        "Out of memory": [
            "(?:runtime\\/cgo:)? pthread_create failed: Resource temporarily unavailable",
            "^ERROR: .* failed: (\\(Killed\\)|\\(Exit (33|137)\\)): .* failed: error executing command.*$",
            "^cc1plus: out of memory allocating [0-9]+ bytes after a total of [0-9]+ bytes$",
            "^virtual memory exhausted: Cannot allocate memory$",
            "There is insufficient memory for the [a-zA-Z\\s]+ to continue.$",
            "OutOfMemoryError thrown during Starlark evaluation"
        ]
    },
    "Build - Misra": {
        "Errors in analysis of variants": ["Errors occurred in [0-9] variants: \\['[a-zA-Z0-9_-]+'\\]"]
    },
    "Build - ncar": {
        "dependency check": ["ERROR\\s+Bazel query failed!", "ERROR\\s+Dependency rule '\\w+' has violations!"],
        "architecture check": ["The bazel-check-architecture has found some not allowed packages.\\s+Read.*on how to proceed"],
        "lslint": ["bazel\\-bin\\/tools\\/ls_lint\\/lslint((.|\\n)*)failed for rules\\: regex"]
    },
    "Build - TRLC": {
        "": ["^(?P<file>.+?):(?P<line>\\d+).*: trlc (?P<type>(lex |check )?(warning|error|ICE)): (?P<details>.*)"]
    },
    "Build - PDX-Generation": {
        "Timeout E-Sys": ["ERROR\\s.*PDX-generation unsuccessful:.*Timeout occurred while waiting for E-Sys."]
    },
    "Build - python": {
        "Authentication error": ["^.*Traceback.+\\n( .+\\n)+.*pip/download.py.+handle_401.*$"],
        "guestfs_launch failed": ["RuntimeError: guestfs_launch failed"],
        "HTTPError": ["^requests.exceptions.HTTPError: .+$"],
        "pip": ["ERROR: Pip failed:.*"],
        "pip install failed": [
            "^ERROR: No matching distribution found for.*$",
            "^Could not install packages due to an.*$"
        ],
        "Failed to install python dependencies": [
            "^ERROR: could not install deps .+$",
            "Preparing metadata \\(setup\\.py\\): finished with status 'error'"
        ],
        "libguestfs": ["RuntimeError: guestfs_launch failed.+$"],
        "pytest": ["(?s)=========================== short test summary info ============================.*?\\sin\\s.*?=+"],
        "thread": ["^.*python.+\\n( .+\\n).*error: can't start new thread"],
        "": [
            "^(.*Traceback.+\\n( .+\\n)+(?P<type>\\S.+Error.*?):.+\\n?(?P<details>(\\s.+\\n)*)?)+",
            "ERROR: .*: This target is being built for Python 3 but \\(transitively\\) includes Python 2-only sources.",
            "\\/usr\\/bin\\/python.*: No module named .*$"
        ],
        "unrecognized arguments": ["(?P<file>[\\w-]+\\.py): error: unrecognized arguments:.+$"],
        "Exception raised": ["Exception:(.*)Check missing paths here(.*)"]
    },
    "Build - Java": {
        "EValidator": ["^.*ERROR\\s.*\\s-\\sError\\sexecuting\\sEValidator"],
        "SIGBUS": ["^#  SIGBUS\\s\\(0x7\\)\\sat\\spc=0[xX][0-9a-fA-F]+,\\spid=\\d+,\\stid=0[xX][0-9a-fA-F]+$"],
        "": ["Error: (?P<type>.+)\\n(?P<details>Exception .+\\n([\\t\\w].+\\n)+)"]
    },
    "Build - Symphony": {
        "": ["ERROR(\\s*)Logger(\\s*)-?(\\s*)###(?P<details>.+)", "^(.+ERROR\\s+generate_symphony_artifacts:.+\\n?)+"]
    },
    "Build - System Error": {
        "": [
            "^.+ is not (known|recognized) as [\\s\\S]+?\\.",
            "The system cannot find the (path|file) specified\\.",
            "^.+: (?P<file>(?!.*mount error\\(*).+?): Permission denied",
            "^PermissionError: \\[WinError 32\\] The process cannot access the file because it is being used by another"
        ]
    },
    "Build - Shell execution": {
        "": [
            "^(.+\\n)?/bin/sh: \\d+: (?P<type>.+error): (?P<details>.+)",
            "^/bin/bash: line \\d+: (?P<file>.+): (?P<details>.+)",
            "\\/bin\\/bash: .* command not found.*$",
            "The command .* returned a non-zero code: [0-9]*",
            "\\/bin\\/bash: .* No such file or directory.*$",
            "^cp: cannot stat '(?P<file>.+)': .+$"
        ]
    },
    "Build - Ansible": {
        "assert": ["^Assertion failed$"],
        "syntax": [
            "The error was: (?P<details>.+)[\\w\\s]+.(?P<file>[\\w/\\.-]+).+: line (?P<line>\\d+)",
            "\\'\\w+\\' is undefined"
        ],
        "templating": ["recursive loop detected in template string: .+", "templat(e|ing.*) error .+"],
        "creating file/dir": ["^There was an issue creating.+$"],
        "missing file": ["Could not find or access '(?P<file>.*)' on the Ansible Controller.\\n.*$"],
        "undefined variable": ["AnsibleUndefinedVariable:.+$"]
    },
    "Build - Git LFS": {
        "": [
            "^(?P<details>.+runtime error: (.*\\n)+?Stopping at .(?P<file>[\\w/-]+).+)",
            "^(?P<details>((?!Git LFS:).+\\n)?error: .+\\nStopping at .(?P<file>[\\w/-]+).+)",
            "^.*\\nerror: failed to fetch some objects.+$",
            "ERROR: Git LFS .*"
        ]
    },
    "Build - Test(s) failed": {
        "": [
            "\\/\\/.*\\s+FAILED in [0-9.]+s",
            "^\\/\\/.+ FAILED in [0-9\\.]+s$",
            "\\/\\/.*\\s+FAILED in [0-9]* out of [0-9]*"
        ]
    },
    "Build - Test Guide": {
        "connector": ["\\[INFO \\] .* Test Guide connector terminated with error..."],
        "Tests failing": ["Tests still failing after all excludes"]
    },
    "Build - Test(s) timeout": {
        "": ["\\/\\/.*\\s+TIMEOUT in [0-9]*"]
    },
    "Build - Test(s) failed to build": {
        "": ["\\/\\/.*\\s+FAILED TO BUILD[$]?"]
    },
    "Build - Terminate without exception": {
        "": ["terminate called without an active exception"]
    },
    "Build - Unknown test failure cause": {
        "": ["ScenarioInstance: Shutting down\\.\\.\\."]
    },
    "Build - Dependency Error": {
        "File not found": ["ERROR:.*no such package.*file not found in any of the following directories"]
    },
    "Build - Bazel": {
        "failed on target analysis": ["^ERROR: Analysis of target.+$"],
        "crash": ["^Internal error .*java\\.lang\\.OutOfMemoryError"],
        "error loading package": ["ERROR:(.*)error loading package(.*)"],
        "error finding package": [
            "ERROR: \\/workspace\\/deployment\\/ecu_instances\\/casp_base\\/tc4_eth\\/cdd\\/BUILD:13:17\\: no such package .+: The repository .+ could not be resolved\\: Repository .+ is not defined and referenced by"
        ],
        "unknown configuration": ["ERROR: Config value .* is not defined in any \\.rc file"],
        "server terminated": ["^Server terminated abruptly \\(error code:.+$"],
        "error executing shell command": ["ERROR: .* error executing shell command: .* failed \\(Exit [0-9]*\\)"],
        "error executing command": [
            "Executing .* failed: \\(Exit [0-9]*\\)\\: .* failed\\: error executing command",
            "ERROR:.{1,500}error executing command \\(.*\\)"
        ],
        "building test target failed": ["FAILED: Build did NOT complete successfully\\n.+FAILED TO BUILD.*$"],
        "loading phase errors": ["ERROR: command succeeded, but there were loading phase errors"],
        "no targets found": [
            "^ERROR: Skipping.+no targets found beneath.+$",
            "^ERROR: no targets found beneath.+$"
        ],
        "could not build file": ["ERROR: .* Couldn't build file .* failed \\(Exit [0-9]*\\).*$"],
        "missing input file": ["ERROR:(.*)input file\\(s\\) do not exist", "ERROR:(.*)missing input file '.*'"],
        "output was not created": ["ERROR:.*output.*was not created"],
        "not all outputs were created or valid": ["ERROR:.*not all outputs were created or valid"],
        "name is not defined": [
            "ERROR: (.*) name '(.*)' is not defined(?: \\(did you mean (.*)\\?\\))?"
        ],
        "Failed to extract": ["^FATAL: Failed to extract embedded binaries:.+(?P<file>'.+').+$"],
        "Unrecognized option": ["ERROR: Unrecognized option:.+$"],
        "target name": ["ERROR:.+no such target .* not declared in package .* defined by .*$"],
        "A2l failed": ["(?s)a2lfactory\\.exe failed:(?P<details>.+\\n)FAILED: Build did NOT complete successfully"],
        "Missing deps. declaration": [
            "ERROR(.*\\n)this rule is missing dependency declarations for the following files included by(.+\\n){0,10}"
        ],
        "BUILD file not found": ["ERROR: command succeeded, but not all targets were analyzed"],
        "action cache initialization": [
            "^ERROR: Error during action cache initialization: Failed action cache referential integrity check: Validation mismatch: validation entry [0-9]+ is too large compared to index size [0-9]+\\. Corrupted files were renamed to '.*'\\. Bazel will now reset action cache data, causing a full rebuild$"
        ],
        "Artifact error": [
            "^ERROR: Unexpected exception, please file an issue with the Bazel team: Artifact.*is neither header nor source file."
        ],
        "Symlink - missing input file": [
            "^ERROR: (?P<build>.+) Symlinking (?P<file>.+) failed: missing input file '(?P<detail>.+)'$"
        ],
        "Crashed due to an internal error": [
            "FATAL: bazel crashed due to an internal error. Printing stack trace:"
        ],
        "Sandbox execution error": [
            "ERROR: .* failed: I\\/O exception during sandboxed execution\\:.*$"
        ],
        "Build Event Protocol upload timed out": ["^ERROR: The Build Event Protocol upload timed out"]
    },
    "Build - SRec / S19 not created": {
        "": ["^ERROR: .+BUILD:[0-9]+:[0-9]+: output.*\\.s19.+$"]
    },
    "Build - Generating functional code failed": {
        "": [
            "^(?P<file>.+?):(?P<line>\\d+).*: ERROR:.+\\/BUILD:[0-9]+:[0-9]+: .* - Generating funct.* failed \\(Exit 2\\):.*$",
            "^(?P<file>.+?):(?P<line>\\d+).*: ERROR:.+\\/BUILD:[0-9]+:[0-9]+: Franca2ARXML.*failed \\(Exit 5\\).*$",
            "^ERROR:.+Generate\\sCode\\sfrom\\sARXML.+bash failed: error executing command",
            "ERROR: .+ Generating arxml files failed\\: \\(Exit .\\)\\: .+ failed: error executing command",
            "^ERROR:.+Generating SWE:.+payload_options failed: error executing command"
        ]
    },
    "Build - Win logging error": {
        "Failed to open Log-Path": ["^Get-ChildItem : Cannot find path .+logs.+$"],
        "Failed to create logman counter": ["Error:.*Data Collector already exists"]
    },
    "Build - Toolchain": {
        "Failed to fetch/setup toolchain (e.g. eyeq_sdk, llvm_toolchain)": [
            "^ERROR: .+\\/BUILD:[0-9]+:[0-9]+: \\/\\/bazel\\/toolchains\\/.+$"
        ]
    },
    "Build - Dependency": {
        "Failed to fetch dependency": [
            "^ERROR: .+\\/BUILD:[0-9]+:[0-9]+: .+ depends on .+ which failed to fetch\\..+$"
        ]
    },
    "Build - Symlink": {
        "Failed to create symlink": [
            "^ERROR: .+\\/BUILD:[0-9]+:[0-9]+: failed to create symbolic link .+$",
            "Create symlink from bazel_default_output_base=\\/root\\/.* to target\\=\\/var\\/cache\\/bazel"
        ]
    },
    "Build - Formatting error": {
        "": ["^Formatting errors found in .+$"]
    },
    "Build - redirected output": {
        "Small Checks - Bazel queries check": [
            "^@tu-cc-ci-adp-github-eof(?:(?:\\s+type:(?P<type>\\S*))|(?:\\s+file:(?P<file>\\S*))|(?:\\s+line:(?P<line>\\S*)))*\\s+(?P<details>(?:.|[\\r\\n])*(- Bazel queries check)(?:.|[\\r\\n])*)"
        ],
        "Small Checks - BUILD-File Validator": [
            "^@tu-cc-ci-adp-github-eof(?:(?:\\s+type:(?P<type>\\S*))|(?:\\s+file:(?P<file>\\S*))|(?:\\s+line:(?P<line>\\S*)))*\\s+(?P<details>(?:.|[\\r\\n])*(- BUILD-File Validator)(?:.|[\\r\\n])*)"
        ],
        "Small Checks - Buildifier-check": [
            "^@tu-cc-ci-adp-github-eof(?:(?:\\s+type:(?P<type>\\S*))|(?:\\s+file:(?P<file>\\S*))|(?:\\s+line:(?P<line>\\S*)))*\\s+(?P<details>(?:.|[\\r\\n])*(- Buildifier-check)(?:.|[\\r\\n])*)"
        ],
        "Small Checks - Check CI jobs branch filters": [
            "^@tu-cc-ci-adp-github-eof(?:(?:\\s+type:(?P<type>\\S*))|(?:\\s+file:(?P<file>\\S*))|(?:\\s+line:(?P<line>\\S})))*\\s+(?P<details>(?:.|[\\r\\n])*(- Check CI jobs branch filters)(?:.|[\\r\\n])*)"
        ]
    },
    "Build - Matlab": {
        "Execution error": ["(?s)(?<=ERROR MatlabExecutor - Matlab execution error:)(.*$)"],
        "Generation error": ["(^.*)Generating functional code(.*)failed(.*?$)"],
        "Task(s) fail(ed)": ["Code generation for module .* failed."]
    },
    "Build - Docker": {
        "build": [
            "^(?P<details>Error building (.+)code(.+)message(.+)), logs:",
            "^E: Unable to locate package.+$",
            "[E|W]:.+\\nE: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing\\?$",
            "^error pulling image configuration:.+$",
            "An image does not exist locally with the tag: (.*$)"
        ]
    },
    "Build - Kubernetes": {
        "": ["^Failed to patch object.+$"]
    },
    "Build - clang tidy": {
        "": ["^\\[ FAIL \\] Clang Tidy produced.+$"]
    },
    "Build - rsync": {
        "": ["^rsync error:.+$"]
    },
    "Build - astas": {
        "test": ["^FAILED - gui-core interaction tests$"]
    },
    "Build - FuSa Violation Found (Check 'bazel_wrapper_log.txt' on the logs folder)": {
        "": ["Failed actions detected in bazel_wrapper_log.txt file"]
    },
    "Build - FuSa Violation Found (Check 'mitguard_report.html' on the logs folder)": {
        "": ["Mitguard check failure"]
    },
    "Build - FuSa Violation Found (Check the log on 'Nightwatch' folder)": {
        "": ["Nightwatch verdict: rejected\\."]
    },
    "Build - Network Traffic Check": {
        "": ["^Network traffic check has failed$"]
    },
    "Build - Mount error": {
        "Permission denied": ["Error mounting .+ Permission denied.+$", "^.+: (?P<file>mount error.+?): Permission denied"],
        "Mounted FS stat failure": ["Error: statfs \\/mnt.+ no such file or directory"],
        "Failed to copy": ["failed to copy: .+\\/mnt\\/.+"],
        "Failed to Umount": ["Error\\srmdir\\s[a-zA-z-:/]+\\s\\[Errno\\s[0-9]+\\]\\s[a-zA-z\\s\\W]+"]
    },
    "Build - Param Server error": {
        "": ["ERROR:.+ param_server_gen failed.+$"]
    },
    "Build - License": {
        "Invalid License": ["^.*No valid license found for .*"],
        "License not available": [
            "All licenses are currently in use",
            "ERROR: License server valid, no license available",
            "ERROR: Couldn't obtain the license after \\d+ retries.+$"
        ]
    },
    "Build - Invoking Requirements Tracing": {
        "": ["ERROR.*Invoking Requirements.*driver_tracing failed: \\(Exit 1\\)"]
    },
    "Build - Invalid Main repository mapping": {
        "": ["^ERROR:.Error computing the main repository mapping:.at.+ is invalid because.+is not a package.+perhaps you meant to put the colon here: .+?$"]
    },
    "Build - Cptc Error": {
        "": ["cptc .+ cannot open source file.+$"]
    },
    "Build - Cmake Error": {
        "": ["^make.*Error"]
    },
    "Build - windows": {
        "Restart-Service": ["Service 'sshd \\(sshd\\)' cannot be stopped due to the following error: Cannot stop sshd service on "]
    },
    "Build - tar": {
        "error executing command": ["^ERROR: .+ Action .+\\.tar\\.gz failed: \\(Exit 1\\): bash failed: error executing command$"]
    },
    "Build - Linux": {
    "": ["\\[Errno 2\\] No such file or directory"]
}
}