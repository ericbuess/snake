export class Board {
  constructor(element, game) {
    this.element = element;
    this.game = game;
    this.selectedSquare = null;
    this.init();
    // Add move history element
    this.historyElement = document.createElement("div");
    this.historyElement.className = "move-history";
    this.element.parentElement.appendChild(this.historyElement);
  }

  init() {
    this.element.innerHTML = "";
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const square = document.createElement("div");
        square.className = `square ${(row + col) % 2 ? "dark" : "light"}`;
        square.dataset.row = row;
        square.dataset.col = col;
        square.addEventListener("click", (e) => this.handleSquareClick(e));
        this.element.appendChild(square);
      }
    }
    this.render();
  }

  render() {
    const squares = this.element.getElementsByClassName("square");
    for (let square of squares) {
      const row = parseInt(square.dataset.row);
      const col = parseInt(square.dataset.col);
      const piece = this.game.getPiece(row, col);

      square.innerHTML = piece ? this.createPieceHTML(piece) : "";
      square.classList.remove("selected", "valid-move");
    }
  }

  createPieceHTML(piece) {
    const color = piece.color === "white" ? "w" : "b";
    const type = piece.type.charAt(0).toLowerCase();
    return `<div class="piece">${color}${type}</div>`;
  }

  handleSquareClick(e) {
    const square = e.currentTarget;
    const row = parseInt(square.dataset.row);
    const col = parseInt(square.dataset.col);

    if (this.selectedSquare) {
      const startRow = parseInt(this.selectedSquare.dataset.row);
      const startCol = parseInt(this.selectedSquare.dataset.col);

      if (this.game.makeMove(startRow, startCol, row, col)) {
        this.render();
        this.updateMoveHistory();
      }

      this.clearSelection();
    } else if (this.game.getPiece(row, col)) {
      this.selectedSquare = square;
      square.classList.add("selected");
      this.showValidMoves(row, col);
    }
  }

  showValidMoves(row, col) {
    const validMoves = this.game.getValidMoves(row, col);
    validMoves.forEach(([r, c]) => {
      const square = this.element.children[r * 8 + c];
      square.classList.add("valid-move");
    });
  }

  clearSelection() {
    this.selectedSquare = null;
    const squares = this.element.getElementsByClassName("square");
    for (let square of squares) {
      square.classList.remove("selected", "valid-move");
    }
  }

  updateMoveHistory() {
    const history = this.game.getMoveHistory();
    const lastMove = history[history.length - 1];
    if (!lastMove) return;

    const moveText = document.createElement("div");
    moveText.className = "move";

    const from = `${String.fromCharCode(97 + lastMove.from.col)}${
      8 - lastMove.from.row
    }`;
    const to = `${String.fromCharCode(97 + lastMove.to.col)}${
      8 - lastMove.to.row
    }`;

    moveText.textContent = `${history.length}. ${lastMove.piece.color} ${
      lastMove.piece.type
    } ${from}-${to}${lastMove.captured ? " x" : ""}`;

    this.historyElement.appendChild(moveText);
  }
}
