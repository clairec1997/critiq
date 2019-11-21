tinymce.init({
    selector:'#tinytext',
    plugins: ['wordcount hr spellchecker'],
    toolbar: ['undo redo | bold italic underline strikethrough |', 
            'alignleft aligncenter alignright |',
            'bullist numlist | blockquote hr | removeformat'],
    menubar: false,
    width: 600, //px
    height: 300,
    element_format: 'html',
    //skin: 'someskin',
    //content_css: 'somefile.css'
});