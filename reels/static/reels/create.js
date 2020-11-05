button_color_unclicked = '#104060'
button_color_clicked = '#F64086'

function uploadVideo() {
    document.getElementById('video_file_button').click();
    document.getElementById('video_file_button').onchange = function(){document.getElementById('upload_video_form').submit()};
};

function uploadAudio() {
    document.getElementById('audio_file_button').click();
    document.getElementById('audio_file_button').onchange = function(){document.getElementById('upload_audio_form').submit()};
};

var chosenPresetButton = document.getElementById('basic_button');
function presetClick(type) {
    Object.assign(chosenPresetButton.style, {
        backgroundColor: button_color_unclicked
    });
    chosenPresetButton = document.getElementById(type + '_button');
    Object.assign(chosenPresetButton.style, {
        backgroundColor: button_color_clicked
    })
    document.getElementById(type + '_radio').click();
}

/* Create form elements based on buttons */
for (but of document.getElementById('preset-container').getElementsByTagName('button')) {
    var radio = document.createElement("input");
    radio.type = 'radio';
    radio.id = but.value + '_radio';
    radio.name = 'preset';
    radio.value = but.value;
    if (but.value == 'basic') {
        radio.checked = 'checked';
        Object.assign(but.style, {
            backgroundColor: button_color_clicked
        });
    }
    Object.assign(radio.style, {
        display: 'none'
    });
    document.getElementById('preset-form').appendChild(radio);
}
