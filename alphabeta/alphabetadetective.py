from alphabeta import AlphaBeta

class AlphaBetaDetective(AlphaBeta):
  
    def __init__(self, root):
        super.__init__(root)
        return

    def alpha_beta_search(self, node):
        infinity = float('inf')
        best_val = infinity
        alpha = infinity

        successors = self.getSuccessors(node)
        best_state = None
        for state in successors:
            value = self.max_value(state, best_val, alpha)
            if value < best_val:
                best_val = value
                best_state = state
        return best_state