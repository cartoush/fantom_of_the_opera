class AlphaBeta:
    def __init__(self, root):
        self.root = root
        return

    def alpha_beta_search(self, node):
        raise NotImplementedError()

    def max_value(self, node, alpha, beta):
        if self.isTerminal(node):
            return self.getUtility(node)
        infinity = float('inf')
        value = -infinity

        successors = self.getSuccessors(node)
        for state in successors:
            value = max(value, self.min_value(state, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, node, alpha, beta):
        if self.isTerminal(node):
            return self.getUtility(node)
        infinity = float('inf')
        value = infinity

        successors = self.getSuccessors(node)
        for state in successors:
            value = min(value, self.max_value(state, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    def getSuccessors(self, node):
        assert node is not None
        return node.child

    def isTerminal(self, node):
        assert node is not None
        return len(node.child) == 0

    def getUtility(self, node):
        assert node is not None
        return node.score