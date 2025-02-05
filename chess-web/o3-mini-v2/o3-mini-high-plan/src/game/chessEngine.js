import { parseFEN, generateFEN } from "./fen.js";
import config from "../config.js";

// Our chess engine maintains an internal board state.
let boardState = [];
let boardSize = config.boardSize || 8;

export default {
  init() {
    boardState = parseFEN();
  },

  getBoard() {
    return boardState;
  },

  getBoardSize() {
    return boardSize;
  },

  getPiece(row, col) {
    return boardState[row][col];
  },

  // A VERY minimal move validation
  movePiece(from, to) {
    const piece = boardState[from.row][from.col];
    if (!piece) {
      return { success: false, message: "No piece at selected square" };
    }
    // For prototype: allow move if destination is empty or has an opponent's piece.
    // (Does not check real chess moves.)
    const destinationPiece = boardState[to.row][to.col];
    if (destinationPiece && destinationPiece[0] === piece[0]) {
      return { success: false, message: "Cannot capture own piece" };
    }
    // Update board state (no special moves implemented)
    boardState[to.row][to.col] = piece;
    boardState[from.row][from.col] = "";
    // In a complete implementation, update move history with correct notation.
    const moveNotation = `${piece}:${from.row},${from.col} -> ${to.row},${to.col}`;
    return { success: true, moveNotation };
  },
};
