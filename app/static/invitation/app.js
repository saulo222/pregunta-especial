const emailStep = document.querySelector("#email-step");
const questionStep = document.querySelector("#question-step");
const successStep = document.querySelector("#success-step");
const emailForm = document.querySelector("#email-form");
const answerForm = document.querySelector("#answer-form");
const emailInput = document.querySelector("#email");
const emailError = document.querySelector("#email-error");
const answerError = document.querySelector("#answer-error");
const sendButton = document.querySelector("#send-button");

let visitorEmail = "";

function showStep(current, next) {
  current.classList.remove("step--active");
  current.hidden = true;
  next.hidden = false;
  next.classList.add("step--active");
}

emailForm.addEventListener("submit", (event) => {
  event.preventDefault();
  emailError.textContent = "";

  if (!emailInput.checkValidity()) {
    emailError.textContent = "Ingresa un correo electrónico válido para continuar.";
    emailInput.focus();
    return;
  }

  visitorEmail = emailInput.value.trim().toLowerCase();
  showStep(emailStep, questionStep);
  questionStep.querySelector("input[name='answer']").focus();
});

answerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  answerError.textContent = "";

  const formData = new FormData(answerForm);
  if (formData.get("answer") !== "yes") {
    answerError.textContent = "Selecciona “Sí, quiero” para enviar tu respuesta.";
    return;
  }

  sendButton.disabled = true;
  sendButton.firstChild.textContent = "Enviando... ";

  try {
    const response = await fetch("/api/invitation/respond", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: visitorEmail,
        answer: "yes",
        website: formData.get("website") || "",
      }),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.detail || "No pudimos enviar tu respuesta.");
    }

    showStep(questionStep, successStep);
  } catch (error) {
    answerError.textContent = error.message;
    sendButton.disabled = false;
    sendButton.firstChild.textContent = "Enviar mi respuesta ";
  }
});
