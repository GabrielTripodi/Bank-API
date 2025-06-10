import { API, sendRequest, showFailureAlert, getAlert, handleApiResponse, showConfirmationAlert, clearFields } from "./utilities.js";

let isCompanyName;
let ibanId = "";

async function setInputFields() {
  const url = `${API}ibans`;
  const response = await sendRequest(url);
  if (response.hasOwnProperty("failed") || !response.ok) {
      showFailureAlert("Error!", "Unable to retrieve IBAN list. Please try again later.", "error");
      return; 
  }
  const ibanRecords = await response.json();
  if (ibanRecords.length === 0) {
    showFailureAlert("Error!", "There is no iban to modify", "error")
    return;
  }
  const inputOptions = ibanRecords.reduce((options, record) => {
    const label = record.companyName
      ? `${record.iban} - ${record.companyName}`
      : `${record.iban} - ${record.firstName} ${record.lastName}`;
    options[record.iban] = label;
    return options;
  }, {});
  const { value: selectedIban } = await Swal.fire({
    title: "Select the IBAN to remove",
    input: "select",
    inputOptions: inputOptions,
    inputPlaceholder: "Select an IBAN",
    confirmButtonText: "Ok",
    confirmButtonColor: "#3085d6",
    heightAuto: false,
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      document.getElementsByTagName("option")[0].style.display = "none";
    },
    inputValidator: (value) => {
      return new Promise((resolve) => {
        if (ibanRecords.length > 0 && !value) {
          resolve("You need to select an IBAN");
        }
        else {
          resolve();
        }
      });
    },
  });
  const ibanRecord = ibanRecords.find(record => record.iban === selectedIban);
  if (ibanRecord) {
    ibanId = ibanRecord.id;
    nameInput.value = ibanRecord.firstName || ibanRecord.companyName;
    isCompanyName = Boolean(ibanRecord.companyName);
    surnameInput.value = ibanRecord.lastName || "";
    ibanInput.value = ibanRecord.iban;
  }
}

const removeButton = document.getElementById("remove-btn");
const nameInput = document.getElementById("name");
const surnameInput = document.getElementById("surname");
const ibanInput = document.getElementById("iban");
setInputFields();

document.getElementById("change-btn").addEventListener("click", async function() {
  setInputFields();
})

removeButton.addEventListener("click", async function() {
  const name = nameInput.value;
  const surname = surnameInput.value;
  const iban = ibanInput.value;
  

  showConfirmationAlert(name, surname, iban, "remove", isCompanyName).then(async (result) => {
    if (result.isConfirmed) {
      const url = `${API}ibans/${ibanId}`;
      const response = await sendRequest(url, "DELETE");

      if(response.hasOwnProperty("failed")) {
        getAlert("Error!", "Unable to connect to the server. Please check your network connection and try again.", "error");
        return;
      }

      handleApiResponse(response);
      if (response.ok) {
        clearFields(nameInput, surnameInput, ibanInput);
        ibanId = "";
      }
    }
  });  
});

