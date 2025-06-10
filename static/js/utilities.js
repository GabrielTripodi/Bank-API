export const SERVER = "http://localhost:5000/";

export const API = `${SERVER}api/v1/`;

export function getAlert(title, text, icon) {
  Swal.fire({
    title: title,
    text: text,
    icon: icon,
    confirmButtonText: "Ok",
    confirmButtonColor: "#3085d6",
    heightAuto: false,
    allowOutsideClick: false,
    allowEscapeKey: false
  });
}

export function showFailureAlert(title, text, icon) {
  Swal.fire({
    title: title,
    text: text,
    icon: icon,
    confirmButtonText: "Ok",
    confirmButtonColor: "#3085d6",
    heightAuto: false,
    allowOutsideClick: false,
    allowEscapeKey: false
  }).then((result) => {
    if (result.isConfirmed) {
      location.href = "/";
    }
  });
}

export async function sendRequest(url, method = "GET", data) {
  try {
    const options = { method: method };
    if (method === "POST" || method === "PUT") {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(data);
    }
    const response = await fetch(url, options);
    return response;
  } 
  catch (error) {
    console.error(`Request to ${url} failed: ${error.name} - ${error.message}`);
    return { failed: true };
  }
}

export function showConfirmationAlert(name, surname, iban, action, isCompanyName) {
  const htmlContent = `
    <div style="text-align: left;">
        ${
          isCompanyName
            ? `<p><strong>Company:</strong> ${name}</p>`
            : `<p><strong>Name:</strong> ${name}</p>
                <p><strong>Surname:</strong> ${surname}</p>`
        }
        <p><strong>IBAN:</strong> ${iban}</p>
    </div>
  `;
  const options = {
    title: "Are you sure?",
    html: htmlContent,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: `Yes, ${action} it`,
    allowOutsideClick: false,
    allowEscapeKey: false,
    heightAuto: false
  };
  return Swal.fire(options);
}

export async function handleApiResponse(response, redirectOnSuccess = false) {
  const result = await response.json();
  if (response.ok) {
    if (redirectOnSuccess) {
      location.href = "/";
    } 
    else {
      const title = result.message === "No changes have been made" ? "Info!" : "Success!";
      const icon = result.message === "No changes have been made" ? "info" : "success";
      getAlert(title, result.message, icon);
    }
  } 
  else {
    getAlert("Error!", result.error, "error");
  }
}

export function clearFields(nameInput, surnameInput, ibanInput) {
  nameInput.value = "";
  surnameInput.value = "";
  ibanInput.value = "";
}

export function disableInputFields(nameInput, surnameInput, ibanInput) {
  nameInput.disabled = true;
  surnameInput.disabled = true;
  ibanInput.disabled = true;
}

export function enableInputFields(nameInput, surnameInput, ibanInput) {
  nameInput.disabled = false;
  surnameInput.disabled = false;
  ibanInput.disabled = false;
}

export function hasEmptyRequiredFields(name, surname, iban, isCompanyName) {
  const trimmedName = name.trim();
  const trimmedSurname = surname.trim();
  const trimmedIban = iban.trim();
  if (isCompanyName && (trimmedName === "" || trimmedIban === "")) {
    getAlert("Error!", "Company name and IBAN are required", "error");
    return true;
  }
  if (!isCompanyName && (trimmedName === "" || trimmedSurname === "" || trimmedIban === "")) {
    getAlert("Error!", "All fields are required", "error");
    return true;
  }
  return false;
}
