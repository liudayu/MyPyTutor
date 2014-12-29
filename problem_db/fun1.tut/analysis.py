class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.count = 1
        self.seen_inc = []
        self.seen_double = []

    def visit_Call(self, node):
        super().visit_Call(node)

        func_name = TutorialNodeVisitor.identifier(node.func)
        if func_name == 'double':
            self.seen_double.append(self.count)
            self.count += 1
        elif func_name == 'increment':
            self.seen_inc.append(self.count)
            self.count += 1


class Fun1Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.seen_double:
            self.add_error("You need to use the double function in your single assignment statement")
        if not self.visitor.seen_inc:
            self.add_error("You need to use the increment function in your single assignment statement")

        if len(self.visitor.seen_double) > 1:
            self.add_error("You only need to use double once")
        if len(self.visitor.seen_inc) > 1:
            self.add_error("You only need to use increment once")

        if self.visitor.seen_double and self.visitor.seen_inc \
                and self.visitor.seen_double[0] > self.visitor.seen_inc[0]:
            self.add_error("You should be using increment inside the use of double")


ANALYSER = Fun1Analyser(CodeVisitor)