import { hasEmptyRequiredFields, showConfirmationAlert, API, sendRequest, getAlert, handleApiResponse, clearFields } from "./utilities.js";

const addButton = document.getElementById("add-btn");
const nameInput = document.getElementById("name");
const surnameInput = document.getElementById("surname");
const ibanInput = document.getElementById("iban");
const companyNameCheckbox = document.getElementById("company-name");

companyNameCheckbox.addEventListener("change", function () {
  surnameInput.disabled = this.checked;
  if (this.checked) {
    surnameInput.value = "";
  }
});

addButton.addEventListener("click", async function () {
  const name = nameInput.value;
  const surname = surnameInput.value;
  const iban = ibanInput.value;
  const isCompanyName = companyNameCheckbox.checked;

  if (hasEmptyRequiredFields(name, surname, iban, isCompanyName)) {
    return;
  }

  showConfirmationAlert(name, surname, iban, "add", isCompanyName).then(async (result) => {
    if (result.isConfirmed) {
      const url = `${API}ibans`;
      const data = {
        name: name,
        ...(!isCompanyName && { surname: surname }),
        iban: iban
      };
      const response = await sendRequest(url, "POST", data);

      if (response.hasOwnProperty("failed")) {
        getAlert(
          "Error!",
          "Unable to connect to the server. Please check your network connection and try again.",
          "error"
        );
        return;
      }

      handleApiResponse(response);
      if (response.ok) {
        clearFields(nameInput, surnameInput, ibanInput);
      }
    }
  });
});
