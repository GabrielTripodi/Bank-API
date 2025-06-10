import { sendRequest, getAlert, handleApiResponse } from "./utilities.js";

const loginButton = document.getElementById("login-btn");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const form = document.getElementById("login-form");

loginButton.addEventListener("click", async function () {
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }
  form.classList.remove("was-validated");

  const username = usernameInput.value;
  const password = passwordInput.value;
  const url = location.href;

  const data = { username: username, password: password };
  const response = await sendRequest(url, "POST", data);

  if (response.hasOwnProperty("failed")) {
    getAlert(
      "Error!",
      "Unable to connect to the server. Please check your network connection and try again.",
      "error"
    );
    return;
  }
  handleApiResponse(response, true);
});
