import { ChessGame } from "./game/chessEngine.js";
import { BoardUI } from "./components/Board.js";

const game = new ChessGame();
const board = new BoardUI(game);

document.getElementById("newGame").addEventListener("click", () => {
  game.resetGame();
  board.render();
});

document.getElementById("undoMove").addEventListener("click", () => {
  game.undoMove();
  board.render();
});
