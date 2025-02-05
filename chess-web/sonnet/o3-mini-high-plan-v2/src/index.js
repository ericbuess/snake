import { Board } from "./components/Board.js";
import { ChessGame } from "./game/ChessGame.js";

const game = new ChessGame();
const board = new Board(document.getElementById("board"), game);

document.getElementById("newGame").addEventListener("click", () => {
  game.reset();
  board.render();
});
