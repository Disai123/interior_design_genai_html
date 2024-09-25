document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("design-form");
  const emailInput = document.getElementById("email");
  const errorMessage = document.getElementById("error-message");
  const imageContainer = document.getElementById("result-container");
  const resultImage = document.getElementById("result-image");

  let imageURL = "";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
      api_key: document.getElementById("api_key").value,
      selected_room_type: document.getElementById("selected_room_type").value,
      selected_style: document.getElementById("selected_style").value,
      selected_room_color: document.getElementById("selected_room_color").value,
      additional_instructions: document.getElementById(
        "additional_instructions"
      ).value,
      email: emailInput.value,
    };

    console.log(formData);

    try {
      const response = await fetch("http://127.0.0.1:8000/generateImage/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.ok) {
        imageURL = result.image;
        resultImage.src = imageURL;
        resultImage.style.display = "block";
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      errorMessage.textContent = `Error: ${error.message}`;
    }
  });

  document.getElementById("send-email").addEventListener("click", async (e) => {
    e.preventDefault();

    const email = emailInput.value;
    const selected_room_type =
      document.getElementById("selected_room_type").value;
    const selected_style = document.getElementById("selected_style").value;
    const selected_room_color = document.getElementById(
      "selected_room_color"
    ).value;
    const additional_instructions = document.getElementById(
      "additional_instructions"
    ).value;

    if (imageURL && email) {
      try {
        const response = await fetch("http://127.0.0.1:8000/sendEmail/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email1: email,
            imageUrl: imageURL,
            Selected_type:selected_room_type,
            Selected_style: selected_style,
            Selected_color:selected_room_color,
          }),
        });

        if (response.ok) {
          alert("Email sent successfully!");
        } else {
          const result = await response.json();
          throw new Error(result.error);
        }
      } catch (error) {
        alert(`Failed to send email. Error: ${error.message}`);
      }
    } else {
      alert("Please generate an image and provide an email address.");
    }
  });
});
