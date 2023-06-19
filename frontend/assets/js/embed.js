function send() {

    $('html,body').animate({ scrollTop: $("#showtime").offset().top }, 'slow');

    var photo_src = document.getElementById("formFile_src").files[0];

    if(photo_src === undefined){
        $('#modal-title').text('Not so fast!');
        $('#modal-text').text('Please, choose an input image.');
        $('#myModal').modal('show');
        return;
    }

    var data = new FormData();

    data.append("file", photo_src);

    wi = document.getElementById('wi').value;
    ni = document.getElementById('ni').value;
    mi= document.getElementById('mi').value;

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    $.ajax({
        type: 'POST',
        url: '/embed_watermark?' + $.param({'Wi': wi, 'ni': ni, 'mi': mi }),
        cache: false,
        contentType: false,
        processData: false,
        data: data,
        success: function (result) {
            console.log(result);
            var parent = document.getElementById('result_container');
            var result_img = document.getElementById("result_img");

            if (result_img != null) {
                parent.removeChild(result_img);
            }

            var result_img = document.createElement('img');
            result_img.id = "result_img";
            result_img.className = "img-fluid mx-auto d-block rounded";
            result_img.setAttribute("data-aos", "fade-bottom");
            result_img.style.marginTop = "5%";
            result_img.style.marginBottom = "5%";
            result_img.style.float = "none";
            result_img.src = result
            parent.append(result_img)

        },
        error: function (err) {
            // console.log(err);
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}


function sendUrl(valid_src) {

    valid = valid_src

    if (!valid) {
        $('#modal-title').text('Something Went Wrong :(')
        $("#modal-text").text("Make sure that you entered valid image URLs and try again.")
        $('#myModal').modal('show');
        return;
    }

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    wi = document.getElementById('wi').value;
    ni = document.getElementById('ni').value;
    mi= document.getElementById('mi').value;

    $.ajax({
        type: 'GET',
        url: '/embed_watermark',
        cache: false,
        contentType: false,
        processData: false,
        data: $.param({ 'url': photo_src_url,
                        'Wi': wi,
                        'ni': ni,
                        'mi': mi }),
        success: function (result) {
            console.log(result);
            parent = document.getElementById('result_container');
            result_img = document.getElementById("result_img");

            if (result_img != null) {
                parent.removeChild(result_img);
            }

            result_img = document.createElement('img');
            result_img.id = "result_img";
            result_img.className = "img-fluid mx-auto d-block rounded";
            result_img.setAttribute("data-aos", "fade-bottom");
            result_img.style.marginTop = "5%";
            result_img.style.marginBottom = "5%";
            result_img.style.float = "none";
            result_img.src = result
            parent.append(result_img)

        },
        error: function (err) {
            
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}