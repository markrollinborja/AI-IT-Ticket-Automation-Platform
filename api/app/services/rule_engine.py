from app.schemas.ticket import TicketCreate, TicketPriority


class RuleEngine:
    def determine_priority(self, ticket: TicketCreate) -> TicketPriority:
        text = f"{ticket.title} {ticket.description}".lower()

        if "production down" in text or "system down" in text or "outage" in text:
            return TicketPriority.CRITICAL

        if "cannot login" in text or "vpn" in text or "access denied" in text:
            return TicketPriority.HIGH

        if "password reset" in text or "reset password" in text:
            return TicketPriority.LOW

        return TicketPriority.MEDIUM


rule_engine = RuleEngine()