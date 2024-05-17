from enum import Enum


class TagTypes(str, Enum):
    exploit = "Exploit"
    software = "Software"
    threat_actor = "Threat Actor"
    malware_family = "Malware Family"
    campaign = "Campaign"
    malicious_behavior = "Malicious Behavior"


class TagVisibilityStates(str, Enum):
    public = "Public"
    private = "Private"
    internal = "Internal"
