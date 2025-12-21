"""
Human Escalation Rules for Jarvis
Defines when the system should pause and ask for human input.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum


class EscalationReason(Enum):
    MISSING_API_KEY = "missing_api_key"
    CONSECUTIVE_FAILURES = "consecutive_failures"
    UNCLEAR_REQUIREMENTS = "unclear_requirements"
    EXTERNAL_SERVICE_DOWN = "external_service_down"
    COST_THRESHOLD = "cost_threshold"
    PERMISSION_REQUIRED = "permission_required"
    SECURITY_CONCERN = "security_concern"
    AMBIGUOUS_INSTRUCTION = "ambiguous_instruction"
    DESTRUCTIVE_ACTION = "destructive_action"


@dataclass
class EscalationRule:
    reason: EscalationReason
    condition: Callable[..., bool]
    message_template: str
    priority: int  # 1 = highest


class EscalationManager:
    """
    Manages human escalation rules and triggers.
    
    When any rule triggers, execution pauses and asks for human input.
    """
    
    # Configurable thresholds
    MAX_CONSECUTIVE_FAILURES = 3
    MAX_COST_DOLLARS = 10.0
    
    def __init__(self):
        self.failure_count = 0
        self.total_cost = 0.0
        self.escalation_history = []
        self._setup_rules()
    
    def _setup_rules(self):
        """Define all escalation rules."""
        self.rules: List[EscalationRule] = [
            EscalationRule(
                reason=EscalationReason.MISSING_API_KEY,
                condition=self._check_missing_api_key,
                message_template="Missing API key: {key_name}. Please set the environment variable.",
                priority=1
            ),
            EscalationRule(
                reason=EscalationReason.CONSECUTIVE_FAILURES,
                condition=self._check_consecutive_failures,
                message_template="Failed {count} times in a row. Last error: {error}",
                priority=1
            ),
            EscalationRule(
                reason=EscalationReason.UNCLEAR_REQUIREMENTS,
                condition=self._check_unclear_requirements,
                message_template="Requirements unclear: {ambiguity}. Please clarify.",
                priority=2
            ),
            EscalationRule(
                reason=EscalationReason.EXTERNAL_SERVICE_DOWN,
                condition=self._check_service_down,
                message_template="External service unavailable: {service}. Retry later or provide alternative.",
                priority=1
            ),
            EscalationRule(
                reason=EscalationReason.COST_THRESHOLD,
                condition=self._check_cost_threshold,
                message_template="Estimated cost ${cost:.2f} exceeds threshold ${threshold:.2f}. Proceed?",
                priority=2
            ),
            EscalationRule(
                reason=EscalationReason.DESTRUCTIVE_ACTION,
                condition=self._check_destructive_action,
                message_template="About to perform destructive action: {action}. Confirm?",
                priority=1
            ),
        ]
    
    def should_escalate(self, context: Dict) -> Optional[Dict]:
        """
        Check all rules and return escalation info if any trigger.
        
        Args:
            context: Current execution context with keys like:
                - task: Current task description
                - error: Last error if any
                - api_keys_needed: List of required API keys
                - estimated_cost: Estimated cost in dollars
                - action: Current action being attempted
        
        Returns:
            Dict with escalation info or None if no escalation needed
        """
        for rule in sorted(self.rules, key=lambda r: r.priority):
            if rule.condition(context):
                escalation = {
                    "reason": rule.reason.value,
                    "message": self._format_message(rule.message_template, context),
                    "priority": rule.priority,
                    "context": context
                }
                self.escalation_history.append(escalation)
                return escalation
        
        return None
    
    def record_failure(self, error: str):
        """Record a failure for consecutive failure tracking."""
        self.failure_count += 1
    
    def record_success(self):
        """Reset failure count on success."""
        self.failure_count = 0
    
    def record_cost(self, cost: float):
        """Track accumulated cost."""
        self.total_cost += cost
    
    def reset(self):
        """Reset all counters."""
        self.failure_count = 0
        self.total_cost = 0.0
    
    # === Rule Condition Checkers ===
    
    def _check_missing_api_key(self, context: Dict) -> bool:
        """Check if required API keys are missing."""
        import os
        needed = context.get("api_keys_needed", [])
        for key in needed:
            if not os.environ.get(key):
                context["key_name"] = key
                return True
        return False
    
    def _check_consecutive_failures(self, context: Dict) -> bool:
        """Check if too many consecutive failures."""
        if self.failure_count >= self.MAX_CONSECUTIVE_FAILURES:
            context["count"] = self.failure_count
            context["error"] = context.get("error", "Unknown error")
            return True
        return False
    
    def _check_unclear_requirements(self, context: Dict) -> bool:
        """Check if requirements are ambiguous."""
        task = context.get("task", "").lower()
        
        ambiguous_phrases = [
            "not sure", "maybe", "something like", "etc", "whatever",
            "you decide", "your choice", "as needed", "if possible"
        ]
        
        for phrase in ambiguous_phrases:
            if phrase in task:
                context["ambiguity"] = phrase
                return True
        
        return False
    
    def _check_service_down(self, context: Dict) -> bool:
        """Check if external service is down."""
        return context.get("service_down", False)
    
    def _check_cost_threshold(self, context: Dict) -> bool:
        """Check if cost exceeds threshold."""
        estimated = context.get("estimated_cost", 0)
        if estimated > self.MAX_COST_DOLLARS:
            context["cost"] = estimated
            context["threshold"] = self.MAX_COST_DOLLARS
            return True
        return False
    
    def _check_destructive_action(self, context: Dict) -> bool:
        """Check if action is destructive and needs confirmation."""
        action = context.get("action", "").lower()
        
        destructive_keywords = [
            "delete", "remove", "drop", "truncate", "destroy",
            "wipe", "clear all", "reset", "overwrite", "replace all"
        ]
        
        for keyword in destructive_keywords:
            if keyword in action:
                return True
        
        return False
    
    def _format_message(self, template: str, context: Dict) -> str:
        """Format message template with context values."""
        try:
            return template.format(**context)
        except KeyError:
            return template


# Singleton
escalation_manager = EscalationManager()


def should_escalate(context: Dict) -> Optional[Dict]:
    """Convenience function to check escalation."""
    return escalation_manager.should_escalate(context)
