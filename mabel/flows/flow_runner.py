import uuid
from ..utils import entropy
from ..operators.internals.trace_blocks import TraceBlocks


class FlowRunner():

    def __init__(self, flow):
        self.flow = flow

    def run(
            self,
            data: dict = {},
            context: dict = {},
            trace_sample_rate: float = 1/1000):
        """
        Create a `run` of a flow and execute with a specific data object.

        Parameters:
            data: dictionary, any (optional)
                The data the flow is to process, opinionated to be a dictionary
                however, any data type is accepted.
            context: dictionary (optional)
                Additional information to support the processing of the data
            trace_sample_rate: float (optional)
                The sample for for to emit trace messages for, default is 
                1/1000.
        """
        # create a uuid for the message if it doesn't already have one
        if not context.get('uuid'):
            context['uuid'] = str(uuid.uuid4())

        # create a tracer for the message
        if not context.get('execution_trace'):
            context['execution_trace'] = TraceBlocks(uuid=context['uuid'])

        # if trace hasn't been explicitly set - randomly select based on a sample rate
        if not context.get('trace') and trace_sample_rate:
            context['trace'] = entropy.random_range(1, round(1 / trace_sample_rate)) == 1  # nosec

        # start the flow, walk from the nodes with no incoming links
        for operator_name in self.flow.get_entry_points():
            self._inner_runner(operator_name=operator_name, data=data, context=context)

        # if being traced, send the trace to the trace writer
        if context.get('trace', False) and hasattr(self, 'trace_writer'):
            self.trace_writer(context['execution_trace'], id_=str(context.get('uuid')))  #type:ignore


    def _inner_runner(
            self,
            operator_name: str = None,
            data: dict = {},
            context: dict = None):
        """
        Walk the dag/flow by:
        - Getting the function of the current node
        - Execute the function, wrapped in the base class
        - Find the next step by finding outgoing edges
        - Call this method for the next step
        """
        if not context:
            context = {}

        operator = self.flow.get_operator(operator_name)
        if operator is None:
            raise Exception(F"Invalid Flow - Operator {operator_name} is invalid")
        if not hasattr(operator, "error_writer") and hasattr(self, "error_writer"):
            operator.error_writer = self.error_writer  # type:ignore
        out_going_links = self.flow.get_outgoing_links(operator_name)

        outcome = operator(data, context)

        if outcome:
            if not type(outcome).__name__ in ["generator", "list"]:
                outcome_data, outcome_context = outcome
                outcome = [(outcome_data, outcome_context)]
            for outcome_data, outcome_context in outcome:
                for operator_name in out_going_links:
                    self._inner_runner(operator_name=operator_name, data=outcome_data, context=outcome_context.copy())
