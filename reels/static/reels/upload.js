import animate, {delay} from "./animateplus.js";

var genID = () => {
  return '_' + Math.random().toString(36).substr(2, 9);
};

function uploadToForm(button_id, form_id) {
    document.getElementById(button_id).click();
    document.getElementById(button_id).onchange = function(){document.getElementById(form_id).submit()};
}

const random = (min, max) =>
  Math.random() * (max - min) + min;

var createWorkingElement = () => {
    var workingElement = document.createElement("div");
    workingElement.id = "working-element";
    var contentElement = document.getElementById("content")
    contentElement.append(workingElement);

    const content = {
      h1: "We're working on it...",
    };

    const elements = [];

    const dom = Object.entries(content).reduce((fragment, [type, text]) => {
      const node = text.split("").reduce((element, character) => {
        const span = document.createElement("span");
        span.textContent = character;
        if (character == " ") span.className = "space";
        elements.push(span);
        element.append(span);
        return element;
      }, document.createElement(type));

      fragment.append(node);
      return fragment;
    }, document.createDocumentFragment());

    workingElement.appendChild(dom);

    const play = async () => {
      await animate({
        elements,
        duration: 1000,
        delay: index => index * 10,
        easing: "in-out-exponential",
        opacity: [0, 1],
        transform: ["translate(300px) scale(1)", "0 1"]
      });

      await animate({
        elements,
        duration: 1500,
        delay: 500,
        easing: "out-circular",
        opacity: [1, 0],
        transform: () => [
          "translate(0vw, 0vh) scale(1) rotate(0turn)",
          `${random(-100, 100)} ${random(-100, 100)} ${random(5, 15)} ${random(-1, 1)}`
        ]
      });

      await delay(500);
      play();
    };
    play();
}

var form;
/* Map to find the input object from generated buttons */
var buttons = new Map();
for (form of document.getElementsByClassName("upload-form")) {
    var child;
    var button;
    for (child of form.childNodes) {
        if (child.tagName && child.tagName.toLowerCase() == "input") {
            if (child.type == "file") {
                console.log(child)
                button = document.createElement("button");

                /* Generate ID to be used for finding correct input later */
                child.id = genID();
                button.id = genID();
                buttons.set(button.id, child.id);

                /* Add button information and functionality */
                button.classList.add("reels-button");
                button.innerHTML = "Upload";
                button.addEventListener('click', function() {
                    document.getElementById(buttons.get(this.id)).click();
                });

                /* Set up uploading inputs */
                child.addEventListener('change', function() {
                    createWorkingElement();
                    this.parentElement.submit();
                })
                child.parentElement.parentElement.append(button);
            }
        }
    }
}
