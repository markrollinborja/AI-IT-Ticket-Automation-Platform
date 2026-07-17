# Explicit re-export syntax (`as` aliasing itself) tells the linter these
# imports are intentional, not leftover - other modules import models via
# this package.
from app.models.ticket import Ticket as Ticket
from app.models.workflow_run import WorkflowRun as WorkflowRun
