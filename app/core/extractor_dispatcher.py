from core.extractors.detailed_computer_audit import DetailedComputerAuditExtractor

def get_extractor(filename):
    # Add the logic to match the file and return the corresponding extractor class
    if "Detailed Computer Audit" in filename:
        return DetailedComputerAuditExtractor
    # elif "Device Activity" in filename:
    #     return DeviceActivityExtractor
    # Add more cases for other files
    else:
        raise ValueError(f"No extractor found for file: {filename}")
