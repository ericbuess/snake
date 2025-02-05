export default function Square({ row, col, clickHandler }) {
  const square = document.createElement("div");
  square.classList.add("square");
  // Alternate square color based on coordinates
  if ((row + col) % 2 === 0) {
    square.classList.add("light-square");
  } else {
    square.classList.add("dark-square");
  }
  square.addEventListener("click", clickHandler);
  return square;
}
