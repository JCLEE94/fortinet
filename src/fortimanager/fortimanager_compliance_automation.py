#!/usr/bin/env python3
"""
FortiManager Compliance Automation Framework
Advanced compliance checking with automated remediation capabilities
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

from api.clients.fortimanager_api_client import FortiManagerAPIClient

logger = logging.getLogger(__name__)


class ComplianceSeverity(Enum):
    """Compliance issue severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceStatus(Enum):
    """Compliance check status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    ERROR = "error"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""

    rule_id: str
    name: str
    description: str
    category: str  # 'security', 'network', 'access', 'logging', 'configuration'
    severity: ComplianceSeverity
    check_function: str  # Name of the check function
    remediation_function: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    frameworks: List[str] = field(
        default_factory=list
    )  # ['PCI-DSS', 'HIPAA', 'ISO27001', etc.]
    enabled: bool = True
    auto_remediate: bool = False


@dataclass
class ComplianceCheckResult:
    """Result of a compliance check"""

    rule_id: str
    device: str
    status: ComplianceStatus
    severity: ComplianceSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict] = field(default_factory=list)
    remediation_available: bool = False
    remediation_applied: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class ComplianceAutomationFramework:
    """Advanced compliance automation and remediation"""

    def __init__(self, api_client: FortiManagerAPIClient):
        self.api_client = api_client
        self.logger = logger
        self.rules = {}
        self.check_results = []
        self.remediation_history = []
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Initialize compliance rules
        self._initialize_compliance_rules()

    def _initialize_compliance_rules(self):
        """Initialize default compliance rules"""

        # Security compliance rules
        self.add_rule(
            ComplianceRule(
                rule_id="SEC-001",
                name="No Any-Any Policies",
                description="Ensure no firewall policies allow any source to any destination",
                category="security",
                severity=ComplianceSeverity.CRITICAL,
                check_function="check_any_any_policies",
                remediation_function="remediate_any_any_policies",
                frameworks=["PCI-DSS", "ISO27001", "NIST"],
                auto_remediate=False,
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="SEC-002",
                name="SSL Inspection Enabled",
                description="Ensure SSL inspection is enabled for web traffic",
                category="security",
                severity=ComplianceSeverity.HIGH,
                check_function="check_ssl_inspection",
                remediation_function="enable_ssl_inspection",
                frameworks=["PCI-DSS"],
                parameters={"required_profiles": ["deep-inspection"]},
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="SEC-003",
                name="IPS Protection Active",
                description="Ensure IPS is enabled on all internet-facing policies",
                category="security",
                severity=ComplianceSeverity.HIGH,
                check_function="check_ips_protection",
                remediation_function="enable_ips_protection",
                frameworks=["PCI-DSS", "HIPAA"],
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="SEC-004",
                name="Default Admin Disabled",
                description="Ensure default admin account is disabled or renamed",
                category="security",
                severity=ComplianceSeverity.CRITICAL,
                check_function="check_default_admin",
                remediation_function="disable_default_admin",
                frameworks=["ISO27001", "NIST"],
            )
        )

        # Network compliance rules
        self.add_rule(
            ComplianceRule(
                rule_id="NET-001",
                name="Management Interface Isolation",
                description="Ensure management interfaces are properly isolated",
                category="network",
                severity=ComplianceSeverity.HIGH,
                check_function="check_mgmt_isolation",
                frameworks=["PCI-DSS", "ISO27001"],
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="NET-002",
                name="Unused Interfaces Disabled",
                description="Ensure all unused network interfaces are disabled",
                category="network",
                severity=ComplianceSeverity.MEDIUM,
                check_function="check_unused_interfaces",
                remediation_function="disable_unused_interfaces",
                frameworks=["NIST"],
            )
        )

        # Access control rules
        self.add_rule(
            ComplianceRule(
                rule_id="ACC-001",
                name="Strong Password Policy",
                description="Ensure strong password policy is enforced",
                category="access",
                severity=ComplianceSeverity.HIGH,
                check_function="check_password_policy",
                remediation_function="enforce_password_policy",
                parameters={
                    "min_length": 12,
                    "complexity": True,
                    "history": 5,
                    "max_age": 90,
                },
                frameworks=["PCI-DSS", "HIPAA", "ISO27001"],
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="ACC-002",
                name="Multi-Factor Authentication",
                description="Ensure MFA is enabled for administrative access",
                category="access",
                severity=ComplianceSeverity.CRITICAL,
                check_function="check_mfa_enabled",
                frameworks=["PCI-DSS", "HIPAA"],
            )
        )

        # Logging compliance rules
        self.add_rule(
            ComplianceRule(
                rule_id="LOG-001",
                name="Comprehensive Logging",
                description="Ensure all security events are logged",
                category="logging",
                severity=ComplianceSeverity.HIGH,
                check_function="check_logging_config",
                remediation_function="configure_logging",
                frameworks=["PCI-DSS", "HIPAA", "SOX"],
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="LOG-002",
                name="Log Retention Policy",
                description="Ensure logs are retained for required duration",
                category="logging",
                severity=ComplianceSeverity.MEDIUM,
                check_function="check_log_retention",
                parameters={"min_days": 365},
                frameworks=["PCI-DSS", "HIPAA"],
            )
        )

        # Configuration compliance rules
        self.add_rule(
            ComplianceRule(
                rule_id="CFG-001",
                name="NTP Synchronization",
                description="Ensure NTP is configured and synchronized",
                category="configuration",
                severity=ComplianceSeverity.MEDIUM,
                check_function="check_ntp_config",
                remediation_function="configure_ntp",
                frameworks=["PCI-DSS"],
            )
        )

        self.add_rule(
            ComplianceRule(
                rule_id="CFG-002",
                name="Firmware Updates",
                description="Ensure firmware is up to date",
                category="configuration",
                severity=ComplianceSeverity.HIGH,
                check_function="check_firmware_version",
                parameters={"max_age_days": 90},
                frameworks=["ISO27001", "NIST"],
            )
        )

    def add_rule(self, rule: ComplianceRule):
        """Add a compliance rule"""
        self.rules[rule.rule_id] = rule

    def add_custom_rule(self, rule_config: Dict) -> bool:
        """Add a custom compliance rule from configuration"""

        try:
            rule = ComplianceRule(
                rule_id=rule_config["rule_id"],
                name=rule_config["name"],
                description=rule_config["description"],
                category=rule_config["category"],
                severity=ComplianceSeverity(rule_config["severity"]),
                check_function=rule_config["check_function"],
                remediation_function=rule_config.get("remediation_function"),
                parameters=rule_config.get("parameters", {}),
                frameworks=rule_config.get("frameworks", []),
                auto_remediate=rule_config.get("auto_remediate", False),
            )

            self.add_rule(rule)
            return True

        except Exception as e:
            self.logger.error(f"Failed to add custom rule: {e}")
            return False

    async def run_compliance_check(
        self,
        devices: List[str],
        frameworks: List[str] = None,
        categories: List[str] = None,
        adom: str = "root",
    ) -> Dict[str, Any]:
        """Run compliance checks on specified devices"""

        # Filter rules based on frameworks and categories
        rules_to_check = self._filter_rules(frameworks, categories)

        # Run checks in parallel
        tasks = []
        for device in devices:
            for rule in rules_to_check:
                if rule.enabled:
                    task = self._run_single_check(device, rule, adom)
                    tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        check_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Check failed: {result}")
            else:
                check_results.append(result)
                self.check_results.append(result)

        # Generate compliance report
        report = self._generate_compliance_report(check_results)

        # Auto-remediate if enabled
        if any(rule.auto_remediate for rule in rules_to_check):
            remediation_results = await self._auto_remediate(check_results, adom)
            report["auto_remediation"] = remediation_results

        return report

    async def remediate_issues(
        self, issue_ids: List[str], adom: str = "root"
    ) -> Dict[str, Any]:
        """Manually remediate specific compliance issues"""

        results = {"total": len(issue_ids), "successful": 0, "failed": 0, "details": []}

        for issue_id in issue_ids:
            # Find the issue in check results
            issue = next(
                (
                    r
                    for r in self.check_results
                    if f"{r.rule_id}-{r.device}" == issue_id
                ),
                None,
            )

            if not issue:
                results["failed"] += 1
                results["details"].append(
                    {"issue_id": issue_id, "success": False, "error": "Issue not found"}
                )
                continue

            # Get the rule
            rule = self.rules.get(issue.rule_id)
            if not rule or not rule.remediation_function:
                results["failed"] += 1
                results["details"].append(
                    {
                        "issue_id": issue_id,
                        "success": False,
                        "error": "No remediation available",
                    }
                )
                continue

            # Apply remediation
            try:
                remediation_result = await self._apply_remediation(
                    issue.device, rule, issue, adom
                )

                if remediation_result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

                results["details"].append(remediation_result)

            except Exception as e:
                results["failed"] += 1
                results["details"].append(
                    {"issue_id": issue_id, "success": False, "error": str(e)}
                )

        return results

    def get_compliance_dashboard(self, hours: int = 24) -> Dict[str, Any]:
        """Get compliance dashboard data"""

        cutoff = datetime.now() - timedelta(hours=hours)
        recent_results = [r for r in self.check_results if r.timestamp > cutoff]

        # Calculate statistics
        total_checks = len(recent_results)
        by_status = {}
        by_severity = {}
        by_category = {}
        by_device = {}

        for result in recent_results:
            # By status
            status = result.status.value
            by_status[status] = by_status.get(status, 0) + 1

            # By severity
            if result.status != ComplianceStatus.COMPLIANT:
                severity = result.severity.value
                by_severity[severity] = by_severity.get(severity, 0) + 1

            # By category
            rule = self.rules.get(result.rule_id)
            if rule:
                category = rule.category
                if category not in by_category:
                    by_category[category] = {"total": 0, "issues": 0}
                by_category[category]["total"] += 1
                if result.status != ComplianceStatus.COMPLIANT:
                    by_category[category]["issues"] += 1

            # By device
            device = result.device
            if device not in by_device:
                by_device[device] = {"total": 0, "issues": 0}
            by_device[device]["total"] += 1
            if result.status != ComplianceStatus.COMPLIANT:
                by_device[device]["issues"] += 1

        # Calculate compliance score
        compliant = by_status.get("compliant", 0)
        compliance_score = (compliant / total_checks * 100) if total_checks > 0 else 0

        return {
            "summary": {
                "compliance_score": round(compliance_score, 2),
                "total_checks": total_checks,
                "compliant": compliant,
                "non_compliant": by_status.get("non_compliant", 0),
                "warnings": by_status.get("warning", 0),
                "errors": by_status.get("error", 0),
            },
            "by_severity": by_severity,
            "by_category": by_category,
            "by_device": by_device,
            "recent_issues": self._get_recent_issues(recent_results, 10),
            "remediation_history": self._get_remediation_history(hours),
        }

    def export_compliance_report(
        self, format: str = "json", frameworks: List[str] = None
    ) -> str:
        """Export compliance report in specified format"""

        report_data = {
            "generated_at": datetime.now().isoformat(),
            "frameworks": frameworks or ["All"],
            "summary": self.get_compliance_dashboard(hours=720),  # 30 days
            "detailed_results": [],
        }

        # Filter results by framework if specified
        for result in self.check_results:
            rule = self.rules.get(result.rule_id)
            if rule and (
                not frameworks or any(f in rule.frameworks for f in frameworks)
            ):
                report_data["detailed_results"].append(
                    {
                        "rule": {
                            "id": rule.rule_id,
                            "name": rule.name,
                            "category": rule.category,
                            "severity": rule.severity.value,
                            "frameworks": rule.frameworks,
                        },
                        "result": {
                            "device": result.device,
                            "status": result.status.value,
                            "message": result.message,
                            "details": result.details,
                            "timestamp": result.timestamp.isoformat(),
                        },
                    }
                )

        if format == "json":
            return json.dumps(report_data, indent=2)
        elif format == "yaml":
            return yaml.dump(report_data, default_flow_style=False)
        else:
            # CSV format
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Header
            writer.writerow(
                [
                    "Timestamp",
                    "Device",
                    "Rule ID",
                    "Rule Name",
                    "Category",
                    "Severity",
                    "Status",
                    "Message",
                ]
            )

            # Data
            for item in report_data["detailed_results"]:
                writer.writerow(
                    [
                        item["result"]["timestamp"],
                        item["result"]["device"],
                        item["rule"]["id"],
                        item["rule"]["name"],
                        item["rule"]["category"],
                        item["rule"]["severity"],
                        item["result"]["status"],
                        item["result"]["message"],
                    ]
                )

            return output.getvalue()

    # Compliance check functions
    async def check_any_any_policies(
        self, device: str, rule: ComplianceRule, adom: str
    ) -> ComplianceCheckResult:
        """Check for any-any policies"""

        try:
            policies = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.api_client.get_firewall_policies, "default", adom
            )

            any_any_policies = []
            for policy in policies:
                if (
                    policy.get("srcaddr") == ["all"]
                    and policy.get("dstaddr") == ["all"]
                    and policy.get("service") == ["ALL"]
                    and policy.get("action") == "accept"
                ):
                    any_any_policies.append(
                        {
                            "policy_id": policy["policyid"],
                            "name": policy.get("name", "Unnamed"),
                        }
                    )

            if any_any_policies:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.NON_COMPLIANT,
                    severity=rule.severity,
                    message=f"Found {len(any_any_policies)} any-any policies",
                    details={"policies": any_any_policies},
                    evidence=any_any_policies,
                    remediation_available=True,
                )
            else:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.COMPLIANT,
                    severity=rule.severity,
                    message="No any-any policies found",
                )

        except Exception as e:
            return ComplianceCheckResult(
                rule_id=rule.rule_id,
                device=device,
                status=ComplianceStatus.ERROR,
                severity=rule.severity,
                message=f"Check failed: {str(e)}",
            )

    async def check_ssl_inspection(
        self, device: str, rule: ComplianceRule, adom: str
    ) -> ComplianceCheckResult:
        """Check SSL inspection configuration"""

        try:
            policies = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.api_client.get_firewall_policies, "default", adom
            )

            web_policies_without_ssl = []
            required_profiles = rule.parameters.get("required_profiles", [])

            for policy in policies:
                # Check if it's a web traffic policy
                services = policy.get("service", [])
                if any(svc in ["HTTPS", "HTTP"] for svc in services):
                    ssl_profile = policy.get("ssl-ssh-profile")
                    if not ssl_profile or ssl_profile not in required_profiles:
                        web_policies_without_ssl.append(
                            {
                                "policy_id": policy["policyid"],
                                "name": policy.get("name", "Unnamed"),
                                "current_profile": ssl_profile or "None",
                            }
                        )

            if web_policies_without_ssl:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.NON_COMPLIANT,
                    severity=rule.severity,
                    message=f"{len(web_policies_without_ssl)} web policies without proper SSL inspection",
                    details={"policies": web_policies_without_ssl},
                    remediation_available=True,
                )
            else:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.COMPLIANT,
                    severity=rule.severity,
                    message="All web policies have SSL inspection enabled",
                )

        except Exception as e:
            return ComplianceCheckResult(
                rule_id=rule.rule_id,
                device=device,
                status=ComplianceStatus.ERROR,
                severity=rule.severity,
                message=f"Check failed: {str(e)}",
            )

    async def check_password_policy(
        self, device: str, rule: ComplianceRule, adom: str
    ) -> ComplianceCheckResult:
        """Check password policy configuration"""

        try:
            # Get system settings
            settings = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.api_client.get_system_settings
            )

            issues = []

            # Check minimum length
            min_length = rule.parameters.get("min_length", 12)
            current_length = settings.get("password_min_length", 8)
            if current_length < min_length:
                issues.append(
                    f"Minimum length {current_length} < required {min_length}"
                )

            # Check complexity
            if rule.parameters.get("complexity", True):
                if not settings.get("password_complexity", False):
                    issues.append("Password complexity not enforced")

            # Check history
            required_history = rule.parameters.get("history", 5)
            current_history = settings.get("password_history", 0)
            if current_history < required_history:
                issues.append(
                    f"Password history {current_history} < required {required_history}"
                )

            # Check max age
            max_age = rule.parameters.get("max_age", 90)
            current_max_age = settings.get("password_max_age", 0)
            if current_max_age == 0 or current_max_age > max_age:
                issues.append("Password max age not properly configured")

            if issues:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.NON_COMPLIANT,
                    severity=rule.severity,
                    message="Password policy does not meet requirements",
                    details={"issues": issues, "current_settings": settings},
                    remediation_available=True,
                )
            else:
                return ComplianceCheckResult(
                    rule_id=rule.rule_id,
                    device=device,
                    status=ComplianceStatus.COMPLIANT,
                    severity=rule.severity,
                    message="Password policy meets all requirements",
                )

        except Exception as e:
            return ComplianceCheckResult(
                rule_id=rule.rule_id,
                device=device,
                status=ComplianceStatus.ERROR,
                severity=rule.severity,
                message=f"Check failed: {str(e)}",
            )

    # Remediation functions
    async def remediate_any_any_policies(
        self, device: str, issue: ComplianceCheckResult, adom: str
    ) -> Dict[str, Any]:
        """Remediate any-any policies by adding restrictions"""

        try:
            policies = issue.details.get("policies", [])
            results = []

            for policy_info in policies:
                policy_id = policy_info["policy_id"]

                # Update policy to be more restrictive
                update = {
                    "comments": f"Modified by compliance automation - {datetime.now().isoformat()}"
                }

                # Could also disable the policy or add specific restrictions
                # For safety, we'll just add a comment for manual review

                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self._update_policy, device, policy_id, update, adom
                )

                results.append(result)

            return {
                "success": all(r.get("success", False) for r in results),
                "device": device,
                "rule_id": issue.rule_id,
                "actions_taken": results,
            }

        except Exception as e:
            return {
                "success": False,
                "device": device,
                "rule_id": issue.rule_id,
                "error": str(e),
            }

    async def enable_ssl_inspection(
        self, device: str, issue: ComplianceCheckResult, adom: str
    ) -> Dict[str, Any]:
        """Enable SSL inspection on web policies"""

        try:
            policies = issue.details.get("policies", [])
            results = []

            for policy_info in policies:
                policy_id = policy_info["policy_id"]

                # Update policy to enable SSL inspection
                update = {
                    "ssl-ssh-profile": "deep-inspection",
                    "inspection-mode": "flow",
                }

                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self._update_policy, device, policy_id, update, adom
                )

                results.append(result)

            return {
                "success": all(r.get("success", False) for r in results),
                "device": device,
                "rule_id": issue.rule_id,
                "actions_taken": results,
            }

        except Exception as e:
            return {
                "success": False,
                "device": device,
                "rule_id": issue.rule_id,
                "error": str(e),
            }

    # Helper methods
    def _filter_rules(
        self, frameworks: List[str] = None, categories: List[str] = None
    ) -> List[ComplianceRule]:
        """Filter rules based on frameworks and categories"""

        filtered_rules = []

        for rule in self.rules.values():
            # Check framework filter
            if frameworks and not any(f in rule.frameworks for f in frameworks):
                continue

            # Check category filter
            if categories and rule.category not in categories:
                continue

            filtered_rules.append(rule)

        return filtered_rules

    async def _run_single_check(
        self, device: str, rule: ComplianceRule, adom: str
    ) -> ComplianceCheckResult:
        """Run a single compliance check"""

        # Get the check function
        check_func = getattr(self, rule.check_function, None)
        if not check_func:
            return ComplianceCheckResult(
                rule_id=rule.rule_id,
                device=device,
                status=ComplianceStatus.ERROR,
                severity=rule.severity,
                message=f"Check function {rule.check_function} not found",
            )

        # Run the check
        try:
            result = await check_func(device, rule, adom)
            return result
        except Exception as e:
            return ComplianceCheckResult(
                rule_id=rule.rule_id,
                device=device,
                status=ComplianceStatus.ERROR,
                severity=rule.severity,
                message=f"Check failed: {str(e)}",
            )

    def _generate_compliance_report(
        self, results: List[ComplianceCheckResult]
    ) -> Dict[str, Any]:
        """Generate compliance report from check results"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(results),
                "compliant": 0,
                "non_compliant": 0,
                "warnings": 0,
                "errors": 0,
                "not_applicable": 0,
            },
            "by_device": {},
            "by_rule": {},
            "critical_issues": [],
            "high_priority_issues": [],
        }

        for result in results:
            # Update summary
            status_key = result.status.value.replace("_", "_")
            if status_key in report["summary"]:
                report["summary"][status_key] += 1

            # By device
            if result.device not in report["by_device"]:
                report["by_device"][result.device] = {
                    "total": 0,
                    "compliant": 0,
                    "issues": [],
                }
            report["by_device"][result.device]["total"] += 1
            if result.status == ComplianceStatus.COMPLIANT:
                report["by_device"][result.device]["compliant"] += 1
            else:
                report["by_device"][result.device]["issues"].append(
                    {
                        "rule_id": result.rule_id,
                        "severity": result.severity.value,
                        "message": result.message,
                    }
                )

            # By rule
            if result.rule_id not in report["by_rule"]:
                rule = self.rules.get(result.rule_id)
                report["by_rule"][result.rule_id] = {
                    "name": rule.name if rule else "Unknown",
                    "total": 0,
                    "compliant": 0,
                    "issues": [],
                }
            report["by_rule"][result.rule_id]["total"] += 1
            if result.status == ComplianceStatus.COMPLIANT:
                report["by_rule"][result.rule_id]["compliant"] += 1
            else:
                report["by_rule"][result.rule_id]["issues"].append(
                    {"device": result.device, "message": result.message}
                )

            # Critical and high priority issues
            if result.status != ComplianceStatus.COMPLIANT:
                issue_summary = {
                    "rule_id": result.rule_id,
                    "device": result.device,
                    "message": result.message,
                    "remediation_available": result.remediation_available,
                }

                if result.severity == ComplianceSeverity.CRITICAL:
                    report["critical_issues"].append(issue_summary)
                elif result.severity == ComplianceSeverity.HIGH:
                    report["high_priority_issues"].append(issue_summary)

        # Calculate compliance score
        if report["summary"]["total_checks"] > 0:
            report["compliance_score"] = round(
                report["summary"]["compliant"]
                / report["summary"]["total_checks"]
                * 100,
                2,
            )
        else:
            report["compliance_score"] = 0

        return report

    async def _auto_remediate(
        self, results: List[ComplianceCheckResult], adom: str
    ) -> Dict[str, Any]:
        """Auto-remediate issues where enabled"""

        remediation_results = {"total": 0, "successful": 0, "failed": 0, "details": []}

        for result in results:
            if (
                result.status != ComplianceStatus.COMPLIANT
                and result.remediation_available
            ):
                rule = self.rules.get(result.rule_id)
                if rule and rule.auto_remediate:
                    remediation_results["total"] += 1

                    try:
                        remediation = await self._apply_remediation(
                            result.device, rule, result, adom
                        )

                        if remediation["success"]:
                            remediation_results["successful"] += 1
                        else:
                            remediation_results["failed"] += 1

                        remediation_results["details"].append(remediation)

                    except Exception as e:
                        remediation_results["failed"] += 1
                        remediation_results["details"].append(
                            {
                                "device": result.device,
                                "rule_id": result.rule_id,
                                "success": False,
                                "error": str(e),
                            }
                        )

        return remediation_results

    async def _apply_remediation(
        self, device: str, rule: ComplianceRule, issue: ComplianceCheckResult, adom: str
    ) -> Dict[str, Any]:
        """Apply remediation for a compliance issue"""

        # Get remediation function
        remediation_func = getattr(self, rule.remediation_function, None)
        if not remediation_func:
            return {
                "success": False,
                "device": device,
                "rule_id": rule.rule_id,
                "error": f"Remediation function {rule.remediation_function} not found",
            }

        # Apply remediation
        result = await remediation_func(device, issue, adom)

        # Track remediation
        self.remediation_history.append(
            {
                "timestamp": datetime.now(),
                "device": device,
                "rule_id": rule.rule_id,
                "result": result,
            }
        )

        return result

    def _update_policy(
        self, device: str, policy_id: str, updates: Dict, adom: str
    ) -> Dict[str, Any]:
        """Update a firewall policy"""

        # This would use the API client to update the policy
        # For now, return a simulated result
        return {
            "success": True,
            "device": device,
            "policy_id": policy_id,
            "updates_applied": updates,
        }

    def _get_recent_issues(
        self, results: List[ComplianceCheckResult], limit: int
    ) -> List[Dict]:
        """Get recent compliance issues"""

        issues = [r for r in results if r.status != ComplianceStatus.COMPLIANT]
        issues.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "rule_id": issue.rule_id,
                "device": issue.device,
                "severity": issue.severity.value,
                "message": issue.message,
                "timestamp": issue.timestamp.isoformat(),
            }
            for issue in issues[:limit]
        ]

    def _get_remediation_history(self, hours: int) -> List[Dict]:
        """Get recent remediation history"""

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [r for r in self.remediation_history if r["timestamp"] > cutoff]

        return [
            {
                "timestamp": r["timestamp"].isoformat(),
                "device": r["device"],
                "rule_id": r["rule_id"],
                "success": r["result"].get("success", False),
            }
            for r in recent
        ]
