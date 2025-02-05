import Square from "./Square.js";
import MoveHistory from "./MoveHistory.js";
import ChessEngine from "../game/chessEngine.js";
import { indexToAlgebraic } from "../utils/coords.js";

export default class Board {
  constructor(rootElement) {
    this.root = rootElement;
    this.selectedSquare = null;
    this.moveHistoryComponent = new MoveHistory();
  }

  render() {
    // Create a board container
    const boardContainer = document.createElement("div");
    boardContainer.classList.add("board-container");

    const boardSize = ChessEngine.getBoardSize();
    // Render an 8x8 board
    for (let row = 0; row < boardSize; row++) {
      const rowDiv = document.createElement("div");
      rowDiv.classList.add("board-row");
      for (let col = 0; col < boardSize; col++) {
        const square = Square({
          row,
          col,
          clickHandler: this.onSquareClick.bind(this),
        });
        // Set an id using algebraic notation
        square.id = indexToAlgebraic(row, col);
        rowDiv.appendChild(square);
      }
      boardContainer.appendChild(rowDiv);
    }
    this.root.appendChild(boardContainer);
    this.root.appendChild(this.moveHistoryComponent.render());
    this.refreshBoard();
  }

  refreshBoard() {
    // Update board squares with pieces from the engine state
    const boardState = ChessEngine.getBoard();
    for (let row = 0; row < boardState.length; row++) {
      for (let col = 0; col < boardState[row].length; col++) {
        const coord = indexToAlgebraic(row, col);
        const squareEl = document.getElementById(coord);
        squareEl.innerHTML = ""; // clear previous content
        if (boardState[row][col] !== "") {
          // Render piece inside the square
          const pieceEl = document.createElement("div");
          pieceEl.classList.add("piece");
          pieceEl.innerText = boardState[row][col]; // simple text for prototype
          squareEl.appendChild(pieceEl);
        }
      }
    }
  }

  onSquareClick(e) {
    const squareId = e.currentTarget.id;
    const { col, row } = this.getRowColFromId(squareId);
    if (!this.selectedSquare) {
      // select piece if present at clicked square
      const piece = ChessEngine.getPiece(row, col);
      if (piece !== "") {
        this.selectedSquare = { row, col };
        e.currentTarget.classList.add("selected");
      }
    } else {
      // Attempt to move
      const from = this.selectedSquare;
      const to = { row, col };

      const moveResult = ChessEngine.movePiece(from, to);
      if (moveResult.success) {
        this.moveHistoryComponent.addMove(moveResult.moveNotation);
        this.clearSelection();
        this.refreshBoard();
      } else {
        alert(moveResult.message || "Illegal move");
        this.clearSelection();
      }
    }
  }

  clearSelection() {
    // Remove 'selected' class from all squares
    document
      .querySelectorAll(".selected")
      .forEach((el) => el.classList.remove("selected"));
    this.selectedSquare = null;
  }

  getRowColFromId(id) {
    // id is in algebraic notation. Convert back using indexToAlgebraic logic.
    const files = "abcdefgh";
    const ranks = "87654321";
    return {
      col: files.indexOf(id[0]),
      row: ranks.indexOf(id[1]),
    };
  }
}
