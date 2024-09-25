import json
import extract_build_failures.error_patterns as error_patterns


# I think I do not need this anymore

INFRA_PATTERNS = error_patterns.INFRA_PATTERNS
BUILD_PATTERNS = error_patterns.BUILD_PATTERNS

def save_pattern(patterns, file_path):
    with open(file_path, 'w') as f:
        json.dump(patterns, f)


def restructure_pattern(pattern):
    """
    Restructures the input patterns dictionary to a more structured format.
    """
    restructured_patterns = {}
    for pattern_type, subpatterns in pattern.items():
        if isinstance(subpatterns, (set, list)):
            restructured_patterns[pattern_type] = {"": list(subpatterns)}
        elif isinstance(subpatterns, dict):
            restructured_patterns[pattern_type] = {}
            for subtype, regex_list in subpatterns.items():
                if isinstance(regex_list, (list, set)):
                    restructured_patterns[pattern_type][subtype] = list(regex_list)
                else:
                    raise ValueError(f"Unexpected type for regex list: {type(regex_list)}")
        else:
            raise ValueError(f"Unexpected type for subpatterns: {type(subpatterns)}")
    
    return restructured_patterns

restructured_infra_pattern = restructure_pattern(INFRA_PATTERNS)
restructured_build_pattern = restructure_pattern(BUILD_PATTERNS)

save_pattern(restructured_infra_pattern, "infra_patterns.json")
save_pattern(restructured_build_pattern, "build_patterns.json")