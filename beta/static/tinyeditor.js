tinymce.init({
    selector:'#tinytext',
    plugins: ['wordcount hr spellchecker lists'],
    toolbar: ['undo redo | bold italic underline strikethrough | alignleft aligncenter alignright | bullist numlist | blockquote hr indent outdent | removeformat'],
    menubar: false, //sorry scott that line above needs to be long
    width: 700, //px
    height: 600,
    element_format: 'html',
    init_instance_callback : function(editor) {
        editor.setContent(story)
        var freeTiny = document.querySelector('.tox .tox-notification--in');
        freeTiny.style.display = 'none';
    }
});