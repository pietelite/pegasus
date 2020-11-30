import animate, {delay} from "./animateplus.js";

const INDICATOR_DURATION = 500;

var genID = () => {
  return '_' + Math.random().toString(36).substr(2, 9);
};

function uploadToForm(button_id, form_id) {
    document.getElementById(button_id).click();
    document.getElementById(button_id).onchange = function(){document.getElementById(form_id).submit()};
}

const random = (min, max) =>
  Math.random() * (max - min) + min;

const randomColor = () => `rgb(${random(0, 255)},${random(0, 255)},${random(0, 255)})`

/* === WORKING OVERLAY WHEN UPLOADING === */
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


/* === FIX FORMS */
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

/* === ANIMATE CIRCULAR INDICATORS === */
var circIndicators = document.getElementsByClassName("circular-indicator");
var circ;

var createProcessingElements = () => {
    var processingElements = document.getElementsByClassName("processing-element")

    const content = {
      span: "Processing...",
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

    var processingElement;
    for (processingElement of processingElements) {
        processingElement.appendChild(dom);
    }

    const animateProcessing = async () => {
      await animate({
        elements,
        duration: 500,
        delay: index => index * 20,
        easing: "out-cubic",
        transform: ["translate(0px, 0px)", "0 -5"]
      });

      await animate({
        elements,
        duration: 1000,
        delay: index => index * 10,
        easing: "out-elastic 3 0.3",
        transform: ["translate(0px, -5px)", "0 0"]
      });

      await delay(100);
      animateProcessing();
    };
    animateProcessing();
}

createProcessingElements();

// const startIndicators = async (thumb) => {
//     await animate({
//       elements: thumb,
//       duration: INDICATOR_DURATION,
//       easing: "in-out-quartic",
//       transform: ["translate(0px, 0px)", "20 0"]
//     });
//     await animate({
//       elements: thumb,
//       duration: INDICATOR_DURATION,
//       easing: "in-out-quartic",
//       transform: ["translate(20px, 0px)", "0 20"]
//     });
//     await animate({
//       elements: thumb,
//       duration: INDICATOR_DURATION,
//       easing: "in-out-quartic",
//       transform: ["translate(0px, 20px)", "20 20"]
//     });
//     await animate({
//       elements: thumb,
//       duration: INDICATOR_DURATION,
//       easing: "in-out-quartic",
//       transform: ["translate(20px, 20px)", "0 0"]
//     });
//     startIndicators(thumb);
// };
// const changeColor = async (elem, duration) => {
//     elem.style.background = randomColor();
//     await delay(duration);
//     changeColor(elem, duration);
// }
//
// for (circ of circIndicators) {
//     Object.assign(circ.style, {
//         'position': 'relative',
//         'width': '20px',
//         'height': '20px',
//         'margin': '0 5px 0 5px',
//     });
//
//     var thumb = document.createElement('span');
//     Object.assign(thumb.style, {
//         position: 'absolute',
//         width: `5px`,
//         height: `5px`,
//         left: `0px`,
//         top: `0px`,
//         background: `white`,
//         borderRadius: '3px',
//     });
//     thumb.classList.add('circle-indicator-thumb')
//     circ.appendChild(thumb);
//     startIndicators(thumb);
//     delay(INDICATOR_DURATION/2).then(() => changeColor(thumb, INDICATOR_DURATION))
// }
