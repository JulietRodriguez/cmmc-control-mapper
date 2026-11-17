"""Build data/cmmc_controls.json: all 110 CMMC Level 2 practices.

Every field comes from a named public source, kept in the tables below so a
reviewer can check any row:

  * Practice IDs and short titles: DoD CIO, CMMC Assessment Guide - Level 2,
    Version 2.13 (September 2024). Version 2.13 writes every Level 2 practice,
    including the 17 that are also required at Level 1, as "XX.L2-3.x.y".
  * Requirement text: NIST SP 800-171 Rev. 2 (CMMC Level 2 is based on Rev. 2).
  * NIST SP 800-53 controls: NIST SP 800-171 Rev. 2, Appendix D, Tables D-1 to
    D-14. Appendix D maps to SP 800-53 **Rev. 4** control IDs.
  * AWS Config rules: chosen from the AWS Config conformance pack
    "Operational Best Practices for CMMC 2.0 Level 2". A rule is only listed for
    a practice if AWS maps it to that practice. Practices AWS doesn't map to any
    managed rule (training, physical, personnel, most policy practices) have an
    empty list on purpose: they are verified by process, not by a Config rule.
  * AWS services: derived from the listed Config rules, plus a short, curated
    list for practices with no Config rule where an AWS feature clearly applies.

Run:  python tools/build_controls.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "cmmc_controls.json"

DOMAINS = {
    "AC": "Access Control",
    "AT": "Awareness & Training",
    "AU": "Audit & Accountability",
    "CM": "Configuration Management",
    "IA": "Identification & Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PS": "Personnel Security",
    "PE": "Physical Protection",
    "RA": "Risk Assessment",
    "CA": "Security Assessment",
    "SC": "System & Communications Protection",
    "SI": "System & Information Integrity",
}
FAMILY_TO_DOMAIN = {
    "3.1": "AC", "3.2": "AT", "3.3": "AU", "3.4": "CM", "3.5": "IA", "3.6": "IR",
    "3.7": "MA", "3.8": "MP", "3.9": "PS", "3.10": "PE", "3.11": "RA", "3.12": "CA",
    "3.13": "SC", "3.14": "SI",
}  # fmt: skip

# The 17 practices that are also CMMC Level 1 (FAR 52.204-21 safeguarding).
LEVEL_1 = {
    "3.1.1", "3.1.2", "3.1.20", "3.1.22", "3.5.1", "3.5.2", "3.8.3", "3.10.1",
    "3.10.3", "3.10.4", "3.10.5", "3.13.1", "3.13.5", "3.14.1", "3.14.2", "3.14.4",
    "3.14.5",
}  # fmt: skip

# (800-171 number, CMMC short title, NIST SP 800-171 Rev. 2 requirement text)
PRACTICES = [
    ("3.1.1", "Authorized Access Control", "Limit system access to authorized users, processes acting on behalf of authorized users, and devices (including other systems)."),
    ("3.1.2", "Transaction & Function Control", "Limit system access to the types of transactions and functions that authorized users are permitted to execute."),
    ("3.1.3", "Control CUI Flow", "Control the flow of CUI in accordance with approved authorizations."),
    ("3.1.4", "Separation of Duties", "Separate the duties of individuals to reduce the risk of malevolent activity without collusion."),
    ("3.1.5", "Least Privilege", "Employ the principle of least privilege, including for specific security functions and privileged accounts."),
    ("3.1.6", "Non-Privileged Account Use", "Use non-privileged accounts or roles when accessing nonsecurity functions."),
    ("3.1.7", "Privileged Functions", "Prevent non-privileged users from executing privileged functions and capture the execution of such functions in audit logs."),
    ("3.1.8", "Unsuccessful Logon Attempts", "Limit unsuccessful logon attempts."),
    ("3.1.9", "Privacy & Security Notices", "Provide privacy and security notices consistent with applicable CUI rules."),
    ("3.1.10", "Session Lock", "Use session lock with pattern-hiding displays to prevent access and viewing of data after a period of inactivity."),
    ("3.1.11", "Session Termination", "Terminate (automatically) a user session after a defined condition."),
    ("3.1.12", "Control Remote Access", "Monitor and control remote access sessions."),
    ("3.1.13", "Remote Access Confidentiality", "Employ cryptographic mechanisms to protect the confidentiality of remote access sessions."),
    ("3.1.14", "Remote Access Routing", "Route remote access via managed access control points."),
    ("3.1.15", "Privileged Remote Access", "Authorize remote execution of privileged commands and remote access to security-relevant information."),
    ("3.1.16", "Wireless Access Authorization", "Authorize wireless access prior to allowing such connections."),
    ("3.1.17", "Wireless Access Protection", "Protect wireless access using authentication and encryption."),
    ("3.1.18", "Mobile Device Connection", "Control connection of mobile devices."),
    ("3.1.19", "Encrypt CUI on Mobile", "Encrypt CUI on mobile devices and mobile computing platforms."),
    ("3.1.20", "External Connections", "Verify and control/limit connections to and use of external systems."),
    ("3.1.21", "Portable Storage Use", "Limit use of portable storage devices on external systems."),
    ("3.1.22", "Control Public Information", "Control CUI posted or processed on publicly accessible systems."),
    ("3.2.1", "Role-Based Risk Awareness", "Ensure that managers, systems administrators, and users of organizational systems are made aware of the security risks associated with their activities and of the applicable policies, standards, and procedures related to the security of those systems."),
    ("3.2.2", "Role-Based Training", "Ensure that personnel are trained to carry out their assigned information security-related duties and responsibilities."),
    ("3.2.3", "Insider Threat Awareness", "Provide security awareness training on recognizing and reporting potential indicators of insider threat."),
    ("3.3.1", "System Auditing", "Create and retain system audit logs and records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity."),
    ("3.3.2", "User Accountability", "Ensure that the actions of individual system users can be uniquely traced to those users, so they can be held accountable for their actions."),
    ("3.3.3", "Event Review", "Review and update logged events."),
    ("3.3.4", "Audit Failure Alerting", "Alert in the event of an audit logging process failure."),
    ("3.3.5", "Audit Correlation", "Correlate audit record review, analysis, and reporting processes for investigation and response to indications of unlawful, unauthorized, suspicious, or unusual activity."),
    ("3.3.6", "Reduction & Reporting", "Provide audit record reduction and report generation to support on-demand analysis and reporting."),
    ("3.3.7", "Authoritative Time Source", "Provide a system capability that compares and synchronizes internal system clocks with an authoritative source to generate time stamps for audit records."),
    ("3.3.8", "Audit Protection", "Protect audit information and audit logging tools from unauthorized access, modification, and deletion."),
    ("3.3.9", "Audit Management", "Limit management of audit logging functionality to a subset of privileged users."),
    ("3.4.1", "System Baselining", "Establish and maintain baseline configurations and inventories of organizational systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles."),
    ("3.4.2", "Security Configuration Enforcement", "Establish and enforce security configuration settings for information technology products employed in organizational systems."),
    ("3.4.3", "System Change Management", "Track, review, approve or disapprove, and log changes to organizational systems."),
    ("3.4.4", "Security Impact Analysis", "Analyze the security impact of changes prior to implementation."),
    ("3.4.5", "Access Restrictions for Change", "Define, document, approve, and enforce physical and logical access restrictions associated with changes to organizational systems."),
    ("3.4.6", "Least Functionality", "Employ the principle of least functionality by configuring organizational systems to provide only essential capabilities."),
    ("3.4.7", "Nonessential Functionality", "Restrict, disable, or prevent the use of nonessential programs, functions, ports, protocols, and services."),
    ("3.4.8", "Application Execution Policy", "Apply deny-by-exception (blacklisting) policy to prevent the use of unauthorized software or deny-all, permit-by-exception (whitelisting) policy to allow the execution of authorized software."),
    ("3.4.9", "User-Installed Software", "Control and monitor user-installed software."),
    ("3.5.1", "Identification", "Identify system users, processes acting on behalf of users, and devices."),
    ("3.5.2", "Authentication", "Authenticate (or verify) the identities of users, processes, or devices, as a prerequisite to allowing access to organizational systems."),
    ("3.5.3", "Multifactor Authentication", "Use multifactor authentication for local and network access to privileged accounts and for network access to non-privileged accounts."),
    ("3.5.4", "Replay-Resistant Authentication", "Employ replay-resistant authentication mechanisms for network access to privileged and non-privileged accounts."),
    ("3.5.5", "Identifier Reuse", "Prevent reuse of identifiers for a defined period."),
    ("3.5.6", "Identifier Handling", "Disable identifiers after a defined period of inactivity."),
    ("3.5.7", "Password Complexity", "Enforce a minimum password complexity and change of characters when new passwords are created."),
    ("3.5.8", "Password Reuse", "Prohibit password reuse for a specified number of generations."),
    ("3.5.9", "Temporary Passwords", "Allow temporary password use for system logons with an immediate change to a permanent password."),
    ("3.5.10", "Cryptographically-Protected Passwords", "Store and transmit only cryptographically-protected passwords."),
    ("3.5.11", "Obscure Feedback", "Obscure feedback of authentication information."),
    ("3.6.1", "Incident Handling", "Establish an operational incident-handling capability for organizational systems that includes preparation, detection, analysis, containment, recovery, and user response activities."),
    ("3.6.2", "Incident Reporting", "Track, document, and report incidents to designated officials and/or authorities both internal and external to the organization."),
    ("3.6.3", "Incident Response Testing", "Test the organizational incident response capability."),
    ("3.7.1", "Perform Maintenance", "Perform maintenance on organizational systems."),
    ("3.7.2", "System Maintenance Control", "Provide controls on the tools, techniques, mechanisms, and personnel used to conduct system maintenance."),
    ("3.7.3", "Equipment Sanitization", "Ensure equipment removed for off-site maintenance is sanitized of any CUI."),
    ("3.7.4", "Media Inspection", "Check media containing diagnostic and test programs for malicious code before the media are used in organizational systems."),
    ("3.7.5", "Nonlocal Maintenance", "Require multifactor authentication to establish nonlocal maintenance sessions via external network connections and terminate such connections when nonlocal maintenance is complete."),
    ("3.7.6", "Maintenance Personnel", "Supervise the maintenance activities of maintenance personnel without required access authorization."),
    ("3.8.1", "Media Protection", "Protect (i.e., physically control and securely store) system media containing CUI, both paper and digital."),
    ("3.8.2", "Media Access", "Limit access to CUI on system media to authorized users."),
    ("3.8.3", "Media Disposal", "Sanitize or destroy system media containing CUI before disposal or release for reuse."),
    ("3.8.4", "Media Markings", "Mark media with necessary CUI markings and distribution limitations."),
    ("3.8.5", "Media Accountability", "Control access to media containing CUI and maintain accountability for media during transport outside of controlled areas."),
    ("3.8.6", "Portable Storage Encryption", "Implement cryptographic mechanisms to protect the confidentiality of CUI stored on digital media during transport unless otherwise protected by alternative physical safeguards."),
    ("3.8.7", "Removable Media", "Control the use of removable media on system components."),
    ("3.8.8", "Shared Media", "Prohibit the use of portable storage devices when such devices have no identifiable owner."),
    ("3.8.9", "Protect Backups", "Protect the confidentiality of backup CUI at storage locations."),
    ("3.9.1", "Screen Individuals", "Screen individuals prior to authorizing access to organizational systems containing CUI."),
    ("3.9.2", "Personnel Actions", "Ensure that organizational systems containing CUI are protected during and after personnel actions such as terminations and transfers."),
    ("3.10.1", "Limit Physical Access", "Limit physical access to organizational systems, equipment, and the respective operating environments to authorized individuals."),
    ("3.10.2", "Monitor Facility", "Protect and monitor the physical facility and support infrastructure for organizational systems."),
    ("3.10.3", "Escort Visitors", "Escort visitors and monitor visitor activity."),
    ("3.10.4", "Physical Access Logs", "Maintain audit logs of physical access."),
    ("3.10.5", "Manage Physical Access", "Control and manage physical access devices."),
    ("3.10.6", "Alternative Work Sites", "Enforce safeguarding measures for CUI at alternate work sites."),
    ("3.11.1", "Risk Assessments", "Periodically assess the risk to organizational operations (including mission, functions, image, or reputation), organizational assets, and individuals, resulting from the operation of organizational systems and the associated processing, storage, or transmission of CUI."),
    ("3.11.2", "Vulnerability Scan", "Scan for vulnerabilities in organizational systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified."),
    ("3.11.3", "Vulnerability Remediation", "Remediate vulnerabilities in accordance with risk assessments."),
    ("3.12.1", "Security Control Assessment", "Periodically assess the security controls in organizational systems to determine if the controls are effective in their application."),
    ("3.12.2", "Operational Plan of Action", "Develop and implement plans of action designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational systems."),
    ("3.12.3", "Security Control Monitoring", "Monitor security controls on an ongoing basis to ensure the continued effectiveness of the controls."),
    ("3.12.4", "System Security Plan", "Develop, document, and periodically update system security plans that describe system boundaries, system environments of operation, how security requirements are implemented, and the relationships with or connections to other systems."),
    ("3.13.1", "Boundary Protection", "Monitor, control, and protect communications (i.e., information transmitted or received by organizational systems) at the external boundaries and key internal boundaries of organizational systems."),
    ("3.13.2", "Security Engineering", "Employ architectural designs, software development techniques, and systems engineering principles that promote effective information security within organizational systems."),
    ("3.13.3", "Role Separation", "Separate user functionality from system management functionality."),
    ("3.13.4", "Shared Resource Control", "Prevent unauthorized and unintended information transfer via shared system resources."),
    ("3.13.5", "Public-Access System Separation", "Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks."),
    ("3.13.6", "Network Communication by Exception", "Deny network communications traffic by default and allow network communications traffic by exception (i.e., deny all, permit by exception)."),
    ("3.13.7", "Split Tunneling", "Prevent remote devices from simultaneously establishing non-remote connections with organizational systems and communicating via some other connection to resources in external networks (i.e., split tunneling)."),
    ("3.13.8", "Data in Transit", "Implement cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission unless otherwise protected by alternative physical safeguards."),
    ("3.13.9", "Connections Termination", "Terminate network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity."),
    ("3.13.10", "Key Management", "Establish and manage cryptographic keys for cryptography employed in organizational systems."),
    ("3.13.11", "CUI Encryption", "Employ FIPS-validated cryptography when used to protect the confidentiality of CUI."),
    ("3.13.12", "Collaborative Device Control", "Prohibit remote activation of collaborative computing devices and provide indication of devices in use to users present at the device."),
    ("3.13.13", "Mobile Code", "Control and monitor the use of mobile code."),
    ("3.13.14", "Voice over Internet Protocol", "Control and monitor the use of Voice over Internet Protocol (VoIP) technologies."),
    ("3.13.15", "Communications Authenticity", "Protect the authenticity of communications sessions."),
    ("3.13.16", "Data at Rest", "Protect the confidentiality of CUI at rest."),
    ("3.14.1", "Flaw Remediation", "Identify, report, and correct system flaws in a timely manner."),
    ("3.14.2", "Malicious Code Protection", "Provide protection from malicious code at designated locations within organizational systems."),
    ("3.14.3", "Security Alerts & Advisories", "Monitor system security alerts and advisories and take action in response."),
    ("3.14.4", "Update Malicious Code Protection", "Update malicious code protection mechanisms when new releases are available."),
    ("3.14.5", "System & File Scanning", "Perform periodic scans of organizational systems and real-time scans of files from external sources as files are downloaded, opened, or executed."),
    ("3.14.6", "Monitor Communications for Attacks", "Monitor organizational systems, including inbound and outbound communications traffic, to detect attacks and indicators of potential attacks."),
    ("3.14.7", "Identify Unauthorized Use", "Identify unauthorized use of organizational systems."),
]  # fmt: skip

# NIST SP 800-171 Rev. 2, Appendix D (Tables D-1 to D-14): SP 800-53 Rev. 4 controls.
NIST_800_53 = {
    "3.1.1": ["AC-2", "AC-3", "AC-17"], "3.1.2": ["AC-2", "AC-3", "AC-17"],
    "3.1.3": ["AC-4"], "3.1.4": ["AC-5"], "3.1.5": ["AC-6", "AC-6(1)", "AC-6(5)"],
    "3.1.6": ["AC-6(2)"], "3.1.7": ["AC-6(9)", "AC-6(10)"], "3.1.8": ["AC-7"],
    "3.1.9": ["AC-8"], "3.1.10": ["AC-11", "AC-11(1)"], "3.1.11": ["AC-12"],
    "3.1.12": ["AC-17(1)"], "3.1.13": ["AC-17(2)"], "3.1.14": ["AC-17(3)"],
    "3.1.15": ["AC-17(4)"], "3.1.16": ["AC-18"], "3.1.17": ["AC-18(1)"],
    "3.1.18": ["AC-19"], "3.1.19": ["AC-19(5)"], "3.1.20": ["AC-20", "AC-20(1)"],
    "3.1.21": ["AC-20(2)"], "3.1.22": ["AC-22"],
    "3.2.1": ["AT-2", "AT-3"], "3.2.2": ["AT-2", "AT-3"], "3.2.3": ["AT-2(2)"],
    "3.3.1": ["AU-2", "AU-3", "AU-3(1)", "AU-6", "AU-12"],
    "3.3.2": ["AU-2", "AU-3", "AU-3(1)", "AU-6", "AU-12"],
    "3.3.3": ["AU-2(3)"], "3.3.4": ["AU-5"], "3.3.5": ["AU-6(3)"], "3.3.6": ["AU-7"],
    "3.3.7": ["AU-8", "AU-8(1)"], "3.3.8": ["AU-9"], "3.3.9": ["AU-9(4)"],
    "3.4.1": ["CM-2", "CM-6", "CM-8", "CM-8(1)"], "3.4.2": ["CM-2", "CM-6", "CM-8", "CM-8(1)"],
    "3.4.3": ["CM-3"], "3.4.4": ["CM-4"], "3.4.5": ["CM-5"], "3.4.6": ["CM-7"],
    "3.4.7": ["CM-7(1)", "CM-7(2)"], "3.4.8": ["CM-7(4)", "CM-7(5)"], "3.4.9": ["CM-11"],
    "3.5.1": ["IA-2", "IA-5"], "3.5.2": ["IA-2", "IA-5"],
    "3.5.3": ["IA-2(1)", "IA-2(2)", "IA-2(3)"], "3.5.4": ["IA-2(8)", "IA-2(9)"],
    "3.5.5": ["IA-4"], "3.5.6": ["IA-4"], "3.5.7": ["IA-5(1)"], "3.5.8": ["IA-5(1)"],
    "3.5.9": ["IA-5(1)"], "3.5.10": ["IA-5(1)"], "3.5.11": ["IA-6"],
    "3.6.1": ["IR-2", "IR-4", "IR-5", "IR-6", "IR-7"], "3.6.2": ["IR-2", "IR-4", "IR-5", "IR-6", "IR-7"],
    "3.6.3": ["IR-3", "IR-3(2)"],
    "3.7.1": ["MA-2", "MA-3", "MA-3(1)", "MA-3(2)"], "3.7.2": ["MA-2", "MA-3", "MA-3(1)", "MA-3(2)"],
    "3.7.3": ["MA-2"], "3.7.4": ["MA-3(2)"], "3.7.5": ["MA-4"], "3.7.6": ["MA-5"],
    "3.8.1": ["MP-2", "MP-4", "MP-6"], "3.8.2": ["MP-2", "MP-4", "MP-6"], "3.8.3": ["MP-2", "MP-4", "MP-6"],
    "3.8.4": ["MP-3"], "3.8.5": ["MP-5"], "3.8.6": ["MP-5(4)"], "3.8.7": ["MP-7"],
    "3.8.8": ["MP-7(1)"], "3.8.9": ["CP-9"],
    "3.9.1": ["PS-3"], "3.9.2": ["PS-4", "PS-5"],
    "3.10.1": ["PE-2", "PE-5", "PE-6"], "3.10.2": ["PE-2", "PE-5", "PE-6"],
    "3.10.3": ["PE-3"], "3.10.4": ["PE-3"], "3.10.5": ["PE-3"], "3.10.6": ["PE-17"],
    "3.11.1": ["RA-3"], "3.11.2": ["RA-5", "RA-5(5)"], "3.11.3": ["RA-5"],
    "3.12.1": ["CA-2"], "3.12.2": ["CA-5"], "3.12.3": ["CA-7"], "3.12.4": ["PL-2"],
    "3.13.1": ["SC-7", "SA-8"], "3.13.2": ["SC-7", "SA-8"], "3.13.3": ["SC-2"],
    "3.13.4": ["SC-4"], "3.13.5": ["SC-7"], "3.13.6": ["SC-7(5)"], "3.13.7": ["SC-7(7)"],
    "3.13.8": ["SC-8", "SC-8(1)"], "3.13.9": ["SC-10"], "3.13.10": ["SC-12"],
    "3.13.11": ["SC-13"], "3.13.12": ["SC-15"], "3.13.13": ["SC-18"], "3.13.14": ["SC-19"],
    "3.13.15": ["SC-23"], "3.13.16": ["SC-28"],
    "3.14.1": ["SI-2", "SI-3", "SI-5"], "3.14.2": ["SI-2", "SI-3", "SI-5"],
    "3.14.3": ["SI-2", "SI-3", "SI-5"], "3.14.4": ["SI-3"], "3.14.5": ["SI-3"],
    "3.14.6": ["SI-4", "SI-4(4)"], "3.14.7": ["SI-4"],
}  # fmt: skip

# Selected from AWS "Operational Best Practices for CMMC 2.0 Level 2" (AWS Config docs).
AWS_CONFIG_RULES = {
    "3.1.1": ["iam-root-access-key-check", "iam-user-unused-credentials-check", "mfa-enabled-for-iam-console-access", "iam-policy-no-statements-with-admin-access", "s3-bucket-public-read-prohibited"],
    "3.1.2": ["iam-policy-no-statements-with-admin-access", "iam-user-no-policies-check", "iam-user-group-membership-check", "iam-no-inline-policy-check"],
    "3.1.3": ["vpc-default-security-group-closed", "restricted-ssh", "no-unrestricted-route-to-igw", "s3-account-level-public-access-blocks-periodic", "lambda-inside-vpc"],
    "3.1.4": ["iam-group-has-users-check", "iam-user-group-membership-check", "iam-policy-no-statements-with-full-access"],
    "3.1.5": ["iam-policy-no-statements-with-admin-access", "iam-policy-no-statements-with-full-access", "iam-root-access-key-check", "iam-inline-policy-blocked-kms-actions"],
    "3.1.6": ["iam-root-access-key-check", "iam-user-no-policies-check", "iam-user-group-membership-check"],
    "3.1.7": ["cloudtrail-enabled", "multi-region-cloudtrail-enabled", "iam-policy-no-statements-with-admin-access", "iam-customer-policy-blocked-kms-actions"],
    "3.1.12": ["cloud-trail-cloud-watch-logs-enabled", "guardduty-enabled-centralized", "securityhub-enabled"],
    "3.1.13": ["elb-tls-https-listeners-only", "alb-http-to-https-redirection-check", "api-gw-ssl-enabled", "acm-certificate-expiration-check"],
    "3.1.20": ["internet-gateway-authorized-vpc-only", "no-unrestricted-route-to-igw", "ec2-instance-no-public-ip", "alb-waf-enabled"],
    "3.3.1": ["cloudtrail-enabled", "multi-region-cloudtrail-enabled", "cw-loggroup-retention-period-check", "s3-bucket-logging-enabled", "rds-logging-enabled"],
    "3.3.2": ["cloudtrail-enabled", "cloudtrail-s3-dataevents-enabled", "elb-logging-enabled", "api-gw-execution-logging-enabled"],
    "3.3.4": ["cloudwatch-alarm-action-check", "cloud-trail-cloud-watch-logs-enabled"],
    "3.3.5": ["guardduty-enabled-centralized", "securityhub-enabled"],
    "3.3.8": ["cloud-trail-encryption-enabled", "cloud-trail-log-file-validation-enabled", "cloudwatch-log-group-encrypted", "s3-bucket-default-lock-enabled", "s3-bucket-versioning-enabled"],
    "3.4.1": ["ec2-managedinstance-association-compliance-status-check", "ec2-volume-inuse-check", "ec2-stopped-instance", "eip-attached"],
    "3.4.2": ["ec2-instance-managed-by-systems-manager", "ec2-managedinstance-patch-compliance-status-check", "account-part-of-organizations", "rds-automatic-minor-version-upgrade-enabled"],
    "3.4.3": ["cloudtrail-enabled", "multi-region-cloudtrail-enabled", "ec2-instance-managed-by-systems-manager"],
    "3.4.6": ["ec2-instance-no-public-ip", "restricted-common-ports", "vpc-sg-open-only-to-authorized-ports", "ssm-document-not-public"],
    "3.4.7": ["restricted-ssh", "restricted-common-ports", "vpc-sg-open-only-to-authorized-ports", "vpc-default-security-group-closed"],
    "3.4.9": ["ec2-instance-managed-by-systems-manager", "ec2-managedinstance-association-compliance-status-check"],
    "3.5.1": ["cloudtrail-s3-dataevents-enabled", "cloud-trail-cloud-watch-logs-enabled", "emr-kerberos-enabled"],
    "3.5.2": ["iam-password-policy", "iam-user-mfa-enabled", "mfa-enabled-for-iam-console-access", "root-account-mfa-enabled"],
    "3.5.3": ["iam-user-mfa-enabled", "mfa-enabled-for-iam-console-access", "root-account-hardware-mfa-enabled", "root-account-mfa-enabled"],
    "3.5.6": ["iam-user-unused-credentials-check", "iam-password-policy"],
    "3.5.7": ["iam-password-policy"],
    "3.5.8": ["iam-password-policy"],
    "3.5.10": ["s3-bucket-ssl-requests-only", "elb-tls-https-listeners-only", "encrypted-volumes", "rds-storage-encrypted"],
    "3.6.1": ["guardduty-enabled-centralized", "guardduty-non-archived-findings", "securityhub-enabled"],
    "3.7.5": ["iam-user-mfa-enabled", "mfa-enabled-for-iam-console-access"],
    "3.11.2": ["ec2-managedinstance-patch-compliance-status-check", "guardduty-enabled-centralized", "securityhub-enabled"],
    "3.12.3": ["guardduty-enabled-centralized", "securityhub-enabled"],
    "3.13.1": ["alb-waf-enabled", "vpc-default-security-group-closed", "restricted-ssh", "internet-gateway-authorized-vpc-only", "guardduty-enabled-centralized"],
    "3.13.2": ["account-part-of-organizations", "rds-multi-az-support", "s3-bucket-versioning-enabled", "db-instance-backup-enabled"],
    "3.13.4": ["ebs-snapshot-public-restorable-check", "rds-snapshots-public-prohibited", "s3-bucket-public-read-prohibited", "ssm-document-not-public"],
    "3.13.8": ["s3-bucket-ssl-requests-only", "elb-tls-https-listeners-only", "alb-http-to-https-redirection-check", "redshift-require-tls-ssl", "acm-certificate-expiration-check"],
    "3.13.10": ["cmk-backing-key-rotation-enabled", "kms-cmk-not-scheduled-for-deletion"],
    "3.13.15": ["elbv2-acm-certificate-required", "elb-acm-certificate-required", "api-gw-ssl-enabled"],
    "3.13.16": ["encrypted-volumes", "rds-storage-encrypted", "s3-bucket-server-side-encryption-enabled", "efs-encrypted-check", "ec2-ebs-encryption-by-default"],
    "3.14.1": ["securityhub-enabled", "guardduty-enabled-centralized", "cloudwatch-alarm-action-check"],
    "3.14.2": ["guardduty-enabled-centralized"],
    "3.14.3": ["securityhub-enabled", "guardduty-enabled-centralized", "cloudwatch-alarm-action-check"],
    "3.14.5": ["ecr-private-image-scanning-enabled"],
    "3.14.6": ["guardduty-enabled-centralized", "wafv2-logging-enabled", "alb-waf-enabled", "securityhub-enabled"],
    "3.14.7": ["cloudtrail-enabled", "guardduty-enabled-centralized", "s3-bucket-logging-enabled", "elb-logging-enabled"],
}  # fmt: skip

# Rule-name prefix -> AWS service. Longest matching prefix wins.
RULE_SERVICE = {
    "access-keys": "AWS IAM", "iam-": "AWS IAM", "mfa-": "AWS IAM", "root-account": "AWS IAM",
    "s3-": "Amazon S3", "cloudtrail": "AWS CloudTrail", "cloud-trail": "AWS CloudTrail",
    "multi-region-cloudtrail": "AWS CloudTrail", "guardduty": "Amazon GuardDuty",
    "securityhub": "AWS Security Hub", "vpc-": "Amazon VPC", "restricted-": "Amazon VPC",
    "no-unrestricted-route": "Amazon VPC", "internet-gateway": "Amazon VPC",
    "subnet-": "Amazon VPC", "ec2-managedinstance": "AWS Systems Manager",
    "ec2-instance-managed-by-systems-manager": "AWS Systems Manager", "ssm-": "AWS Systems Manager",
    "ec2-ebs-encryption": "Amazon EBS", "encrypted-volumes": "Amazon EBS",
    "ebs-": "Amazon EBS", "ec2-": "Amazon EC2", "eip-": "Amazon EC2",
    "lambda-": "AWS Lambda", "rds-": "Amazon RDS", "db-instance": "Amazon RDS",
    "cw-": "Amazon CloudWatch", "cloudwatch-": "Amazon CloudWatch", "elb-": "Elastic Load Balancing",
    "elbv2-": "Elastic Load Balancing", "alb-http": "Elastic Load Balancing", "alb-waf": "AWS WAF",
    "wafv2-": "AWS WAF", "api-gw": "Amazon API Gateway", "acm-": "AWS Certificate Manager",
    "cmk-": "AWS KMS", "kms-": "AWS KMS", "efs-": "Amazon EFS", "ecr-": "Amazon ECR",
    "account-part-of-organizations": "AWS Organizations", "redshift-": "Amazon Redshift",
    "emr-": "Amazon EMR",
}  # fmt: skip

# Practices with no AWS-mapped Config rule where an AWS feature clearly applies.
EXTRA_SERVICES = {
    "3.1.11": ["AWS IAM Identity Center", "AWS Systems Manager"],
    "3.1.14": ["AWS Client VPN", "AWS Systems Manager"],
    "3.1.15": ["AWS IAM", "AWS Systems Manager"],
    "3.1.22": ["Amazon S3", "Amazon Macie"],
    "3.3.3": ["AWS CloudTrail"],
    "3.3.6": ["Amazon CloudWatch", "Amazon Athena"],
    "3.3.7": ["Amazon Time Sync Service"],
    "3.3.9": ["AWS IAM", "AWS Organizations"],
    "3.4.4": ["AWS CloudFormation"],
    "3.4.5": ["AWS IAM", "AWS Organizations"],
    "3.5.9": ["AWS IAM"],
    "3.7.1": ["AWS Systems Manager"],
    "3.7.2": ["AWS Systems Manager"],
    "3.8.9": ["AWS Backup", "AWS KMS"],
    "3.10.1": ["AWS Artifact"],
    "3.10.2": ["AWS Artifact"],
    "3.10.3": ["AWS Artifact"],
    "3.10.4": ["AWS Artifact"],
    "3.10.5": ["AWS Artifact"],
    "3.11.3": ["AWS Systems Manager", "Amazon Inspector"],
    "3.12.1": ["AWS Audit Manager"],
    "3.13.3": ["AWS Organizations", "AWS IAM"],
    "3.13.5": ["Amazon VPC"],
    "3.13.6": ["Amazon VPC"],
    "3.13.7": ["AWS Client VPN"],
    "3.13.9": ["Elastic Load Balancing", "AWS Systems Manager"],
    "3.13.11": ["AWS KMS"],
}

NOTES = {
    "3.10.1": "Physical security of AWS data centers is inherited from AWS; AWS Artifact provides the audit reports as evidence. Your own facilities still need their own controls.",
}
for _n in ("3.10.2", "3.10.3", "3.10.4", "3.10.5"):
    NOTES[_n] = NOTES["3.10.1"]


def service_for(rule: str) -> str:
    match = max((p for p in RULE_SERVICE if rule.startswith(p)), key=len, default=None)
    if match is None:
        raise ValueError(f"no AWS service mapping for rule {rule!r}")
    return RULE_SERVICE[match]


def build() -> list[dict]:
    controls = []
    for nist_id, title, text in PRACTICES:
        family = nist_id.rsplit(".", 1)[0]
        code = FAMILY_TO_DOMAIN[family]
        rules = AWS_CONFIG_RULES.get(nist_id, [])
        services = sorted({service_for(r) for r in rules} | set(EXTRA_SERVICES.get(nist_id, [])))
        level = 1 if nist_id in LEVEL_1 else 2
        controls.append(
            {
                "id": f"{code}.L2-{nist_id}",
                "nist_800_171": nist_id,
                "title": title,
                "domain": DOMAINS[code],
                "domain_code": code,
                "level": level,
                "cmmc_level": f"Level {level}",
                "practice": text,
                "nist_mapping": NIST_800_53[nist_id],
                "aws_services": services,
                "aws_config_rules": rules,
                "notes": NOTES.get(nist_id, ""),
            }
        )
    return controls


def main() -> None:
    controls = build()
    OUT.write_text(json.dumps(controls, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(controls)} practices to {OUT}")


if __name__ == "__main__":
    main()
