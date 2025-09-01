function showContent(type) {
  const content = document.getElementById("content");
  if (type === "secuencial") {
    content.innerHTML =
      "<h2>Búsqueda Secuencial</h2><p>Aquí irá el simulador de búsqueda secuencial.</p>";
  } else if (type === "binaria") {
    content.innerHTML =
      "<h2>Búsqueda Binaria</h2><p>Aquí irá el simulador de búsqueda binaria.</p>";
  } else if (type === "hashing") {
    content.innerHTML =
      "<h2>Hashing</h2><p>Aquí irá el simulador de hashing con su tabla.</p>";
  }
}
