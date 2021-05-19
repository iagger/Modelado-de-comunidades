var imagen, titulo, autor, categoria, idWiki, miPath;

const cuadros = $.getJSON("http://localhost:8080/artworks", function(resp) {
    $.each(resp, function(k, v) {
        $("#estados").append('<option name="' + v + '">' + v['Title'] + '</option>');
    }); 
});

function carga(v) {
    var i = 1;
    $.each(v, function(ki, vi) {
        document.getElementById("imagenes"+i).src = vi.Image;
        document.getElementById('titulo'+i).innerHTML = "Titulo: " + vi.Title;
        document.getElementById("autor"+i).innerHTML = "Autor: " + vi.Artist;
        document.getElementById("categoria"+i).innerHTML = "Movimiento: " + vi.Category;
        document.getElementById("indice"+i).innerHTML = "Indice de similitud: " + (vi.Similarity.toFixed(4) * 100) + "%";
        i++;
    });
};

function cargaPDF() {
    // var pdf = $.getJSON("http://localhost:8080/artworks/similarity/clusters");
    document.getElementById("miPdf").src = "kmed7_[60,10,10,10,10].pdf";
};

$("#ComDetectadas").click(function () {
    window.location="../index2.html";
    parent.location="../index2.html";
});

$("#simArts").click(function () {
    window.location="../index3.html";
    parent.location="../index3.html";
});

$("#estados").change(function() {
    console.log($("#estados").val());
    $.each(cuadros.responseJSON, function(key,value) {
        if ($("#estados").val() == value.Title) {
            imagen = value.Image;
            titulo = value.Title
            autor = value.Artist;
            categoria = value.Category;
            document.getElementById("artworkID").value = value.Id;
            document.getElementById("imagenes").src = imagen;
            $('#titulo').html("Titulo: " + titulo + "\n");
            $('#autor').html("Autor: " + autor + "\n");
            $('#categoria').html("Movimiento: " + categoria + "\n");
        }
    });
});

$("#aceptar").click(function () {
    var simAutor = $("#autorSim").val();
    var simSize = $("#sizeSim").val();
    var simColor = $("#colorSim").val();
    var simADepics = $("#depicsSim").val();
    var simrsm = $("#rsmSim").val();
    const str = '{ "Depicts" : ' + simADepics + ', "Size": ' + simSize + ', "Color": ' + simColor + ', "Artist": ' + simAutor + ', "ImageMSE": ' + simrsm + ' }';
    idWiki = document.getElementById("artworkID").value;
    miPath = "http://localhost:8080/artworks/similarity/artworkID?id=" + idWiki;
    $.post(miPath, str, function(resp) {
        $.each(resp, function(k, v) {
            if (k == "Similar artworks"){
                carga(v);
            };
        }); 
    });
});

