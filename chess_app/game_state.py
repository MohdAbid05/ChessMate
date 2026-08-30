import chess

PIECE_VALUE = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}


class GameState:
    def __init__(self):
        self.move_history = []
        self.captured_by_white = []
        self.captured_by_black = []
        self._capture_target_log = []

    def record_move(self, board_before, move, san):
        captured_piece = None
        if board_before.is_capture(move):
            if board_before.is_en_passant(move):
                captured_piece = chess.Piece(chess.PAWN, not board_before.turn)
            else:
                captured_piece = board_before.piece_at(move.to_square)

        self.move_history.append(san)
        if captured_piece:
            symbol = captured_piece.symbol().upper()
            if captured_piece.color == chess.WHITE:
                self.captured_by_black.append(symbol)
                self._capture_target_log.append("black")
            else:
                self.captured_by_white.append(symbol)
                self._capture_target_log.append("white")
        else:
            self._capture_target_log.append(None)

    def undo_last(self):
        if not self.move_history:
            return
        self.move_history.pop()
        target = self._capture_target_log.pop()
        if target == "white":
            self.captured_by_white.pop()
        elif target == "black":
            self.captured_by_black.pop()

    def material_diff(self):
        return sum(PIECE_VALUE[p] for p in self.captured_by_white) - sum(PIECE_VALUE[p] for p in self.captured_by_black)
