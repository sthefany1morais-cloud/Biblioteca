const API = "/livros";
let books = [];

const $ = (id) => document.getElementById(id);

function showAlert(message, type = "success") {
  const box = $("alertBox");
  box.className = `alert alert-${type}`;
  box.textContent = message;
  box.hidden = false;
  window.clearTimeout(showAlert.timer);
  showAlert.timer = window.setTimeout(() => box.hidden = true, 4500);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.erro || data.mensagem || `Erro HTTP ${response.status}`);
  }

  return data;
}

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[char]));
}

function renderBooks() {
  const term = $("searchInput").value.trim().toLocaleLowerCase("pt-BR");

  const filtered = books.filter(book =>
    [book.titulo, book.autor, book.genero, book.ano]
      .some(value => String(value ?? "").toLocaleLowerCase("pt-BR").includes(term))
  );

  $("totalBooks").textContent = books.length;
  $("availableBooks").textContent = books.filter(book => book.disponivel !== false).length;
  $("loanedBooks").textContent = books.filter(book => book.disponivel === false).length;

  $("recordsCount").textContent =
    `${filtered.length} ${filtered.length === 1 ? "registro" : "registros"}`;

  $("tableSummary").textContent = `Exibindo ${filtered.length} de ${books.length} livros`;

  if (!filtered.length) {
    $("booksTable").innerHTML = `
      <tr>
        <td colspan="6" class="empty-state">
          <span class="empty-icon"><i class="fa-solid fa-book-open"></i></span>
          <strong>${term ? "Nenhum resultado encontrado" : "Seu acervo ainda está vazio"}</strong>
          <span>${term ? "Tente buscar com outros termos." : "Adicione o primeiro livro para começar."}</span>
          ${term ? "" : '<button class="btn btn-primary btn-small" onclick="openModal()">Adicionar primeiro livro</button>'}
        </td>
      </tr>`;
    return;
  }

  $("booksTable").innerHTML = filtered.map(book => {
    const id = safeText(book._id);
    const available = book.disponivel !== false;
    const initials = String(book.titulo || "L").trim().slice(0, 1).toUpperCase();

    return `
      <tr>
        <td>
          <div class="book-cell">
            <span class="book-cover">${safeText(initials)}</span>
            <span class="book-title">${safeText(book.titulo)}</span>
          </div>
        </td>
        <td>${safeText(book.autor)}</td>
        <td>${safeText(book.ano)}</td>
        <td><span class="genre-pill">${safeText(book.genero)}</span></td>
        <td>
          <span class="status ${available ? "status-available" : "status-loaned"}">
            <span></span>${available ? "Disponível" : "Emprestado"}
          </span>
        </td>
        <td>
          <div class="row-actions">
            <button class="icon-button edit-button" title="Editar livro"
              aria-label="Editar ${safeText(book.titulo)}"
              onclick="editBook('${id}')">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button class="icon-button delete-button" title="Excluir livro"
              aria-label="Excluir ${safeText(book.titulo)}"
              onclick="deleteBook('${id}')">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>`;
  }).join("");
}

async function loadBooks() {
  $("booksTable").innerHTML = `
    <tr>
      <td colspan="6" class="table-message">
        <span class="spinner"></span> Carregando acervo...
      </td>
    </tr>`;

  try {
    const result = await apiRequest(API);
    books = Array.isArray(result) ? result : [];
    renderBooks();
  } catch (error) {
    $("booksTable").innerHTML = `
      <tr>
        <td colspan="6" class="table-message error-text">
          <i class="fa-solid fa-triangle-exclamation"></i>
          Não foi possível carregar os livros. ${safeText(error.message)}
          <br><small>Confira se o Flask e o MongoDB estão em execução.</small>
        </td>
      </tr>`;

    $("totalBooks").textContent = "—";
    $("availableBooks").textContent = "—";
    $("loanedBooks").textContent = "—";
  }
}

function openModal(book = null) {
  $("bookForm").reset();
  $("formError").hidden = true;
  $("bookId").value = book?._id || "";

  $("modalTitle").textContent = book ? "Editar livro" : "Adicionar livro";

  $("saveBtn").innerHTML = book
    ? '<i class="fa-solid fa-floppy-disk"></i> Salvar alterações'
    : '<i class="fa-solid fa-floppy-disk"></i> Salvar livro';

  $("title").value = book?.titulo || "";
  $("author").value = book?.autor || "";
  $("year").value = book?.ano ?? "";
  $("genre").value = book?.genero || "";
  $("available").checked = book ? book.disponivel !== false : true;

  $("bookModal").hidden = false;
  document.body.classList.add("modal-open");

  setTimeout(() => $("title").focus(), 50);
}

function closeModal() {
  $("bookModal").hidden = true;
  document.body.classList.remove("modal-open");
}

function editBook(id) {
  const book = books.find(item => item._id === id);
  if (book) openModal(book);
}

async function deleteBook(id) {
  const book = books.find(item => item._id === id);

  if (!book || !confirm(`Deseja realmente excluir "${book.titulo}"? Esta ação não pode ser desfeita.`)) {
    return;
  }

  try {
    await apiRequest(`${API}/${encodeURIComponent(id)}`, {
      method: "DELETE"
    });

    showAlert("Livro excluído com sucesso.");
    await loadBooks();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

$("bookForm").addEventListener("submit", async event => {
  event.preventDefault();

  const id = $("bookId").value;

  const payload = {
    titulo: $("title").value.trim(),
    autor: $("author").value.trim(),
    ano: Number($("year").value),
    genero: $("genre").value.trim(),
    disponivel: $("available").checked
  };

  if (
    !payload.titulo ||
    !payload.autor ||
    !payload.genero ||
    !Number.isInteger(payload.ano) ||
    payload.ano < 0 ||
    payload.ano > 2100
  ) {
    $("formError").textContent = "Confira os campos. O ano deve ser um número inteiro válido.";
    $("formError").hidden = false;
    return;
  }

  const button = $("saveBtn");
  button.disabled = true;
  button.innerHTML = '<span class="spinner spinner-light"></span> Salvando...';

  try {
    await apiRequest(id ? `${API}/${encodeURIComponent(id)}` : API, {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(payload)
    });

    closeModal();

    showAlert(
      id ? "Livro atualizado com sucesso." : "Livro cadastrado com sucesso."
    );

    await loadBooks();

  } catch (error) {
    $("formError").textContent = error.message;
    $("formError").hidden = false;

  } finally {
    button.disabled = false;

    button.innerHTML = id
      ? '<i class="fa-solid fa-floppy-disk"></i> Salvar alterações'
      : '<i class="fa-solid fa-floppy-disk"></i> Salvar livro';
  }
});

$("addBookBtn").addEventListener("click", () => openModal());
$("navAdd").addEventListener("click", () => openModal());
$("closeModal").addEventListener("click", closeModal);
$("cancelModal").addEventListener("click", closeModal);
$("refreshBtn").addEventListener("click", loadBooks);
$("searchInput").addEventListener("input", renderBooks);

$("bookModal").addEventListener("click", event => {
  if (event.target === $("bookModal")) closeModal();
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape" && !$("bookModal").hidden) {
    closeModal();
  }
});

loadBooks();