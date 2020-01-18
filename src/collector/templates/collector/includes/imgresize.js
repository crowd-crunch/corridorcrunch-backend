<script type="text/javascript">
(function() {

var img = document.getElementById('imagecontainer').firstChild;
img.onload = function() {
    if(img.height > img.width) {
        img.height = '100%';
        img.width = 'auto';
    }
};

}());
</script>
