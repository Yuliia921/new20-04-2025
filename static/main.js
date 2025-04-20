
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("generatePdfBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    const form = document.getElementById("ultrasoundForm");
    const inputs = form.querySelectorAll("input, textarea");
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    inputs.forEach((input, index) => {
      const label = input.previousElementSibling?.textContent || input.name;
      const value = input.value;
      doc.text(`${label}: ${value}`, 10, 10 + index * 10);
    });

    doc.save("protocol.pdf");
  });
});
