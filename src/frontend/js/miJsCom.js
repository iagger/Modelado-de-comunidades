

document.body.onload = cargaDatos;

const resultado = $.getJSON("http://localhost:8080/artworks/similarity/clustersHTML");


function cargaDatos() {
    cargaDatosIndice();  
    cargaIndice();
    cargaCluster();
    cargaDatosClusters();
};

function  cargaDatosIndice() {
    metadata = resultado.responseJSON.Metadata;
    // Descripcion
    $("#desc").html(metadata.Desc);
    // Tabla pesos
    $("#pAutor").html(metadata.Params.weights.Artist);
    $("#pTam").html(metadata.Params.weights.Size);
    $("#pColor").html(metadata.Params.weights.Dominantcolor);
    $("#pDepics").html(metadata.Params.weights.Depicts);
    $("#pMSE").html(metadata.Params.weights.Imagemse);
    // Algoritmo
    $("#algoritmo").html(metadata.Method);
    // Tabla paramentros
    $("#pEPS").html(metadata.Params.eps);
    $("#pSamples").html(metadata.Params.min_samples);
    $("#pModo").html(metadata.Params.mode);
};

function cargaIndice() {
    document.querySelector('#menuIzq').insertAdjacentHTML('beforeend','<li class="nav-item"> <a class="nav-link active" aria-current="page" href="#info" ><strong><h4>Información</strong></h4></a> </li>');
    i = 0;
    $.each(resultado.responseJSON.Clusters, function(ki, vi) {
        document.querySelector('#menuIzq').insertAdjacentHTML(
            'beforeend',
            '<li class="nav-item"> <a class="nav-link active" aria-current="page" href="#cluster' + i + '" ><strong><h4>' + "Cluster " + i + '</h4></strong></a> </li>');
        i++;
    });
};

function cargaCluster() {
    i = 0;
    $.each(resultado.responseJSON.Clusters, function(ki, vi) {
        document.querySelector('#fila').insertAdjacentHTML('beforeend',
        '<main class="col-md-9 ms-sm-auto col-lg-10 px-md-4" id="cluster' + i +'" name="cluster' + i + '">' +
        '<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">' +
        '<h1>Cluster ' + i + '</h1></div>' + 
        '<strong><h2 class="subTitulo"><u>' + "Número de integrantes del cluster " + '</u></h2></strong>'+
        '<strong><h4 id="nIndividuos' + i + '" name="nIndividuos' + i +'"></h4></strong><br>' +
        '<strong><h2 class="subTitulo"><u>Datos demograficos</u></h2></strong>' +
        '<strong><h3 class="subTitulo">Edad</h3></strong>' +
        '<div id="graphE' + i + '"name="graphE' + i + '" ></div><br>' +
        '<strong><h3 class="subTitulo">Nacionalidad</h3></strong>' +
        '<div id="graphN' + i + '"name="graphN' + i + '" ></div><br>' +
        '<strong><h3 class="subTitulo">Género</h3></strong>' +
        '<div id="graphG' + i + '"name="graphG' + i + '" ></div><br>');
        cargaCarrusel(i);
        document.querySelector("#cluster" + i).insertAdjacentHTML('beforeend',
        '<strong><h2 class="subTitulo"><u>Artistas mejor valorados</u></h2></strong>' +
        '<strong><h4 class="subTitulo" id="top1' + i + '"name="top1' + i + '"></h4></strong>' +
        '<strong><h4 class="subTitulo" id="top2' + i + '"name="top2' + i + '"></h4></strong>' +
        '<strong><h4 class="subTitulo" id="top3' + i + '"name="top3' + i + '"></h4></strong><br>' +
        '<strong><h2 class="subTitulo"><u>Artistas peor valorados</u></h2></strong>' +
        '<strong><h4 class="subTitulo" id="but1' + i + '"name="but1' + i + '"></h4></strong>' +
        '<strong><h4 class="subTitulo" id="but3' + i + '"name="but3' + i + '"></h4></strong>' +
        '<strong><h4 class="subTitulo" id="but3' + i + '"name="but3' + i + '"></h4></strong><br>' +
        '<strong><h2 class="subTitulo"><u>Movimiento artístico favorito</u></h2></strong>' +
        '<strong><h4 class="subTitulo" id="cat' + i + '"name="cat' + i + '"></h4></strong><br>' +
        '<strong><h2 class="subTitulo"><u>Emociones más frecuentes</u></h2></strong>' +
        '<div id="donut' + i + '"name="donut' + i + '" ></div><br>');
        document.querySelector('#fila').insertAdjacentHTML('beforeend', '</div><br><br></main>');
        i++;
    });
};

function cargaCarrusel(i){
    var aux = "#cluster" + i;
    document.querySelector(aux).insertAdjacentHTML('beforeend','<strong><h2 class="subTitulo"><u>Obras más populares</u></h2></strong>');
    document.querySelector(aux).insertAdjacentHTML('beforeend','<div id="carouselExampleControls' + i + '" class="carousel slide align="left"" data-bs-ride="carousel"></div>');
    document.querySelector("#carouselExampleControls"+i).insertAdjacentHTML('beforeend','<div class="carousel-inner" name="inT' + i + '" id="inT' + i + '"></div>');
    
    var cluster = "Cluster " + i;
    var seccion = resultado.responseJSON.Clusters[cluster].Artistic["Most valued"];
    var j = 0;
    $.each(seccion, function(ki, vi) {
        if (j== 0) {
            document.querySelector("#inT"+i).insertAdjacentHTML('beforeend','<div class="carousel-item active" name="carTopI' + i + '_' + j + '" id="carTopI' + i + '_' + j + '"></div>');
        }
        else {
            document.querySelector("#inT"+i).insertAdjacentHTML('beforeend','<div class="carousel-item" name="carTopI' + i + '_' + j + '" id="carTopI' + i + '_' + j + '"></div>');
        }
        document.querySelector("#carTopI"+i+ '_' + j).insertAdjacentHTML('beforeend','<div class="container  align="left"" name="carTop' + i + '_' + j + '" id="carTop' + i + '_' + j + '"></div>');
        document.querySelector("#carTop" + i + '_' + j).insertAdjacentHTML('beforeend',
        '<h5 class="display-8 subTitulo" id="tituloM'+ i + '_' + j + '" name="tituloM'+ i + '_' + j + '"><b></b></h5>'+
        '<h5 class="display-8 subTitulo" id="valPosM'+ i + '_' + j + '" name="valPosM'+ i + '_' + j + '"><b></b></h5>'+
        '<h5 class="display-8 subTitulo" id="valNegM'+ i + '_' + j + '" name="valNegM'+ i + '_' + j + '"><b></b></h5>'
        );
        document.querySelector("#carTopI"+i+ '_' + j).insertAdjacentHTML('beforeend',
        '<div class="container"><img class="d-block w-90" id="top' + i + '_' + j + '"name="top" width="400" height=""></div>');
        j++;
    });
    document.querySelector("#carouselExampleControls" + i).insertAdjacentHTML('beforeend',
    '<button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls' + i + '" data-bs-slide="prev">'+
    '<span class="carousel-control-prev-icon" aria-hidden="true"></span>'+
    '<span class="visually-hidden">Previous</span>'+
    '</button>'+
    '<button class="carousel-control-next" type="button" data-bs-target="#carouselExampleControls' + i + '" data-bs-slide="next">'+
    '<span class="carousel-control-next-icon" aria-hidden="true"></span>'+
    '<span class="visually-hidden">Next</span>'+
    '</button> <br><br>'
    );
    
    var aux = "#cluster" + i;
    document.querySelector(aux).insertAdjacentHTML('beforeend','<strong><h2 class="subTitulo"><u>Obras menos populares</u></h2></strong>');
    document.querySelector(aux).insertAdjacentHTML('beforeend','<div id="carouselExampleControls2' + i + '" class="carousel slide" data-bs-ride="carousel"></div>');
    document.querySelector("#carouselExampleControls2"+i).insertAdjacentHTML('beforeend','<div class="carousel-inner" name="inL' + i + '" id="inL' + i + '"></div>');
    
    seccion = resultado.responseJSON.Clusters[cluster].Artistic["Least valued"];
    j = 0;
    $.each(seccion, function(ki, vi) {
        if (j== 0) {
            document.querySelector("#inL"+i).insertAdjacentHTML('beforeend','<div class="carousel-item active" name="carTopT' + i + '_' + j + '" id="carTopT' + i + '_' + j + '"></div>');
        }
        else {
            document.querySelector("#inL"+i).insertAdjacentHTML('beforeend','<div class="carousel-item" name="carTopT' + i + '_' + j + '" id="carTopT' + i + '_' + j + '"></div>');
        }
        document.querySelector("#carTopT"+i+ '_' + j).insertAdjacentHTML('beforeend','<div class="container" name="carTo' + i + '_' + j + '" id="carTo' + i + '_' + j + '"></div>');
        document.querySelector("#carTo" + i + '_' + j).insertAdjacentHTML('beforeend',
        '<h5 class="display-8 subTitulo" id="tituloL'+ i + '_' + j + '" name="tituloL'+ i + '_' + j + '"><b></b></h5>'+
        '<h5 class="display-8 subTitulo" id="valPosL'+ i + '_' + j + '" name="valPosL'+ i + '_' + j + '"><b></b></h5>'+
        '<h5 class="display-8 subTitulo" id="valNegL'+ i + '_' + j + '" name="valNegL'+ i + '_' + j + '"><b></b></h5>'
        );
        document.querySelector("#carTopT"+i+ '_' + j).insertAdjacentHTML('beforeend',
        '<div class="container"><img class="d-block w-90" id="least'+ i + '_' + j + '" name="least'+ i + '_' + j + '" width="400" height=""></div>');
        j++;
    });
    document.querySelector("#carouselExampleControls2" + i).insertAdjacentHTML('beforeend',
    '<button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls2' + i + '" data-bs-slide="prev">'+
    '<span class="carousel-control-prev-icon" aria-hidden="true"></span>'+
    '<span class="visually-hidden">Previous</span>'+
    '</button>'+
    '<button class="carousel-control-next" type="button" data-bs-target="#carouselExampleControls2' + i + '" data-bs-slide="next">'+
    '<span class="carousel-control-next-icon" aria-hidden="true"></span>'+
    '<span class="visually-hidden">Next</span>'+
    '</button><br><br>'
    );
 
};

function cargaDatosClusters() {
    i = 0;
    $.each(resultado.responseJSON.Clusters, function(ki, vi) {
        $("#nIndividuos"+i).html(vi.Size + " individuos");
        cargaHistograma("graphE"+i, vi.Demographics.age);
        cargaHistograma("graphN"+i, vi.Demographics.country);
        cargaHistograma("graphG"+i, vi.Demographics.gender);
        cargaCarruselT(vi.Artistic["Most valued"], i);
        cargaCarruselL(vi.Artistic["Least valued"], i);
        $("#top1"+i).html('-'+vi.Artistic["Popular artists"][0]);
        $("#top2"+i).html('-'+vi.Artistic["Popular artists"][1]);
        $("#top3"+i).html('-'+vi.Artistic["Popular artists"][2]);
        $("#but1"+i).html('-'+vi.Artistic["Unpopular artists"][0]);
        $("#but2"+i).html('-'+vi.Artistic["Unpopular artists"][1]);
        $("#but3"+i).html('-'+vi.Artistic["Unpopular artists"][2]);
        $("#cat"+i).html('-'+vi.Artistic["Top Category"]);
        cargaSentimientos("donut"+i, vi.Emotions)
        i++;
    });
};

function cargaHistograma(name, dataD) {
    Morris.Bar({
        element: name,
        data: miAux(dataD),
        xkey: 'x',
        ykeys: ['y'],
        labels: ['Porcentaje']
    });
}

function miAux(dataD) {
    var arr = [];
    var i = 0;
    $.each(dataD, function(ki, vi) {
        arr[i]={x: ki , y: math.round(vi*100)};
        i++;
    });
    return arr;
}

function cargaSentimientos(name, dataD) {
    Morris.Donut({
        element: name,
        data: miAux2(dataD),
        formatter: function (x) { return x + "%"}
      }).on('click', function(i, row){
        console.log(i, row);
      });
}

function miAux2(dataD) {
    var arr = [];
    var i = 0;
    $.each(dataD, function(ki, vi) {
        arr[i]={value: math.round(vi*100), label: ki};
        i++;
    });
    return arr;
}

function cargaCarruselT(dataD, i) {
    var j = 0;
    $.each(dataD, function(ki, vi) {
        $("#tituloM"+i + "_" +j).html("Titulo: " + vi.Title);
        $("#valPosM"+i + "_" +j).html("Número valoraciones positivas: " + vi.Positive);
        $("#valNegM"+i + "_" +j).html("Número valoraciones negativas: "+ vi.Negative);
        document.getElementById("top"+i + "_" +j).src = vi.Image;
        j++;
    });
}

function cargaCarruselL(dataD, i) {
    var j = 0;
    $.each(dataD, function(ki, vi) {
        $("#tituloL"+i + "_" +j).html("Titulo: " + vi.Title);
        $("#valPosL"+i + "_" +j).html("Número valoraciones positivas: " + vi.Positive);
        $("#valNegL"+i + "_" +j).html("Número valoraciones negativas: "+ vi.Negative);
        document.getElementById("least"+i + "_" +j).src = vi.Image;
        j++;
    });
}









