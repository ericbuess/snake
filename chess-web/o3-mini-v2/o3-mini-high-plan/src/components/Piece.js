// For this prototype we are rendering the piece as simple text.
// In a future update, you may use an <img> tag with assets.
export default function Piece(pieceCode) {
  const pieceEl = document.createElement("div");
  pieceEl.classList.add("piece");
  pieceEl.innerText = pieceCode; // e.g., "wP" for white pawn
  return pieceEl;
}
