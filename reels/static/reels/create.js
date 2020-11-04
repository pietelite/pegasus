function uploadVideo() {
    document.getElementById('video_file_button').click();
    document.getElementById('video_file_button').onchange = function(){document.getElementById('upload_video_form').submit()};
};

function uploadMusic() {
    document.getElementById('music_file_button').click();
    document.getElementById('music_file_button').onchange = function(){document.getElementById('upload_music_form').submit()};
};

var chosenPresetButton;
function presetClick(type) {
    if (chosenPresetButton) {
        Object.assign(chosenPresetButton.style, {
            backgroundColor: '#104060'
        });
    }
    chosenPresetButton = document.getElementById(type + '_button');
    Object.assign(chosenPresetButton.style, {
        backgroundColor: 'red'
    })
    document.getElementById(type + '_radio').click();
}

/* Create form elements based on buttons */
for (but of document.getElementById('preset-container').getElementsByTagName('button')) {
    var radio = document.createElement("input");
    radio.type = 'radio';
    radio.id = but.value + '_radio';
    radio.name = 'preset';
    Object.assign(radio.style, {
        display: 'none'
    });
    document.getElementById('preset-form').appendChild(radio);
}
