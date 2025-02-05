export default class MoveHistory {
  constructor() {
    this.moves = [];
  }

  addMove(moveNotation) {
    this.moves.push(moveNotation);
    // Re-render history if needed
    if (this.listEl) {
      const moveEl = document.createElement("li");
      moveEl.innerText = moveNotation;
      this.listEl.appendChild(moveEl);
    }
  }

  render() {
    const container = document.createElement("div");
    container.classList.add("move-history");
    const title = document.createElement("h3");
    title.innerText = "Move History";
    container.appendChild(title);
    this.listEl = document.createElement("ul");
    container.appendChild(this.listEl);
    return container;
  }
}
