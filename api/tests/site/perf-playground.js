window.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("images-grid");
  const heavyPayloadNode = document.getElementById("heavyPayload");

  if (grid) {
    for (let i = 0; i < 140; i += 1) {
      const img = document.createElement("img");
      img.alt = `synthetic image ${i}`;
      img.src = `./pixel-ok.svg?img=${i}&cacheBust=${Date.now()}`;
      grid.appendChild(img);
    }
  }

  for (let i = 0; i < 120; i += 1) {
    fetch(`./pixel-ok.svg?fetch=${i}&cacheBust=${Date.now()}`).catch(() => {});
  }

  if (heavyPayloadNode) {
    const block = "X".repeat(1024);
    heavyPayloadNode.textContent = Array.from({ length: 3500 }, () => block).join("|");
  }
});
