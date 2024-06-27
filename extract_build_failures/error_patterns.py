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

BUILD_PATTERNS = {
    "test-msg": [r"Check if msg is being posted to PR"],
    "cc-test": [r"CC-ERROR: .*"],
    "tresos": [r"Error \d+: ERROR .+? \((?P<type>.+?)\) .+"],
    "gtest": [
        r"^(?P<file>.+?):(?P<line>\d+): Failure.*\n(?P<details>[^.[]*)(\[  FAILED  \].+)?",
        r"^(?P<file>.+?)\((?P<line>\d+)\): error: (?P<details>.+\n([^.[].+\n)*)(\[  FAILED  \].+)?",
    ],
    "CTest": [r"Errors while running CTest"],
    "Codeowners Validator": {
        "Duplicated Pattern Checker": [r"\s+\[err\]\s+Pattern .* is defined \d+ times in lines:.*"],
        "File Exist Checker": [r"\s+\[err\]\sline\s\d+:.*does not match any files in repository"],
        "Valid Syntax Checker": [r"CODEOWNERS group .*does not match regex expression.*and not found in.*file"],
        "Not Owned File Checker": [r"\s+\[err\](.*)Found (\d*) not owned files"],
    },
    "Codify": {
        "MappingsCheck - Violation detected": [r"ERROR Mappings.*Check - Violation detected"],
        "Code generation": [
            r"ERROR(.*)Codify generating code(.*)failed(.*)codify.exe failed(.*)",
            r"ERROR(.*)Generating resolved json(.*)failed(.*)codify.exe failed(.*)",
            r"ERROR(.*)Generating codify-data for(.*)failed(.*)codify_bin failed(.*)",
        ],
        "Unresolved references": [r"ERROR DefaultLogger \- All references have to be resolved! .*? are unresolved\:"],
    },
    "Coverage": [r"fatal error: test coverage is too low for target .*"],
    "Compiler": {
        "clang-tidy": [
            r"".join(
                [
                    r"(?s)^ERROR: .*Running clang-tidy on file (?P<file>.*) failed: ",
                    r"\(Exit.*(?P<details>INFO: \d+ counting clang-tidy .*\nINFO:.*\n.*?",
                    r"At least one clang-tidy finding was treated as error)",
                ]
            )
        ],
        "clang": [r"^ERROR: .*: Compiling .* failed: \(Exit \d\): clang\+\+ failed: error executing command"],
        "gnu": [
            r"^ERROR: .*: Compiling .* failed: \(Exit \d\): x86_64-linux-gnu-g\+\+ failed: error executing command.*$"
        ],
        "gcc - Failure while compiling C++": [
            r"^(?P<file>.+?):(?P<line>\d+).*: ERROR:.+BUILD(.bazel)?:[0-9]+:[0-9]+: C\+\+.*gcc failed.*$",
            r"^(?P<file>.+?):(?P<line>\d+).*: ERROR:.+BUILD(.bazel)?:[0-9]+:[0-9]+: C\+\+ compilation of rule.* failed.*$",
            r"^(?P<file>.+?):(?P<line>\d+).*: C\+\+ compilation of rule.* failed.*$",
        ],
        "qcc - Failure executing command": [
            r"^ERROR:.+ Compiling application.+qcc failed: error executing command.+\)"
        ],
        "ghs": [
            r'^(\S.+\n)?"(?P<file>.+?)", line (?P<line>\d+): (?P<type>(fatal )?error #.+)\n' r"(?P<details>(\s.+\n)+)",
            r"FAILED: (?P<file>.+)\n.+\n(?P<details>FATAL ERROR: .+)",
        ],
        "NDS": [r"^ERROR.*Converting physical model from NDS to C\+\+ Headers"],
        "ltc": [r"^.*ltc E106: unresolved external.*"],
        "vs": [
            r"^(?!\s|\d|>)(?P<file>.+?)\((?P<line>.+)\):( fatal)? error (?P<type>(C|MSB)\d+): " r"(?P<details>.+)",
            r'MT: command ".+" failed .+\s+mt :.* error (?P<type>\w+): .+',
        ],
        "Warnings": [r"Compiler warnings filter evaluation complete. Num lines evaluated is .+: Errors [1-9].+"],
        "Tasking ctc": [
            r"^ERROR: .*: Compiling .* failed: \(Exit \d\): cctc_wrapper\.bat failed: error executing command$",
            r"^ctc E\d+: \[\"(?P<file>.+?)\" (?P<line>\d+)/\d+\] .+$",
        ],
        "Typescript": [r"^ERROR:.*: Compiling TypeScript project.*[tsc -p .*] failed: .*"],
    },
    "Converter": {"franca_arxml_converter": [r"ERROR:.*franca_arxml_converter failed: error executing command"]},
    "Driving Approval Automation Tool (DAAT)": {
        "Incorrect Config Template. Follow the steps in tool README correctly": [r"E.*:.*Verification.*failed"],
        "Tool failure": [r"ERROR:root:DAAT.*"],
    },
    "Linker": {
        "gcc": [r"error: ld returned \d+ exit status\n?"],
        "ghs": [
            r"^.+\n\[elxr\] \(error #.+\) (?P<type>.+?):.*\n(?P<details>([^\[]*\n)+\[elxr\] " r"\(error\).+)?",
            r"(\[elxr\] \(error #.+\).+\n)+",
        ],
        "vs": [r"^(?P<file>.+?):( fatal)? error (?P<type>LNK\d+): (?P<details>.+)"],
        "": [r"^ERROR: .*: Linking .* failed: \(Exit \d\): .* failed: error executing command"],
    },
    "Mentor": {
        "mentor_generator timeout": [r"ERROR in mentor_generator\.py\s+\-\stimeout\sexpired"],
    },
    "Memory": {
        "double free or corruption": [r"^double free or corruption \(out\)$"],
        "Out of memory": [
            r"(?:runtime\/cgo:)? pthread_create failed: Resource temporarily unavailable",
            r"^ERROR: .* failed: (\(Killed\)|\(Exit (33|137)\)): .* failed: error executing command.*$",
            r"^cc1plus: out of memory allocating [0-9]+ bytes after a total of [0-9]+ bytes$",
            r"^virtual memory exhausted: Cannot allocate memory$",
            r"There is insufficient memory for the [a-zA-Z\s]+ to continue.$",
            r"OutOfMemoryError thrown during Starlark evaluation",
        ],
    },
    "Misra": {"Errors in analysis of variants": [r"Errors occurred in [0-9] variants: \['[a-zA-Z0-9_-]+'\]"]},
    "ncar": {
        "dependency check": [r"ERROR\s+Bazel query failed!", r"ERROR\s+Dependency rule '\w+' has violations!"],
        "architecture check": [
            r"The bazel-check-architecture has found some not allowed packages.\s+Read.*on how to proceed"
        ],
        "lslint": [r"bazel\-bin\/tools\/ls_lint\/lslint((.|\n)*)failed for rules\: regex"],
    },
    "TRLC": [r"^(?P<file>.+?):(?P<line>\d+).*: trlc (?P<type>(lex |check )?(warning|error|ICE)): (?P<details>.*)"],
    "PDX-Generation": {
        "Timeout E-Sys": [r"ERROR\s.*PDX-generation unsuccessful:.*Timeout occurred while waiting for E-Sys."]
    },
    "python": {
        "Authentication error": [r"^.*Traceback.+\n( .+\n)+.*pip/download.py.+handle_401.*$"],
        "guestfs_launch failed": [r"RuntimeError: guestfs_launch failed"],
        "HTTPError": [r"^requests.exceptions.HTTPError: .+$"],
        "pip": [r"ERROR: Pip failed:.*"],
        "pip install failed": [
            r"^ERROR: No matching distribution found for.*$",
            r"^Could not install packages due to an.*$",
        ],
        "Failed to install python dependencies": [
            r"^ERROR: could not install deps .+$",
            r"Preparing metadata \(setup\.py\): finished with status 'error'",
        ],
        "libguestfs": [r"RuntimeError: guestfs_launch failed.+$"],
        "pytest": [
            r"(?s)=========================== short test summary info ============================.*?\sin\s.*?=+"
        ],
        "thread": [r"^.*python.+\n( .+\n).*error: can't start new thread"],
        "": [
            r"^(.*Traceback.+\n( .+\n)+(?P<type>\S.+Error.*?):.+\n?(?P<details>(\s.+\n)*)?)+",
            r"ERROR: .*: This target is being built for Python 3 but \(transitively\) includes Python 2-only sources.",
            r"\/usr\/bin\/python.*: No module named .*$",
        ],
        "unrecognized arguments": [r"(?P<file>[\w-]+\.py): error: unrecognized arguments:.+$"],
        "Exception raised": [
            r"Exception:(.*)Check missing paths here(.*)",
        ],
    },
    "Java": {
        "EValidator": [r"^.*ERROR\s.*\s-\sError\sexecuting\sEValidator"],
        "SIGBUS": [r"^#  SIGBUS\s\(0x7\)\sat\spc=0[xX][0-9a-fA-F]+,\spid=\d+,\stid=0[xX][0-9a-fA-F]+$"],
        "": [r"Error: (?P<type>.+)\n(?P<details>Exception .+\n([\t\w].+\n)+)"],
    },
    "Symphony": [
        r"ERROR(\s*)Logger(\s*)-?(\s*)###(?P<details>.+)",
        r"^(.+ERROR\s+generate_symphony_artifacts:.+\n?)+",
    ],
    "System Error": [
        r"^.+ is not (known|recognized) as [\s\S]+?\.",
        r"The system cannot find the (path|file) specified\.",
        r"^.+: (?P<file>(?!.*mount error\(*).+?): Permission denied",
        r"^PermissionError: \[WinError 32\] The process cannot access the file because it is being used by another",
    ],
    "Shell execution": [
        r"^(.+\n)?/bin/sh: \d+: (?P<type>.+error): (?P<details>.+)",
        r"^/bin/bash: line \d+: (?P<file>.+): (?P<details>.+)",
        r"\/bin\/bash: .* command not found.*$",
        r"The command .* returned a non-zero code: [0-9]*",
        r"\/bin\/bash: .* No such file or directory.*$",
        r"^cp: cannot stat '(?P<file>.+)': .+$",
    ],
    "Ansible": {
        "assert": [r"^Assertion failed$"],
        "syntax": [
            r"The error was: (?P<details>.+)[\w\s]+.(?P<file>[\w/\.-]+).+: line (?P<line>\d+)",
            r"\'\w+\' is undefined",
        ],
        "templating": [r"recursive loop detected in template string: .+", r"templat(e|ing.*) error .+"],
        "creating file/dir": [r"^There was an issue creating.+$"],
        "missing file": [r"Could not find or access '(?P<file>.*)' on the Ansible Controller.\n.*$"],
        "undefined variable": [r"AnsibleUndefinedVariable:.+$"],
    },
    "Git LFS": [
        r"^(?P<details>.+runtime error: (.*\n)+?Stopping at .(?P<file>[\w/-]+).+)",
        r"^(?P<details>((?!Git LFS:).+\n)?error: .+\nStopping at .(?P<file>[\w/-]+).+)",
        r"^.*\nerror: failed to fetch some objects.+$",
        r"ERROR: Git LFS .*",
    ],
    "Test(s) failed": {
        r"\/\/.*\s+FAILED in [0-9.]+s",
        r"\/\/.*\s+FAILED in [0-9]* out of [0-9]*",
        r"^\/\/.+ FAILED in [0-9\.]+s$",
        # r"Executed [0-9]* out of [0-9]* test.*: .* locally.",
    },
    "Test Guide": {
        "connector": [r"\[INFO \] .* Test Guide connector terminated with error..."],
        "Tests failing": [r"Tests still failing after all excludes"],
    },
    "Test(s) timeout": {r"\/\/.*\s+TIMEOUT in [0-9]*"},
    "Test(s) failed to build": {r"\/\/.*\s+FAILED TO BUILD[$]?"},
    "Terminate without exception": [r"terminate called without an active exception"],
    "Unknown test failure cause": [r"ScenarioInstance: Shutting down\.\.\."],
    "Dependency Error": {
        "File not found": [r"ERROR:.*no such package.*file not found in any of the following directories"],
    },
    "Bazel": {
        "failed on target analysis": [r"^ERROR: Analysis of target.+$"],
        "crash": [r"^Internal error .*java\.lang\.OutOfMemoryError"],
        "error loading package": [r"ERROR:(.*)error loading package(.*)"],
        "error finding package": [
            r"ERROR: \/workspace\/deployment\/ecu_instances\/casp_base\/tc4_eth\/cdd\/BUILD:13:17\: no such package .+: The repository .+ could not be resolved\: Repository .+ is not defined and referenced by"
        ],
        "unknown configuration": [r"ERROR: Config value .* is not defined in any \.rc file"],
        "server terminated": [r"^Server terminated abruptly \(error code:.+$"],
        "error executing shell command": [r"ERROR: .* error executing shell command: .* failed \(Exit [0-9]*\)"],
        "error executing command": [
            r"Executing .* failed: \(Exit [0-9]*\)\: .* failed\: error executing command",
            r"ERROR:.{1,500}error executing command \(.*\)",
        ],
        "building test target failed": [r"FAILED: Build did NOT complete successfully\n.+FAILED TO BUILD.*$"],
        "loading phase errors": [r"ERROR: command succeeded, but there were loading phase errors"],
        "no targets found": [r"^ERROR: Skipping.+no targets found beneath.+$", r"^ERROR: no targets found beneath.+$"],
        "could not build file": [r"ERROR: .* Couldn't build file .* failed \(Exit [0-9]*\).*$"],
        "missing input file": [r"ERROR:(.*)input file\(s\) do not exist", r"ERROR:(.*)missing input file '.*'"],
        "output was not created": [r"ERROR:.*output.*was not created"],
        "not all outputs were created or valid": [r"ERROR:.*not all outputs were created or valid"],
        "name is not defined": [r"ERROR: (.*) name '(.*)' is not defined(?: \(did you mean (.*)\?\))?"],
        "Failed to extract": [r"^FATAL: Failed to extract embedded binaries:.+(?P<file>'.+').+$"],
        "Unrecognized option": [r"ERROR: Unrecognized option:.+$"],
        "target name": [r"ERROR:.+no such target .* not declared in package .* defined by .*$"],
        "A2l failed": [r"(?s)a2lfactory\.exe failed:(?P<details>.+\n)FAILED: Build did NOT complete successfully"],
        "Missing deps. declaration": [
            r"ERROR(.*\n)this rule is missing dependency declarations for the following files included by(.+\n){0,10}"
        ],
        "BUILD file not found": [r"ERROR: command succeeded, but not all targets were analyzed"],
        "action cache initialization": [
            r"^ERROR: Error during action cache initialization: Failed action cache referential integrity check: Validation mismatch: validation entry [0-9]+ is too large compared to index size [0-9]+\. Corrupted files were renamed to '.*'\. Bazel will now reset action cache data, causing a full rebuild$"
        ],
        "Artifact error": [
            r"^ERROR: Unexpected exception, please file an issue with the Bazel team: Artifact.*is neither header nor source file."
        ],
        "Symlink - missing input file": [
            r"^ERROR: (?P<build>.+) Symlinking (?P<file>.+) failed: missing input file '(?P<detail>.+)'$"
        ],
        "Crashed due to an internal error": [r"FATAL: bazel crashed due to an internal error. Printing stack trace:"],
        "Sandbox execution error": [r"ERROR: .* failed: I\/O exception during sandboxed execution\:.*$"],
        "Build Event Protocol upload timed out": [r"^ERROR: The Build Event Protocol upload timed out"],
    },
    "SRec / S19 not created": [r"^ERROR: .+BUILD:[0-9]+:[0-9]+: output.*\.s19.+$"],
    "Generating functional code failed": [
        r"^(?P<file>.+?):(?P<line>\d+).*: ERROR:.+\/BUILD:[0-9]+:[0-9]+: .* - Generating funct.* failed \(Exit 2\):.*$",
        r"^(?P<file>.+?):(?P<line>\d+).*: ERROR:.+\/BUILD:[0-9]+:[0-9]+: Franca2ARXML.*failed \(Exit 5\).*$",
        r"^ERROR:.+Generate\sCode\sfrom\sARXML.+bash failed: error executing command",
        r"ERROR: .+ Generating arxml files failed\: \(Exit .\)\: .+ failed: error executing command",
        r"^ERROR:.+Generating SWE:.+payload_options failed: error executing command",
    ],
    "Win logging error": {
        "Failed to open Log-Path": [r"^Get-ChildItem : Cannot find path .+logs.+$"],
        "Failed to create logman counter": [r"Error:.*Data Collector already exists"],
    },
    "Toolchain": {
        "Failed to fetch/setup toolchain (e.g. eyeq_sdk, llvm_toolchain)": [
            r"^ERROR: .+\/BUILD:[0-9]+:[0-9]+: \/\/bazel\/toolchains\/.+$"
        ]
    },
    "Dependency": {
        "Failed to fetch dependency": [r"^ERROR: .+\/BUILD:[0-9]+:[0-9]+: .+ depends on .+ which failed to fetch\..+$"]
    },
    "Symlink": {
        "Failed to create symlink": [
            r"^ERROR: .+\/BUILD:[0-9]+:[0-9]+: failed to create symbolic link .+$",
            r"Create symlink from bazel_default_output_base=\/root\/.* to target\=\/var\/cache\/bazel",
        ]
    },
    "Formatting error": {
        "": [r"^Formatting errors found in .+$"],
    },
    "redirected output": {
        "Small Checks - Bazel queries check": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Bazel queries check)(?:.|[\r\n])*)"
        ],
        "Small Checks - BUILD-File Validator": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- BUILD-File Validator)(?:.|[\r\n])*)"
        ],
        "Small Checks - Buildifier-check": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Buildifier-check)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check CI jobs branch filters": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check CI jobs branch filters)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check CI jobs maintainers": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check CI jobs maintainers)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check dependencies for config adp_gcc9": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check dependencies for config adp_gcc9)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check the CI governance job": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check the CI governance job)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check-no-boardnet-switch-is-used": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check-no-boardnet-switch-is-used)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check_imports_in_py_rules": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check_imports_in_py_rules)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check_includes_in_cc_rules": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check_includes_in_cc_rules)(?:.|[\r\n])*)"
        ],
        "Small Checks - Check_strip_include_prefix_in_cc_rules": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check_strip_include_prefix_in_cc_rules)(?:.|[\r\n])*)"
        ],
        "Small Checks - Clang format": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Clang-format)(?:.|[\r\n])*)"
        ],
        "Small Checks - Filesystem-layout": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Filesystem-layout)(?:.|[\r\n])*)"
        ],
        "Small Checks - Include-guards": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Include-guards)(?:.|[\r\n])*)"
        ],
        "Small Checks - Python-compile-check": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Python-compile-check)(?:.|[\r\n])*)"
        ],
        "Small Checks - Python-format-check": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Python-format-check)(?:.|[\r\n])*)"
        ],
        "Small Checks - Runfile path check": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Runfile path check)(?:.|[\r\n])*)"
        ],
        "Small Checks - Validate teamscale architecture": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Validate teamscale architecture)(?:.|[\r\n])*)"
        ],
        "Small Checks - collect-FEP-002-violations": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- collect-FEP-002-violations)(?:.|[\r\n])*)"
        ],
        "Small Checks - correct-git-lfs-file-tracking": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- correct-git-lfs-file-tracking)(?:.|[\r\n])*)"
        ],
        "Fusa Small Checks - Check-docker-image-tags": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check-docker-image-tags)(?:.|[\r\n])*)"
        ],
        "Fusa Small Checks - Check-non-qualified-libraries": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check-non-qualified-libraries)(?:.|[\r\n])*)"
        ],
        "Fusa Small Checks - Check-Bazel-rules-in-FuSa-critical-components": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Check-Bazel-rules-in-FuSa-critical-components)(?:.|[\r\n])*)"
        ],
        "Fusa Small Checks - Windows-filename": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- Windows-filename)(?:.|[\r\n])*)"
        ],
        "Third-party Small Checks - third_party best practices": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*(- third_party best practices)(?:.|[\r\n])*)"
        ],
        # Matches only if no previous regex matched.
        # Keep this as last regex matching the redirected output log type.
        "default": [
            r"^@tu-cc-ci-adp-github-eof(?:(?:\s+type:(?P<type>\S*))|(?:\s+file:(?P<file>\S*))|(?:\s+line:(?P<line>\S*)))*\s+(?P<details>(?:.|[\r\n])*)"
        ],
    },
    "Matlab": {
        "Execution error": [r"(?s)(?<=ERROR MatlabExecutor - Matlab execution error:)(.*$)"],
        "Generation error": [r"(^.*)Generating functional code(.*)failed(.*?$)"],
        "Task(s) fail(ed)": [r"Code generation for module .* failed."],
    },
    "Docker": {
        "build": [
            r"^(?P<details>Error building (.+)code(.+)message(.+)), logs:",
            r"^E: Unable to locate package.+$",
            r"[E|W]:.+\nE: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing\?$",
            r"^error pulling image configuration:.+$",
            r"An image does not exist locally with the tag: (.*$)",
        ]
    },
    "Kubernetes": [r"^Failed to patch object.+$"],
    "clang tidy": [r"^\[ FAIL \] Clang Tidy produced.+$"],
    "rsync": [r"^rsync error:.+$"],
    "astas": {"test": [r"^FAILED - gui-core interaction tests$"]},
    "FuSa Violation Found (Check 'bazel_wrapper_log.txt' on the logs folder)": [
        r"Failed actions detected in bazel_wrapper_log.txt file"
    ],
    "FuSa Violation Found (Check 'mitguard_report.html' on the logs folder)": [r"Mitguard check failure"],
    "FuSa Violation Found (Check the log on 'Nightwatch' folder)": [r"Nightwatch verdict: rejected\."],
    "Network Traffic Check": [r"^Network traffic check has failed$"],
    "Mount error": {
        "Permission denied": [
            r"Error mounting .+ Permission denied.+$",
            r"^.+: (?P<file>mount error.+?): Permission denied",
        ],
        "Mounted FS stat failure": [r"Error: statfs \/mnt.+ no such file or directory"],
        "Failed to copy": [r"failed to copy: .+\/mnt\/.+"],
        "Failed to Umount": [r"Error\srmdir\s[a-zA-z-:/]+\s\[Errno\s[0-9]+\]\s[a-zA-z\s\W]+"],
    },
    "Param Server error": [r"ERROR:.+ param_server_gen failed.+$"],
    "License": {
        "Invalid License": [r"^.*No valid license found for .*"],
        "License not available": [
            r"All licenses are currently in use",
            r"ERROR: License server valid, no license available",
            r"ERROR: Couldn't obtain the license after \d+ retries.+$",
        ],
    },
    "Invoking Requirements Tracing": [r"ERROR.*Invoking Requirements.*driver_tracing failed: \(Exit 1\)"],
    "Invalid Main repository mapping": [
        r"^ERROR:.Error computing the main repository mapping:.at.+ is invalid because.+is not a package.+perhaps you meant to put the colon here: .+?$"
    ],
    "Cptc Error": [r"cptc .+ cannot open source file.+$"],
    "Cmake Error": [r"^make.*Error"],
    "windows": {
        "Restart-Service": [
            r"Service 'sshd \(sshd\)' cannot be stopped due to the following error: Cannot stop sshd service on "
        ]
    },
    "tar": {
        "error executing command": [
            r"^ERROR: .+ Action .+\.tar\.gz failed: \(Exit 1\): bash failed: error executing command$"
        ]
    },
    "Linux": ["\[Errno 2\] No such file or directory"],
}
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