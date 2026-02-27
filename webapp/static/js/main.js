document.addEventListener("DOMContentLoaded", function () {
  // Listo para inicializar componentes si se requieren
});

async function addToCart(productId) {
  try {
    const qtyInput = document.querySelector(`#qty-${productId}`);
    const quantity = qtyInput ? parseInt(qtyInput.value || "1", 10) : 1;

    const res = await fetch(`/add-to-cart/${productId}`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ quantity: String(quantity) }),
    });

    if (!res.ok) {
      console.error("No se pudo agregar al carrito");
    } else {
      window.location.href = "/cart";
    }
  } catch (e) {
    console.error(e);
  }
}

function updateCartQuantity(itemId, quantity) {
  // (opcional) para implementar luego si haces endpoints AJAX
  console.log("updateCartQuantity", itemId, quantity);
}

function removeFromCart(itemId) {
  // (opcional) para implementar luego si haces endpoints AJAX
  console.log("removeFromCart", itemId);
}
